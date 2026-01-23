<script setup lang="ts">
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ArrowLeft, Clipboard, Folder } from 'lucide-vue-next'
import Switch from '@/components/ui/switch/Switch.vue';
import { useRouter } from 'vue-router'
const router = useRouter()
const routeToSettings = () => {
    router.push('/')
}
</script>
<template>
    <div class="w-full overflow-auto h-full flex justify-center items-center transition-all! duration-400! ease-linear!">
        <div id="settings-container" class="w-3/5 h-full px-4 py-4 max-w-[768px]">
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
            <div class="mt-4">
                <div class="rounded-xl my-2 h-1/4 bg-sidebar px-8 py-4">
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
                <div class="rounded-xl my-2 h-1/4 bg-sidebar px-8 py-4">
                    <p class="text-xl font-bold">Default Background</p>
                    <div class="grid grid-cols-4 gap-4 mt-4">
                        <div v-for="i in 16" :key="i" class=" duration-350 ease-in-out flex justify-center items-center aspect-square rounded-2xl cursor-pointer bg-[url(/src/assets/bg-imgs/3.jpeg)] object-cover">
                        </div>
                    </div>
                </div>
                <!-- <div v-for="i in 10" :key="i" class="rounded-xl my-2 h-1/4 bg-sidebar px-8 py-4">
                    <p class="text-xl font-bold">Default Background</p>
                </div> -->
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

</style>