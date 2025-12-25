<template>
  <div class="message-wrapper" ref="messageWrapper">
    <div :class="['message', message.role]">
      <div class="message-avatar">
        <svg v-if="message.role === 'user'" viewBox="0 0 1024 1024" fill="currentColor">
          <path d="M445.781333 378.311111c-19.456 0-35.271111 15.815111-35.271111 35.271111V450.56c0 19.456 15.815111 35.271111 35.271111 35.271111s35.271111-15.815111 35.271111-35.271111v-36.977778c0-19.456-15.815111-35.271111-35.271111-35.271111zM615.879111 485.831111c19.456 0 35.271111-15.815111 35.271111-35.271111v-36.977778c0-19.456-15.815111-35.271111-35.271111-35.271111s-35.271111 15.815111-35.271111 35.271111V450.56c0 19.456 15.815111 35.271111 35.271111 35.271111z"/>
          <path d="M791.665778 841.272889c-0.113778-1.024-0.227556-2.048-0.455111-2.958222-6.144-33.678222-22.983111-65.536-47.445334-89.543111-9.329778-9.216-19.456-16.952889-30.378666-23.210667 16.611556-11.377778 32.199111-24.348444 46.762666-38.798222 61.326222-61.326222 95.118222-142.904889 95.118223-229.717334s-33.792-168.391111-95.118223-229.717333-142.904889-95.118222-229.717333-95.118222c-86.812444 0-168.391111 33.792-229.717333 95.118222-61.326222 61.326222-95.118222 142.904889-95.118223 229.717333s33.792 168.391111 95.118223 229.717334c14.449778 14.449778 30.151111 27.420444 46.762666 38.798222-10.581333 6.257778-20.593778 13.994667-29.582222 23.096889-23.665778 24.007111-40.049778 56.775111-46.08 92.16-0.113778 0.568889-0.227556 1.251556-0.227555 1.820444L265.102222 898.844444c-2.275556 19.342222 11.605333 36.864 30.947556 39.139556 1.365333 0.113778 2.730667 0.227556 4.096 0.227556 17.635556 0 32.881778-13.198222 35.043555-31.175112l6.371556-55.296c8.988444-51.086222 44.942222-74.296889 74.638222-74.296888h1.820445l42.894222-2.275556c0.682667 0 1.251556-0.113778 1.820444-0.113778 21.959111 4.664889 44.600889 7.054222 67.584 7.054222 23.096889 0 45.738667-2.389333 67.811556-7.054222 0.682667 0.113778 1.365333 0.113778 2.161778 0.227556l42.439111 2.275555h1.820444c39.253333 0 69.632 36.522667 76.8 72.362667l5.347556 56.433778c1.706667 18.204444 17.066667 31.971556 35.043555 31.971555 1.137778 0 2.275556 0 3.413334-0.113777 19.342222-1.820444 33.678222-19.000889 31.744-38.456889l-5.233778-58.481778zM472.177778 706.901333c-2.730667-1.137778-5.688889-1.820444-8.760889-2.161777-42.780444-11.491556-82.033778-34.133333-114.232889-66.332445-48.469333-48.469333-75.207111-112.867556-75.207111-181.475555s26.737778-133.006222 75.207111-181.475556S462.051556 200.248889 530.659556 200.248889s133.006222 26.737778 181.475555 75.207111c48.469333 48.469333 75.207111 112.867556 75.207111 181.475556S760.490667 589.937778 712.021333 638.293333c-32.312889 32.312889-71.68 71.68-71.68 113.379556V706.901333z"/>
        </svg>
        <svg v-else viewBox="0 0 1024 1024" fill="currentColor">
          <path d="M850.367451 513.489934c4.208858-5.538133 8.271384-11.088546 12.139481-16.651238 55.695486-80.095199 69.303412-153.764036 38.315654-207.435423-30.986735-53.671387-101.583606-78.719876-198.802812-70.535473-6.750751 0.568958-13.588483 1.310855-20.488637 2.187829-2.691295-6.414083-5.467525-12.70844-8.350179-18.838044-41.517579-88.280626-98.512664-136.898927-160.487158-136.898927-61.974493 0-118.969579 48.618301-160.485111 136.898927-2.883677 6.130627-5.658883 12.423961-8.350179 18.839067-6.901177-0.876973-13.739932-1.61887-20.490683-2.187829-97.209996-8.18645-167.813007 16.865109-198.800765 70.535473-30.987758 53.671387-17.380856 127.340223 38.314631 207.435423 3.867074 5.561669 7.9296 11.113105 12.139481 16.651238-4.209882 5.538133-8.271384 11.088546-12.139481 16.651238-55.694463 80.095199-69.301366 153.764036-38.314631 207.434399 27.13808 47.004547 84.658122 72.055083 163.830299 72.055083 11.228739 0 22.897499-0.50449 34.970466-1.51961 6.750751-0.568958 13.589506-1.310855 20.490683-2.187829 2.691295 6.414083 5.467525 12.70844 8.351202 18.839067 41.515532 88.281649 98.510618 136.89995 160.485111 136.89995 61.974493 0 118.969579-48.618301 160.487158-136.89995 2.883677-6.130627 5.658883-12.423961 8.350179-18.839067 6.900154 0.876973 13.737886 1.61887 20.488637 2.187829 12.081153 1.01819 23.737634 1.51961 34.972513 1.51961 79.162968 0 136.693242-25.052582 163.830299-72.055083 30.986735-53.670363 17.379832-127.3392-38.315654-207.434399C858.639858 524.579503 854.577333 519.028067 850.367451 513.489934zM705.378266 258.742972c79.704296-6.715959 138.322345 11.755742 160.790056 50.669006 22.467711 38.914288 9.157567 98.901521-36.513612 164.583452-1.775436 2.554172-3.603061 5.106298-5.459339 7.656377-27.969005-31.598672-61.164035-62.346977-98.369402-91.212398-6.39464-46.653553-16.426111-90.774423-29.806863-130.796952C699.155541 259.309884 702.278671 259.003915 705.378266 258.742972zM603.368964 670.542876c-30.015617 17.32969-60.426231 32.621978-90.675162 45"/>
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
              @click="toggleReasoning"
              class="toggle-reasoning"
            >
              {{ showReasoning ? '收起' : '展开' }}
            </button>
          </div>
          <div v-show="showReasoning" class="reasoning-content">
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
                  @click="toggleToolResult(toolIndex)"
                  class="drawer-toggle"
                  :class="{ expanded: isToolResultExpanded(toolIndex) }"
                >
                  {{ isToolResultExpanded(toolIndex) ? '收起' : '展开' }}
                </button>
              </div>
              <div class="drawer-content">
                <div v-if="!isToolResultExpanded(toolIndex)" class="result-preview">
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
          <!-- 🆕 文本内容 - 支持嵌入酒店卡片 -->
          <template v-if="content.type === 'text'">
            <div v-if="message.hotelsData && message.hotelsData.length">
              <!-- 解析文本并插入酒店卡片 -->
              <template v-for="(segment, segmentIndex) in parseTextWithHotelCards(content.text, message.hotelsData)" :key="segmentIndex">
                <div v-if="segment.type === 'text'" class="message-text markdown-body" v-html="renderMarkdown(segment.content)"></div>
                <template v-else-if="isHotelSegment(segment)">
                  <div class="hotel-card-inline">
                    <div class="hotel-card">
                      <div v-if="segment.hotel.image" class="hotel-image-wrapper">
                        <img :src="segment.hotel.image" :alt="segment.hotel.name" class="hotel-image" loading="lazy" />
                      </div>
                      <div class="hotel-info">
                        <h3 class="hotel-name">{{ segment.hotel.name }}</h3>
                        <div class="hotel-details">
                          <div class="hotel-price">{{ segment.hotel.price }}</div>
                          <div class="hotel-score">⭐ {{ segment.hotel.score }}</div>
                        </div>
                        <div class="hotel-location">📍 {{ segment.hotel.location }}</div>
                        <div v-if="segment.hotel.facilities && segment.hotel.facilities.length" class="hotel-facilities">
                          <span v-for="(facility, facilityIndex) in segment.hotel.facilities.slice(0, 3)" :key="facilityIndex" class="facility-tag">
                            {{ facility }}
                          </span>
                        </div>
                        <a
                          v-if="segment.hotel.url"
                          :href="segment.hotel.url"
                          target="_blank"
                          rel="noopener noreferrer"
                          class="booking-btn"
                        >
                          立即预订 →
                        </a>
                      </div>
                    </div>
                  </div>
                </template>
              </template>
            </div>
            <div v-else class="message-text markdown-body" v-html="renderMarkdown(content.text)"></div>
          </template>
          <div v-else-if="content.type === 'html'" class="message-html" v-html="content.text"></div>
          <img v-if="content.type === 'image_url' && content.image_url" :src="content.image_url.url" class="message-image" />
        </div>

        <!-- 轻量流式状态提示 -->
        <div v-if="message.isStreaming" class="streaming-status">生成中…</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { renderMarkdown, parseTextWithHotelCards, isHotelSegment } from '@/utils/chatUtils'
import type { Message } from '@/types/chat'

const props = defineProps<{
  message: Message
  index: number
  showReasoningGlobal: boolean
}>()

const showReasoning = ref(false)
const toolResultExpanded = ref<Record<number, boolean>>({})
const messageWrapper = ref<HTMLElement | null>(null)

const toggleReasoning = () => {
  showReasoning.value = !showReasoning.value
}

const toggleToolResult = (toolIndex: number) => {
  toolResultExpanded.value[toolIndex] = !toolResultExpanded.value[toolIndex]
}

const isToolResultExpanded = (toolIndex: number) => {
  return toolResultExpanded.value[toolIndex] ?? false
}

const truncateText = (text: string, maxLength: number) => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength)
}

// Map Rendering Logic
const DAY_COLORS = [
  '#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#A8E6CF', '#FFD3B6', '#FFAAA5'
]

const travelMaps = new Map<string, any>()
const travelMapData = new Map<string, { itinerary: any[], coordsMap: Map<string, number[]>, daySpots: any[] }>()

const renderTravelMap = async () => {
  await nextTick()
  if (!messageWrapper.value) return

  const mapContainer = messageWrapper.value.querySelector('.travel-map') as HTMLElement
  if (!mapContainer) return

  const mapId = mapContainer.getAttribute('data-map-id') || ''
  if (!mapId) return

  // Check if map already exists
  if (travelMaps.has(mapId)) return

  const mapStatus = messageWrapper.value.querySelector(`.map-status[data-map-id="${mapId}"]`) as HTMLElement

  try {
    // Determine source of data: message.mapData or parse from HTML/message content
    // In ChatView.vue, it parsed itinerary from the plan result.
    // Here, we might not have the plan object directly available if it was just HTML.
    // However, ChatView.vue attached mapData to the message!

    let itinerary: any[] = []
    let city = ''
    let coordsMap = new Map<string, number[]>()

    if (props.message.mapData) {
      // Use cached data
      itinerary = props.message.mapData.itinerary
      city = props.message.mapData.city
      Object.entries(props.message.mapData.coordsMap).forEach(([name, coords]) => {
        coordsMap.set(name, coords)
      })
    } else if (props.message.content.some(c => c.type === 'html' && c.text?.includes('daily-plan'))) {
       // We might need to rely on the parent having set mapData.
       // If mapData is missing, we can't easily re-parse the HTML to get the itinerary structure.
       // But wait, ChatView.vue sets mapData immediately after generation.
       // So we should expect mapData to be present for maps that need rendering.
       if (mapStatus) mapStatus.textContent = '地图数据丢失'
       return
    } else {
      return
    }

    // Prepare daySpots
    const daySpots: Array<{ day: number; spots: string[]; color: string }> = []
    const allPlaces: string[] = []
    for (const day of itinerary) {
      if (Array.isArray(day.activities) && day.activities.length) {
        const spots = day.activities.map((act: any) => act.name).filter((name: string) => name)
        daySpots.push({
          day: day.day,
          spots,
          color: DAY_COLORS[(day.day - 1) % DAY_COLORS.length]
        })
        allPlaces.push(...spots)
      }
    }

    if (allPlaces.length === 0) {
      if (mapStatus) mapStatus.textContent = '无景点数据'
      return
    }

    // If coordsMap is empty (first run), fetch coords
    // But typically mapData has coordsMap.
    // If not, we would need to fetch.
    // Let's assume mapData is complete for now as ChatView ensures it.

    const allCoords = Array.from(coordsMap.values())
    if (allCoords.length === 0) {
       if (mapStatus) mapStatus.textContent = '无有效坐标'
       return
    }

    const centerLng = allCoords.reduce((sum, c) => sum + c[0], 0) / allCoords.length
    const centerLat = allCoords.reduce((sum, c) => sum + c[1], 0) / allCoords.length

    // @ts-ignore
    if (!window.AMap) {
      if (mapStatus) mapStatus.textContent = '地图API未加载'
      return
    }

    // @ts-ignore
    const map = new AMap.Map(mapContainer, {
      zoom: 12,
      center: [centerLng, centerLat],
      viewMode: '2D',
      mapStyle: 'amap://styles/light'
    })

    travelMaps.set(mapId, map)
    travelMapData.set(mapId, { itinerary, coordsMap, daySpots })

    // Draw
    for (const dayInfo of daySpots) {
      const dayCoords = dayInfo.spots
        .map(spot => coordsMap.get(spot))
        .filter((coords): coords is number[] => coords !== undefined)

      if (dayCoords.length === 0) continue

      if (dayCoords.length > 1) {
        // @ts-ignore
        const outlinePolyline = new AMap.Polyline({
          path: dayCoords,
          strokeColor: '#FFFFFF',
          strokeWeight: 8,
          strokeOpacity: 0.9,
          lineJoin: 'round',
          lineCap: 'round',
          zIndex: 10
        })
        map.add(outlinePolyline)

        // @ts-ignore
        const polyline = new AMap.Polyline({
          path: dayCoords,
          strokeColor: dayInfo.color,
          strokeWeight: 5,
          strokeOpacity: 1,
          lineJoin: 'round',
          lineCap: 'round',
          zIndex: 11
        })
        map.add(polyline)
      }

      dayInfo.spots.forEach((spotName, index) => {
        const coords = coordsMap.get(spotName)
        if (!coords) return

        // @ts-ignore
        const marker = new AMap.Marker({
          position: coords,
          title: spotName,
          label: {
            content: `<div style="display: flex; align-items: center; gap: 6px;">
              <div style="background: ${dayInfo.color}; color: white; padding: 6px 10px; border-radius: 16px; font-size: 13px; font-weight: bold; box-shadow: 0 3px 8px rgba(0,0,0,0.25); border: 2px solid white;">${index + 1}</div>
              <div style="background: rgba(255,255,255,0.95); color: ${dayInfo.color}; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; box-shadow: 0 2px 6px rgba(0,0,0,0.2);">Day ${dayInfo.day}</div>
            </div>`,
            direction: 'top',
            offset: [0, -10]
          }
        })

        // @ts-ignore
        marker.on('click', () => {
          // @ts-ignore
          const infoWindow = new AMap.InfoWindow({
            content: `<div style="padding: 10px;"><h4 style="margin: 0 0 6px 0; color: ${dayInfo.color};">${spotName}</h4><p style="margin: 0; color: #666; font-size: 13px; font-weight: 500;">Day ${dayInfo.day} - 第 ${index + 1} 站</p></div>`
          })
          infoWindow.open(map, coords)
        })

        map.add(marker)
      })
    }

    map.setFitView()
    if (mapStatus) mapStatus.textContent = '✓ 已加载'

    bindTabSwitchEvents(mapId)

  } catch (error) {
    console.error('渲染地图失败:', error)
    if (mapStatus) mapStatus.textContent = '渲染失败'
  }
}

const bindTabSwitchEvents = (mapId: string) => {
  nextTick(() => {
    if (!messageWrapper.value) return
    const dailyPlan = messageWrapper.value.querySelector(`.daily-plan[data-map-id="${mapId}"]`)
    if (!dailyPlan) return

    const tabBtns = dailyPlan.querySelectorAll('.tab-btn')
    const tabContents = dailyPlan.querySelectorAll('.tab-content')

    tabBtns.forEach(btn => {
      btn.addEventListener('click', function(this: HTMLElement) {
        const tabName = this.getAttribute('data-tab')
        const dayNum = this.getAttribute('data-day')

        tabBtns.forEach(b => b.classList.remove('active'))
        this.classList.add('active')

        tabContents.forEach(content => {
          const contentName = content.getAttribute('data-content')
          if (contentName === tabName) {
            content.classList.add('active')
          } else {
            content.classList.remove('active')
          }
        })

        if (tabName === 'all') {
          filterMapByDay(mapId, null)
        } else if (dayNum) {
          filterMapByDay(mapId, parseInt(dayNum))
        }
      })
    })
  })
}

const filterMapByDay = (mapId: string, dayNum: number | null) => {
  const map = travelMaps.get(mapId)
  const mapData = travelMapData.get(mapId)

  if (!map || !mapData) return

  const { daySpots, coordsMap } = mapData
  map.clearMap()

  const filteredDaySpots = dayNum === null
    ? daySpots
    : daySpots.filter((ds: any) => ds.day === dayNum)

  for (const dayInfo of filteredDaySpots) {
    const dayCoords = dayInfo.spots
      .map((spot: string) => coordsMap.get(spot))
      .filter((coords: any): coords is number[] => coords !== undefined)

    if (dayCoords.length === 0) continue

    if (dayCoords.length > 1) {
      // @ts-ignore
      const outlinePolyline = new AMap.Polyline({
        path: dayCoords,
        strokeColor: '#FFFFFF',
        strokeWeight: 8,
        strokeOpacity: 0.9,
        lineJoin: 'round',
        lineCap: 'round',
        zIndex: 10
      })
      map.add(outlinePolyline)

      // @ts-ignore
      const polyline = new AMap.Polyline({
        path: dayCoords,
        strokeColor: dayInfo.color,
        strokeWeight: 5,
        strokeOpacity: 1,
        lineJoin: 'round',
        lineCap: 'round',
        zIndex: 11
      })
      map.add(polyline)
    }

    dayInfo.spots.forEach((spotName: string, index: number) => {
      const coords = coordsMap.get(spotName)
      if (!coords) return

      // @ts-ignore
      const marker = new AMap.Marker({
        position: coords,
        title: spotName,
        label: {
          content: `<div style="display: flex; align-items: center; gap: 6px;">
            <div style="background: ${dayInfo.color}; color: white; padding: 6px 10px; border-radius: 16px; font-size: 13px; font-weight: bold; box-shadow: 0 3px 8px rgba(0,0,0,0.25); border: 2px solid white;">${index + 1}</div>
            <div style="background: rgba(255,255,255,0.95); color: ${dayInfo.color}; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; box-shadow: 0 2px 6px rgba(0,0,0,0.2);">Day ${dayInfo.day}</div>
          </div>`,
          direction: 'top',
          offset: [0, -10]
        }
      })

      // @ts-ignore
      marker.on('click', () => {
        // @ts-ignore
        const infoWindow = new AMap.InfoWindow({
          content: `<div style="padding: 10px;"><h4 style="margin: 0 0 6px 0; color: ${dayInfo.color};">${spotName}</h4><p style="margin: 0; color: #666; font-size: 13px; font-weight: 500;">Day ${dayInfo.day} - 第 ${index + 1} 站</p></div>`
        })
        infoWindow.open(map, coords)
      })

      map.add(marker)
    })
  }
  map.setFitView()
}

onMounted(() => {
  renderTravelMap()
})

</script>

<style scoped>
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
  background-color: #e2e8f0;
}

.message-content {
  padding: 12px 16px;
  border-radius: 18px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  word-wrap: break-word;
}

.message.user .message-content {
  background-color: #3b82f6;
  color: white;
}

/* Markdown Styles */
:deep(.markdown-body) {
  line-height: 1.6;
  font-size: 15px;
}

:deep(.markdown-body p) {
  margin: 0 0 10px 0;
}

:deep(.markdown-body p:last-child) {
  margin-bottom: 0;
}

:deep(.markdown-body ul), :deep(.markdown-body ol) {
  padding-left: 20px;
  margin: 0 0 10px 0;
}

:deep(.markdown-body li) {
  margin-bottom: 4px;
}

:deep(.markdown-body h1), :deep(.markdown-body h2), :deep(.markdown-body h3),
:deep(.markdown-body h4), :deep(.markdown-body h5), :deep(.markdown-body h6) {
  margin: 16px 0 8px 0;
  font-weight: 600;
  line-height: 1.4;
}

:deep(.markdown-body h1:first-child), :deep(.markdown-body h2:first-child),
:deep(.markdown-body h3:first-child) {
  margin-top: 0;
}

:deep(.markdown-body pre) {
  background-color: #f1f5f9;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 10px 0;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  color: #334155;
}

:deep(.markdown-body code) {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

:deep(.markdown-body pre code) {
  background-color: transparent;
  padding: 0;
  color: inherit;
}

:deep(.markdown-body blockquote) {
  margin: 10px 0;
  padding-left: 12px;
  border-left: 4px solid #e2e8f0;
  color: #64748b;
}

:deep(.markdown-body a) {
  color: #2563eb;
  text-decoration: none;
}

:deep(.markdown-body a:hover) {
  text-decoration: underline;
}

/* User Message Markdown Overrides */
.message.user :deep(.markdown-body a) {
  color: #dbeafe;
}

.message.user :deep(.markdown-body pre) {
  background-color: rgba(0, 0, 0, 0.2);
  color: #f8fafc;
}

.message.user :deep(.markdown-body code) {
  background-color: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

.message.user :deep(.markdown-body blockquote) {
  border-left-color: rgba(255, 255, 255, 0.3);
  color: #e2e8f0;
}

.tool-calls-section {
  margin-top: 12px;
  padding: 12px;
  border-radius: 8px;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  font-size: 13px;
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
  padding: 6px 10px;
  background: #f1f3f5;
  font-size: 12px;
  color: #495057;
}

.drawer-toggle {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 12px;
  padding: 0;
}

.drawer-toggle:hover {
  text-decoration: underline;
}

.drawer-content {
  padding: 8px;
  background: #fff;
  font-size: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.result-preview {
  color: #333;
  white-space: pre-wrap;
}

.result-full {
  white-space: pre-wrap;
  font-family: monospace;
}

.more-indicator {
  color: #999;
}

.expand-hint {
  font-size: 10px;
  color: #007bff;
  margin-left: 4px;
}

.tool-error {
  color: #dc3545;
  font-size: 12px;
  margin-top: 4px;
}

.steps-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.step-item {
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #dee2e6;
  font-size: 14px;
}

.step-item.running {
  border-left-color: #007bff;
  background: #e8f4ff;
}

.step-item.completed {
  border-left-color: #28a745;
  background: #e6ffed;
}

.step-item.error {
  border-left-color: #dc3545;
  background: #ffe6e6;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-icon {
  font-size: 16px;
}

.step-info {
  flex: 1;
}

.step-title {
  font-weight: 500;
  color: #333;
}

.reasoning-section {
  margin-bottom: 12px;
  border-radius: 8px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  overflow: hidden;
}

.reasoning-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f1f3f5;
  cursor: pointer;
}

.reasoning-header .left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.reasoning-icon {
  width: 16px;
  height: 16px;
  color: #6c757d;
}

.reasoning-title {
  font-size: 13px;
  font-weight: 600;
  color: #495057;
}

.toggle-reasoning {
  background: none;
  border: none;
  color: #007bff;
  font-size: 12px;
  cursor: pointer;
}

.reasoning-content {
  padding: 12px;
  font-size: 13px;
  color: #495057;
  white-space: pre-wrap;
  line-height: 1.5;
  border-top: 1px solid #e9ecef;
}

.streaming-status {
  margin-top: 4px;
  font-size: 12px;
  color: #999;
  font-style: italic;
}

.hotel-card-inline {
  margin: 10px 0;
}

.hotel-card {
  display: flex;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border: 1px solid #eee;
  transition: transform 0.2s;
}

.hotel-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.hotel-image-wrapper {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}

.hotel-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hotel-info {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.hotel-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.hotel-details {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 14px;
}

.hotel-price {
  color: #e53935;
  font-weight: 600;
}

.hotel-score {
  color: #fbc02d;
}

.hotel-location {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hotel-facilities {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.facility-tag {
  font-size: 10px;
  padding: 2px 6px;
  background: #f5f5f5;
  border-radius: 4px;
  color: #666;
}

.booking-btn {
  align-self: flex-start;
  padding: 4px 12px;
  background: #1976d2;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 12px;
  transition: background 0.2s;
}

.booking-btn:hover {
  background: #1565c0;
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
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--day-color, #1a73e8);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--day-color, #1a73e8) 20%, white);
  border: 2px solid white;
}
.message-html :deep(.day-card:not(:last-child)::after) {
  content: '';
  position: absolute;
  left: 14px;
  top: 28px;
  bottom: -14px;
  width: 3px;
  background: linear-gradient(to bottom,
    color-mix(in srgb, var(--day-color, #E8F0FE) 30%, white),
    color-mix(in srgb, var(--day-color, #E8F0FE) 10%, white));
  border-radius: 2px;
}
.message-html :deep(.skeleton) { opacity: 0.7 }
.message-html :deep(.day-title) {
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 16px;
}
.message-html :deep(.activities) {
  list-style: none;
  padding: 0;
  margin: 0;
}
/* 🎨 路线容器 - Google风格 */
.message-html :deep(.route-container) {
  margin: 8px 0;
  list-style: none;
}

.message-html :deep(.route-chip) {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  background: #F8F9FA;
  border: 1px solid #E0E0E0;
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 500;
  color: #202124;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.message-html :deep(.route-chip:hover) {
  background: #F1F3F4;
  border-color: #DADCE0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.message-html :deep(.route-chip.expanded) {
  background: #E8F0FE;
  border-color: #1A73E8;
  color: #1A73E8;
}

.message-html :deep(.route-icon) {
  font-size: 18px;
  line-height: 1;
}

.message-html :deep(.route-text) {
  flex: 1;
  font-weight: 500;
}

.message-html :deep(.expand-icon) {
  font-size: 10px;
  color: #5F6368;
  transition: transform 0.2s ease;
}

.message-html :deep(.route-chip.expanded .expand-icon) {
  transform: rotate(180deg);
}

/* 路线详情面板 */
.message-html :deep(.route-details) {
  margin-top: 8px;
  background: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}

.message-html :deep(.route-loading) {
  text-align: center;
  color: #5F6368;
  padding: 12px;
}

/* 路线模式选择 */
.message-html :deep(.route-modes) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-html :deep(.route-mode) {
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.message-html :deep(.route-mode:hover) {
  border-color: #DADCE0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.message-html :deep(.route-mode.active) {
  border-color: #1A73E8;
  background: #F8FBFF;
}

.message-html :deep(.mode-header) {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  cursor: pointer;
  background: #FAFAFA;
  transition: background 0.2s ease;
}

.message-html :deep(.route-mode.active .mode-header) {
  background: #E8F0FE;
}

.message-html :deep(.mode-header:hover) {
  background: #F1F3F4;
}

.message-html :deep(.mode-icon) {
  font-size: 20px;
  line-height: 1;
}

.message-html :deep(.mode-name) {
  font-weight: 600;
  color: #202124;
  font-size: 14px;
}

.message-html :deep(.mode-time) {
  margin-left: auto;
  font-weight: 600;
  color: #1A73E8;
  font-size: 14px;
}

.message-html :deep(.mode-distance) {
  color: #5F6368;
  font-size: 13px;
}

/* 路线步骤 */
.message-html :deep(.mode-content) {
  padding: 16px;
  background: #FFFFFF;
}

.message-html :deep(.route-steps) {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-html :deep(.route-step) {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.message-html :deep(.step-number) {
  min-width: 24px;
  height: 24px;
  background: #1A73E8;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.message-html :deep(.step-content) {
  flex: 1;
}

.message-html :deep(.step-instruction) {
  color: #202124;
  font-size: 14px;
  line-height: 1.4;
  margin-bottom: 4px;
}

.message-html :deep(.step-distance) {
  color: #5F6368;
  font-size: 12px;
}

/* 公交步骤 */
.message-html :deep(.transit-steps) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-html :deep(.transit-step) {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: #F8F9FA;
  border-radius: 8px;
}

.message-html :deep(.bus-step) {
  background: #E8F0FE;
}

.message-html :deep(.walk-step) {
  background: #FEF7E0;
}

.message-html :deep(.step-icon) {
  font-size: 20px;
  line-height: 1;
}

.message-html :deep(.bus-line) {
  font-weight: 600;
  color: #1A73E8;
  font-size: 14px;
}

.message-html :deep(.bus-stops) {
  color: #5F6368;
  font-size: 12px;
  margin-top: 2px;
}

.message-html :deep(.walk-distance) {
  color: #E37400;
  font-size: 13px;
  font-weight: 500;
}

.message-html :deep(.no-steps) {
  text-align: center;
  color: #9AA0A6;
  padding: 16px;
  font-size: 13px;
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

/* 地图容器样式 - 大厂风格 */
.message-html :deep(.map-container) {
  background: #FFFFFF;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08), 0 12px 32px rgba(0, 0, 0, 0.08);
  margin: 16px 0;
  transition: all 0.3s ease;
}

.message-html :deep(.map-container:hover) {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12), 0 16px 48px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.message-html :deep(.map-header) {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  font-size: 15px;
}

.message-html :deep(.map-icon) {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.message-html :deep(.map-status) {
  margin-left: auto;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 500;
}

.message-html :deep(.travel-map) {
  width: 100%;
  height: 480px;
  background: #f0f2f5;
  position: relative;
}

/* 地图图例样式 */
.message-html :deep(.map-legend) {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding: 12px 20px;
  background: linear-gradient(to bottom, rgba(255,255,255,0.95), rgba(248,249,250,0.95));
  border-top: 1px solid rgba(0,0,0,0.08);
  flex-wrap: wrap;
}

.message-html :deep(.legend-item) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
  transition: all 0.2s ease;
}

.message-html :deep(.legend-item:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.12);
}

.message-html :deep(.legend-color) {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 0 0 1px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.15);
}

.message-html :deep(.legend-text) {
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

/* Tab导航栏样式 */
.message-html :deep(.itinerary-tabs) {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: #F8F9FA;
  border-radius: 12px;
  margin-top: 16px;
  overflow-x: auto;
  scrollbar-width: thin;
}

.message-html :deep(.itinerary-tabs::-webkit-scrollbar) {
  height: 6px;
}

.message-html :deep(.itinerary-tabs::-webkit-scrollbar-thumb) {
  background: #CCC;
  border-radius: 3px;
}

.message-html :deep(.tab-btn) {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: white;
  border: 2px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #5F6368;
  transition: all 0.3s ease;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}

.message-html :deep(.tab-btn:hover) {
  background: #F1F3F4;
  border-color: var(--tab-color, #1A73E8);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.12);
}

.message-html :deep(.tab-btn.active) {
  background: linear-gradient(135deg, var(--tab-color, #1A73E8) 0%, color-mix(in srgb, var(--tab-color, #1A73E8) 85%, black) 100%);
  color: white;
  border-color: var(--tab-color, #1A73E8);
  box-shadow: 0 4px 12px rgba(26, 115, 232, 0.25);
}

.message-html :deep(.tab-icon) {
  font-size: 16px;
  line-height: 1;
}

/* Tab内容区域 */
.message-html :deep(.tab-content-wrapper) {
  margin-top: 16px;
}

.message-html :deep(.tab-content) {
  display: none;
  animation: fadeIn 0.3s ease;
}

.message-html :deep(.tab-content.active) {
  display: block;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 单天详细卡片样式 */
.message-html :deep(.day-detail-card) {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.message-html :deep(.day-detail-header) {
  padding: 20px;
  color: white;
  text-align: center;
}

.message-html :deep(.day-detail-header h3) {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 700;
}

</style>
