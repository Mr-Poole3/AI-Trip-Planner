const ROUTE_CACHE_KEY = 'ai_trip_route_cache'

export const readRouteCache = () => {
  try { return JSON.parse(localStorage.getItem(ROUTE_CACHE_KEY) || '{}') } catch { return {} }
}

export const writeRouteCache = (cache: Record<string, any>) => {
  localStorage.setItem(ROUTE_CACHE_KEY, JSON.stringify(cache))
}

export const makeRouteKey = (city: string, origin: string, destination: string) => {
  const c = (city || '').trim().toLowerCase()
  const o = (origin || '').trim().toLowerCase()
  const d = (destination || '').trim().toLowerCase()
  return `${c}|${o}|${d}`
}

export const getMultiModeRouteFromCache = (city: string, origin: string, destination: string) => {
  const cache = readRouteCache()
  const item = cache[makeRouteKey(city, origin, destination)]
  if (!item) return null
  if (Date.now() - item.ts > 7 * 24 * 3600 * 1000) return null
  return item.routes
}

export const setMultiModeRouteCache = (city: string, origin: string, destination: string, routes: any) => {
  const cache = readRouteCache()
  cache[makeRouteKey(city, origin, destination)] = { routes, ts: Date.now() }
  writeRouteCache(cache)
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

// 生成路线详情HTML（Google风格）
export const buildRouteDetailsHtml = (routes: any) => {
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
        <div class="mode-content" style="display: block;">
          ${buildStepsHtml(routes.driving.steps, 'driving')}
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
          <span class="mode-distance">${routes.transit.cost ? '¥' + routes.transit.cost : ''}</span>
        </div>
        <div class="mode-content" style="display: none;">
          ${buildTransitStepsHtml(routes.transit.segments)}
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
          ${buildStepsHtml(routes.walking.steps, 'walking')}
        </div>
      </div>
    `
  }

  html += '</div>'
  return html
}

// 更新路线显示
export const updateRouteDisplay = (chipEl: HTMLElement, routeId: string, routes: any) => {
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

// 绑定路线展开/折叠事件
export const bindRouteExpandEvents = (container: HTMLElement) => {
  // 绑定路线芯片点击事件
  const chips = container.querySelectorAll('.route-chip')
  chips.forEach(chip => {
    // Clone to remove old event listeners
    const newChip = chip.cloneNode(true) as HTMLElement
    chip.parentNode?.replaceChild(newChip, chip)

    newChip.addEventListener('click', function(this: HTMLElement, e: Event) {
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
  // Note: Since we are replacing innerHTML for details, we need to bind events to static parents or re-bind after update.
  // The current implementation in ChatView.vue re-binds on populateRoutesForMessage.
  // But buildRouteDetailsHtml creates new DOM elements.
  // So we should bind delegate events or bind after creation.
  // Here we assume container is the message element and we bind to all .mode-header inside it.
  
  const modeHeaders = container.querySelectorAll('.mode-header')
  modeHeaders.forEach(header => {
    // Clone to remove old event listeners
    const newHeader = header.cloneNode(true) as HTMLElement
    header.parentNode?.replaceChild(newHeader, header)

    newHeader.addEventListener('click', function(this: HTMLElement) {
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
