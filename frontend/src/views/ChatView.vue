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
            <svg v-if="message.role === 'user'" viewBox="0 0 1024 1024" fill="currentColor">
              <path d="M445.781333 378.311111c-19.456 0-35.271111 15.815111-35.271111 35.271111V450.56c0 19.456 15.815111 35.271111 35.271111 35.271111s35.271111-15.815111 35.271111-35.271111v-36.977778c0-19.456-15.815111-35.271111-35.271111-35.271111zM615.879111 485.831111c19.456 0 35.271111-15.815111 35.271111-35.271111v-36.977778c0-19.456-15.815111-35.271111-35.271111-35.271111s-35.271111 15.815111-35.271111 35.271111V450.56c0 19.456 15.815111 35.271111 35.271111 35.271111z"/>
              <path d="M791.665778 841.272889c-0.113778-1.024-0.227556-2.048-0.455111-2.958222-6.144-33.678222-22.983111-65.536-47.445334-89.543111-9.329778-9.216-19.456-16.952889-30.378666-23.210667 16.611556-11.377778 32.199111-24.348444 46.762666-38.798222 61.326222-61.326222 95.118222-142.904889 95.118223-229.717334s-33.792-168.391111-95.118223-229.717333-142.904889-95.118222-229.717333-95.118222c-86.812444 0-168.391111 33.792-229.717333 95.118222-61.326222 61.326222-95.118222 142.904889-95.118223 229.717333s33.792 168.391111 95.118223 229.717334c14.449778 14.449778 30.151111 27.420444 46.762666 38.798222-10.581333 6.257778-20.593778 13.994667-29.582222 23.096889-23.665778 24.007111-40.049778 56.775111-46.08 92.16-0.113778 0.568889-0.227556 1.251556-0.227555 1.820444L265.102222 898.844444c-2.275556 19.342222 11.605333 36.864 30.947556 39.139556 1.365333 0.113778 2.730667 0.227556 4.096 0.227556 17.635556 0 32.881778-13.198222 35.043555-31.175112l6.371556-55.296c8.988444-51.086222 44.942222-74.296889 74.638222-74.296888h1.820445l42.894222-2.275556c0.682667 0 1.251556-0.113778 1.820444-0.113778 21.959111 4.664889 44.600889 7.054222 67.584 7.054222 23.096889 0 45.738667-2.389333 67.811556-7.054222 0.682667 0.113778 1.365333 0.113778 2.161778 0.227556l42.439111 2.275555h1.820444c39.253333 0 69.632 36.522667 76.8 72.362667l5.347556 56.433778c1.706667 18.204444 17.066667 31.971556 35.043555 31.971555 1.137778 0 2.275556 0 3.413334-0.113777 19.342222-1.820444 33.678222-19.000889 31.744-38.456889l-5.233778-58.481778zM472.177778 706.901333c-2.730667-1.137778-5.688889-1.820444-8.760889-2.161777-42.780444-11.491556-82.033778-34.133333-114.232889-66.332445-48.469333-48.469333-75.207111-112.867556-75.207111-181.475555s26.737778-133.006222 75.207111-181.475556S462.051556 200.248889 530.659556 200.248889s133.006222 26.737778 181.475555 75.207111c48.469333 48.469333 75.207111 112.867556 75.207111 181.475556S760.490667 589.937778 712.021333 638.293333c-32.312889 32.312889-71.68 54.954667-114.688 66.446223-2.389333 0.341333-4.778667 0.910222-7.054222 1.820444-19.342222 4.551111-39.367111 6.940444-59.733333 6.940444-19.911111 0-39.480889-2.275556-58.368-6.599111z"/>
            </svg>
            <svg v-else viewBox="0 0 1024 1024" fill="currentColor">
              <path d="M850.367451 513.489934c4.208858-5.538133 8.271384-11.088546 12.139481-16.651238 55.695486-80.095199 69.303412-153.764036 38.315654-207.435423-30.986735-53.671387-101.583606-78.719876-198.802812-70.535473-6.750751 0.568958-13.588483 1.310855-20.488637 2.187829-2.691295-6.414083-5.467525-12.70844-8.350179-18.838044-41.517579-88.280626-98.512664-136.898927-160.487158-136.898927-61.974493 0-118.969579 48.618301-160.485111 136.898927-2.883677 6.130627-5.658883 12.423961-8.350179 18.839067-6.901177-0.876973-13.739932-1.61887-20.490683-2.187829-97.209996-8.18645-167.813007 16.865109-198.800765 70.535473-30.987758 53.671387-17.380856 127.340223 38.314631 207.435423 3.867074 5.561669 7.9296 11.113105 12.139481 16.651238-4.209882 5.538133-8.271384 11.088546-12.139481 16.651238-55.694463 80.095199-69.301366 153.764036-38.314631 207.434399 27.13808 47.004547 84.658122 72.055083 163.830299 72.055083 11.228739 0 22.897499-0.50449 34.970466-1.51961 6.750751-0.568958 13.589506-1.310855 20.490683-2.187829 2.691295 6.414083 5.467525 12.70844 8.351202 18.839067 41.515532 88.281649 98.510618 136.89995 160.485111 136.89995 61.974493 0 118.969579-48.618301 160.487158-136.89995 2.883677-6.130627 5.658883-12.423961 8.350179-18.839067 6.900154 0.876973 13.737886 1.61887 20.488637 2.187829 12.081153 1.01819 23.737634 1.51961 34.972513 1.51961 79.162968 0 136.693242-25.052582 163.830299-72.055083 30.986735-53.670363 17.379832-127.3392-38.315654-207.434399C858.639858 524.579503 854.577333 519.028067 850.367451 513.489934zM705.378266 258.742972c79.704296-6.715959 138.322345 11.755742 160.790056 50.669006 22.467711 38.914288 9.157567 98.901521-36.513612 164.583452-1.775436 2.554172-3.603061 5.106298-5.459339 7.656377-27.969005-31.598672-61.164035-62.346977-98.369402-91.212398-6.39464-46.653553-16.426111-90.774423-29.806863-130.796952C699.155541 259.309884 702.278671 259.003915 705.378266 258.742972zM603.368964 670.542876c-30.015617 17.32969-60.426231 32.621978-90.675162 45.690622-30.248931-13.068643-60.659545-28.360931-90.675162-45.690622-30.015617-17.32969-58.46353-36.019355-84.905762-55.680137-3.805676-32.730449-5.767354-66.712401-5.767354-101.371782 0-34.659381 1.961678-68.64338 5.768377-101.373829 26.442232-19.660782 54.890144-38.350446 84.904739-55.680137 30.015617-17.32969 60.427254-32.621978 90.675162-45.690622 30.248931 13.068643 60.658522 28.360931 90.675162 45.690622 30.016641 17.32969 58.464553 36.020378 84.907809 55.68116 3.805676 32.730449 5.768377 66.713424 5.768377 101.372805 0 34.659381-1.961678 68.641333-5.767354 101.370759C661.833517 634.522498 633.385605 653.213185 603.368964 670.542876zM679.918407 669.814282c-6.14393 32.457226-14.217816 63.196321-24.11728 91.542926-29.498848-5.600555-60.157101-13.977339-91.338265-24.885783 19.729344-9.582239 39.413662-20.017916 58.912761-31.275307C642.875746 693.938726 661.755746 682.109306 679.918407 669.814282zM460.924741 736.471424c-31.181163 10.908444-61.839417 19.285229-91.337241 24.885783-9.898441-28.346605-17.972327-59.0857-24.116257-91.541903 18.162662 12.295024 37.041638 24.12342 56.539714 35.380812C421.510056 716.454532 441.194374 726.889185 460.924741 736.471424zM293.701159 580.147076c-25.037233-21.548782-47.620577-43.911092-67.219961-66.657142 19.599384-22.74605 42.183751-45.108361 67.219961-66.658166-1.566682 21.877263-2.371 44.142359-2.371 66.658166C291.330158 536.00574 292.134477 558.269813 293.701159 580.147076zM345.471242 357.163539c6.14393-32.457226 14.217816-63.195298 24.116257-91.541903 29.497824 5.600555 60.156078 13.977339 91.336218 24.885783-19.729344 9.582239-39.413662 20.016893-58.912761 31.275307C382.511857 333.040119 363.633904 344.868515 345.471242 357.163539zM564.463885 290.50742c31.18014-10.907421 61.838394-19.284205 91.337241-24.885783 9.898441 28.346605 17.97335 59.0857 24.11728 91.542926-18.162662-12.295024-37.042661-24.124444-56.541761-35.381835C603.877547 310.524313 584.193229 300.088636 564.463885 290.50742zM731.688491 446.832791c25.036209 21.548782 47.620577 43.911092 67.219961 66.657142-19.599384 22.745027-42.182728 45.107337-67.219961 66.656119 1.566682-21.87624 2.371-44.141336 2.371-66.656119C734.059492 490.974128 733.255173 468.710055 731.688491 446.832791zM388.417357 219.247446c34.046421-72.393797 79.343069-113.913423 124.276445-113.913423s90.230024 41.519626 124.275421 113.913423c1.324158 2.815115 2.619664 5.67321 3.900843 8.55484-41.349757 8.422833-84.576257 21.796422-128.176264 39.584554-43.600007-17.788132-86.826508-31.16172-128.176264-39.584554C385.798716 224.919632 387.094222 222.061538 388.417357 219.247446zM195.73494 473.994408c-45.672202-65.680908-58.980299-125.669164-36.513612-164.583452 19.435655-33.662681 65.900919-52.022841 129.693828-52.022841 9.952676 0 20.338211 0.447185 31.096229 1.353834 3.099594 0.260943 6.222725 0.567935 9.359158 0.899486-13.379729 40.021505-23.411199 84.142375-29.806863 130.794905-37.205367 28.865421-70.400397 59.613726-98.370425 91.213421C199.338001 479.099682 197.510376 476.54858 195.73494 473.994408zM320.010361 768.235872c-79.70839 6.711865-138.322345-11.754718-160.790056-50.667983-22.466688-38.913265-9.157567-98.902544 36.513612-164.582429 1.775436-2.554172 3.603061-5.105275 5.458315-7.655354 27.970028 31.598672 61.165058 62.346977 98.370425 91.211375 6.39464 46.65253 16.426111 90.7734 29.806863 130.794905C326.234109 767.667937 323.109955 767.974929 320.010361 768.235872zM636.969223 807.733445c-34.046421 72.392774-79.343069 113.912399-124.275421 113.912399s-90.230024-41.519626-124.276445-113.912399c-1.324158-2.815115-2.620687-5.674233-3.900843-8.556886 41.35078-8.422833 84.577281-21.797445 128.177288-39.585577 43.601031 17.788132 86.827531 31.16172 128.177288 39.584554C639.58991 802.059212 638.293381 804.918329 636.969223 807.733445zM866.168322 717.567889c-22.467711 38.913265-81.075527 57.387012-160.790056 50.667983-3.099594-0.260943-6.222725-0.567935-9.359158-0.899486 13.380752-40.021505 23.412223-84.143399 29.806863-130.795928 37.205367-28.864398 70.399373-59.612703 98.369402-91.210351 1.855254 2.550079 3.682879 5.102205 5.459339 7.656377C875.325889 618.667392 888.633986 678.654624 866.168322 717.567889z"/>
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
              <!-- 🆕 文本内容 - 支持嵌入酒店卡片 -->
              <template v-if="content.type === 'text'">
                <div v-if="message.hotelsData && message.hotelsData.length">
                  <!-- 解析文本并插入酒店卡片 -->
                  <template v-for="(segment, segmentIndex) in parseTextWithHotelCards(content.text, message.hotelsData)" :key="segmentIndex">
                    <div v-if="segment.type === 'text'" class="message-text markdown-body" v-html="renderMarkdown(segment.content)"></div>
                    <div v-else-if="segment.type === 'hotel'" class="hotel-card-inline">
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

// 🆕 酒店数据接口
interface HotelData {
  name: string
  url?: string | null  // 🆕 预订页面URL
  image?: string | null  // 🆕 酒店图片URL
  price: string
  score: string
  location: string
  facilities: string[]
}

interface Message {
  role: 'user' | 'assistant'
  content: MessageContent[]
  reasoning?: string  // 思考过程
  isStreaming?: boolean  // 是否正在流式接收
  toolCalls?: ToolCall[]  // 工具调用信息
  hotelSteps?: StepInfo[] // 酒店步骤
  hotelsData?: HotelData[]  // 🆕 酒店列表数据（包含URL和图片）
  travelSteps?: StepInfo[] // 旅行步骤
  mapData?: MapData  // 地图数据（用于缓存和重新渲染）
  routesData?: Record<string, any>  // 🆕 路线数据缓存（避免重复API调用）
}

// 地图数据结构
interface MapData {
  itinerary: any[]  // 行程数据
  city: string      // 城市
  coordsMap: Record<string, number[]>  // 景点坐标映射（序列化后的 Map）
  mapId: string     // 地图容器ID
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

// 旅行计划草稿状态管理
interface TravelPlanDraft {
  destination: string | null
  origin: string | null
  start_date: string | null
  end_date: string | null
  people: number | null
  attractions: string[]
}

const travelPlanDraft = ref<TravelPlanDraft | null>(null)
// DRAFT_STORAGE_KEY 已废弃：草稿现在跟会话绑定，存储在 ChatSession.draft 中

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

// 聊天会话接口
interface ChatSession {
  id: string
  title: string
  messages: Message[]
  createdAt: number
  updatedAt: number
  draft?: TravelPlanDraft | null  // 🆕 每个会话独立的草稿
  currentPlan?: any  // 🆕 当前激活的旅行计划（用于修改）
  currentPlanMsgIndex?: number | null  // 🆕 当前计划所在的消息索引
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

/**
 * 🆕 解析文本中的酒店卡片占位符，将文本分割成文本段和酒店卡片段
 * @param text 原始文本，包含 [HOTEL_CARD:X] 占位符
 * @param hotelsData 酒店数据数组
 * @returns 包含文本段和酒店段的数组
 */
const parseTextWithHotelCards = (text: string | undefined, hotelsData: HotelData[]) => {
  if (!text) return [{ type: 'text', content: '' }]
  
  const segments: Array<{ type: 'text' | 'hotel', content?: string, hotel?: HotelData }> = []
  
  // 使用正则表达式匹配 [HOTEL_CARD:X] 占位符
  const hotelCardRegex = /\[HOTEL_CARD:(\d+)\]/g
  
  let lastIndex = 0
  let match
  
  while ((match = hotelCardRegex.exec(text)) !== null) {
    // 添加占位符之前的文本
    if (match.index > lastIndex) {
      const textContent = text.substring(lastIndex, match.index)
      if (textContent.trim()) {
        segments.push({ type: 'text', content: textContent })
      }
    }
    
    // 添加酒店卡片
    const hotelIndex = parseInt(match[1])
    if (hotelIndex >= 0 && hotelIndex < hotelsData.length) {
      segments.push({ type: 'hotel', hotel: hotelsData[hotelIndex] })
    }
    
    lastIndex = match.index + match[0].length
  }
  
  // 添加最后剩余的文本
  if (lastIndex < text.length) {
    const textContent = text.substring(lastIndex)
    if (textContent.trim()) {
      segments.push({ type: 'text', content: textContent })
    }
  }
  
  // 如果没有找到任何占位符，返回原始文本
  if (segments.length === 0) {
    segments.push({ type: 'text', content: text })
  }
  
  return segments
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

            // 渲染地图和路线
            renderTravelMap(msgIndex, itinerary, city).then(coordsMap => {
              return populateRoutesForMessage(msgIndex, city, coordsMap)
            }).then(() => {
              resetDraft()
              saveCurrentSession()
            }).catch(err => {
              console.error('渲染失败:', err)
              resetDraft()
              saveCurrentSession()
            })
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

        if (!city) {
          console.error('❌ 缺少城市信息，无法查询公交路线')
        }

        console.log(`🏙️ 城市信息: ${city} (来源: ${result?.plan?.city ? 'LLM识别' : 'destination降级'})`)

        // 🆕 如果是修改模式，需要清除旧地图并滚动到计划位置
        if (isModification) {
          console.log('🔄 修改模式：准备重新渲染地图')
          // 等待DOM更新后滚动到计划位置
          await nextTick()
          const planMessage = document.querySelectorAll('.message')[msgIndex]
          if (planMessage) {
            planMessage.scrollIntoView({ behavior: 'smooth', block: 'center' })
          }
        }

        // 优化：先获取坐标，再复用坐标（避免重复地理编码）
        renderTravelMap(msgIndex, itinerary, city || '未知城市').then(coordsMap => {
          // 使用已获取的坐标映射来计算路线，避免重复请求地理编码
          return populateRoutesForMessage(msgIndex, city || '未知城市', coordsMap)
        }).then(() => {
          // 计划生成完成，重置草稿（仅在非修改模式下）
          if (!isModification) {
            resetDraft()
          }
          saveCurrentSession()

          // 🆕 修改模式下，重新绑定标签页切换事件
          if (isModification) {
            console.log('✅ 地图重新渲染完成，重新绑定标签页事件')
            nextTick(() => {
              // 从DOM中获取更新后的mapId
              const planMessage = document.querySelectorAll('.message')[msgIndex]
              const dailyPlanDiv = planMessage?.querySelector('.daily-plan[data-map-id]')
              const updatedMapId = dailyPlanDiv?.getAttribute('data-map-id')
              if (updatedMapId) {
                bindTabSwitchEvents(updatedMapId)
              }
            })
          }
        }).catch(err => {
          console.error('渲染失败:', err)
          if (!isModification) {
            resetDraft()
          }
          saveCurrentSession()
        })

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
        console.log('🏨 传递旅行计划到酒店搜索:', currentActivePlan.value)
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
                console.log('📦 接收到酒店列表数据:', data.hotels)
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

// 旧的clearChat函数已被clearCurrentChat替代

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

// 从localStorage加载草稿（已废弃，改为从会话中加载）
const loadDraftFromStorage = () => {
  // 🆕 草稿现在从会话中加载，此函数已废弃
  // 加载会话时会自动加载草稿（见 loadChatSession 函数）
  console.log('⚠️ loadDraftFromStorage 已废弃，草稿现在跟会话绑定')
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
  console.log('创建新聊天被调用')
  const newChatId = Date.now().toString()
  currentChatId.value = newChatId
  messages.value = []

  // 🆕 重置草稿（新会话应该是干净的）
  travelPlanDraft.value = null
  console.log('🗑️ 新会话，草稿已重置')

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

const loadChatSession = async (session: ChatSession) => {
  currentChatId.value = session.id
  messages.value = [...session.messages]

  // 🔄 加载该会话的草稿（会话级隔离）
  travelPlanDraft.value = session.draft || null
  console.log(`📋 加载会话 ${session.id} 的草稿:`, travelPlanDraft.value)

  // 🆕 恢复当前激活的计划
  currentActivePlan.value = session.currentPlan || null
  currentActivePlanMessageIndex.value = session.currentPlanMsgIndex ?? null
  if (currentActivePlan.value) {
    console.log(`📍 恢复会话 ${session.id} 的激活计划，索引: ${currentActivePlanMessageIndex.value}`)
  }

  await nextTick()

  // 🔄 重新渲染缓存的地图
  await rerenderCachedMaps()

  // 填充缓存的路线
  await prefillRoutesFromCacheAll()
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

// 地图实例存储
const travelMaps = new Map<string, any>()
// 地图数据存储（用于Tab切换时过滤显示）
const travelMapData = new Map<string, { itinerary: any[], coordsMap: Map<string, number[]>, daySpots: any[] }>()

// 定义每天的路线颜色
const DAY_COLORS = [
  '#FF6B6B', // Day 1: 红色
  '#4ECDC4', // Day 2: 青色
  '#FFE66D', // Day 3: 黄色
  '#95E1D3', // Day 4: 绿色
  '#A8E6CF', // Day 5: 浅绿
  '#FFD3B6', // Day 6: 橙色
  '#FFAAA5', // Day 7: 粉色
]

// 渲染旅行地图，返回坐标映射供后续使用
const renderTravelMap = async (msgIndex: number, itinerary: any[], city: string): Promise<Map<string, number[]>> => {
  await nextTick()
  const coordsMap = new Map<string, number[]>()

  const wrappers = messagesContainer.value?.querySelectorAll('.message-wrapper') || []
  const el = wrappers[msgIndex] as HTMLElement
  if (!el) return coordsMap

  const mapContainer = el.querySelector('.travel-map') as HTMLElement
  if (!mapContainer) return coordsMap

  const mapId = mapContainer.getAttribute('data-map-id') || ''
  const mapStatus = el.querySelector(`.map-status[data-map-id="${mapId}"]`) as HTMLElement

  try {
    // 收集所有景点名称
    const allPlaces: string[] = []
    const daySpots: Array<{ day: number; spots: string[]; color: string }> = []

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
      return coordsMap
    }

    // 批量获取地理编码
    if (mapStatus) mapStatus.textContent = '获取坐标中...'
    const response = await fetch('http://localhost:9000/api/batch-geocode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ places: allPlaces, city })
    })

    if (!response.ok) {
      if (mapStatus) mapStatus.textContent = '坐标获取失败'
      return coordsMap
    }

    const data = await response.json()
    if (!data.success || !data.results) {
      if (mapStatus) mapStatus.textContent = '坐标解析失败'
      return coordsMap
    }

    // 构建景点坐标映射
    for (const result of data.results) {
      if (result.success && result.coords) {
        coordsMap.set(result.name, result.coords)
      }
    }

    // 计算地图中心点
    const allCoords = Array.from(coordsMap.values())
    if (allCoords.length === 0) {
      if (mapStatus) mapStatus.textContent = '无有效坐标'
      return coordsMap
    }

    const centerLng = allCoords.reduce((sum, c) => sum + c[0], 0) / allCoords.length
    const centerLat = allCoords.reduce((sum, c) => sum + c[1], 0) / allCoords.length

    // 创建地图
    if (mapStatus) mapStatus.textContent = '渲染地图中...'

    // @ts-ignore
    if (!window.AMap) {
      if (mapStatus) mapStatus.textContent = '地图API未加载'
      return coordsMap
    }

    // @ts-ignore
    const map = new AMap.Map(mapId, {
      zoom: 12,
      center: [centerLng, centerLat],
      viewMode: '2D',
      mapStyle: 'amap://styles/light'  // 使用浅色地图
    })

    // 保存地图实例
    travelMaps.set(mapId, map)

    // 绘制每天的路线和标记
    for (const dayInfo of daySpots) {
      const dayCoords = dayInfo.spots
        .map(spot => coordsMap.get(spot))
        .filter((coords): coords is number[] => coords !== undefined)

      if (dayCoords.length === 0) continue

      // 绘制路线 - 双层描边效果
      if (dayCoords.length > 1) {
        // 第一层：白色描边（粗线）
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

        // 第二层：彩色实线（细线）
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

      // 绘制标记
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

        // 点击标记显示信息窗口
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

    // 自动调整视野
    map.setFitView()

    if (mapStatus) mapStatus.textContent = '✓ 已加载'

    // 💾 保存地图数据到消息中（用于缓存和重新渲染）
    if (messages.value[msgIndex]) {
      const coordsRecord: Record<string, number[]> = {}
      coordsMap.forEach((coords, name) => {
        coordsRecord[name] = coords
      })

      messages.value[msgIndex].mapData = {
        itinerary,
        city,
        coordsMap: coordsRecord,
        mapId
      }

      // 保存到本地存储
      saveCurrentSession()
      console.log(`✅ 地图数据已缓存到消息 ${msgIndex}`)
    }

    // 💾 保存地图数据用于Tab切换过滤
    travelMapData.set(mapId, { itinerary, coordsMap, daySpots })

    // 🎯 绑定Tab切换事件
    bindTabSwitchEvents(mapId)

    return coordsMap
  } catch (error) {
    console.error('渲染地图失败:', error)
    if (mapStatus) mapStatus.textContent = '渲染失败'
    return coordsMap
  }
}

// 🎯 绑定Tab切换事件
const bindTabSwitchEvents = (mapId: string) => {
  nextTick(() => {
    const dailyPlan = document.querySelector(`.daily-plan[data-map-id="${mapId}"]`)
    if (!dailyPlan) return

    const tabBtns = dailyPlan.querySelectorAll('.tab-btn')
    const tabContents = dailyPlan.querySelectorAll('.tab-content')

    tabBtns.forEach(btn => {
      btn.addEventListener('click', function(this: HTMLElement) {
        const tabName = this.getAttribute('data-tab')
        const dayNum = this.getAttribute('data-day')

        // 切换Tab按钮的激活状态
        tabBtns.forEach(b => b.classList.remove('active'))
        this.classList.add('active')

        // 切换Tab内容的显示
        tabContents.forEach(content => {
          const contentName = content.getAttribute('data-content')
          if (contentName === tabName) {
            content.classList.add('active')
          } else {
            content.classList.remove('active')
          }
        })

        // 过滤地图显示
        if (tabName === 'all') {
          filterMapByDay(mapId, null) // 显示所有天数
        } else if (dayNum) {
          filterMapByDay(mapId, parseInt(dayNum)) // 只显示指定天数
        }
      })
    })

    console.log(`✅ Tab切换事件已绑定到地图 ${mapId}`)
  })
}

// 🗺️ 按天数过滤地图显示
const filterMapByDay = (mapId: string, dayNum: number | null) => {
  const map = travelMaps.get(mapId)
  const mapData = travelMapData.get(mapId)

  if (!map || !mapData) {
    console.warn(`⚠️ 地图数据未找到: ${mapId}`)
    return
  }

  const { daySpots, coordsMap } = mapData

  // 清除所有现有的覆盖物
  map.clearMap()

  // 根据dayNum过滤要显示的天数
  const filteredDaySpots = dayNum === null
    ? daySpots
    : daySpots.filter((ds: any) => ds.day === dayNum)

  // 重新绘制过滤后的路线和标记
  for (const dayInfo of filteredDaySpots) {
    const dayCoords = dayInfo.spots
      .map((spot: string) => coordsMap.get(spot))
      .filter((coords: any): coords is number[] => coords !== undefined)

    if (dayCoords.length === 0) continue

    // 绘制路线 - 双层描边效果
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

    // 绘制标记
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

  // 自动调整视野
  map.setFitView()
  console.log(`🗺️ 地图已过滤显示: ${dayNum === null ? '所有天数' : `Day ${dayNum}`}`)
}

// 🔄 重新渲染缓存的地图
const rerenderCachedMaps = async () => {
  await nextTick()

  messages.value.forEach(async (message, msgIndex) => {
    if (message.mapData) {
      console.log(`🔄 检测到缓存的地图数据，准备重新渲染消息 ${msgIndex}`)

      // 找到地图容器
      const wrappers = messagesContainer.value?.querySelectorAll('.message-wrapper') || []
      const el = wrappers[msgIndex] as HTMLElement
      if (!el) {
        console.warn(`⚠️ 未找到消息 ${msgIndex} 的DOM元素`)
        return
      }

      const mapContainer = el.querySelector('.travel-map') as HTMLElement
      if (!mapContainer) {
        console.warn(`⚠️ 未找到消息 ${msgIndex} 的地图容器`)
        return
      }

      const mapId = mapContainer.getAttribute('data-map-id') || ''
      const mapStatus = el.querySelector(`.map-status[data-map-id="${mapId}"]`) as HTMLElement

      try {
        if (mapStatus) mapStatus.textContent = '正在恢复地图...'

        // 从 mapData 恢复坐标映射
        const coordsMap = new Map<string, number[]>()
        Object.entries(message.mapData.coordsMap).forEach(([name, coords]) => {
          coordsMap.set(name, coords)
        })

        const { itinerary, city } = message.mapData
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
        const map = new AMap.Map(mapId, {
          zoom: 12,
          center: [centerLng, centerLat],
          viewMode: '2D',
          mapStyle: 'amap://styles/light'  // 使用浅色地图
        })

        // 保存地图实例
        travelMaps.set(mapId, map)

        // 绘制每天的路线和标记
        const rerenderDaySpots: Array<{ day: number; spots: string[]; color: string }> = []
        for (const day of itinerary) {
          if (Array.isArray(day.activities) && day.activities.length) {
            const spots = day.activities.map((act: any) => act.name).filter((name: string) => name)
            rerenderDaySpots.push({
              day: day.day,
              spots,
              color: DAY_COLORS[(day.day - 1) % DAY_COLORS.length]
            })
          }
        }

        for (const dayInfo of rerenderDaySpots) {
          const dayCoords = dayInfo.spots
            .map(spot => coordsMap.get(spot))
            .filter((coords): coords is number[] => coords !== undefined)

          if (dayCoords.length === 0) continue

          // 绘制路线 - 双层描边效果
          if (dayCoords.length > 1) {
            // 第一层：白色描边（粗线）
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

            // 第二层：彩色实线（细线）
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

          // 绘制标记
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
        if (mapStatus) mapStatus.textContent = '✓ 已恢复'
        console.log(`✅ 地图 ${msgIndex} 重新渲染完成`)

        // 💾 保存地图数据用于Tab切换
        const cachedDaySpots: Array<{ day: number; spots: string[]; color: string }> = []
        for (const day of itinerary) {
          if (Array.isArray(day.activities) && day.activities.length) {
            const spots = day.activities.map((act: any) => act.name).filter((name: string) => name)
            cachedDaySpots.push({
              day: day.day,
              spots,
              color: DAY_COLORS[(day.day - 1) % DAY_COLORS.length]
            })
          }
        }
        travelMapData.set(mapId, { itinerary, coordsMap, daySpots: cachedDaySpots })

        // 🎯 重新绑定Tab切换事件
        bindTabSwitchEvents(mapId)

      } catch (error) {
        console.error(`❌ 地图 ${msgIndex} 重新渲染失败:`, error)
        if (mapStatus) mapStatus.textContent = '恢复失败'
      }
    }
  })
}

// 填充路线芯片：基于相邻活动名称调用后端路线测试接口（支持多模式）
const ROUTE_CACHE_KEY = 'route_cache_v2'  // 升级版本
const readRouteCache = () => {
  try { return JSON.parse(localStorage.getItem(ROUTE_CACHE_KEY) || '{}') } catch { return {} }
}
const writeRouteCache = (cache: Record<string, any>) => {
  localStorage.setItem(ROUTE_CACHE_KEY, JSON.stringify(cache))
}
const makeRouteKey = (city: string, origin: string, destination: string) => {
  const c = (city || '').trim().toLowerCase()
  const o = (origin || '').trim().toLowerCase()
  const d = (destination || '').trim().toLowerCase()
  return `${c}|${o}|${d}`
}
const getMultiModeRouteFromCache = (city: string, origin: string, destination: string) => {
  const cache = readRouteCache()
  const item = cache[makeRouteKey(city, origin, destination)]
  if (!item) return null
  if (Date.now() - item.ts > 7 * 24 * 3600 * 1000) return null
  return item.routes  // 返回多模式路线数据
}
const setMultiModeRouteCache = (city: string, origin: string, destination: string, routes: any) => {
  const cache = readRouteCache()
  cache[makeRouteKey(city, origin, destination)] = { routes, ts: Date.now() }
  writeRouteCache(cache)
}

const populateRoutesForMessage = async (msgIndex: number, city: string, coordsMap?: Map<string, number[]>) => {
  await nextTick()
  const wrappers = messagesContainer.value?.querySelectorAll('.message-wrapper') || []
  const el = wrappers[msgIndex] as HTMLElement
  if (!el) return

  const chips = el.querySelectorAll('.route-chip')

  // 初始化消息级别的路线数据缓存
  if (!messages.value[msgIndex].routesData) {
    messages.value[msgIndex].routesData = {}
  }
  const messageRoutesCache = messages.value[msgIndex].routesData!

  for (const chip of Array.from(chips)) {
    const chipEl = chip as HTMLElement
    const origin = chipEl.getAttribute('data-origin') || ''
    const destination = chipEl.getAttribute('data-destination') || ''
    const cityAttr = chipEl.getAttribute('data-city') || city
    const routeId = chipEl.getAttribute('data-route-id') || ''

    if (!origin || !destination || !routeId) continue

    const routeKey = `${origin}->${destination}`

    // 🔍 优先检查消息级缓存（避免重复API调用）
    if (messageRoutesCache[routeKey]) {
      console.log(`✅ 使用消息缓存: ${routeKey}`)
      updateRouteDisplay(chipEl, routeId, messageRoutesCache[routeKey])
      continue
    }

    // 🔍 检查localStorage缓存
    const cachedRoutes = getMultiModeRouteFromCache(cityAttr, origin, destination)
    if (cachedRoutes) {
      console.log(`✅ 使用localStorage缓存: ${routeKey}`)
      messageRoutesCache[routeKey] = cachedRoutes  // 同步到消息缓存
      updateRouteDisplay(chipEl, routeId, cachedRoutes)
      continue
    }

    // 🌐 调用API获取路线数据
    try {
      // 如果已有坐标映射，使用多模式路线API
      if (coordsMap && coordsMap.has(origin) && coordsMap.has(destination)) {
        const originCoords = coordsMap.get(origin)!
        const destCoords = coordsMap.get(destination)!

        console.log(`🌐 调用API: ${routeKey}`)

        const res = await fetch('http://localhost:9000/api/multi-mode-route', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            origin_coords: originCoords,
            destination_coords: destCoords,
            origin_name: origin,
            destination_name: destination,
            city: cityAttr
          })
        })

        if (res.ok) {
          const data = await res.json()
          if (data?.success && data?.routes) {
            // 💾 三层缓存：localStorage + 消息级 + 显示
            setMultiModeRouteCache(cityAttr, origin, destination, data.routes)
            messageRoutesCache[routeKey] = data.routes
            updateRouteDisplay(chipEl, routeId, data.routes)

            console.log(`💾 已缓存路线数据: ${routeKey}`)
            continue
          }
        }
      }

      // 降级：如果没有坐标，显示错误
      const textEl = chipEl.querySelector('.route-text')
      if (textEl) {
        textEl.textContent = '路线待确认'
      }
    } catch (error) {
      console.error('路线计算失败:', error)
      const textEl = chipEl.querySelector('.route-text')
      if (textEl) {
        textEl.textContent = '路线待确认'
      }
    }
  }

  // 保存消息（包含路线缓存）
  saveCurrentSession()

  // 绑定展开/折叠事件
  bindRouteExpandEvents(el)
}

// 更新路线显示
const updateRouteDisplay = (chipEl: HTMLElement, routeId: string, routes: any) => {
  // 更新按钮显示（默认显示驾车信息）
  const textEl = chipEl.querySelector('.route-text')
  if (textEl && routes.driving) {
    textEl.textContent = routes.driving.display
  }

  // 生成详细信息HTML
  const detailsContainer = document.getElementById(routeId)
  if (detailsContainer) {
    detailsContainer.innerHTML = buildRouteDetailsHtml(routes)
  }
}

// 生成路线详情HTML（Google风格）
const buildRouteDetailsHtml = (routes: any) => {
  let html = '<div class="route-modes">'

  // 驾车
  if (routes.driving) {
    html += `
      <div class="route-mode active" data-mode="driving">
        <div class="mode-header">
          <span class="mode-icon">🚗</span>
          <span class="mode-name">驾车</span>
          <span class="mode-time">${routes.driving.duration_min}分钟</span>
          <span class="mode-distance">${routes.driving.distance_km}km</span>
        </div>
        <div class="mode-content">
          ${routes.driving.steps ? buildStepsHtml(routes.driving.steps, 'driving') : '<div class="no-steps">无详细路线</div>'}
        </div>
      </div>
    `
  }

  // 步行
  if (routes.walking) {
    html += `
      <div class="route-mode" data-mode="walking">
        <div class="mode-header">
          <span class="mode-icon">🚶</span>
          <span class="mode-name">步行</span>
          <span class="mode-time">${routes.walking.duration_min}分钟</span>
          <span class="mode-distance">${routes.walking.distance_km}km</span>
        </div>
        <div class="mode-content" style="display: none;">
          ${routes.walking.steps ? buildStepsHtml(routes.walking.steps, 'walking') : '<div class="no-steps">无详细路线</div>'}
        </div>
      </div>
    `
  }

  // 公交
  if (routes.transit) {
    html += `
      <div class="route-mode" data-mode="transit">
        <div class="mode-header">
          <span class="mode-icon">🚌</span>
          <span class="mode-name">公交</span>
          <span class="mode-time">${routes.transit.duration_min}分钟</span>
          <span class="mode-distance">${routes.transit.distance_km}km</span>
        </div>
        <div class="mode-content" style="display: none;">
          ${routes.transit.steps ? buildTransitStepsHtml(routes.transit.steps) : '<div class="no-steps">无详细路线</div>'}
        </div>
      </div>
    `
  }

  html += '</div>'
  return html
}

// 生成步骤HTML（驾车/步行）
const buildStepsHtml = (steps: any[], mode: string) => {
  if (!steps || steps.length === 0) return '<div class="no-steps">无详细路线</div>'

  let html = '<div class="route-steps">'
  steps.forEach((step, index) => {
    html += `
      <div class="route-step">
        <div class="step-number">${index + 1}</div>
        <div class="step-content">
          <div class="step-instruction">${step.instruction || step.road || '前进'}</div>
          ${step.distance ? `<div class="step-distance">${Math.round(parseInt(step.distance) / 1000 * 10) / 10}km</div>` : ''}
        </div>
      </div>
    `
  })
  html += '</div>'
  return html
}

// 生成公交步骤HTML
const buildTransitStepsHtml = (steps: any[]) => {
  if (!steps || steps.length === 0) return '<div class="no-steps">无公交方案</div>'

  let html = '<div class="transit-steps">'
  steps.forEach((step, index) => {
    if (step.type === 'bus') {
      html += `
        <div class="transit-step bus-step">
          <div class="step-icon">🚌</div>
          <div class="step-content">
            <div class="bus-line">${step.name}</div>
            <div class="bus-stops">${step.via_stops}站</div>
          </div>
        </div>
      `
    } else if (step.type === 'walk' && step.distance > 0) {
      html += `
        <div class="transit-step walk-step">
          <div class="step-icon">🚶</div>
          <div class="step-content">
            <div class="walk-distance">步行 ${step.distance}km</div>
          </div>
        </div>
      `
    }
  })
  html += '</div>'
  return html
}

// 绑定路线展开/折叠事件
const bindRouteExpandEvents = (container: HTMLElement) => {
  // 绑定路线芯片点击事件
  const chips = container.querySelectorAll('.route-chip')
  chips.forEach(chip => {
    chip.addEventListener('click', function(this: HTMLElement, e: Event) {
      e.stopPropagation()
      const chipEl = this
      const routeId = chipEl.getAttribute('data-route-id')
      const detailsEl = document.getElementById(routeId!)
      const expandIcon = chipEl.querySelector('.expand-icon')

      if (detailsEl) {
        const isVisible = detailsEl.style.display !== 'none'
        detailsEl.style.display = isVisible ? 'none' : 'block'
        if (expandIcon) {
          expandIcon.textContent = isVisible ? '▼' : '▲'
        }
        chipEl.classList.toggle('expanded', !isVisible)
      }
    })
  })

  // 绑定模式切换事件
  const modeHeaders = container.querySelectorAll('.mode-header')
  modeHeaders.forEach(header => {
    header.addEventListener('click', function(this: HTMLElement) {
      const modeEl = this.closest('.route-mode')
      const allModes = modeEl?.parentElement?.querySelectorAll('.route-mode')
      const content = modeEl?.querySelector('.mode-content')

      if (allModes) {
        allModes.forEach((m: Element) => {
          m.classList.remove('active')
          const c = m.querySelector('.mode-content') as HTMLElement
          if (c) c.style.display = 'none'
        })
      }

      if (modeEl && content) {
        modeEl.classList.add('active')
        ;(content as HTMLElement).style.display = 'block'
      }
    })
  })
}

const prefillRoutesFromCacheAll = async () => {
  await nextTick()
  const chips = messagesContainer.value?.querySelectorAll('.route-chip') || []
  for (const chip of Array.from(chips)) {
    const chipEl = chip as HTMLElement
    const origin = chipEl.getAttribute('data-origin') || ''
    const destination = chipEl.getAttribute('data-destination') || ''
    const cityAttr = chipEl.getAttribute('data-city') || ''
    const routeId = chipEl.getAttribute('data-route-id') || ''

    if (!origin || !destination || !routeId) continue

    const cachedRoutes = getMultiModeRouteFromCache(cityAttr, origin, destination)
    if (cachedRoutes) {
      updateRouteDisplay(chipEl, routeId, cachedRoutes)
    }
  }

  // 重新绑定事件
  const containers = messagesContainer.value?.querySelectorAll('.message-wrapper') || []
  containers.forEach(container => {
    bindRouteExpandEvents(container as HTMLElement)
  })
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
  // 🆕 草稿现在跟会话绑定，不需要单独加载

  // 加载聊天会话
  loadChatSessions()

  // 如果有会话，加载最新的一个（会自动加载该会话的草稿），否则创建新会话
  if (chatSessions.value.length > 0) {
    const latestSession = chatSessions.value[0]
    await loadChatSession(latestSession)  // 这里会自动加载草稿、重新渲染地图和填充路线
  } else {
    createNewChat()  // 新会话，草稿为空
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

.message-html :deep(.day-detail-header p) {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.message-html :deep(.activities-detail) {
  list-style: none;
  padding: 20px;
  margin: 0;
}

.message-html :deep(.activity-detail) {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  margin-bottom: 12px;
  background: #F8F9FA;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.message-html :deep(.activity-detail:hover) {
  background: #E8F0FE;
  transform: translateX(4px);
}

.message-html :deep(.activity-number) {
  min-width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 16px;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

.message-html :deep(.activity-info) {
  flex: 1;
}

.message-html :deep(.activity-name) {
  font-size: 16px;
  font-weight: 600;
  color: #202124;
  margin-bottom: 4px;
}

.message-html :deep(.activity-notes) {
  font-size: 14px;
  color: #5F6368;
  line-height: 1.5;
}

.message-html :deep(.route-container-detail) {
  padding: 0 16px;
  margin: 12px 0;
}

.message-html :deep(.day-detail-summary) {
  padding: 16px 20px;
  background: #FFF8E1;
  border-top: 1px solid #FFF3CC;
  color: #856404;
  font-size: 14px;
  line-height: 1.6;
}

/* 行程卡片容器 */
.message-html :deep(.itinerary-container) {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 景点hover效果 */
.message-html :deep(.activity[data-spot]) {
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 8px;
  margin: 0 -8px;
  padding: 12px 8px;
}

.message-html :deep(.activity[data-spot]:hover) {
  background: #F8F9FA;
  transform: translateX(4px);
}

/* 响应式布局 */
@media (max-width: 768px) {
  .message-html :deep(.travel-map) {
    height: 320px;
  }

  .message-html :deep(.map-header) {
    padding: 12px 16px;
    font-size: 14px;
  }
}

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
  background: #ffffff;
  border: 1px solid #e0e0e0;
}

.message.user .message-avatar svg {
  color: #2c2c2c;
}

.message.assistant .message-avatar {
  background: #ffffff;
  border: 1px solid #e0e0e0;
}

.message.assistant .message-avatar svg {
  color: #2c2c2c;
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

/* 🆕 酒店卡片展示样式 */
.hotel-card-inline {
  margin: 16px 0;
  display: flex;
  justify-content: center;
}

.hotel-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  max-width: 400px;
  width: 100%;
}

.hotel-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.hotel-image-wrapper {
  width: 100%;
  height: 180px;
  overflow: hidden;
  background: #f5f5f5;
}

.hotel-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.hotel-card:hover .hotel-image {
  transform: scale(1.05);
}

.hotel-info {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.hotel-name {
  font-size: 16px;
  font-weight: 600;
  color: #2c2c2c;
  margin: 0;
  line-height: 1.4;
}

.hotel-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.hotel-price {
  font-size: 18px;
  font-weight: 700;
  color: #007bff;
}

.hotel-score {
  font-size: 14px;
  font-weight: 600;
  color: #f39c12;
}

.hotel-location {
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 4px;
}

.hotel-facilities {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.facility-tag {
  font-size: 12px;
  padding: 4px 10px;
  background: #e8f4f8;
  color: #007bff;
  border-radius: 12px;
  white-space: nowrap;
}

.booking-btn {
  display: inline-block;
  width: 100%;
  padding: 10px 16px;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  text-align: center;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s;
  margin-top: auto;
}

.booking-btn:hover {
  background: linear-gradient(135deg, #0056b3 0%, #003d82 100%);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
  transform: translateY(-1px);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .hotel-card {
    max-width: 100%;
  }
  
  .hotel-image-wrapper {
    height: 200px;
  }
}
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
