<script setup lang="ts">
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ArrowLeft, Clipboard, Folder,Upload } from 'lucide-vue-next'
import Switch from '@/components/ui/switch/Switch.vue';
import { Kbd, KbdGroup } from '@/components/ui/kbd'
import { useRouter } from 'vue-router'
const router = useRouter()
const routeToSettings = () => {
    router.push('/')
}
</script>
<template>
    <div class="w-full overflow-auto h-full flex justify-center items-center transition-all! duration-400! ease-linear! my-8">
        <div id="settings-container" class="w-3/5 h-full px-4 py-4 max-w-[768px] ">
            <header class="w-full h-16 flex items-center justify-start">
                <Button variant="ghost" size="icon" @click="routeToSettings">
                    <ArrowLeft />
                </Button>
                <div class="flex flex-col justify-start mx-4">
                    <p class="text-2xl font-bold">Preference</p>
                    <p class="text-sm text-gray-400">Configure your app settings</p>
                </div>
            </header>
            <Separator class="mt-1" />
            <div class="mt-4 h-auto">
                <div class="rounded-xl my-2 h-1/4 bg-sidebar px-8 py-4" id="general-setting">
                    <p class="text-xl font-bold">General</p>
                    <div>
                        <div class="flex text-sm">
                            <div class="flex items-center py-2">
                                <Folder class="w-4.5 h-4.5"/>
                                <p class="mx-2">Save Directory</p>
                            </div>
                        </div>
                        <Input placeholder="Select save directory" />
                        <p class="text-xs mt-2">Screenshot will be saved to this directory</p>
                    </div>
                    <div class="w-full mt-4">
                        <div class="flex text-sm ">
                            <div class="flex items-center py-2 justify-between w-full">
                                <div class="">
                                    <div class="flex">
                                        <Clipboard class="w-4.5 h-4.5"/>
                                        <p class="mx-2">copy to clipboard</p>
                                    </div>
                                    
                                    <p class="text-xs mt-2">
                                        Automatically copy screenshots to clipboard after saving
                                    </p>
                                </div>
                                <Switch />
                            </div>
                        </div>
                    </div>
                </div>
                <div class="rounded-xl my-2 h-1/4 bg-sidebar px-8 py-4 mt-8" id="background-editor">
                    <p class="text-xl font-bold">Default Background</p>
                    <div class="flex justify-between items-center mt-8">
                        <p class="text-sm">Default Background Image</p>
                        <Button class="cursor-pointer">
                            <Upload />Upload
                        </Button>
                    </div>
                    <div class="grid grid-cols-4 gap-4 mt-4">
                        <div v-for="i in 7" :key="i" class=" duration-350 ease-in-out flex justify-center items-center aspect-square rounded-2xl cursor-pointer bg-select-dsplay" :style="{ backgroundImage: `url(/src/assets/bg-imgs/${i%5+1}.jpeg)` }"> </div>
                    </div>

                    <div class="flex justify-between items-center mt-8">
                        <p class="text-sm">Windows/MacOS/Linux Assets</p>
                    </div>
                    <div class="grid grid-cols-4 gap-4 mt-4">
                        <div v-for="i in 7" :key="i" class=" duration-350 ease-in-out flex justify-center items-center aspect-square rounded-2xl cursor-pointer bg-select-dsplay" :style="{ backgroundImage: `url(/src/assets/bg-imgs/${i%5+1}.jpeg)` }"> </div>
                    </div>
                </div>
                <div class="rounded-xl mb-20 h-1/4 bg-sidebar px-8 py-4 mt-8" id="keyboard-shortcut-editor">
                    <p class="text-xl font-bold select-none">Keyboard Shortcuts</p>
                    <div class="w-full mt-4">
                        <p class="text-sm text-foreground/50 select-none">Keyboard Shortcuts</p>
                        <div class="flex mt-2 flex-col gap-2">
                            <div v-for="i in 3" :key="i" class="bg-background rounded-lg px-4 flex items-center py-4 justify-between w-full">
                                <p class="text-sm text-foreground/50">
                                    {{ i === 1 ? 'Save Screenshot' : i === 2 ? 'Open Save Directory' : i === 3 ? 'Open App Directory' : i === 4 ? 'Open App Logs' : i === 5 ? 'Restart App' : 'Exit App' }}
                                </p>
                                <div class="flex gap-2">
                                    
                                    <KbdGroup class="cursor-pointer p-1 rounded text-xs bg-background/80 hover:bg-secondary transition-colors! duration-400">
                                        <Kbd>⌘</Kbd>
                                        <span>+</span>
                                        <Kbd>E</Kbd>
                                    </KbdGroup>
                                    <Button size="sm" class="cursor-pointer" variant="ghost">Enable</Button>
                                </div>
                                
                            </div>
                            <div v-for="i in 3" :key="i" class="hidden bg-background rounded-lg px-4 flex items-center py-4 justify-between w-full">
                                <Input placeholder="Press shortcut" size="sm"></Input>
                                <div class="flex gap-2">
                                    <Button size="sm" class="cursor-pointer" variant="ghost">Cancel</Button>
                                </div>
                                <div class="flex gap-2">
                                    <Button size="sm" class="cursor-pointer" variant="ghost">Enable</Button>
                                </div>
                                
                            </div>
                        </div>
                    </div>
                    
                    <Separator class="mt-4" />
                    <div class="w-full mt-4" >
                        
                        <p class="text-sm text-foreground/50 select-none">EDITOR</p>
                        <div class="grid grid-cols-2 gap-4 mt-2">
                            <div v-for="i in 6" :key="i" class=" flex items-center py-1 justify-between w-full">
                                <p class="text-sm text-foreground/50 select-none">
                                    {{ i === 1 ? 'Save Screenshot' : i === 2 ? 'Open Save Directory' : i === 3 ? 'Open App Directory' : i === 4 ? 'Open App Logs' : i === 5 ? 'Restart App' : 'Exit App' }}
                                </p>
                                <KbdGroup class="cursor-pointer bg-sidebar p-1 rounded text-xs hover:bg-secondary transition-colors! duration-400">
                                    <Kbd>⌘</Kbd>
                                    <span>+</span>
                                    <Kbd>E</Kbd>
                                </KbdGroup>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
        </div>
       
    </div>
</template>

<style scoped>
::-webkit-scrollbar {
  height: 6px;
  margin: 0 12px;
}
::-webkit-scrollbar-track {
  background-color: #2a2b2d;
  border-radius: 2px;
}

::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 2px;
  transition: background-color 0.2s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: #777;
}

* {  
  scrollbar-color: transparent transparent;
  transition: scrollbar-color 0.2s ease;
}
*:hover {  
  scrollbar-color: #d3d3d345 transparent;
}

.bg-select-dsplay {
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

</style>