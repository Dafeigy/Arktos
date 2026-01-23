<script setup lang="ts">
// import { ref } from "vue";
// import { invoke } from "@tauri-apps/api/core";

// const greetMsg = ref("");
// const name = ref("");

// async function greet() {
//   // Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
//   greetMsg.value = await invoke("greet", { name: name.value });
// }
import Main from '@/components/Main.vue';
</script>

<template class="flex flex-col">
  <Main class="h-screen w-screen flex flex-col"/>
</template>
