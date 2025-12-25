<template>
  <div class="sidebar">
    <div class="sidebar-content">
      <!-- 功能模块区域 -->
      <div class="features-section">
        <div class="feature-item new-chat-btn" @click="$emit('create-new-chat')">
          <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          <span class="feature-text">新聊天</span>
        </div>
      </div>
      <!-- 搜索框 -->
      <div class="search-section">
        <input
          :value="searchQuery"
          @input="$emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
          placeholder="搜索聊天..."
          class="search-input"
        />
      </div>
      <!-- 聊天记录列表 -->
      <div class="chat-history-section">
        <div class="section-title">聊天</div>
        <div class="chat-history-list">
          <div
            v-for="chat in chats"
            :key="chat.id"
            @click="$emit('load-chat', chat)"
            class="chat-history-item"
            :class="{ active: currentChatId === chat.id }"
          >
            <div class="chat-title">{{ chat.title }}</div>
            <div class="chat-time">{{ formatTime(chat.updatedAt) }}</div>
            <button @click.stop="$emit('delete-chat', chat.id)" class="delete-chat-btn">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatTime } from '@/utils/chatUtils'
import type { ChatSession } from '@/types/chat'

defineProps<{
  searchQuery: string
  chats: ChatSession[]
  currentChatId: string | null
}>()

defineEmits<{
  (e: 'update:searchQuery', value: string): void
  (e: 'create-new-chat'): void
  (e: 'load-chat', chat: ChatSession): void
  (e: 'delete-chat', id: string): void
}>()
</script>

<style scoped>
.sidebar {
  width: 260px;
  background: #fff;
  color: #333;
  display: flex;
  flex-direction: column;
}

.sidebar-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding-top: 0;
}

.search-section {
  padding: 8px 16px;
}

/* 功能模块区域样式 */
.features-section {
  padding: 16px 8px 8px 8px;
  margin-bottom: 8px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  color: #333;
}

.feature-item:hover {
  background: #f5f5f5;
}

.feature-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #495057;
}

.feature-text {
  flex: 1;
  font-weight: 500;
}

.search-input {
  width: 100%;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  color: #333;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.search-input::placeholder {
  color: #999;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
  background: #fff;
}

.chat-history-section {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.section-title {
  padding: 16px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.chat-history-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}

.chat-history-item {
  display: flex;
  flex-direction: column;
  padding: 12px 16px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  background: transparent;
}

.chat-history-item:hover {
  background: #f5f5f5;
}

.chat-history-item.active {
  background: #e8f4ff;
}

.chat-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #333;
}

.chat-time {
  font-size: 12px;
  color: #999;
}

.delete-chat-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-chat-btn svg {
  width: 16px;
  height: 16px;
}

.chat-history-item:hover .delete-chat-btn {
  opacity: 1;
}

.delete-chat-btn:hover {
  background: #dc3545;
}

.delete-chat-btn:hover svg {
  color: white;
}
</style>
