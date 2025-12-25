<template>
  <div class="chat-messages" ref="messagesContainer">
    <ChatWelcome
      v-if="messages.length === 0"
      :input-message="inputMessage"
      :is-loading="isLoading"
      :booking-enabled="bookingEnabled"
      @update:input-message="$emit('update:inputMessage', $event)"
      @send-message="$emit('send-message')"
      @toggle-booking="$emit('toggle-booking')"
    />

    <template v-else>
      <ChatMessageItem
        v-for="(message, index) in messages"
        :key="index"
        :message="message"
        :index="index"
        :show-reasoning-global="showReasoningGlobal"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import type { Message } from '@/types/chat'
import ChatWelcome from './ChatWelcome.vue'
import ChatMessageItem from './ChatMessageItem.vue'

defineProps<{
  messages: Message[]
  inputMessage: string
  isLoading: boolean
  bookingEnabled: boolean
  showReasoningGlobal: boolean
}>()

defineEmits<{
  (e: 'update:inputMessage', value: string): void
  (e: 'send-message'): void
  (e: 'toggle-booking'): void
}>()

const messagesContainer = ref<HTMLElement | null>(null)

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

defineExpose({
  scrollToBottom
})
</script>

<style scoped>
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
  /* Ensure relative positioning for absolute children if any */
  position: relative;
}
</style>
