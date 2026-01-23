<script setup lang="ts">
import Badge from '@/components/ui/badge/Badge.vue';
import Button from '@/components/ui/button/Button.vue';
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Crop } from 'lucide-vue-next'
import { Kbd, KbdGroup } from '@/components/ui/kbd'
</script>
<template>
    <div class="h-full w-full flex justify-start items-center flex-col">
        <div id='top' class="flex justify-center items-center mt-16 flex-col">
        <div id="banner" class="flex">
            <h1 class="text-4xl font-bold">Arktos Screentshot</h1>
            <Badge class="ml-2 h-5 min-w-5 rounded-full px-1 font-mono tabular-nums">v0.1.0</Badge>
        </div>
        <p>Professional Windows Screenshot Workflow</p>
    </div>
    <div id='middle' class="w-1/2 bg-sidebar rounded-2xl flex-col mt-4 flex justify-center items-center py-8">
        <div class="w-full flex justify-center py-2 items-center px-8">
            <Button class="w-1/3 mx-1"><Crop/>Region</Button>
            <Button class="w-1/3 mx-1"><Crop/>Screen</Button>
            <Button class="w-1/3 mx-1"><Crop/>Windows</Button>
        </div>
        <div class="w-full ">
            <div class="flex items-center justify-between px-8 mt-4">
                <div>
                    <p class="text-lg font-bold">Auto-apply background</p>
                    <Label for="autoapplybackground" class="text-sm text-gray-400">Apply default background and save instantly</Label>
                </div>
                <Switch id="autoapplybackground" />
            </div>
        </div>
    </div>
    <div id='bottom' class="w-1/2 bg-sidebar rounded-2xl flex-col mt-4 flex justify-center items-center py-4">
        <div class="w-full px-8">
            <p class="text-lg font-bold ">Keyboard Shorcut</p>
        </div>
        <div class="w-full px-8">
            <Label class="text-sm text-gray-400 mt-2">CAPTURE</Label>
            <div class="w-full grid grid-cols-2 gap-2">
                <div v-for="i in 4" :key="i" class="flex justify-between items-center h-6 text-center">
                    <p class="text-xs">Cancel</p>
                    <KbdGroup>
                        <Kbd>⌘</Kbd>
                        <span>+</span>
                        <Kbd>B</Kbd>
                    </KbdGroup>
                </div>
            </div>
            <Label class="text-sm text-gray-400 my-2">EDITOR</Label>
            <div class="w-full grid grid-cols-2 gap-2">
                <div v-for="i in 6" :key="i" class="flex justify-between items-center h-6 text-center">
                    <p class="text-xs">Cancel</p>
                    <KbdGroup>
                        <Kbd>⌘</Kbd>
                        <span>+</span>
                        <Kbd>B</Kbd>
                    </KbdGroup>
                </div>
            </div>
        </div>
    </div>
    </div>
    
</template>