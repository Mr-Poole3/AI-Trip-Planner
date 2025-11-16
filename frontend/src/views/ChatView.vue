<template>
  <div class="app-container">
    <!-- 左侧边栏 -->
    <div class="sidebar">
      <div class="sidebar-content">
        <!-- 功能模块区域 -->
        <div class="features-section">
          <div class="feature-item new-chat-btn" @click="createNewChat">
            <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            <span class="feature-text">新聊天</span>
          </div>
        </div>
        <!-- 搜索框 -->
        <div class="search-section">
          <input
            v-model="searchQuery"
            placeholder="搜索聊天..."
            class="search-input"
          />
        </div>
        <!-- 聊天记录列表 -->
        <div class="chat-history-section">
          <div class="section-title">聊天</div>
          <div class="chat-history-list">
            <div
              v-for="(chat, index) in filteredChatHistory"
              :key="chat.id"
              @click="loadChatSession(chat)"
              class="chat-history-item"
              :class="{ active: currentChatId === chat.id }"
            >
              <div class="chat-title">{{ chat.title }}</div>
              <div class="chat-time">{{ formatTime(chat.updatedAt) }}</div>
              <button @click.stop="deleteChatSession(chat.id)" class="delete-chat-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主聊天区域 -->
    <div class="main-content">
      <div class="chat-header">
        <div class="header-left">
          <h1>AI 助手</h1>
        </div>
        <div class="header-actions">
          <button @click="clearCurrentChat" class="clear-btn">清空对话</button>
        </div>
      </div>

          <div class="chat-messages" ref="messagesContainer">
        <!-- 开始页面 - 当没有消息时显示 -->
        <div v-if="messages.length === 0" class="start-page">
          <div class="start-content">
            <h1 class="start-title">您在忙什么？</h1>
            <div class="start-input-wrapper">
              <input
                v-model="inputMessage"
                @keypress.enter="sendMessage"
                placeholder="向AI助手发送消息"
                class="start-input"
                :disabled="isLoading"
              />
              <button @click="sendMessage" :disabled="isLoading || !canSend" class="start-send-btn">
                <span>↗</span>
              </button>
            </div>
            <div class="start-actions">
              <button @click="bookingEnabled = !bookingEnabled" class="booking-toggle-btn" :class="{ active: bookingEnabled }" title="启用/关闭酒店搜索">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="5" width="18" height="14" rx="2"/>
                  <path d="M8 9h8M8 13h6"/>
                </svg>
                <span>酒店搜索</span>
              </button>
            </div>
          </div>
        </div>

        <!-- 正常聊天消息 -->
        <div v-for="(message, index) in messages" :key="index" class="message-wrapper">
        <div :class="['message', message.role]">
          <div class="message-avatar">
            <svg v-if="message.role === 'user'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="10" rx="2"/>
              <path d="M7 11V7a5 5 0 0110 0v4"/>
            </svg>
          </div>
          <div class="message-content">
            <!-- 酒店步骤展示 -->
            <div v-if="message.hotelSteps && message.hotelSteps.length" class="steps-container">
              <div v-for="(step, stepIndex) in message.hotelSteps" :key="stepIndex" :class="['step-item', step.status]">
                <div class="step-header">
                  <div class="step-icon">
                    <span v-if="step.status === 'running'">⏳</span>
                    <span v-else-if="step.status === 'completed'">✅</span>
                    <span v-else-if="step.status === 'error'">❌</span>
                    <span v-else>⭕</span>
                  </div>
                  <div class="step-info">
                    <div class="step-title">步骤 {{ step.step }}: {{ step.message }}</div>
                    <div v-if="step.data" class="step-data">
                      <pre>{{ JSON.stringify(step.data, null, 2) }}</pre>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!-- 旅行规划步骤展示 -->
            <div v-if="message.travelSteps && message.travelSteps.length" class="steps-container">
              <div v-for="(step, stepIndex) in message.travelSteps" :key="stepIndex" :class="['step-item', step.status]">
                <div class="step-header">
                  <div class="step-icon">
                    <span v-if="step.status === 'running'">⏳</span>
                    <span v-else-if="step.status === 'completed'">✅</span>
                    <span v-else-if="step.status === 'error'">❌</span>
                    <span v-else>⭕</span>
                  </div>
                  <div class="step-info">
                    <div class="step-title">步骤 {{ step.step }}: {{ step.message }}</div>
                  </div>
                </div>
              </div>
            </div>
            <!-- 思考过程展示 -->
            <div v-if="showReasoningGlobal && message.reasoning && message.reasoning.trim()" class="reasoning-section">
              <div class="reasoning-header">
                <div class="left">
                  <svg class="reasoning-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/>
                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                  <span class="reasoning-title">思考过程</span>
                </div>
                <button
                  @click="showReasoning[index] = !showReasoning[index]"
                  class="toggle-reasoning"
                >
                  {{ showReasoning[index] ? '收起' : '展开' }}
                </button>
              </div>
              <div v-show="showReasoning[index]" class="reasoning-content">
                {{ message.reasoning }}
              </div>
            </div>

            <!-- 工具调用信息 -->
            <div v-if="message.toolCalls && message.toolCalls.length > 0" class="tool-calls-section">
              <div class="tool-calls-header">
                <svg class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/>
                </svg>
                <span class="tool-title">工具调用</span>
              </div>
              <div v-for="(toolCall, toolIndex) in message.toolCalls" :key="toolIndex" class="tool-call">
                <div class="tool-call-header">
                  <span class="tool-name">{{ toolCall.name }}</span>
                  <span v-if="toolCall.server_name" class="tool-server">({{ toolCall.server_name }})</span>
                </div>

                <!-- 工具参数 -->
                <div v-if="toolCall.arguments && Object.keys(toolCall.arguments).length > 0" class="tool-arguments">
                  <strong>参数:</strong>
                  <code>{{ JSON.stringify(toolCall.arguments, null, 2) }}</code>
                </div>

                <!-- 工具结果 - 使用抽屉展示 -->
                <div v-if="toolCall.result" class="tool-result-drawer">
                  <div class="drawer-header">
                    <strong>结果:</strong>
                    <button
                      @click="toggleToolResult(index, toolIndex)"
                      class="drawer-toggle"
                      :class="{ expanded: isToolResultExpanded(index, toolIndex) }"
                    >
                      {{ isToolResultExpanded(index, toolIndex) ? '收起' : '展开' }}
                    </button>
                  </div>
                  <div class="drawer-content">
                    <div v-if="!isToolResultExpanded(index, toolIndex)" class="result-preview">
                      {{ truncateText(toolCall.result, 100) }}
                      <span v-if="toolCall.result.length > 100" class="more-indicator">
                        ...
                        <span class="expand-hint">点击展开查看完整内容</span>
                      </span>
                    </div>
                    <div v-else class="result-full">
                      <pre>{{ toolCall.result }}</pre>
                    </div>
                  </div>
                </div>

                <!-- 工具错误 -->
                <div v-if="toolCall.error" class="tool-error">
                  <strong>错误:</strong> {{ toolCall.error }}
                </div>
              </div>
            </div>

            <!-- 消息内容 -->
            <div v-for="(content, contentIndex) in message.content" :key="contentIndex">
              <div v-if="content.type === 'text'" class="message-text markdown-body" v-html="renderMarkdown(content.text)"></div>
              <div v-else-if="content.type === 'html'" class="message-html" v-html="content.text"></div>
              <img v-if="content.type === 'image_url' && content.image_url" :src="content.image_url.url" class="message-image" />
            </div>

            <!-- 轻量流式状态提示 -->
            <div v-if="message.isStreaming" class="streaming-status">生成中…</div>
          </div>
        </div>
      </div>

      <!-- 取消底部加载占位文本框 -->
    </div>
          <div v-if="messages.length > 0" class="chat-input-container">
        <div v-if="selectedImage" class="image-preview">
        <img :src="selectedImage" alt="预览图片" />
        <button @click="removeImage" class="remove-image-btn">×</button>
      </div>

      <div class="input-wrapper">
        <input
          type="file"
          ref="fileInput"
          @change="handleImageUpload"
          accept="image/*"
          style="display: none"
        />
        <button @click="fileInput?.click()" class="image-btn" title="上传图片">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <path d="M21 15l-5-5L5 21"/>
          </svg>
        </button>
        <!-- 酒店搜索开关按钮，样式与“深度思考”按钮一致的圆角与布局 -->
        <button @click="bookingEnabled = !bookingEnabled" class="booking-toggle-btn" :class="{ active: bookingEnabled }" title="启用/关闭酒店搜索">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="5" width="18" height="14" rx="2"/>
            <path d="M8 9h8M8 13h6"/>
          </svg>
          <span>酒店搜索</span>
        </button>
        <input
          v-model="inputMessage"
          @keypress.enter="sendMessage"
          placeholder="输入消息..."
          class="message-input"
          :disabled="isLoading"
        />
        <button @click="sendMessage" :disabled="isLoading || !canSend" class="send-btn">
          发送
        </button>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { marked, Renderer } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

interface MessageContent {
  type: 'text' | 'image_url' | 'html'
  text?: string
  image_url?: { url: string }
}

// 酒店步骤信息类型
interface StepInfo {
  step: number
  status: 'pending' | 'running' | 'completed' | 'error'
  message: string
  data?: any
}

interface Message {
  role: 'user' | 'assistant'
  content: MessageContent[]
  reasoning?: string  // 思考过程
  isStreaming?: boolean  // 是否正在流式接收
  toolCalls?: ToolCall[]  // 工具调用信息
  hotelSteps?: StepInfo[] // 酒店步骤
  travelSteps?: StepInfo[] // 旅行步骤
}

interface ToolCall {
  name: string
  arguments: Record<string, any>
  result?: string
  error?: string
  server_name?: string
}

const messages = ref<Message[]>([])
const inputMessage = ref('')
const selectedImage = ref<string | null>(null)
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement>()
const fileInput = ref<HTMLInputElement>()
const showReasoning = ref<Record<number, boolean>>({})
const bookingEnabled = ref(false)
const travelStepMsgMap = ref<Record<number, number>>({})

// 思考过程显示控制（默认关闭）
const showReasoningGlobal = ref(false)

// 历史记录管理
const CHAT_HISTORY_KEY = 'ai_chat_history'
const CHAT_SESSIONS_KEY = 'ai_chat_sessions'
const MAX_HISTORY_COUNT = 10


const searchQuery = ref('')
const currentChatId = ref<string | null>(null)
const chatSessions = ref<ChatSession[]>([])

// 聊天会话接口
interface ChatSession {
  id: string
  title: string
  messages: Message[]
  createdAt: number
  updatedAt: number
}

const canSend = computed(() => {
  return (inputMessage.value.trim() || selectedImage.value) && !isLoading.value
})

// Markdown 渲染配置与工具
// 使用 Renderer 覆盖代码块渲染以实现高亮
const renderer = new Renderer()
renderer.code = (code: string, infostring?: string) => {
  const lang = (infostring || '').trim()
  let highlighted = ''
  try {
    if (lang && hljs.getLanguage(lang)) {
      highlighted = hljs.highlight(code, { language: lang }).value
    } else {
      highlighted = hljs.highlightAuto(code).value
    }
  } catch {
    highlighted = code
  }
  const classAttr = lang ? ` class="language-${lang}"` : ''
  return `<pre><code${classAttr}>${highlighted}</code></pre>`
}

marked.setOptions({ gfm: true, breaks: true, renderer })

const renderMarkdown = (text: string | undefined) => {
  const parsed = marked.parse(text || '')
  if (typeof parsed === 'string') {
    return DOMPurify.sanitize(parsed)
  }
  // Fallback: 如果返回 Promise（未启用 async），同步返回原文的安全版本
  return DOMPurify.sanitize(text || '')
}

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
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const handleImageUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

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
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const sendMessage = async () => {
  if (!canSend.value) return

  const content: MessageContent[] = []

  if (inputMessage.value.trim()) {
    content.push({
      type: 'text',
      text: inputMessage.value.trim()
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
  if (fileInput.value) {
    fileInput.value.value = ''
  }

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

      const response = await fetch('http://localhost:9000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: original,
          system_prompt: (() => {
            const fmt = new Intl.DateTimeFormat('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
            const s = fmt.format(new Date()).replace(/\//g, '-')
            return `当前北京时间：${s}。请参考该时间理解用户在本次消息中的日期表达（未给年份时礼貌确认，勿自行假设）。可选项（人数、景点）未提供时，请直接生成不含这些字段的计划，不要向用户提问可选项；如需建议，用notes字段说明，勿使用ask。输出活动仅包含景点推荐，所有activities[].name必须为单一、标准化的中文景点官方名称，不得包含斜杠、顿号或并列名称；不输出time字段；需要说明从属关系或补充信息写入notes。`
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

      if (result.type === 'ask') {
        messages.value.push({ role: 'assistant', content: [], travelSteps: [{ step: 2, status: 'completed', message: '需要补充信息' }] })
        messages.value.push({ role: 'assistant', content: [{ type: 'text', text: result.content }] })
        saveCurrentSession()
        return
      }

      if (result.type === 'daily_plan_json') {
        messages.value.push({ role: 'assistant', content: [], travelSteps: [{ step: 2, status: 'running', message: '正在生成每日计划...' }] })
        const html = buildDailyPlanHtml(result)
        messages.value.push({ role: 'assistant', content: [{ type: 'html', text: html }] })
        const idx2 = messages.value.length - 2
        messages.value[idx2].travelSteps = [{ step: 2, status: 'completed', message: '每日计划生成完成' }]
        messages.value[idx2] = { ...messages.value[idx2] }
        await populateRoutesForMessage(messages.value.length - 1, result?.plan?.destination || '')
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

      const response = await fetch('http://localhost:9000/api/hotel-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: (content.find(c => c.type === 'text')?.text) || '' })
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

// 旧的clearChat函数已被clearCurrentChat替代



const createNewChat = () => {
  console.log('创建新聊天被调用')
  const newChatId = Date.now().toString()
  currentChatId.value = newChatId
  messages.value = []

  // 清空输入框和选中的图片
  inputMessage.value = ''
  selectedImage.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }

  // 清空工具调用结果展开状态
  toolResultExpanded.value = {}

  console.log('新聊天已创建，ID:', newChatId)
  console.log('当前消息数量:', messages.value.length)

  // 滚动到顶部显示开始页面
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = 0
    }
  })

  // 不添加欢迎消息，显示开始页面
}

const loadChatSession = (session: ChatSession) => {
  currentChatId.value = session.id
  messages.value = [...session.messages]
}

const deleteChatSession = (sessionId: string) => {
  chatSessions.value = chatSessions.value.filter(chat => chat.id !== sessionId)
  saveChatSessions()

  if (currentChatId.value === sessionId) {
    createNewChat()
  }
}

const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (diffDays === 1) {
    return '昨天'
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else {
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }
}

const clearCurrentChat = () => {
  messages.value = []

  // 清空输入框和选中的图片
  inputMessage.value = ''
  selectedImage.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }

  // 不添加欢迎消息，显示开始页面
}

// 应用建议
const applySuggestion = (suggestion: string) => {
  inputMessage.value = suggestion
}

// 历史记录相关函数
const loadChatHistory = () => {
  try {
    const stored = localStorage.getItem(CHAT_HISTORY_KEY)
    if (stored) {
      const history = JSON.parse(stored)
      if (Array.isArray(history)) {
        messages.value = history
      }
    }
  } catch (error) {
    console.error('加载聊天历史失败:', error)
  }
}

const saveChatHistory = () => {
  try {
    // 只保存最近的10条消息
    const messagesToSave = messages.value.slice(-MAX_HISTORY_COUNT)
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(messagesToSave))
  } catch (error) {
    console.error('保存聊天历史失败:', error)
  }
}

const clearChatHistory = () => {
  try {
    localStorage.removeItem(CHAT_HISTORY_KEY)
  } catch (error) {
    console.error('清除聊天历史失败:', error)
  }
}

// 会话管理函数
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
    updatedAt: Date.now()
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

// 工具调用结果抽屉状态
const toolResultExpanded = ref<Record<number, Record<number, boolean>>>({})

const toggleToolResult = (messageIndex: number, toolIndex: number) => {
  if (!toolResultExpanded.value[messageIndex]) {
    toolResultExpanded.value[messageIndex] = {}
  }
  toolResultExpanded.value[messageIndex][toolIndex] = !toolResultExpanded.value[messageIndex][toolIndex]
}

const isToolResultExpanded = (messageIndex: number, toolIndex: number) => {
  return toolResultExpanded.value[messageIndex]?.[toolIndex] ?? false
}

const truncateText = (text: string, maxLength: number) => {
  if (text.length <= maxLength) {
    return text
  }
  return text.substring(0, maxLength)
}

const buildDailyPlanHtml = (data: any) => {
  try {
    const plan = data?.plan || {}
    const itinerary = Array.isArray(data?.itinerary) ? data.itinerary : []
    const notes = data?.notes
    let html = `<div class="daily-plan">`
    html += `<div class="plan-header"><div class="plan-title">每日行程</div><div class="plan-meta">出发地：${plan.origin || '-'} ｜ 目的地：${plan.destination || '-'} ｜ 日期：${plan.start_date || '-'} 至 ${plan.end_date || '-'}</div></div>`
    for (const day of itinerary) {
      html += `<div class="day-card"><div class="day-title">${day.title || `Day ${day.day}`}（${day.date || ''}）</div>`
      if (Array.isArray(day.activities) && day.activities.length) {
        html += `<ul class="activities">`
        for (let i = 0; i < day.activities.length; i++) {
          const act = day.activities[i]
          html += `<li class="activity"><span class="name">${act.name || ''}</span>${act.notes ? `<span class="notes">${act.notes}</span>` : ''}</li>`
          if (i < day.activities.length - 1) {
            const next = day.activities[i + 1]
            const o = String(act?.name || '').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            const d = String(next?.name || '').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            html += `<li class="route-chip" data-origin="${o}" data-destination="${d}">🚗 计算中 ></li>`
          }
        }
        html += `</ul>`
      } else {
        if (day.summary && String(day.summary).trim()) {
          html += `<ul class="activities">`
          const safeSummary = String(day.summary).replace(/</g, '&lt;').replace(/>/g, '&gt;')
          html += `<li class="activity"><span class="time">全天</span><span class="name">当天安排</span><span class="notes">${safeSummary}</span></li>`
          html += `</ul>`
        }
      }
      if (day.summary) {
        html += `<div class="day-summary">${day.summary}</div>`
      }
      html += `</div>`
    }
    if (notes) {
      html += `<div class="plan-notes">${notes}</div>`
    }
    html += `</div>`
    return html
  } catch {
    return '行程解析失败'
  }
}

const buildDailyPlanPreview = (buffer: string) => {
  // 轻量预览：提取已出现的 day 与 title，生成骨架卡片
  try {
    const titles: Array<{ day?: string; title?: string }> = []
    const dayRegex = /"day"\s*:\s*(\d+)/g
    const titleRegex = /"title"\s*:\s*"([^"]+)"/g
    const days: number[] = []
    let m: RegExpExecArray | null
    while ((m = dayRegex.exec(buffer))) {
      days.push(Number(m[1]))
    }
    const tt: string[] = []
    let t: RegExpExecArray | null
    while ((t = titleRegex.exec(buffer))) {
      tt.push(t[1])
    }
    const len = Math.max(days.length, tt.length)
    for (let i = 0; i < len; i++) {
      titles.push({ day: days[i]?.toString(), title: tt[i] })
    }
    let html = `<div class="daily-plan">`
    html += `<div class="plan-header"><div class="plan-title">每日行程（预览）</div><div class="plan-meta">正在生成…</div></div>`
    titles.forEach((d, idx) => {
      html += `<div class="day-card skeleton"><div class="day-title">${d.title || `Day ${d.day || idx + 1}`}</div><div class="activities"><div class="activity"><span class="time">…</span><span class="name">生成中</span></div></div></div>`
    })
    html += `</div>`
    return html
  } catch {
    return '<div class="daily-plan">正在生成每日行程预览…</div>'
  }
}

// 填充路线芯片：基于相邻活动名称调用后端路线测试接口
const populateRoutesForMessage = async (msgIndex: number, city: string) => {
  await nextTick()
  const wrappers = messagesContainer.value?.querySelectorAll('.message-wrapper') || []
  const el = wrappers[msgIndex] as HTMLElement
  if (!el) return
  const chips = el.querySelectorAll('.route-chip')
  for (const chip of Array.from(chips)) {
    const origin = (chip as HTMLElement).getAttribute('data-origin') || ''
    const destination = (chip as HTMLElement).getAttribute('data-destination') || ''
    if (!origin || !destination) continue
    try {
      const res = await fetch('http://localhost:9000/api/amap-route-test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ origin_name: origin, destination_name: destination, city })
      })
      if (!res.ok) {
        (chip as HTMLElement).textContent = '🚗 路线待确认 >'
        continue
      }
      const data = await res.json()
      if (data?.success && data?.display) (chip as HTMLElement).textContent = data.display; else (chip as HTMLElement).textContent = '🚗 路线待确认 >'
    } catch {
      (chip as HTMLElement).textContent = '🚗 路线待确认 >'
    }
  }
}

// 新增的侧边栏功能方法
const focusSearch = () => {
  const searchInput = document.querySelector('.search-input') as HTMLInputElement
  if (searchInput) {
    searchInput.focus()
  }
}

const openLibrary = () => {
  console.log('打开库功能')
  // TODO: 实现库功能
}

const openSora = () => {
  console.log('打开Sora功能')
  // TODO: 实现Sora功能
}

const openGPT = () => {
  console.log('打开GPT功能')
  // TODO: 实现GPT功能
}

const openTravelGuide = () => {
  console.log('打开旅行指南功能')
  // TODO: 实现旅行指南功能
}

const openPaperWriter = () => {
  console.log('打开论文写手功能')
  // TODO: 实现论文写手功能
}

const openScholarGPT = () => {
  console.log('打开学术GPT功能')
  // TODO: 实现学术GPT功能
}

onMounted(async () => {
  // 加载聊天会话
  loadChatSessions()

  // 如果有会话，加载最新的一个，否则创建新会话
  if (chatSessions.value.length > 0) {
    const latestSession = chatSessions.value[0]
    loadChatSession(latestSession)
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

.message-html :deep(.daily-plan) {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  background: #F8F9FA;
  border: 1px solid #E9ECEF;
}
.message-html :deep(.plan-header) {
  margin-bottom: 4px;
}
.message-html :deep(.plan-title) {
  font-size: 18px;
  font-weight: 600;
  color: #202124;
}
.message-html :deep(.plan-meta) {
  font-size: 13px;
  color: #5F6368;
}
.message-html :deep(.day-card) {
  margin-top: 0;
  padding: 14px 16px 14px 28px;
  border-radius: 12px;
  background: #FFFFFF;
  border: 1px solid #E6E9EF;
  position: relative;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.message-html :deep(.day-card:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.10), 0 12px 28px rgba(0,0,0,0.12);
}
.message-html :deep(.day-card::before) {
  content: '';
  position: absolute;
  left: 10px;
  top: 18px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #1a73e8;
  box-shadow: 0 0 0 3px #E8F0FE;
}
.message-html :deep(.day-card:not(:last-child)::after) {
  content: '';
  position: absolute;
  left: 14px;
  top: 28px;
  bottom: -14px;
  width: 2px;
  background: #E8F0FE;
}
.message-html :deep(.skeleton) { opacity: 0.7 }
.message-html :deep(.day-title) {
  font-weight: 600;
  margin-bottom: 8px;
  color: #202124;
}
.message-html :deep(.activities) {
  list-style: none;
  padding: 0;
  margin: 0;
}
.message-html :deep(.route-chip) {
  display: inline-block;
  margin: 8px 0;
  background: #E8F0FE;
  color: #1a73e8;
  border: 1px solid #D2E3FC;
  border-radius: 10px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 600;
}
.message-html :deep(.activity) {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px dashed #ECEFF1;
  flex-wrap: wrap;
}
.message-html :deep(.activity:last-child) {
  border-bottom: none;
}
.message-html :deep(.time) {
  background: #E8F0FE;
  color: #1a73e8;
  border: 1px solid #D2E3FC;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 28px;
  width: 88px;
  padding: 0 12px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  line-height: 28px;
  white-space: nowrap;
  flex-shrink: 0;
}
.message-html :deep(.name) { font-weight: 600; color: #202124; flex: 1; min-width: 0; }
.message-html :deep(.notes) { color: #5F6368; flex-basis: 100%; margin-left: 0; }
.message-html :deep(.day-summary) { margin-top: 8px; color: #3C4043; }
.plan-notes { margin-top: 8px; font-size: 13px; color: #555; }

/* 侧边栏样式 */
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
  padding: 16px 24px;
  background: white;
  color: #333;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}



.chat-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-indicator {
  font-size: 12px;
  color: #6c757d;
  background: #e9ecef;
  padding: 4px 8px;
  border-radius: 12px;
  cursor: help;
}

.clear-btn {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  color: #333;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  background: #e9ecef;
}



.tool-calls-section {
  margin-bottom: 12px;
  padding: 12px;
  background: rgba(40, 167, 69, 0.1);
  border-radius: 8px;
  border-left: 4px solid #28a745;
  max-width: 100%;
  overflow: hidden;
}

.tool-calls-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 600;
  color: #28a745;
  font-size: 14px;
}

.tool-calls-header .tool-icon {
  width: 16px;
  height: 16px;
  color: #28a745;
}

.tool-call {
  background: rgba(255, 255, 255, 0.7);
  padding: 8px;
  border-radius: 6px;
  margin-bottom: 8px;
  max-width: 100%;
  overflow: hidden;
}

.tool-call:last-child {
  margin-bottom: 0;
}

.tool-call-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.tool-name {
  font-weight: 600;
  color: #495057;
}

.tool-server {
  color: #6c757d;
  font-size: 12px;
}

.tool-arguments {
  background: #f8f9fa;
  padding: 6px;
  border-radius: 4px;
  font-size: 12px;
  font-family: monospace;
  margin-bottom: 4px;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
  overflow-x: hidden;
}

.tool-result-drawer {
  margin-top: 8px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
  max-width: 100%;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f0f0f0;
  border-bottom: 1px solid #e0e0e0;
  font-weight: 600;
  color: #495057;
  font-size: 14px;
}

.drawer-toggle {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  transition: all 0.2s ease;
}

.drawer-toggle:hover {
  text-decoration: underline;
}

.drawer-toggle.expanded {
  color: #6c757d;
}

.drawer-content {
  padding: 12px;
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
  max-width: 100%;
  overflow: hidden;
}

.result-preview {
  font-family: monospace;
  font-size: 13px;
  line-height: 1.4;
  color: #343a40;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: break-word;
  max-height: 100px; /* 控制预览高度 */
  max-width: 100%;
  overflow-x: hidden;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch; /* 优化滚动体验 */
}

.result-full {
  font-family: monospace;
  font-size: 13px;
  line-height: 1.4;
  color: #343a40;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: break-word;
  max-height: 300px; /* 控制完整内容高度 */
  max-width: 100%;
  overflow-x: hidden;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch; /* 优化滚动体验 */
}

.more-indicator {
  color: #007bff;
  cursor: pointer;
  font-weight: bold;
}

.expand-hint {
  font-size: 12px;
  color: #6c757d;
  margin-left: 4px;
}

.tool-result {
  color: #28a745;
  font-size: 14px;
  margin-bottom: 4px;
}

.tool-error {
  color: #dc3545;
  font-size: 14px;
  margin-bottom: 4px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #fff;
  display: flex;
  flex-direction: column;
}

/* 开始页面样式 */
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

/* 建议提示样式 */
.suggestions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  width: 100%;
  max-width: 500px;
}

.suggestion-item {
  padding: 12px 16px;
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  color: #333;
  text-align: center;
}

.suggestion-item:hover {
  background: #e9ecef;
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
}

.message-wrapper {
  margin-bottom: 16px;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.message.user {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message.assistant {
  margin-right: auto;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-avatar svg {
  width: 20px;
  height: 20px;
}

.message.user .message-avatar {
  background: #007bff;
}

.message.user .message-avatar svg {
  color: white;
}

.message.assistant .message-avatar {
  background: #6c757d;
}

.message.assistant .message-avatar svg {
  color: white;
}

.message-content {
  background: white;
  padding: 12px 16px;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  word-wrap: break-word;
}

.message.user .message-content {
  background: #007bff;
  color: white;
}

.message-text {
  margin: 0;
  line-height: 1.5;
}

/* Markdown 基本样式 */
.markdown-body h1, .markdown-body h2, .markdown-body h3 {
  margin: 0.6em 0 0.4em;
}
.markdown-body pre {
  background: #f6f8fa;
  padding: 8px;
  border-radius: 8px;
  overflow: auto;
}
.markdown-body code {
  background: #f0f0f0;
  padding: 2px 4px;
  border-radius: 4px;
}
.markdown-body ul, .markdown-body ol {
  margin: 0.5em 0 0.5em 1.2em;
}

.message-image {
  max-width: 200px;
  max-height: 200px;
  border-radius: 8px;
  margin-top: 8px;
}

.reasoning-section {
  margin-bottom: 12px;
  padding: 12px;
  background: rgba(108, 117, 125, 0.1);
  border-radius: 8px;
  border-left: 4px solid #6c757d;
}

.reasoning-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  font-weight: 600;
  color: #6c757d;
  font-size: 14px;
}

.reasoning-header .left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-reasoning {
  background: rgba(108, 117, 125, 0.1);
  border: 1px solid rgba(108, 117, 125, 0.3);
  color: #6c757d;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.toggle-reasoning:hover {
  background: rgba(108, 117, 125, 0.2);
}

.reasoning-icon {
  width: 18px;
  height: 18px;
  color: #6c757d;
}

.reasoning-content {
  font-size: 14px;
  line-height: 1.4;
  color: #495057;
  white-space: pre-wrap;
}

/* 移除流式光标样式 */

/* 轻量的流式状态提示 */
.streaming-status {
  display: inline-block;
  margin-top: 4px;
  font-size: 12px;
  color: #6c757d;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #6c757d;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

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

/* 酒店搜索开关按钮 */
.booking-toggle-btn {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 10px 12px;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #495057;
}
.booking-toggle-btn svg {
  width: 18px;
  height: 18px;
}
.booking-toggle-btn:hover { background: #e9ecef; }
.booking-toggle-btn.active {
  background: #e8f4ff;
  border-color: #007bff;
  color: #0056b3;
}

/* 酒店步骤展示样式 */
.steps-container { display: flex; flex-direction: column; gap: 10px; }
.step-item { padding: 12px; border-radius: 8px; border-left: 4px solid #ccc; background: #f8f9fa; }
.step-item.running { border-left-color: #ffc107; background: #fff8e1; }
.step-item.completed { border-left-color: #28a745; background: #d4edda; }
.step-item.error { border-left-color: #dc3545; background: #f8d7da; }
.step-header { display: flex; gap: 10px; align-items: flex-start; }
.step-icon { font-size: 18px; flex-shrink: 0; }
.step-info { flex: 1; }
.step-title { font-weight: 600; color: #333; margin-bottom: 5px; }
.step-data { margin-top: 8px; padding: 8px; background: white; border-radius: 4px; font-size: 12px; }
.step-data pre { margin: 0; white-space: pre-wrap; word-break: break-word; }
</style>
const populateRoutesForMessage = async (msgIndex: number, city: string) => {
  await nextTick()
  const wrappers = messagesContainer.value?.querySelectorAll('.message-wrapper') || []
  const el = wrappers[msgIndex] as HTMLElement
  if (!el) return
  const chips = el.querySelectorAll('.route-chip')
  for (const chip of Array.from(chips)) {
    const origin = (chip as HTMLElement).getAttribute('data-origin') || ''
    const destination = (chip as HTMLElement).getAttribute('data-destination') || ''
    if (!origin || !destination) continue
    try {
      const res = await fetch('http://localhost:9000/api/amap-route-test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ origin_name: origin, destination_name: destination, city })
      })
      if (!res.ok) {
        (chip as HTMLElement).textContent = '🚗 路线待确认 >'
        continue
      }
      const data = await res.json()
      if (data?.success && data?.display) (chip as HTMLElement).textContent = data.display; else (chip as HTMLElement).textContent = '🚗 路线待确认 >'
    } catch {
      (chip as HTMLElement).textContent = '🚗 路线待确认 >'
    }
  }
}
