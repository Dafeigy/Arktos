# Arktos Pipeline 架构设计

## 1. 设计目标

Arktos 的 Guard 服务需要在 LLM 请求进入模型之前完成输入审查，并满足企业内部应用的低延迟、高并发和可扩展要求。

核心目标：

- 基于 FastAPI 构建异步 HTTP 服务。
- 支持 300+ 并发请求。
- 支持可插拔检测管道，每个检测器可独立启用、禁用、排序和配置。
- 支持规则、PII、注入/越狱、内容安全等检测器并行执行。
- 支持高危命中后的早期短路，并尽快取消其他耗时检测。
- 输出统一三态结果：`Blocked`、`Masked`、`Passed`。

## 2. 总体架构

建议请求链路如下：

```text
Client
  |
  v
FastAPI Guard Service
  |
  v
Request Middleware
  |
  v
Preprocessor
  |
  v
Schema Validator
  |
  v
Pipeline Orchestrator
  |
  +--> Rule Engine Detector
  +--> PII Detector
  +--> Prompt Injection Detector
  +--> Content Safety Detector
  +--> Custom Detector
  |
  v
Policy Decision Engine
  |
  v
Audit Logger
  |
  v
Response
```

## 3. 三态决策模型

Arktos 对外只暴露三种最终状态：

- `Blocked`：请求被阻断，不允许继续调用下游 LLM。
- `Masked`：请求可继续调用下游 LLM，但原始输入已被脱敏或替换。
- `Passed`：请求通过审查，原始输入可继续传递。

内部检测器可以返回更细的风险信号，但最终由策略决策器收敛到这三种状态。

建议优先级：

```text
Blocked > Masked > Passed
```

示例：

- 命中高危越狱规则：`Blocked`
- 命中手机号、邮箱、Token 等敏感信息且策略允许脱敏：`Masked`
- 未命中任何风险或仅命中低风险观察项：`Passed`

## 4. Pipeline 分层

### 4.1 预处理层

职责：

- Unicode 规范化，例如 NFKC。
- 移除或标记不可见字符。
- 标准化换行、空白和控制字符。
- 基础编码处理。
- 保留原文与规范化文本，方便审计与脱敏回写。

注意事项：

- 预处理不应直接丢弃业务内容。
- 对不可见字符建议记录风险信号，因为它可能是绕过检测的手段。

### 4.2 结构校验层

职责：

- 校验文本长度。
- 校验必填字段。
- 识别语言或文本类型。
- 校验应用、租户、策略等元数据。

建议：

- 超长输入可以直接 `Blocked` 或按策略截断后检测。
- 结构校验属于廉价同步步骤，应在并行检测前完成。

### 4.3 并行检测层

检测器按配置组成执行计划。常见检测器包括：

- 规则引擎：关键词、正则、字典、白名单。
- PII 检测：本地规则 + 可选 LLM/API 辅助识别 + 脱敏建议。
- 注入/越狱分类模型：本地轻量模型或远程模型 API。
- 内容安全分类模型：本地分类器或第三方审核服务。
- 自定义检测器：业务团队注入的规则或模型。

并行检测层应支持：

- 每个检测器独立超时。
- 每个检测器独立错误隔离。
- 全局请求超时。
- 高危结果触发短路。
- 对运行中的慢任务发出取消信号。

### 4.4 策略决策层

职责：

- 聚合各检测器结果。
- 根据策略优先级决策最终状态。
- 合并脱敏建议。
- 生成审查原因、命中规则、风险标签和 trace ID。

建议策略逻辑：

- 任一检测器返回强阻断信号，最终结果为 `Blocked`。
- 无阻断但存在脱敏建议，最终结果为 `Masked`。
- 无阻断、无脱敏建议，最终结果为 `Passed`。

重要约束：

- 检测器不直接决定最终响应，只产出风险信号或文本变换建议。
- 策略决策器负责将多个检测器结果合并为唯一最终状态。
- Masked 文本不建议由单个检测器直接覆盖生成，应由统一的 Mask 合并器基于片段建议重建。

## 5. 检测器插件协议

检测器可以按职责分为两类：

- `SignalDetector`：只负责检测 `Blocked` / `Passed`，例如高危关键词、Prompt Injection、Jailbreak、内容安全分类。
- `TransformDetector`：负责检测 `Masked` / `Blocked` / `Passed`，例如 PII、密钥、内部资产标识、业务敏感词检测。

两类检测器都不直接返回最终响应。区别在于 `TransformDetector` 可以额外返回 `mask_spans`，也就是“建议替换哪些文本片段，以及替换成什么”。

建议每个检测器实现统一接口：

```python
from typing import Protocol

class Detector(Protocol):
    name: str
    priority: int
    timeout_ms: int
    enabled: bool
    can_short_circuit: bool

    async def detect(self, context: "GuardContext") -> "DetectorResult":
        ...
```

建议检测器声明能力：

```python
class DetectorCapabilities:
    can_block: bool
    can_mask: bool
    can_pass: bool = True
```

建议检测器结果：

```python
class DetectorResult:
    detector: str
    status: str  # Blocked, Masked, Passed
    risk_level: str  # low, medium, high, critical
    reason_codes: list[str]
    matches: list[dict]
    mask_spans: list["MaskSpan"]
    should_short_circuit: bool
    metadata: dict
```

建议 Mask 片段模型：

```python
class MaskSpan:
    start: int
    end: int
    replacement: str
    mask_type: str  # pii, secret, keyword, internal_asset
    priority: int
    confidence: float
    detector: str
    reason_code: str
```

设计要点：

- 检测器不直接决定最终响应，只提供风险信号。
- `should_short_circuit=True` 表示该结果足以立即结束其他检测。
- `mask_spans` 是候选脱敏建议，最终由策略层统一合并。
- 检测器必须是无状态或弱状态，便于横向扩展。
- `SignalDetector` 不返回 `mask_spans`。
- `TransformDetector` 可以同时返回阻断信号和脱敏建议，例如命中普通手机号时建议 `Masked`，命中私钥时建议 `Blocked`。

## 6. Mask 合并策略

多个检测器可能同时命中同一段或相邻文本。例如邮箱检测器、账号检测器和企业词典检测器可能都命中 `alice@example.com` 的不同子串。为了避免文本被多次替换、索引错位或检测器互相覆盖，建议使用“片段提案 + 统一重建”的合并方法。

### 6.1 合并原则

- 所有 `MaskSpan` 的 `start` / `end` 都基于同一份规范化后的输入文本。
- 检测器只提交片段替换建议，不提交完整 `masked_text`。
- 策略层先解决片段冲突，再一次性重建最终文本。
- 重叠片段只保留一个获胜片段。
- 非重叠片段全部保留。
- 最终状态为 `Masked` 时，响应中返回合并后的 `masked_text`。

### 6.2 冲突解决规则

建议按以下顺序决定重叠片段的获胜者：

1. 阻断优先：如果任一结果为 `Blocked`，直接进入阻断决策，不再需要生成最终 Masked 文本。
2. 策略优先级：`priority` 越小优先级越高。
3. 风险类型优先级：例如 `secret > pii > internal_asset > keyword`。
4. 覆盖范围优先：范围更长的片段优先，避免只遮掉局部 token。
5. 置信度优先：`confidence` 更高的片段优先。
6. 稳定排序：以上都相同则按 `start` 更小、检测器名称字典序排序，保证结果可复现。

### 6.3 推荐算法

推荐把合并过程拆成三步：收集、裁决、重建。

```python
def merge_mask_spans(text: str, spans: list[MaskSpan]) -> tuple[str, list[MaskSpan]]:
    sorted_spans = sorted(
        spans,
        key=lambda span: (
            span.start,
            span.end - span.start,
            -span.confidence,
        ),
    )

    accepted: list[MaskSpan] = []

    for span in sorted_spans:
        if span.start >= span.end:
            continue

        overlaps = [
            accepted_span
            for accepted_span in accepted
            if not (span.end <= accepted_span.start or span.start >= accepted_span.end)
        ]

        if not overlaps:
            accepted.append(span)
            continue

        winner = choose_mask_winner([span, *overlaps])
        if winner is span:
            accepted = [
                accepted_span
                for accepted_span in accepted
                if accepted_span not in overlaps
            ]
            accepted.append(span)

    accepted.sort(key=lambda span: span.start)

    chunks = []
    cursor = 0
    for span in accepted:
        chunks.append(text[cursor:span.start])
        chunks.append(span.replacement)
        cursor = span.end
    chunks.append(text[cursor:])

    return "".join(chunks), accepted
```

`choose_mask_winner` 应由策略配置驱动，而不是写死在检测器里：

```python
MASK_TYPE_RANK = {
    "secret": 0,
    "pii": 1,
    "internal_asset": 2,
    "keyword": 3,
}

def choose_mask_winner(spans: list[MaskSpan]) -> MaskSpan:
    return min(
        spans,
        key=lambda span: (
            span.priority,
            MASK_TYPE_RANK.get(span.mask_type, 99),
            -(span.end - span.start),
            -span.confidence,
            span.start,
            span.detector,
        ),
    )
```

### 6.4 决策器合并流程

策略决策器建议按下面顺序工作：

1. 聚合所有检测器结果。
2. 如果存在 `Blocked` 结果，返回 `Blocked`，并记录阻断原因。
3. 收集所有 `MaskSpan`。
4. 使用 Mask 合并器生成 `masked_text` 和最终采纳片段。
5. 如果采纳片段非空，返回 `Masked`。
6. 否则返回 `Passed`。

伪代码：

```python
def decide(context: GuardContext, results: list[DetectorResult]) -> GuardDecision:
    blocking_results = [result for result in results if result.status == "Blocked"]
    if blocking_results:
        return GuardDecision(
            status="Blocked",
            text=None,
            reason_codes=collect_reason_codes(blocking_results),
        )

    spans = [
        span
        for result in results
        for span in result.mask_spans
    ]

    masked_text, accepted_spans = merge_mask_spans(context.normalized_text, spans)

    if accepted_spans:
        return GuardDecision(
            status="Masked",
            text=masked_text,
            mask_spans=accepted_spans,
            reason_codes=collect_reason_codes(results),
        )

    return GuardDecision(status="Passed", text=context.original_text)
```

### 6.5 实现注意事项

- 如果预处理会改变文本长度，必须维护 original text 与 normalized text 的 offset 映射。
- 首期为了降低复杂度，可以要求所有检测器基于 normalized text 工作，并返回 normalized text 的 Masked 结果。
- 对用户实际传给 LLM 的文本，建议使用 `masked_text`，而不是让上游应用自行替换。
- 审计日志只记录采纳后的 `MaskSpan`，未采纳的冲突片段可放入 debug 级别或采样日志。
- 对密钥、私钥、访问令牌等高危内容，策略可以直接把 `TransformDetector` 的结果提升为 `Blocked`，不必返回 `Masked`。

## 7. 并行执行与早期短路

推荐使用 Python `asyncio` 作为第一版并发模型。FastAPI 本身适合异步 I/O，远程模型/API 调用也应使用异步 HTTP 客户端。

核心思路：

1. 先执行廉价且确定性强的预处理和结构校验。
2. 将检测器按策略分组。
3. 对并行组创建 `asyncio.Task`。
4. 使用 `asyncio.as_completed` 或 `asyncio.wait(..., return_when=FIRST_COMPLETED)` 消费结果。
5. 如果某个结果触发 `should_short_circuit`，立即取消未完成任务。
6. 对取消失败或不响应取消的远程调用设置较短超时。

伪代码：

```python
async def run_pipeline(context: GuardContext, detectors: list[Detector]) -> GuardDecision:
    tasks = {
        asyncio.create_task(run_detector(detector, context)): detector
        for detector in detectors
        if detector.enabled
    }
    results = []

    try:
        while tasks:
            done, pending = await asyncio.wait(
                tasks.keys(),
                return_when=asyncio.FIRST_COMPLETED,
                timeout=context.remaining_timeout,
            )

            if not done:
                break

            for task in done:
                detector = tasks.pop(task)
                result = await collect_result(task, detector)
                results.append(result)

                if result.should_short_circuit:
                    for pending_task in pending:
                        pending_task.cancel()
                    await asyncio.gather(*pending, return_exceptions=True)
                    return decide(results)

    finally:
        for task in tasks:
            if not task.done():
                task.cancel()

    return decide(results)
```

关键注意点：

- 任务取消并不等于远程 HTTP 请求一定立刻终止，因此每个远程检测器必须配置客户端超时。
- 对 LLM/API 类检测器应设置连接池、最大连接数和重试上限。
- 早期短路应主要由本地高危规则触发，避免远程模型结果反复打断其他任务造成不可预测延迟。

## 8. 检测器排序策略

虽然并行检测可以降低总耗时，但仍建议保留排序语义，用于执行计划生成：

- `priority` 越小越早执行。
- 高危本地规则可放入 `pre_gate` 阶段，先于其他并行检测执行。
- 普通规则、PII、内容安全和模型检测进入 `parallel` 阶段。
- 依赖前置结果的检测器进入 `post` 阶段。

建议阶段：

```text
pre_gate
  - 高危关键词
  - 明确阻断规则

parallel
  - 普通规则引擎
  - PII 检测
  - 注入/越狱分类
  - 内容安全分类

post
  - 脱敏合并
  - 策略决策
  - 审计输出
```

这样既能支持可排序检测器，也能保证高危规则尽早拦截。

## 9. 300+ 并发性能建议

### 9.1 服务运行

建议部署方式：

```text
uvicorn workers/processes + async I/O + connection pooling
```

示例参数方向：

- 多进程 worker：按 CPU 核数设置，例如 `2 * CPU + 1` 起步压测。
- 单 worker 内使用异步并发处理 I/O。
- 为远程模型/API 客户端设置连接池上限。
- 为每个请求设置全局 deadline。

### 9.2 超时预算

建议首期预算：

- 总请求超时：`500ms - 1000ms`
- 本地规则检测：`10ms - 50ms`
- PII 本地检测：`20ms - 80ms`
- 远程 PII/LLM 检测：`200ms - 600ms`
- 注入/越狱模型：`100ms - 300ms`
- 内容安全模型：`100ms - 300ms`

实际值需要通过压测校准。

### 9.3 限流与背压

为了保证 300+ 并发下系统稳定，建议：

- 对远程模型检测器增加 semaphore 并发上限。
- 对每个租户/应用配置 QPS 限制。
- 对慢检测器启用降级策略。
- 超时后可按策略选择 `Blocked`、`Passed with audit` 或 `Review`，但对外仍收敛为三态时建议映射为 `Blocked` 或 `Passed`。

## 10. 审计日志设计

审计日志建议异步输出，避免阻塞主请求路径。

建议记录：

- `trace_id`
- `tenant_id`
- `app_id`
- `user_id_hash`
- `policy_id`
- `final_status`
- `risk_level`
- `reason_codes`
- `matched_rules`
- `detector_results`
- `latency_ms`
- `short_circuited`
- `created_at`

敏感注意事项：

- 默认不存储原文。
- 如需排障，可只存脱敏文本、哈希摘要或受控采样。
- 审计日志中的命中片段也要二次脱敏。

## 11. 推荐首期实现顺序

1. 定义请求、响应、上下文和检测器结果模型。
2. 实现预处理与结构校验。
3. 实现检测器插件协议。
4. 实现本地规则引擎，并支持高危短路。
5. 实现 PII 检测与 `MaskSpan` 产出。
6. 实现 Mask 合并器。
7. 实现异步 Pipeline Orchestrator。
8. 实现策略决策器，将结果收敛为 `Blocked`、`Masked`、`Passed`。
9. 实现审计日志异步输出。
10. 添加并发压测脚本，验证 300+ 并发目标。

## 12. 首期验收标准

- 支持 `POST /v1/inspect`。
- 支持按配置启用、禁用、排序检测器。
- 支持规则、PII、注入/越狱、内容安全四类检测器并行执行。
- 命中高危规则时能够立即返回 `Blocked`。
- 早期短路时未完成检测器会收到取消信号。
- 支持多个 Masked 检测器产出的 `MaskSpan` 合并。
- 重叠 Mask 片段可按策略优先级稳定裁决。
- 返回结果只包含 `Blocked`、`Masked`、`Passed` 三种状态之一。
- 在压测环境中达到 300+ 并发，且无明显连接泄漏、任务泄漏和审计阻塞。
