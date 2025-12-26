<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <div class="logo-container">
        <div class="logo-icon">
          <Plane class="w-5 h-5" />
        </div>
        <span class="logo-text">AI Trip Planner</span>
      </div>
    </div>

    <div class="sidebar-content">
      <!-- 功能模块区域 -->
      <div class="features-section">
        <button class="new-chat-btn" @click="$emit('create-new-chat')">
          <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="feature-text">新聊天</span>
          <span class="shortcut">Cmd K</span>
        </button>
      </div>

      <!-- 搜索框 -->
      <div class="search-section">
        <div class="search-wrapper">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
          </svg>
          <input
            :value="searchQuery"
            @input="$emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
            placeholder="搜索聊天历史..."
            class="search-input"
          />
        </div>
      </div>

      <!-- 聊天记录列表 -->
      <div class="chat-history-section">
        <div class="section-header">
          <span class="section-title">最近记录</span>
          <span class="count-badge">{{ chats.length }}</span>
        </div>
        <div class="chat-history-list custom-scrollbar">
          <div
            v-for="chat in chats"
            :key="chat.id"
            @click="$emit('load-chat', chat)"
            class="chat-history-item"
            :class="{ active: currentChatId === chat.id }"
          >
            <div class="item-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <div class="item-content">
              <div class="chat-title">{{ chat.title }}</div>
              <div class="chat-time">{{ formatTime(chat.updatedAt) }}</div>
            </div>
            <button @click.stop="$emit('delete-chat', chat.id)" class="delete-chat-btn" title="删除会话">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
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
import { Plane } from 'lucide-vue-next'

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
  width: 280px;
  background: #fcfcfd;
  color: #1a1a1a;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #f0f0f2;
  height: 100vh;
}

.sidebar-header {
  padding: 20px 16px;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: #3b82f6;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 800;
  font-size: 16px;
}

.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
  letter-spacing: -0.01em;
}

.sidebar-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 功能模块区域样式 */
.features-section {
  padding: 0 16px 16px 16px;
}

.new-chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.new-chat-btn:hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3);
}

.new-chat-btn:active {
  transform: translateY(0);
}

.feature-icon {
  width: 18px;
  height: 18px;
}

.feature-text {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  text-align: left;
}

.shortcut {
  font-size: 10px;
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

/* 搜索框 */
.search-section {
  padding: 0 16px 20px 16px;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  width: 16px;
  height: 16px;
  color: #94a3b8;
}

.search-input {
  width: 100%;
  background: #f1f5f9;
  border: 1px solid transparent;
  color: #1e293b;
  padding: 10px 12px 10px 36px;
  border-radius: 10px;
  font-size: 13px;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  background: white;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

/* 聊天历史列表 */
.chat-history-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.section-header {
  padding: 0 16px 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-title {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  font-weight: 700;
}

.count-badge {
  font-size: 11px;
  background: #f1f5f9;
  color: #64748b;
  padding: 1px 6px;
  border-radius: 6px;
  font-weight: 600;
}

.chat-history-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}

.chat-history-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  margin-bottom: 2px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chat-history-item:hover {
  background: #f1f5f9;
}

.chat-history-item.active {
  background: #eff6ff;
}

.chat-history-item.active .item-icon {
  color: #3b82f6;
}

.item-icon {
  width: 18px;
  height: 18px;
  margin-top: 2px;
  color: #94a3b8;
  flex-shrink: 0;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.chat-title {
  font-size: 13.5px;
  font-weight: 500;
  color: #334155;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-history-item.active .chat-title {
  color: #1e40af;
  font-weight: 600;
}

.chat-time {
  font-size: 11px;
  color: #94a3b8;
}

.delete-chat-btn {
  opacity: 0;
  padding: 4px;
  color: #94a3b8;
  background: transparent;
  border: none;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
  align-self: center;
}

.chat-history-item:hover .delete-chat-btn {
  opacity: 1;
}

.delete-chat-btn:hover {
  background: #fee2e2;
  color: #ef4444;
}

.delete-chat-btn svg {
  width: 14px;
  height: 14px;
}

/* 自定义滚动条 */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>
