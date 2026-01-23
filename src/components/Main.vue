<script setup lang="ts">
import Header from '@/components/general/Header.vue';
</script>
<template>
    <div class="w-full h-full flex flex-col">
        <Header class="h-10"></Header>
        <router-view v-slot="{ Component }" class="flex-1">
            <transition
            name="page"
            mode="out-in"
            >
            <component :is="Component" />
            </transition>
        </router-view>
    </div>
</template>

<style>
.page-enter-active,
.page-leave-active {
  transition: all 0.15s ease-out;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>