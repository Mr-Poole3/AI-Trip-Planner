<template>
  <div class="start-page">
    <div class="start-content">
      <h1 class="start-title">开始一段旅行✈️</h1>
      <div class="start-input-wrapper">
        <input
          :value="inputMessage"
          @input="$emit('update:inputMessage', ($event.target as HTMLInputElement).value)"
          @keypress.enter="$emit('send-message')"
          placeholder="向AI助手发送消息"
          class="start-input"
          :disabled="isLoading"
        />
        <button @click="$emit('send-message')" :disabled="isLoading || !inputMessage.trim()" class="start-send-btn">
          <span>↗</span>
        </button>
      </div>
      <div class="start-actions">
        <button @click="$emit('toggle-booking')" class="booking-toggle-btn" :class="{ active: bookingEnabled }" title="启用/关闭酒店搜索">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="5" width="18" height="14" rx="2"/>
            <path d="M8 9h8M8 13h6"/>
          </svg>
          <span>酒店搜索</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  inputMessage: string
  isLoading: boolean
  bookingEnabled: boolean
}>()

defineEmits<{
  (e: 'update:inputMessage', value: string): void
  (e: 'send-message'): void
  (e: 'toggle-booking'): void
}>()
</script>

<style scoped>
.start-page {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  min-height: 60vh;
  padding: 20px;
}

.start-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
  max-width: 600px;
  width: 100%;
  text-align: center;
}

.start-title {
  font-size: 32px;
  font-weight: 600;
  color: #333;
  margin: 0;
  text-align: center;
}

.start-input-wrapper {
  position: relative;
  width: 100%;
  max-width: 500px;
}

.start-input {
  width: 100%;
  padding: 16px 60px 16px 20px;
  border: 1px solid #e0e0e0;
  border-radius: 25px;
  font-size: 16px;
  outline: none;
  transition: all 0.2s ease;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.start-input:focus {
  border-color: #007bff;
  box-shadow: 0 2px 12px rgba(0, 123, 255, 0.2);
}

.start-input::placeholder {
  color: #999;
}

.start-send-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: #007bff;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: all 0.2s ease;
}

.start-send-btn:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-50%) scale(1.05);
}

.start-send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: translateY(-50%);
}

.start-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
}

/* 复用 ChatInput 中的 booking-toggle-btn 样式 */
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
