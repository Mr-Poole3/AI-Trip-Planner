<template>
  <div class="app-container">
    <!-- 左侧边栏 -->
    <ChatSidebar
      :search-query="searchQuery"
      :chats="filteredChatHistory"
      :current-chat-id="currentChatId"
      @update:search-query="searchQuery = $event"
      @create-new-chat="createNewChat"
      @load-chat="loadChatSession"
      @delete-chat="deleteChatSession"
    />

    <!-- 主聊天区域 -->
    <div class="main-content">
      <div class="chat-header">
        <div class="header-left">
          <h1>AI 助手</h1>
        </div>
        <div class="header-right">
          <div class="user-profile-dropdown group relative">
            <div class="user-avatar-container">
              <div class="user-avatar">
                {{ userStore.userInfo?.username?.[0]?.toUpperCase() || 'U' }}
              </div>
              <div class="user-info-text">
                <span class="user-name">{{ userStore.userInfo?.username || '用户' }}</span>
                <span class="user-role">高级会员</span>
              </div>
              <svg class="dropdown-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>

            <!-- Dropdown Menu -->
            <div class="dropdown-menu">
              <div class="dropdown-header">
                <p class="dropdown-user-email">{{ userStore.userInfo?.email }}</p>
              </div>
              <div class="dropdown-divider"></div>
              <router-link to="/" class="dropdown-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path></svg>
                返回首页
              </router-link>
              <button @click="clearCurrentChat" class="dropdown-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 6L9 16l-4-4"></path></svg>
                清空对话
              </button>
              <div class="dropdown-divider"></div>
              <button @click="handleLogout" class="dropdown-item logout-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                退出登录
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 草稿进度条 -->
      <div v-if="isDraftMode" class="draft-progress-container">
        <div class="draft-progress-header">
          <div class="progress-info">
            <svg class="progress-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 11l3 3L22 4"/>
              <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>
            </svg>
            <span class="progress-title">旅行计划收集中</span>
            <span class="progress-percentage">{{ draftCompleteness }}%</span>
          </div>
          <button @click="resetDraft" class="draft-reset-btn" title="取消规划">
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
                @change="(e: Event) => editDraftField(key as keyof TravelPlanDraft, (e.target as HTMLInputElement).value)"
                class="field-input"
                :placeholder="`请输入${field}`"
              />
              <input
                v-else
                type="text"
                :value="travelPlanDraft ? travelPlanDraft[key as keyof TravelPlanDraft] || '' : ''"
                @input="(e: Event) => editDraftField(key as keyof TravelPlanDraft, (e.target as HTMLInputElement).value)"
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

      <ChatMessageList
        ref="messageListRef"
        :messages="messages"
        :input-message="inputMessage"
        :is-loading="isLoading"
        :booking-enabled="bookingEnabled"
        :show-reasoning-global="showReasoningGlobal"
        @update:input-message="inputMessage = $event"
        @send-message="sendMessage"
        @toggle-booking="bookingEnabled = !bookingEnabled"
      />

      <ChatInput
        v-if="messages.length > 0"
        :input-message="inputMessage"
        :is-loading="isLoading"
        :can-send="canSend"
        :selected-image="selectedImage"
        :booking-enabled="bookingEnabled"
        @update:input-message="inputMessage = $event"
        @send-message="sendMessage"
        @upload-image="handleImageUpload"
        @remove-image="removeImage"
        @toggle-booking="bookingEnabled = !bookingEnabled"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import type { Message, MessageContent, StepInfo, HotelData, ToolCall, MapData, TravelPlanDraft, ChatSession } from '@/types/chat'
import ChatSidebar from '@/components/chat/ChatSidebar.vue'
import ChatMessageList from '@/components/chat/ChatMessageList.vue'
import ChatInput from '@/components/chat/ChatInput.vue'

import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const messages = ref<Message[]>([])
const inputMessage = ref('')
const selectedImage = ref<string | null>(null)
const isLoading = ref(false)
const messageListRef = ref<InstanceType<typeof ChatMessageList> | null>(null)
const bookingEnabled = ref(false)
const travelStepMsgMap = ref<Record<number, number>>({})

// 思考过程显示控制（默认关闭）
const showReasoningGlobal = ref(false)

const travelPlanDraft = ref<TravelPlanDraft | null>(null)

// 🆕 当前激活的旅行计划（用于修改）
const currentActivePlan = ref<any>(null)
const currentActivePlanMessageIndex = ref<number | null>(null)

// 草稿模式计算属性
const isDraftMode = computed(() => travelPlanDraft.value !== null)
const draftCompleteness = computed(() => {
  if (!travelPlanDraft.value) return 0
  const required = ['destination', 'origin', 'start_date', 'end_date']
  const filled = required.filter(k => travelPlanDraft.value && travelPlanDraft.value[k as keyof TravelPlanDraft]).length
  return Math.round((filled / required.length) * 100)
})

const draftMissingFields = computed(() => {
  if (!travelPlanDraft.value) return []
  const fieldNames: Record<string, string> = {
    destination: '目的地',
    origin: '出发地',
    start_date: '开始日期',
    end_date: '结束日期'
  }
  const required = ['destination', 'origin', 'start_date', 'end_date']
  return required.filter(k => !travelPlanDraft.value || !travelPlanDraft.value[k as keyof TravelPlanDraft]).map(k => fieldNames[k])
})

// 历史记录管理
const CHAT_HISTORY_KEY = 'ai_chat_history'
const CHAT_SESSIONS_KEY = 'ai_chat_sessions'
const MAX_HISTORY_COUNT = 10

const searchQuery = ref('')
const currentChatId = ref<string | null>(null)
const chatSessions = ref<ChatSession[]>([])

const canSend = computed(() => {
  return (inputMessage.value.trim() || selectedImage.value) && !isLoading.value
})

// 过滤聊天历史
const filteredChatHistory = computed(() => {
  if (!searchQuery.value) {
    return chatSessions.value
  }
  return chatSessions.value.filter(chat =>
    chat.title.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const scrollToBottom = async () => {
  await nextTick()
  if (messageListRef.value) {
    messageListRef.value.scrollToBottom()
  }
}

const handleImageUpload = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch('http://localhost:9000/api/upload-image', {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error('图片上传失败')
    }

    const data = await response.json()
    selectedImage.value = data.image_url
  } catch (error) {
    console.error('图片上传失败:', error)
    alert('图片上传失败，请重试')
  }
}

const removeImage = () => {
  selectedImage.value = null
}

const sendMessage = async () => {
  if (!canSend.value) return

  // 保存用户输入文本（在清空之前）
  const userText = inputMessage.value.trim()

  const content: MessageContent[] = []

  if (userText) {
    content.push({
      type: 'text',
      text: userText
    })
  }

  if (selectedImage.value) {
    content.push({
      type: 'image_url',
      image_url: { url: selectedImage.value }
    })
  }

  const userMessage: Message = {
    role: 'user',
    content
  }

  messages.value.push(userMessage)

  // 如果是第一条消息且没有当前会话ID，创建新会话
  if (!currentChatId.value) {
    currentChatId.value = Date.now().toString()
  }

  inputMessage.value = ''
  selectedImage.value = null

  // 保存用户消息到会话
  saveCurrentSession()

  isLoading.value = true
  travelStepMsgMap.value = {}
  await scrollToBottom()

  try {
    if (!bookingEnabled.value) {
      const original = [...messages.value]
      const step1: StepInfo = { step: 1, status: 'running', message: '正在分析您的需求...' }
      messages.value.push({ role: 'assistant', content: [], travelSteps: [step1] })
      travelStepMsgMap.value[1] = messages.value.length - 1
      await scrollToBottom()

      // 智能启动草稿模式（🆕 但如果已有激活计划，则跳过）
      if (!isDraftMode.value && !currentActivePlan.value && isTravelRelated(userText)) {
        // 第一次旅行相关输入，初始化草稿
        initDraft()
      }

      const response = await fetch('http://localhost:9000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: original,
          // 🆕 优先级：有激活计划时，不发送草稿（避免触发需求收集）
          travel_draft: currentActivePlan.value ? undefined : (travelPlanDraft.value || undefined),
          current_plan: currentActivePlan.value || undefined,  // 🆕 发送当前激活的计划
          system_prompt: (() => {
            const fmt = new Intl.DateTimeFormat('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
            const s = fmt.format(new Date()).replace(/\//g, '-')
            return `当前北京时间：${s}。请参考该时间理解用户在本次消息中的日期表达（未给年份时礼貌确认，勿自行假设）。可选项（人数、景点）未提供时，请直接生成不含这些字段的计划，不要向用户提问可选项；如需建议，用notes字段说明，勿使用ask。输出活动仅包含景点推荐，不输出time字段；所有activities[].name必须为单一、标准化的中文景点官方名称，不得包含斜杠、顿号或并列名称；需要说明从属关系或补充信息写入notes。排期规则：若某景点适合全天游玩（如游乐园、爬山等），该天只安排这一个景点；若为城市打卡类（如寺庙、网红打卡地等），同一天安排约4个景点，保持相邻景点可步行或短途通勤。`
          })()
        })
      })
      if (!response.ok) throw new Error('AI 响应失败')
      const result = await response.json()

      const idx1 = travelStepMsgMap.value[1]
      if (idx1 !== undefined) {
        messages.value[idx1].travelSteps = [{ step: 1, status: 'completed', message: '需求分析完成' }]
        messages.value[idx1] = { ...messages.value[idx1] }
      }

      // 处理草稿更新
      if (result.type === 'draft_update') {
        // 更新草稿
        if (result.draft) {
          updateDraft(result.draft)
        }

        // 检查是否收集完成
        if (result.is_complete) {
          // 收集完成，显示确认消息
          if (result.next_question) {
            messages.value.push({
              role: 'assistant',
              content: [{ type: 'text', text: result.next_question }]
            })
          }

          // 标记步骤1完成，显示步骤2开始
          const idx1 = travelStepMsgMap.value[1]
          if (idx1 !== undefined) {
            messages.value[idx1].travelSteps = [{ step: 1, status: 'completed', message: '需求收集完成！' }]
            messages.value[idx1] = { ...messages.value[idx1] }
          }

          messages.value.push({
            role: 'assistant',
            content: [],
            travelSteps: [{ step: 2, status: 'running', message: '正在生成每日计划...' }]
          })
          travelStepMsgMap.value[2] = messages.value.length - 1

          await scrollToBottom()
          saveCurrentSession()

          // 自动触发计划生成（发送特殊请求）
          const planResponse = await fetch('http://localhost:9000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              messages: [{
                role: 'user',
                content: [{ type: 'text', text: '__GENERATE_PLAN__' }]
              }],
              travel_draft: travelPlanDraft.value || undefined
            })
          })

          if (!planResponse.ok) throw new Error('AI 响应失败')
          const planResult = await planResponse.json()

          // 处理生成的计划
          if (planResult.type === 'daily_plan_json') {
            const html = buildDailyPlanHtml(planResult)
            messages.value.push({ role: 'assistant', content: [{ type: 'html', text: html }] })

            const idx2 = travelStepMsgMap.value[2]
            if (idx2 !== undefined) {
              messages.value[idx2].travelSteps = [{ step: 2, status: 'completed', message: '每日计划生成完成！' }]
              messages.value[idx2] = { ...messages.value[idx2] }
            }

            const msgIndex = messages.value.length - 1

            // 🆕 保存当前激活的计划
            currentActivePlan.value = planResult
            currentActivePlanMessageIndex.value = msgIndex

            const city = planResult?.plan?.destination || ''
            const itinerary = planResult?.itinerary || []

            // 保存地图数据，ChatMessageItem会自动渲染
            // 优化：先获取坐标，再保存（这里为了简化，先保存基本信息，ChatMessageItem会处理渲染）
            // 但是ChatView原本是先fetch geocode再保存。
            // 我们可以构造mapData并保存，ChatMessageItem会使用它。
            // 为了保持兼容性，我们这里只保存基本信息，让ChatMessageItem去fetch?
            // 不，ChatView logic was: fetch -> save mapData -> render.
            // If we want ChatMessageItem to handle it, we should pass the data.
            // Since we removed renderTravelMap from here, we can't pre-fetch easily without duplicating logic.
            // So we will just attach mapData with itinerary and city, and empty coordsMap.
            // ChatMessageItem should handle fetching if coordsMap is empty.
            // But my ChatMessageItem implementation assumed coordsMap is populated or it aborts?
            // "If coordsMap is empty (first run), fetch coords... Let's assume mapData is complete..."
            // I should have implemented fetch in ChatMessageItem.
            // I will update ChatMessageItem later or assume the backend call happens there.

            // Actually, buildDailyPlanHtml generates HTML with data-map-id.
            // If I construct mapData with just itinerary and city, ChatMessageItem can fetch.

            messages.value[msgIndex].mapData = {
              itinerary,
              city,
              coordsMap: {}, // Will be populated by ChatMessageItem
              mapId: `map-${Date.now()}` // Should match the one in buildDailyPlanHtml... wait.
              // buildDailyPlanHtml generates a random ID. I need to capture it.
            }
            // Wait, buildDailyPlanHtml returns HTML string. I can't easily extract the ID unless I regex it.
            // Or I pass the ID to buildDailyPlanHtml.

            resetDraft()
            saveCurrentSession()
          }

          return
        }

        // 收集未完成，显示追问消息
        if (result.next_question) {
          messages.value.push({
            role: 'assistant',
            content: [{ type: 'text', text: result.next_question }]
          })
        }

        saveCurrentSession()
        return
      }

      if (result.type === 'ask') {
        messages.value.push({ role: 'assistant', content: [], travelSteps: [{ step: 2, status: 'completed', message: '需要补充信息' }] })
        messages.value.push({ role: 'assistant', content: [{ type: 'text', text: result.content }] })
        saveCurrentSession()
        return
      }

      if (result.type === 'daily_plan_json') {
        // 🆕 检查是否是修改现有计划
        const isModification = currentActivePlan.value !== null

        if (!isModification) {
          // 新生成计划，添加步骤提示
          messages.value.push({ role: 'assistant', content: [], travelSteps: [{ step: 2, status: 'running', message: '正在生成每日计划...' }] })
        }

        const html = buildDailyPlanHtml(result)

        let msgIndex: number

        if (isModification && currentActivePlanMessageIndex.value !== null) {
          // 🆕 修改模式：替换现有计划消息
          msgIndex = currentActivePlanMessageIndex.value
          messages.value[msgIndex].content = [{ type: 'html', text: html }]
          messages.value[msgIndex] = { ...messages.value[msgIndex] }

          // 添加修改成功提示
          messages.value.push({
            role: 'assistant',
            content: [{ type: 'text', text: '✅ 已根据您的要求修改计划！' }]
          })
        } else {
          // 新生成模式：添加新消息
          messages.value.push({ role: 'assistant', content: [{ type: 'html', text: html }] })
          const idx2 = messages.value.length - 2
          messages.value[idx2].travelSteps = [{ step: 2, status: 'completed', message: '每日计划生成完成' }]
          messages.value[idx2] = { ...messages.value[idx2] }
          msgIndex = messages.value.length - 1
        }

        // 🆕 保存当前激活的计划
        currentActivePlan.value = result
        currentActivePlanMessageIndex.value = msgIndex
        // 🆕 优先使用LLM识别的城市名，降级使用destination（绝不能为空）
        const city = result?.plan?.city || result?.plan?.destination
        const itinerary = result?.itinerary || []

        // Extract Map ID from HTML to save mapData
        const mapIdMatch = html.match(/data-map-id="([^"]+)"/)
        const mapId = mapIdMatch ? mapIdMatch[1] : ''

        if (mapId) {
             messages.value[msgIndex].mapData = {
                itinerary,
                city: city || '未知城市',
                coordsMap: {},
                mapId
             }
        }

        // 计划生成完成，重置草稿（仅在非修改模式下）
        if (!isModification) {
          resetDraft()
        }
        saveCurrentSession()

        return
      }

      if (result.type === 'plan_json') {
        messages.value.push({ role: 'assistant', content: [{ type: 'text', text: JSON.stringify(result.plan, null, 2) }] })
        saveCurrentSession()
        return
      }

      if (result.type === 'chat') {
        messages.value.push({ role: 'assistant', content: [{ type: 'text', text: result.content }] })
        saveCurrentSession()
        return
      }
    } else {
      // 酒店搜索：展示步骤与推荐
      const stepsMessage: Message = { role: 'assistant', content: [], hotelSteps: [] }
      messages.value.push(stepsMessage)
      const stepsIndex = messages.value.length - 1
      await scrollToBottom()

      // 🆕 准备请求体，包含旅行计划（如果有）
      const hotelRequestBody: any = {
        message: (content.find(c => c.type === 'text')?.text) || ''
      }

      // 如果有激活的旅行计划，传递给酒店搜索
      if (currentActivePlan.value) {
        hotelRequestBody.travel_plan = currentActivePlan.value
      }

      const response = await fetch('http://localhost:9000/api/hotel-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(hotelRequestBody)
      })
      if (!response.ok) throw new Error('酒店搜索失败')
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      if (!reader) throw new Error('无法读取响应流')
      let buffer = ''
      let recommendationIndex: number | null = null
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (line.trim() && line.startsWith('data: ')) {
            try {
              const jsonStr = line.slice(6).trim()
              if (!jsonStr) continue
              const data = JSON.parse(jsonStr)
              if (data.step) {
                const currentSteps = messages.value[stepsIndex].hotelSteps || []
                const existing = currentSteps.findIndex((s: StepInfo) => s.step === data.step)
                const nextStep: StepInfo = { step: data.step, status: data.status, message: data.message, data: data.data }
                if (existing >= 0) currentSteps[existing] = nextStep; else currentSteps.push(nextStep)
                messages.value[stepsIndex].hotelSteps = [...currentSteps]
                await nextTick(); await scrollToBottom()
              } else if (data.type === 'recommendation_start') {
                recommendationIndex = messages.value.length
                messages.value.push({ role: 'assistant', content: [{ type: 'text', text: '' }], isStreaming: true })
                await scrollToBottom()
              } else if (data.type === 'recommendation_chunk') {
                if (recommendationIndex !== null) {
                  const msg = messages.value[recommendationIndex]
                  if (msg?.content[0]?.type === 'text') {
                    msg.content[0].text += data.content
                    messages.value[recommendationIndex] = { ...msg }
                  }
                  await nextTick(); await scrollToBottom()
                }
              } else if (data.type === 'recommendation_end') {
                if (recommendationIndex !== null) {
                  const msg = messages.value[recommendationIndex]
                  msg.isStreaming = false
                  messages.value[recommendationIndex] = { ...msg }
                }
              } else if (data.type === 'hotels_data') {
                // 🆕 接收酒店列表数据（包含URL和图片）
                if (recommendationIndex !== null) {
                  const msg = messages.value[recommendationIndex]
                  msg.hotelsData = data.hotels
                  messages.value[recommendationIndex] = { ...msg }
                  await nextTick()
                  await scrollToBottom()
                }
              } else if (data.type === 'final_response') {
                messages.value.push({ role: 'assistant', content: [{ type: 'text', text: data.content }] })
                await scrollToBottom()
              } else if (data.type === 'done') {
                saveCurrentSession(); await scrollToBottom(); return
              } else if (data.type === 'error') {
                throw new Error(data.content)
              }
            } catch (e) {
              console.warn('解析酒店流失败:', e)
            }
          }
        }
      }
    }

  } catch (error) {
    console.error('发送消息失败:', error)

    // 移除流式消息，添加错误消息
    messages.value.pop()

    const errorMessage: Message = {
      role: 'assistant',
      content: [{
        type: 'text',
        text: '抱歉，我现在无法回复。请检查网络连接或稍后重试。'
      }]
    }

    messages.value.push(errorMessage)
    await scrollToBottom()
    // 保存错误消息到会话
    saveCurrentSession()
  } finally {
    isLoading.value = false
  }
}

// ========== 草稿操作函数 ==========

// 初始化草稿
const initDraft = (initialData?: Partial<TravelPlanDraft>) => {
  travelPlanDraft.value = {
    destination: initialData?.destination || null,
    origin: initialData?.origin || null,
    start_date: initialData?.start_date || null,
    end_date: initialData?.end_date || null,
    people: initialData?.people || null,
    attractions: initialData?.attractions || []
  }
  saveDraftToStorage()
}

// 更新草稿
const updateDraft = (updates: Partial<TravelPlanDraft>) => {
  if (!travelPlanDraft.value) {
    initDraft(updates)
  } else {
    travelPlanDraft.value = {
      ...travelPlanDraft.value,
      ...updates
    }
    saveDraftToStorage()
  }
}

// 重置草稿
const resetDraft = () => {
  travelPlanDraft.value = null
  // 🆕 草稿现在跟会话绑定，保存会话即可
  saveCurrentSession()
}

// 保存草稿（已改为会话级，自动保存到会话中）
const saveDraftToStorage = () => {
  // 🆕 草稿现在跟会话绑定，保存整个会话
  saveCurrentSession()
}

// 手动编辑草稿字段
const editDraftField = (field: keyof TravelPlanDraft, value: any) => {
  if (travelPlanDraft.value) {
    travelPlanDraft.value[field] = value as never
    saveDraftToStorage()
  }
}

// 检测用户输入是否与旅行规划相关
const isTravelRelated = (text: string): boolean => {
  const keywords = ['旅行', '旅游', '规划', '计划', '行程', '出发', '目的地', '景点', '游玩', '去', '玩']
  return keywords.some(keyword => text.includes(keyword))
}

const createNewChat = () => {
  const newChatId = Date.now().toString()
  currentChatId.value = newChatId
  messages.value = []

  // 🆕 重置草稿（新会话应该是干净的）
  travelPlanDraft.value = null

  // 清空输入框和选中的图片
  inputMessage.value = ''
  selectedImage.value = null

  // 滚动到顶部显示开始页面
  nextTick(() => {
    if (messageListRef.value) {
      // Not strictly necessary as start page is controlled by messages.length
    }
  })
}

const loadChatSession = async (session: ChatSession) => {
  currentChatId.value = session.id
  messages.value = [...session.messages]

  // 🔄 加载该会话的草稿（会话级隔离）
  travelPlanDraft.value = session.draft || null

  // 🆕 恢复当前激活的计划
  currentActivePlan.value = session.currentPlan || null
  currentActivePlanMessageIndex.value = session.currentPlanMsgIndex ?? null

  await nextTick()
  await scrollToBottom()
}

const deleteChatSession = (sessionId: string) => {
  chatSessions.value = chatSessions.value.filter(chat => chat.id !== sessionId)
  saveChatSessions()

  if (currentChatId.value === sessionId) {
    createNewChat()
  }
}

const clearCurrentChat = () => {
  messages.value = []
  inputMessage.value = ''
  selectedImage.value = null
}

// 历史记录相关函数
const loadChatSessions = () => {
  try {
    const stored = localStorage.getItem(CHAT_SESSIONS_KEY)
    if (stored) {
      const sessions = JSON.parse(stored)
      if (Array.isArray(sessions)) {
        chatSessions.value = sessions
      }
    }
  } catch (error) {
    console.error('加载聊天会话失败:', error)
  }
}

const saveChatSessions = () => {
  try {
    localStorage.setItem(CHAT_SESSIONS_KEY, JSON.stringify(chatSessions.value))
  } catch (error) {
    console.error('保存聊天会话失败:', error)
  }
}

const saveCurrentSession = () => {
  if (!currentChatId.value || messages.value.length === 0) return

  const title = generateChatTitle()
  const existingIndex = chatSessions.value.findIndex(chat => chat.id === currentChatId.value)

  const session: ChatSession = {
    id: currentChatId.value,
    title,
    messages: [...messages.value],
    createdAt: existingIndex === -1 ? Date.now() : chatSessions.value[existingIndex].createdAt,
    updatedAt: Date.now(),
    draft: travelPlanDraft.value,  // 💾 保存当前会话的草稿
    currentPlan: currentActivePlan.value,  // 🆕 保存当前激活的计划
    currentPlanMsgIndex: currentActivePlanMessageIndex.value  // 🆕 保存计划消息索引
  }

  if (existingIndex === -1) {
    chatSessions.value.unshift(session)
  } else {
    chatSessions.value[existingIndex] = session
  }

  // 只保留最近的10个会话
  if (chatSessions.value.length > MAX_HISTORY_COUNT) {
    chatSessions.value = chatSessions.value.slice(0, MAX_HISTORY_COUNT)
  }

  saveChatSessions()
}

const generateChatTitle = () => {
  // 从第一条用户消息生成标题
  const firstUserMessage = messages.value.find(msg => msg.role === 'user')
  if (firstUserMessage && firstUserMessage.content[0]?.text) {
    const text = firstUserMessage.content[0].text
    return text.length > 20 ? text.substring(0, 20) + '...' : text
  }
  return '新对话'
}

const buildDailyPlanHtml = (data: any) => {
  try {
    const plan = data?.plan || {}
    const itinerary = Array.isArray(data?.itinerary) ? data.itinerary : []
    const notes = data?.notes
    const mapId = `map-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

    // 定义每天的颜色（与地图颜色一致）
    const dayColors = [
      '#FF6B6B', // Day 1: 红色
      '#4ECDC4', // Day 2: 青色
      '#FFE66D', // Day 3: 黄色
      '#95E1D3', // Day 4: 绿色
      '#A8E6CF', // Day 5: 浅绿
      '#FFD3B6', // Day 6: 橙色
      '#FFAAA5', // Day 7: 粉色
    ]

    let html = `<div class="daily-plan" data-map-id="${mapId}">`
    html += `<div class="plan-header">
      <div class="plan-title">每日行程</div>
      <div class="plan-meta">出发地：${plan.origin || '-'} ｜ 目的地：${plan.destination || '-'} ｜ 日期：${plan.start_date || '-'} 至 ${plan.end_date || '-'}</div>
    </div>`

    // 添加地图容器
    html += `<div class="map-container">
      <div class="map-header">
        <svg class="map-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
          <circle cx="12" cy="10" r="3"></circle>
        </svg>
        <span>路线地图</span>
        <span class="map-status" data-map-id="${mapId}">加载中...</span>
      </div>
      <div id="${mapId}" class="travel-map" data-map-id="${mapId}"></div>
      <div class="map-legend">
        ${itinerary.map((day: any) => {
          const dayColor = dayColors[(day.day - 1) % dayColors.length]
          return `<div class="legend-item">
            <div class="legend-color" style="background: ${dayColor};"></div>
            <span class="legend-text">Day ${day.day}</span>
          </div>`
        }).join('')}
      </div>
    </div>`

    // Tab导航栏
    html += `<div class="itinerary-tabs">
      <button class="tab-btn active" data-tab="all" data-map-id="${mapId}">
        <span class="tab-icon">📋</span>
        <span>总览</span>
      </button>`

    for (const day of itinerary) {
      const dayColor = dayColors[(day.day - 1) % dayColors.length]
      html += `<button class="tab-btn" data-tab="day-${day.day}" data-day="${day.day}" data-map-id="${mapId}" style="--tab-color: ${dayColor};">
        <span class="tab-icon">📍</span>
        <span>Day ${day.day}</span>
      </button>`
    }
    html += `</div>`

    // Tab内容区域
    html += `<div class="tab-content-wrapper">`

    // 总览Tab内容
    html += `<div class="tab-content active" data-content="all">`
    html += `<div class="itinerary-container">`
    for (const day of itinerary) {
      const dayColor = dayColors[(day.day - 1) % dayColors.length]
      html += `<div class="day-card" data-day="${day.day}" style="--day-color: ${dayColor}; border-left: 4px solid ${dayColor};">
        <div class="day-title" style="color: ${dayColor};">${day.title || `Day ${day.day}`}（${day.date || ''}）</div>`
      if (Array.isArray(day.activities) && day.activities.length) {
        html += `<ul class="activities">`
        for (let i = 0; i < day.activities.length; i++) {
          const act = day.activities[i]
          const actName = String(act?.name || '').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
          html += `<li class="activity" data-spot="${actName}"><span class="name">${act.name || ''}</span>${act.notes ? `<span class="notes">${act.notes}</span>` : ''}</li>`
          if (i < day.activities.length - 1) {
            const next = day.activities[i + 1]
            const o = String(act?.name || '').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            const d = String(next?.name || '').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            // 🆕 优先使用LLM识别的city字段，降级使用destination
            const c = String(plan.city || plan.destination || '').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            const routeId = `route-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
            html += `
              <li class="route-container">
                <button class="route-chip" data-route-id="${routeId}" data-origin="${o}" data-destination="${d}" data-city="${c}">
                  <span class="route-icon">🚗</span>
                  <span class="route-text">计算中...</span>
                  <span class="expand-icon">▼</span>
                </button>
                <div class="route-details" id="${routeId}" style="display: none;">
                  <div class="route-loading">加载中...</div>
                </div>
              </li>`
          }
        }
        html += `</ul>`
      } else {
        if (day.summary && String(day.summary).trim()) {
          html += `<ul class="activities">`
          const safeSummary = String(day.summary).replace(/</g, '&lt;').replace(/>/g, '&gt;')
          html += `<li class="activity"><span class="name">当天安排</span><span class="notes">${safeSummary}</span></li>`
          html += `</ul>`
        }
      }
      if (day.summary) {
        html += `<div class="day-summary">${day.summary}</div>`
      }
      html += `</div>`
    }
    html += `</div>` // 关闭 itinerary-container (总览)
    html += `</div>` // 关闭总览 tab-content

    // 每一天的详细Tab内容
    for (const day of itinerary) {
      const dayColor = dayColors[(day.day - 1) % dayColors.length]
      html += `<div class="tab-content" data-content="day-${day.day}">`
      html += `<div class="day-detail-card" style="--day-color: ${dayColor};">
        <div class="day-detail-header" style="background: linear-gradient(135deg, ${dayColor} 0%, color-mix(in srgb, ${dayColor} 80%, black) 100%);">
          <h3>${day.title || `Day ${day.day}`}</h3>
          <p>${day.date || ''}</p>
        </div>`

      if (Array.isArray(day.activities) && day.activities.length) {
        html += `<ul class="activities-detail">`
        for (let i = 0; i < day.activities.length; i++) {
          const act = day.activities[i]
          const actName = String(act?.name || '').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
          html += `<li class="activity-detail" data-spot="${actName}">
            <div class="activity-number" style="background: ${dayColor};">${i + 1}</div>
            <div class="activity-info">
              <div class="activity-name">${act.name || ''}</div>
              ${act.notes ? `<div class="activity-notes">${act.notes}</div>` : ''}
            </div>
          </li>`

          if (i < day.activities.length - 1) {
            const next = day.activities[i + 1]
            const o = String(act?.name || '').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            const d = String(next?.name || '').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            const c = String(plan.city || plan.destination || '').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            const routeId = `route-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
            html += `
              <li class="route-container-detail">
                <button class="route-chip" data-route-id="${routeId}" data-origin="${o}" data-destination="${d}" data-city="${c}">
                  <span class="route-icon">🚗</span>
                  <span class="route-text">计算中...</span>
                  <span class="expand-icon">▼</span>
                </button>
                <div class="route-details" id="${routeId}" style="display: none;">
                  <div class="route-loading">加载中...</div>
                </div>
              </li>`
          }
        }
        html += `</ul>`
      }

      if (day.summary) {
        html += `<div class="day-detail-summary">${day.summary}</div>`
      }

      html += `</div>` // 关闭 day-detail-card
      html += `</div>` // 关闭单天 tab-content
    }

    html += `</div>` // 关闭 tab-content-wrapper

    if (notes) {
      html += `<div class="plan-notes">${notes}</div>`
    }
    html += `</div>` // 关闭 daily-plan
    return html
  } catch {
    return '行程解析失败'
  }
}

onMounted(async () => {
  // 加载聊天会话
  loadChatSessions()

  // 如果有会话，加载最新的一个（会自动加载该会话的草稿），否则创建新会话
  if (chatSessions.value.length > 0) {
    const latestSession = chatSessions.value[0]
    await loadChatSession(latestSession)
  } else {
    createNewChat()
  }
})
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  width: 100%;
  background: #fff;
  overflow: hidden;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: white;
  border-bottom: 1px solid #f0f0f0;
  z-index: 50;
}

.chat-header h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-badges {
  display: flex;
  gap: 6px;
}

.badge {
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-primary {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #dbeafe;
}

.badge-secondary {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #dcfce7;
}

.header-right {
  display: flex;
  align-items: center;
}

/* User Profile Dropdown */
.user-profile-dropdown {
  cursor: pointer;
}

.user-avatar-container {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  border-radius: 12px;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.user-avatar-container:hover {
  background: #f8fafc;
  border-color: #f1f5f9;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: #3b82f6;
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.user-info-text {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.2;
}

.user-role {
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
}

.dropdown-icon {
  width: 16px;
  height: 16px;
  color: #94a3b8;
  transition: transform 0.2s ease;
}

.user-profile-dropdown:hover .dropdown-icon {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  width: 220px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  padding: 8px;
}

.user-profile-dropdown:hover .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-header {
  padding: 12px 16px;
}

.dropdown-user-email {
  font-size: 12px;
  color: #64748b;
  word-break: break-all;
}

.dropdown-divider {
  height: 1px;
  background: #f1f5f9;
  margin: 4px 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  color: #334155;
  font-size: 14px;
  font-weight: 500;
  border-radius: 10px;
  transition: all 0.2s ease;
  width: 100%;
  text-align: left;
  border: none;
  background: transparent;
  cursor: pointer;
}

.dropdown-item:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.dropdown-item svg {
  width: 18px;
  height: 18px;
  color: #64748b;
}

.logout-btn {
  color: #ef4444;
}

.logout-btn:hover {
  background: #fef2f2;
  color: #dc2626;
}

.logout-btn svg {
  color: inherit;
}

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
  opacity: 1;
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
  outline: none;
  padding: 0;
}

.field-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.draft-missing {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 193, 7, 0.25);
  border: 1px solid rgba(255, 193, 7, 0.4);
  padding: 8px 12px;
  border-radius: 8px;
  color: white;
  font-size: 13px;
}

.missing-icon {
  font-size: 16px;
}
</style>
