<template>
  <div class="draft-progress-container">
    <div class="draft-progress-header">
      <div class="progress-info">
        <svg class="progress-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 11l3 3L22 4"/>
          <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>
        </svg>
        <span class="progress-title">旅行计划收集中</span>
        <span class="progress-percentage">{{ draftCompleteness }}%</span>
      </div>
      <button @click="$emit('reset-draft')" class="draft-reset-btn" title="取消规划">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>

    <div class="progress-bar-wrapper">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: draftCompleteness + '%' }"></div>
      </div>
    </div>

    <div class="draft-fields-grid">
      <div
        v-for="(field, key) in {
          destination: '目的地',
          origin: '出发地',
          start_date: '开始日期',
          end_date: '结束日期'
        }"
        :key="key"
        class="draft-field"
        :class="{ filled: travelPlanDraft && travelPlanDraft[key as keyof TravelPlanDraft] }"
      >
        <div class="field-icon" :class="{ filled: travelPlanDraft && travelPlanDraft[key as keyof TravelPlanDraft] }">
          <svg v-if="travelPlanDraft && travelPlanDraft[key as keyof TravelPlanDraft]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
          </svg>
        </div>
        <div class="field-content">
          <div class="field-label">{{ field }}</div>
          <input
            v-if="key === 'start_date' || key === 'end_date'"
            type="date"
            :value="travelPlanDraft ? travelPlanDraft[key as keyof TravelPlanDraft] || '' : ''"
            @change="(e: Event) => $emit('edit-draft-field', key, (e.target as HTMLInputElement).value)"
            class="field-input"
            :placeholder="`请输入${field}`"
          />
          <input
            v-else
            type="text"
            :value="travelPlanDraft ? travelPlanDraft[key as keyof TravelPlanDraft] || '' : ''"
            @input="(e: Event) => $emit('edit-draft-field', key, (e.target as HTMLInputElement).value)"
            class="field-input"
            :placeholder="`请输入${field}`"
          />
        </div>
      </div>
    </div>

    <div v-if="draftMissingFields.length > 0" class="draft-missing">
      <span class="missing-icon">⚠️</span>
      <span>还需要：{{ draftMissingFields.join('、') }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TravelPlanDraft } from '@/types/chat'

defineProps<{
  travelPlanDraft: TravelPlanDraft | null
  draftCompleteness: number
  draftMissingFields: string[]
}>()

defineEmits<{
  (e: 'reset-draft'): void
  (e: 'edit-draft-field', key: string, value: string): void
}>()
</script>

<style scoped>
/* 草稿进度条样式 - 大厂风格，与页面主题色协调 */
.draft-progress-container {
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.draft-progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
}

.progress-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.progress-title {
  font-size: 16px;
  font-weight: 600;
}

.progress-percentage {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
}

.draft-reset-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.draft-reset-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.draft-reset-btn svg {
  width: 18px;
  height: 18px;
}

.progress-bar-wrapper {
  margin-bottom: 16px;
}

.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #66bb6a 0%, #43a047 100%);
  border-radius: 4px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 10px rgba(102, 187, 106, 0.6);
}

.draft-fields-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.draft-field {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
}

.draft-field.filled {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.draft-field:hover {
  background: rgba(255, 255, 255, 0.15);
}

.field-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}

.field-icon.filled {
  color: #66bb6a;
}

.field-icon svg {
  width: 100%;
  height: 100%;
}

.field-content {
  flex: 1;
  min-width: 0;
}

.field-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 4px;
}

.field-input {
  width: 100%;
  background: transparent;
  border: none;
  color: white;
  font-size: 14px;
  padding: 0;
  outline: none;
}

.field-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.draft-missing {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  background: rgba(0, 0, 0, 0.1);
  padding: 8px 12px;
  border-radius: 8px;
  margin-top: 12px;
}

.missing-icon {
  font-size: 14px;
}
</style>
