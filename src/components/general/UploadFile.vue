<script setup lang="ts">
import { ref } from 'vue';
import { Image, Clipboard, Folder, RefreshCcw, Download, Copy } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@/components/ui/empty'
import { Separator } from "@/components/ui/separator"

interface Props {
  onDownload?: () => void;
}
import html2canvas from 'html2canvas-pro';
const handleDownload = async () => {
    const element = document.getElementById('preview');
    if (element) {
        try {
            const canvas = await html2canvas(element, {
                backgroundColor: null,
                scale: 2,
                logging: false,
                useCORS: true,
                onclone: (clonedDoc) => {
                    const elements = clonedDoc.querySelectorAll('*');
                    elements.forEach((el) => {
                        const computedStyle = (el as HTMLElement).style;
                        if (computedStyle.color && computedStyle.color.includes('oklch')) {
                            computedStyle.color = '';
                        }
                        if (computedStyle.backgroundColor && computedStyle.backgroundColor.includes('oklch')) {
                            computedStyle.backgroundColor = '';
                        }
                        if (computedStyle.borderColor && computedStyle.borderColor.includes('oklch')) {
                            computedStyle.borderColor = '';
                        }
                    });
                }
            });
            const link = document.createElement('a');
            link.download = `screenshot-${Date.now()}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
            console.log("Download")
        } catch (error) {
            console.error('Failed to download screenshot:', error);
        }
    }
};

const props = defineProps<Props>();

const selectedImage = ref<string | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);

const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    const file = input.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      selectedImage.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
};

const triggerFileSelect = () => {
  fileInput.value?.click();
};
</script>

<template>
  <div :class="[{'rounded-xl border border-dashed bg-sidebar/80': !selectedImage}]">
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      class="hidden"
      @change="handleFileSelect"
    />
    
    <!-- Selected Image Display -->
    <div v-if="selectedImage" class="p-4">
      <div class="relative group flex justify-center items-start">
        <img 
          :src="selectedImage" 
          alt="Selected image" 
          class="max-w-[90%] object-contain"
        />
        <div class="mx-2 transition-all! opacity-0 group-hover:opacity-100 ease-in-out duration-300 grid grid-cols-1 gap-2">
            <Button 
              class="" 
              variant="default" 
              size="sm"
              @click="selectedImage = null"
            >
              <RefreshCcw/>
            </Button>
            <Button 
                class="" 
                variant="default" 
                size="sm"
                @click="handleDownload()"
                >
                
                <Download />
            </Button>
            <Button 
                class="" 
                variant="default" 
                size="sm"
                >
                <Copy />
            </Button>
        </div>

        
        
        
      </div>
    </div>
    
    <!-- Empty State -->
    <Empty v-else>
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <Image />
        </EmptyMedia>
        <EmptyTitle>Select or Drop Image File</EmptyTitle>
        <EmptyDescription>
          Your screenshot will be display here
        </EmptyDescription>
      </EmptyHeader>
      <Separator />
      <EmptyContent>
        <div class="flex">
          <Button variant="default" size="sm" class="mx-2">
              <Clipboard />Use Clipboard
          </Button>

          <Button variant="outline" size="sm" class="mx-2" @click="triggerFileSelect">
              <Folder />Select File
          </Button>
        </div>

      </EmptyContent>
    </Empty>
  </div>
</template>
