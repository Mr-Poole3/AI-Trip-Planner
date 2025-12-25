<template>
  <div class="chat-input-container">
    <div v-if="selectedImage" class="image-preview">
      <img :src="selectedImage" alt="预览图片" />
      <button @click="$emit('remove-image')" class="remove-image-btn">×</button>
    </div>

    <div class="input-wrapper">
      <input
        type="file"
        ref="fileInputRef"
        @change="handleFileChange"
        accept="image/*"
        style="display: none"
      />
      <button @click="triggerFileInput" class="image-btn" title="上传图片">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <circle cx="8.5" cy="8.5" r="1.5"/>
          <path d="M21 15l-5-5L5 21"/>
        </svg>
      </button>
      
      <button @click="$emit('toggle-booking')" class="booking-toggle-btn" :class="{ active: bookingEnabled }" title="启用/关闭酒店搜索">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="5" width="18" height="14" rx="2"/>
          <path d="M8 9h8M8 13h6"/>
        </svg>
        <span>酒店搜索</span>
      </button>

      <input
        :value="inputMessage"
        @input="$emit('update:inputMessage', ($event.target as HTMLInputElement).value)"
        @keypress.enter="$emit('send-message')"
        placeholder="输入消息..."
        class="message-input"
        :disabled="isLoading"
      />
      <button @click="$emit('send-message')" :disabled="isLoading || !canSend" class="send-btn">
        发送
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  inputMessage: string
  isLoading: boolean
  canSend: boolean
  selectedImage: string | null
  bookingEnabled: boolean
}>()

const emit = defineEmits<{
  (e: 'update:inputMessage', value: string): void
  (e: 'send-message'): void
  (e: 'upload-image', file: File): void
  (e: 'remove-image'): void
  (e: 'toggle-booking'): void
}>()

const fileInputRef = ref<HTMLInputElement | null>(null)

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    emit('upload-image', file)
  }
  // Clear input value to allow selecting same file again
  if (target) target.value = ''
}
</script>

<style scoped>
.chat-input-container {
  padding: 20px;
  background: white;
}

.image-preview {
  position: relative;
  margin-bottom: 12px;
}

.image-preview img {
  max-width: 100px;
  max-height: 100px;
  border-radius: 8px;
  border: 2px solid #e0e0e0;
}

.remove-image-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #dc3545;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
}

.image-btn {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 12px;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-btn svg {
  width: 20px;
  height: 20px;
  color: #495057;
}

.image-btn:hover {
  background: #e9ecef;
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #dee2e6;
  border-radius: 24px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s ease;
}

.message-input:focus {
  border-color: #007bff;
}

.send-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 24px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.send-btn:hover:not(:disabled) {
  background: #0056b3;
}

.send-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.booking-toggle-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
  color: #6c757d;
}

.booking-toggle-btn:hover {
  background: #e9ecef;
}

.booking-toggle-btn.active {
  background: #e8f0fe;
  border-color: #1a73e8;
  color: #1a73e8;
}

.booking-toggle-btn svg {
  width: 16px;
  height: 16px;
}
</style>
