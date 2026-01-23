<script setup lang="ts">
import Header from '@/components/general/Header.vue';
</script>
<template>
    <div class="w-full h-full flex flex-col">
        <Header class="h-10"></Header>
        <router-view class="flex-1"></router-view>    
    </div>
</template>