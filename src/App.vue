<script setup lang="ts">
// import { ref } from "vue";
// import { invoke } from "@tauri-apps/api/core";

// const greetMsg = ref("");
// const name = ref("");

// async function greet() {
//   // Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
//   greetMsg.value = await invoke("greet", { name: name.value });
// }
import Header from '@/components/general/Header.vue';
import Main from '@/components/Main.vue';
</script>

<template>
  <Header class="bg-red-300"/>
  <Main class="h-full"/>
</template>
