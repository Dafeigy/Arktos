<script setup lang="ts">
import { ref, computed } from 'vue';
import { Button } from '@/components/ui/button';
// import { Select } from '@/components/ui/select';
import UploadFile from '@/components/general/UploadFile.vue'
import { ToggleGroup, ToggleGroupItem  } from '@/components/ui/toggle-group';
import { Slider } from '@/components/ui/slider';
import {
    Undo, Redo, Save, Copy,
    MousePointer2, Circle, Square, Minus, Type, ArrowUpRight, Hash
    } from 'lucide-vue-next'


const selectedBackground = ref('asset-24.avif');
const selectedAspectRatio = ref('16:9');

const bgImages = [
    'asset-13.jpg',
    'asset-18.jpg',
    'asset-19.jpg',
    'asset-24.avif',
    'asset-25.jpg',
    'asset-26.jpeg',
    'asset-27.jpeg',
    'asset-28.jpeg',
    'asset-29.jpeg',
    'asset-30.jpeg'
];

const meshImages = [
    'mesh1.webp',
    'mesh2.webp',
    'mesh3.webp',
    'mesh4.webp',
    'mesh5.webp',
    'mesh6.webp',
    'mesh7.webp',
    'mesh8.webp',
    'mesh9.webp',
    'mesh10.webp',
    'mesh11.webp',
    'mesh12.webp',
    'mesh13.webp',
    'mesh14.webp',
    'mesh15.webp',
    'mesh16.webp',
    'mesh17.webp'
];

const getBackgroundImage = computed(() => {
    if (bgImages.includes(selectedBackground.value)) {
        return `url(/src/assets/bg-images/${selectedBackground.value})`;
    } else {
        return `url(/src/assets/mesh/${selectedBackground.value})`;
    }
});

const getAspectRatioClass = computed(() => {
    switch (selectedAspectRatio.value) {
        case '21:9':
            return 'aspect-[21/9]';
        case '16:9':
            return 'aspect-video';
        case '4:3':
            return 'aspect-[4/3]';
        default:
            return 'aspect-video';
    }
});


</script>
<template>
<div class="h-full w-full  flex flex-col transition-all! duration-400! ease-linear! overflow-hidden">
    <div id="editor-header" class="px-4 w-full bg-sidebar h-16 flex justify-between items-center">
        <div class="flex items-center justify-start gap-2">
            <h1 class="text-xl">
                Edit Screenshot
            </h1>
            <Button variant="ghost" size="icon" class="">
                <Undo class="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" class="">
                <Redo class="h-4 w-4" />
            </Button>
        </div>
        <div class="flex justify-end items-center gap-2">
            <Button size="sm" variant="secondary">Cancel</Button>
            <Button size="icon" variant="secondary">
                <Copy />
            </Button>
            <Button size="icon" variant="secondary">
                <Save />
            </Button>
        </div>
    </div>
    <div id="mode-select" class="flex justify-start px-2 py-2 border border-border bg-sidebar">
        <ToggleGroup type="single" class="w-full">
            <ToggleGroupItem value="pointer" aria-label="Toggle Pointer" class="aspect-square mx-1 ">
                    <MousePointer2 class="h-4 w-4 " />
            </ToggleGroupItem>
            <ToggleGroupItem value="circle" aria-label="Toggle Circle" class="aspect-square mx-1 ">
                    <Circle class="h-4 w-4" />
            </ToggleGroupItem>
            <ToggleGroupItem value="square" aria-label="Toggle Square" class="aspect-square mx-1 ">
                    <Square class="h-4 w-4" />
            </ToggleGroupItem>
            <ToggleGroupItem value="minus" aria-label="Toggle Minus" class="aspect-square mx-1 ">
                    <Minus class="h-4 w-4" />
            </ToggleGroupItem>
            <ToggleGroupItem value="arrow" aria-label="Toggle Arrow" class="aspect-square mx-1 ">
                    <ArrowUpRight class="h-4 w-4" />
            </ToggleGroupItem>
            <ToggleGroupItem value="type" aria-label="Toggle Type" class="aspect-square mx-1 ">
                    <Type class="h-4 w-4" />
            </ToggleGroupItem>
            <ToggleGroupItem value="hash" aria-label="Toggle Hash" class="aspect-square mx-1 ">
                    <Hash class="h-4 w-4" />
            </ToggleGroupItem>
        </ToggleGroup>
        
    </div>
    <div class="flex-1 w-full flex overflow-auto">
        <div class="w-1/4 max-w-[400px] bg-sidebar flex flex-col overflow-auto" id="effect-selector">
            <p class="text-sm text-foreground/50 select-none px-4 py-2">Select an annotation to edit</p>
            <p class="text-sm px-4 text-foreground py-2 mt-2">Background</p>
            <div id="background-solid-select" class="flex flex-col w-full">
                <ToggleGroup type="single" class="flex flex-col justify-start items-start" v-model="selectedBackground">
                    <p class="text-xs px-4 text-foreground/50 mt-2">Solid</p>
                    <div class="grid grid-cols-4 gap-2 my-4 px-4 w-full">
                        <ToggleGroupItem v-for="img in bgImages" :key="img" :value="img" aria-label="" class="w-full flex justify-center items-center h-full aspect-square mx-1 cursor-pointer bg-select-dsplay data-[state=on]:border-2 data-[state=on]:border-green-300" :style="{ backgroundImage: `url(/src/assets/bg-images/${img})` }">
                        
                        </ToggleGroupItem>
                    </div>
                    <p class="text-xs px-4 text-foreground/50 mt-2">Gradient</p>
                    <div class="grid grid-cols-4 gap-2 my-4 px-4 w-full">
                        <ToggleGroupItem v-for="img in meshImages" :key="img" :value="img" aria-label="" class="w-full flex justify-center items-center h-full aspect-square mx-1 cursor-pointer bg-select-dsplay data-[state=on]:border-2 data-[state=on]:border-green-300" :style="{ backgroundImage: `url(/src/assets/mesh/${img})` }">
                        
                        </ToggleGroupItem>
                    </div>
                    
                </ToggleGroup>
                
            </div>

            <!-- <p class="text-sm px-4  text-foreground mt-2">Wallpapers</p>
            <div class="w-full px-4 py-2 gap-1 justify-center items-center flex mt-4">
                <ToggleGroup type="single" class="w-full flex justify-center" defaultValue="wallpaper">
                    <ToggleGroupItem value="wallpaper" aria-label="Toggle Wallpaper" class="w-1/2 mx-1">
                        Wallpapers
                    </ToggleGroupItem>
                    <ToggleGroupItem value="italic" aria-label="Toggle Mac" class="w-1/2 mx-1">
                        Mac
                    </ToggleGroupItem>
                </ToggleGroup>
                
            </div>
            <ToggleGroup type="single" class="grid grid-cols-4 gap-2 my-4 px-4 w-full"  defaultValue="1">
                    <ToggleGroupItem v-for="i in 10" :key="i" :value="i" aria-label="" class="w-full flex justify-center items-center h-full aspect-square mx-1 cursor-pointer bg-select-dsplay data-[state=on]:border-2 data-[state=on]:border-green-300" :style="{ backgroundImage: `url(/src/assets/bg-imgs/${i%5+1}.jpeg)` }">
                        
                    </ToggleGroupItem>
            </ToggleGroup> -->

            <p class="text-sm px-4 text-foreground py-2 mt-2">Aspect Ratio</p>
            <div id="aspect-ratio-select" class="flex justify-between flex-col items-center px-4">
                <ToggleGroup type="single" class="w-full flex justify-center" v-model="selectedAspectRatio">
                    <ToggleGroupItem value="21:9" aria-label="Toggle 21:9" class="w-1/3 mx-1">
                        21:9
                    </ToggleGroupItem>
                    <ToggleGroupItem value="16:9" aria-label="Toggle 16:9" class="w-1/3 mx-1">
                        16:9
                    </ToggleGroupItem>
                    <ToggleGroupItem value="4:3" aria-label="Toggle 4:3" class="w-1/3 mx-1">
                        4:3
                    </ToggleGroupItem>
                </ToggleGroup>
                
            </div>
            <p class="text-sm px-4 text-foreground py-2">Background Effetcs</p>
            <div id="background-effetcs" class="flex justify-between flex-col items-center px-4">
                <div class="flex justify-between items-center w-full mt-2">
                    <p class="text-xs text-foreground/50">Blur</p>
                    <p class="text-xs text-foreground/50"> 8px</p>
                </div>
                <Slider
                    :default-value="[0]"
                    :max="100"
                    :step="1"
                    class="w-full py-4"
                />
                <div class="flex justify-between items-center w-full mt-2">
                    <p class="text-xs text-foreground/50">Noise</p>
                    <p class="text-xs text-foreground/50"> 8px</p>
                </div>
                <Slider
                    :default-value="[0]"
                    :max="100"
                    :step="1"
                    class="w-full py-4"
                />
            </div>

            <p class="text-sm px-4 text-foreground py-2">Shadow</p>
            <div id="background-effetcs" class="flex justify-between flex-col items-center px-4">
                <div class="flex justify-between items-center w-full mt-2">
                    <p class="text-xs text-foreground/50">Blur</p>
                    <p class="text-xs text-foreground/50"> 8px</p>
                </div>
                <Slider
                    :default-value="[0]"
                    :max="100"
                    :step="1"
                    class="w-full py-4"
                />
                <div class="flex justify-between items-center w-full mt-2">
                    <p class="text-xs text-foreground/50">Offset X</p>
                    <p class="text-xs text-foreground/50"> 8px</p>
                </div>
                <Slider
                    :default-value="[0]"
                    :max="100"
                    :step="1"
                    class="w-full py-4"
                />
                <div class="flex justify-between items-center w-full mt-2">
                    <p class="text-xs text-foreground/50">Offset Y</p>
                    <p class="text-xs text-foreground/50"> 8px</p>
                </div>
                <Slider
                    :default-value="[0]"
                    :max="100"
                    :step="1"
                    class="w-full py-4"
                />
                <div class="flex justify-between items-center w-full mt-2">
                    <p class="text-xs text-foreground/50">opacity</p>
                    <p class="text-xs text-foreground/50"> 8px</p>
                </div>
                <Slider
                    :default-value="[0]"
                    :max="100"
                    :step="1"
                    class="w-full py-4"
                />
            </div>

            <p class="text-sm px-4 text-foreground py-2">Image Roundeness</p>
            <div id="background-effetcs" class="flex justify-between flex-col items-center px-4">
                <div class="flex justify-between items-center w-full mt-2">
                    <p class="text-xs text-foreground/50">Corner Radius</p>
                    <p class="text-xs text-foreground/50"> 18px</p>
                </div>
                <Slider
                    :default-value="[0]"
                    :max="100"
                    :step="1"
                    class="w-full py-4"
                />
            </div>
            <p class="text-xs text-foreground/50 p-4 text-center">- End of the settings -</p>
        </div>

        
        <div id="preview" class="bg-background w-full justify-center items-center flex">
            <div :class="`h-[80%] ${getAspectRatioClass} rounded-2xl bg-select-dsplay flex justify-center items-center`" id="preview-container" :style="{ backgroundImage: getBackgroundImage }">
                <div class="text-foreground/50 h-9/10  rounded-2xl justify-center flex items-center max-h-[90%] max-w-[90%]">
                    <UploadFile />
                </div>
            </div>
        </div>
    </div>
</div>
</template>

<style>
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
  scrollbar-color: transparent transparent;
}

.bg-select-dsplay {
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
</style>