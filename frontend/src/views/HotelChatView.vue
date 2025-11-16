<template>
  <div class="hotel-chat-container">
    <div class="chat-header">
      <h1>🏨 智能酒店推荐助手</h1>
      <button @click="clearChat" class="clear-btn">清空对话</button>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <!-- 欢迎页面 -->
      <div v-if="messages.length === 0" class="welcome-page">
        <div class="welcome-content">
          <h2>您好！我是您的智能酒店推荐助手</h2>
          <p>告诉我您的旅行计划，我会为您推荐最合适的酒店</p>
          <div class="example-queries">
            <div class="example-item" @click="applySuggestion('我想在成都春熙路附近找个酒店，11月13号入住，住一晚，两个人')">
              "我想在成都春熙路附近找个酒店，11月13号入住，住一晚，两个人"
            </div>
            <div class="example-item" @click="applySuggestion('帮我找上海外滩的酒店，下周五入住，两晚')">
              "帮我找上海外滩的酒店，下周五入住，两晚"
            </div>
          </div>
        </div>
      </div>

      <!-- 聊天消息 -->
      <div v-for="(message, index) in messages" :key="index" class="message-wrapper">
        <div :class="['message', message.role]">
          <div class="message-avatar">
            <span v-if="message.role === 'user'">👤</span>
            <span v-else>🤖</span>
          </div>
          <div class="message-content">
            <div v-if="message.type === 'text'" class="message-text markdown-body" v-html="renderMarkdown(message.content)"></div>
            <div v-else-if="message.type === 'steps'" class="steps-container">
              <div v-for="(step, stepIndex) in message.steps" :key="stepIndex" 
                   :class="['step-item', step.status]">
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
            <div v-else-if="message.type === 'recommendation'" class="recommendation-text markdown-body" v-html="renderMarkdown(message.content)">
            </div>
            <span v-if="message.type === 'recommendation' && message.isStreaming" class="cursor">|</span>
          </div>
        </div>
      </div>

      <!-- 加载指示器 -->
      <div v-if="isLoading" class="message-wrapper">
        <div class="message assistant">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input-container">
      <div class="input-wrapper">
        <input
          v-model="inputMessage"
          @keypress.enter="sendMessage"
          placeholder="告诉我您的旅行计划..."
          class="message-input"
          :disabled="isLoading"
        />
        <button @click="sendMessage" :disabled="isLoading || !inputMessage.trim()" class="send-btn">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { marked, Renderer } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

interface Message {
  role: 'user' | 'assistant'
  type: 'text' | 'steps' | 'recommendation'
  content?: string
  steps?: StepInfo[]
  isStreaming?: boolean
}

interface StepInfo {
  step: number
  status: 'pending' | 'running' | 'completed' | 'error'
  message: string
  data?: any
}

const messages = ref<Message[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement>()

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

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

const renderMarkdown = (text?: string) => {
  const parsed = marked.parse(text || '')
  if (typeof parsed === 'string') {
    return DOMPurify.sanitize(parsed)
  }
  // Fallback: 如果返回 Promise（未启用 async），同步返回原文的安全版本
  return DOMPurify.sanitize(text || '')
}

const applySuggestion = (suggestion: string) => {
  inputMessage.value = suggestion
}

const clearChat = () => {
  messages.value = []
  inputMessage.value = ''
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMessage: Message = {
    role: 'user',
    type: 'text',
    content: inputMessage.value.trim()
  }

  messages.value.push(userMessage)
  const userInput = inputMessage.value.trim()
  inputMessage.value = ''
  isLoading.value = true

  await scrollToBottom()

  // 创建步骤消息
  const stepsMessage: Message = {
    role: 'assistant',
    type: 'steps',
    steps: []
  }
  messages.value.push(stepsMessage)
  // 使用响应式引用来更新步骤，避免直接修改原始对象导致不触发渲染
  const stepsIndex = messages.value.length - 1

  try {
    console.log('发送请求:', userInput)
    const response = await fetch('http://localhost:9000/api/hotel-chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: userInput
      })
    })

    console.log('响应状态:', response.status)

    if (!response.ok) {
      throw new Error('请求失败')
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('无法读取响应流')
    }

    let buffer = ''
    // 使用索引而非原始对象引用，确保通过响应式数组更新触发渲染
    let recommendationIndex: number | null = null

    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        console.log('流式读取完成')
        break
      }

      const chunk = decoder.decode(value, { stream: true })
      console.log('接收到数据块:', chunk.substring(0, 100))
      buffer += chunk
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.trim() && line.startsWith('data: ')) {
          try {
            const jsonStr = line.slice(6).trim()
            if (jsonStr) {
              console.log('接收到数据:', jsonStr) // 调试日志
              const data = JSON.parse(jsonStr)

              if (data.step) {
                // 更新步骤信息
                console.log('更新步骤:', data.step, data.status, data.message)
                const currentSteps = messages.value[stepsIndex].steps || []
                const existingStepIndex = currentSteps.findIndex((s: StepInfo) => s.step === data.step)
                if (existingStepIndex >= 0) {
                  currentSteps[existingStepIndex] = {
                    step: data.step,
                    status: data.status,
                    message: data.message,
                    data: data.data
                  }
                } else {
                  currentSteps.push({
                    step: data.step,
                    status: data.status,
                    message: data.message,
                    data: data.data
                  })
                }
                // 通过响应式数组引用替换，确保渲染更新
                messages.value[stepsIndex].steps = [...currentSteps]
                await nextTick()
                await scrollToBottom()
              } else if (data.type === 'recommendation_start') {
                // 开始接收推荐内容
                recommendationIndex = messages.value.length
                messages.value.push({
                  role: 'assistant',
                  type: 'recommendation',
                  content: '',
                  isStreaming: true
                })
                await scrollToBottom()
              } else if (data.type === 'recommendation_chunk') {
                // 流式接收推荐内容
                if (recommendationIndex !== null) {
                  const msg = messages.value[recommendationIndex]
                  msg.content = (msg.content || '') + data.content
                  // 直接通过响应式引用更新，避免原始对象更新不触发渲染
                  messages.value[recommendationIndex] = { ...msg }
                  await nextTick()
                  await scrollToBottom()
                }
              } else if (data.type === 'recommendation_end') {
                // 推荐内容接收完成
                if (recommendationIndex !== null) {
                  const msg = messages.value[recommendationIndex]
                  msg.isStreaming = false
                  messages.value[recommendationIndex] = { ...msg }
                }
              } else if (data.type === 'final_response') {
                // 兼容旧版本：非流式推荐结果
                messages.value.push({
                  role: 'assistant',
                  type: 'text',
                  content: data.content
                })
                await scrollToBottom()
              } else if (data.type === 'done') {
                // 完成
                await scrollToBottom()
                return
              } else if (data.type === 'error') {
                throw new Error(data.content)
              }
            }
          } catch (parseError) {
            console.warn('解析流数据失败:', parseError)
          }
        }
      }
    }

  } catch (error) {
    console.error('发送消息失败:', error)
    messages.value.push({
      role: 'assistant',
      type: 'text',
      content: '抱歉，处理您的请求时出现错误。请稍后重试。'
    })
    await scrollToBottom()
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.hotel-chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8f9fa;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.chat-header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.clear-btn {
  background: #f0f0f0;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #e0e0e0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome-page {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.welcome-content h2 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.welcome-content p {
  font-size: 16px;
  color: #666;
  margin-bottom: 30px;
}

.example-queries {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 600px;
}

.example-item {
  padding: 15px 20px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  color: #555;
}

.example-item:hover {
  background: #f0f7ff;
  border-color: #007bff;
}

.message-wrapper {
  margin-bottom: 20px;
}

.message {
  display: flex;
  gap: 15px;
  max-width: 800px;
}

.message.user {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #007bff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #28a745;
}

.message-content {
  flex: 1;
  background: white;
  padding: 15px 20px;
  border-radius: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.message.user .message-content {
  background: #e3f2fd;
}

.message-text {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #333;
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

.steps-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.step-item {
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid #ccc;
  background: #f8f9fa;
}

.step-item.running {
  border-left-color: #ffc107;
  background: #fff8e1;
}

.step-item.completed {
  border-left-color: #28a745;
  background: #d4edda;
}

.step-item.error {
  border-left-color: #dc3545;
  background: #f8d7da;
}

.step-header {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.step-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.step-info {
  flex: 1;
}

.step-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
}

.step-data {
  margin-top: 8px;
  padding: 8px;
  background: white;
  border-radius: 4px;
  font-size: 12px;
}

.step-data pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 10px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #999;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

.chat-input-container {
  padding: 20px 30px;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.input-wrapper {
  display: flex;
  gap: 10px;
  max-width: 800px;
  margin: 0 auto;
}

.message-input {
  flex: 1;
  padding: 12px 20px;
  border: 1px solid #e0e0e0;
  border-radius: 25px;
  font-size: 15px;
  outline: none;
  transition: all 0.2s;
}

.message-input:focus {
  border-color: #007bff;
}

.send-btn {
  padding: 12px 30px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #0056b3;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.recommendation-text {
  line-height: 1.8;
  color: #333;
  font-size: 15px;
}

.cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background: #007bff;
  margin-left: 2px;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}
</style>
