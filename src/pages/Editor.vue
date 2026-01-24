<script setup lang="ts">
import { Button } from '@/components/ui/button';
// import { Select } from '@/components/ui/select';
import { ToggleGroup, ToggleGroupItem  } from '@/components/ui/toggle-group';
import { Slider } from '@/components/ui/slider';
import {
    Undo, Redo, Save, Copy,
    MousePointer2, Circle, Square, Minus, Type, ArrowUpRight, Hash
    } from 'lucide-vue-next'
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
            <div class="w-full px-4 py-2 gap-1 justify-center items-center flex">
                <ToggleGroup type="single" class="w-full flex justify-center">
                    <ToggleGroupItem value="wallpaper" aria-label="Toggle Wallpaper" class="w-1/2 mx-1">
                        Wallpapers
                    </ToggleGroupItem>
                    <ToggleGroupItem value="italic" aria-label="Toggle Mac" class="w-1/2 mx-1">
                        Mac
                    </ToggleGroupItem>
                </ToggleGroup>
                
            </div>
            <div class="grid grid-cols-4 gap-2 mt-4 px-4">
                <div v-for="i in 10" :key="i" class="border duration-350 ease-in-out flex justify-center items-center aspect-square rounded-lg cursor-pointer bg-select-dsplay" :style="{ backgroundImage: `url(/src/assets/bg-imgs/${i%5+1}.jpeg)` }"> </div>
            </div>

            <p class="text-sm px-4 text-foreground py-2 mt-2">Aspect Ratio</p>
            <div id="aspect-ratio-select" class="flex justify-between flex-col items-center px-4">
                <ToggleGroup type="single" class="w-full flex justify-center">
                    <ToggleGroupItem value="16:9" aria-label="Toggle 16:9" class="w-1/3 mx-1">
                        21:9
                    </ToggleGroupItem>
                    <ToggleGroupItem value="9:16" aria-label="Toggle 9:16" class="w-1/3 mx-1">
                        16:9
                    </ToggleGroupItem>
                    <ToggleGroupItem value="9:16" aria-label="Toggle 9:16" class="w-1/3 mx-1">
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
            <div class="h-[80%] aspect-video rounded-2xl bg-select-dsplay flex justify-center items-center" id="preview-container" :style="{ backgroundImage: `url(/src/assets/bg-imgs/1.jpeg)` }">
                <div class="text-foreground/50 h-9/10 aspect-video bg-indigo-300/10 rounded-2xl justify-center flex items-center">
                    Your Screenshot will display here...
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