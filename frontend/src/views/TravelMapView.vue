<template>
  <div class="travel-map-container">
    <div class="map-header">
      <h1>上海旅游行程地图</h1>
      <p class="travel-info">出发地：上海 ｜ 目的地：上海 ｜ 日期：2025-11-20 至 2025-11-24</p>
    </div>
    
    <div class="map-legend">
      <h3>行程图例</h3>
      <div class="legend-items">
        <div class="legend-item">
          <span class="legend-marker" style="background-color: #FF6B6B;"></span>
          <span>Day 1 (2025-11-20)</span>
        </div>
        <div class="legend-item">
          <span class="legend-marker" style="background-color: #4ECDC4;"></span>
          <span>Day 2 (2025-11-21)</span>
        </div>
        <div class="legend-item">
          <span class="legend-marker" style="background-color: #FFE66D;"></span>
          <span>Day 3 (2025-11-22)</span>
        </div>
        <div class="legend-item">
          <span class="legend-marker" style="background-color: #95E1D3;"></span>
          <span>Day 4 (2025-11-23)</span>
        </div>
      </div>
    </div>

    <div id="map" class="map"></div>

    <div class="itinerary-panel">
      <h3>详细行程</h3>
      <div class="day-list">
        <div v-for="(day, index) in itinerary" :key="index" class="day-item">
          <h4 :style="{ color: day.color }">{{ day.title }}</h4>
          <ul>
            <li v-for="(spot, spotIndex) in day.spots" :key="spotIndex">{{ spot.name }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import 'ol/ol.css'
import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import XYZ from 'ol/source/XYZ'
import { Feature } from 'ol'
import { Point, LineString } from 'ol/geom'
import { Style, Circle, Fill, Stroke, Text } from 'ol/style'
import { fromLonLat } from 'ol/proj'
import Overlay from 'ol/Overlay'

// 景点数据（经纬度基于上海实际位置）
const itinerary = [
  {
    title: 'Day 1（2025-11-20）',
    color: '#FF6B6B',
    spots: [
      { name: '外滩', coords: [121.4908, 31.2397] },
      { name: '南京路步行街', coords: [121.4759, 31.2353] },
      { name: '豫园', coords: [121.4919, 31.2266] },
      { name: '上海城隍庙旅游区', coords: [121.4924, 31.2258] }
    ]
  },
  {
    title: 'Day 2（2025-11-21）',
    color: '#4ECDC4',
    spots: [
      { name: '田子坊', coords: [121.4667, 31.2103] },
      { name: '武康路', coords: [121.4383, 31.2078] },
      { name: '宋庆龄故居纪念馆', coords: [121.4388, 31.2147] },
      { name: '静安寺', coords: [121.4450, 31.2273] }
    ]
  },
  {
    title: 'Day 3（2025-11-22）',
    color: '#FFE66D',
    spots: [
      { name: '上海迪士尼度假区', coords: [121.6637, 31.1434] }
    ]
  },
  {
    title: 'Day 4（2025-11-23）',
    color: '#95E1D3',
    spots: [
      { name: '上海中心大厦', coords: [121.5058, 31.2336] },
      { name: '东方明珠广播电视塔', coords: [121.5000, 31.2397] },
      { name: '金茂大厦', coords: [121.5063, 31.2348] },
      { name: '上海环球金融中心', coords: [121.5054, 31.2347] }
    ]
  }
]

onMounted(() => {
  // 创建地图 - 使用高德地图（中国大陆可访问）
  const map = new Map({
    target: 'map',
    layers: [
      new TileLayer({
        source: new XYZ({
          url: 'https://webrd0{1-4}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
          crossOrigin: 'anonymous'
        })
      })
    ],
    view: new View({
      center: fromLonLat([121.4737, 31.2304]), // 上海中心
      zoom: 11
    })
  })

  // 为每一天创建图层
  itinerary.forEach((day, dayIndex) => {
    const vectorSource = new VectorSource()

    // 添加景点标记
    day.spots.forEach((spot, spotIndex) => {
      const marker = new Feature({
        geometry: new Point(fromLonLat(spot.coords)),
        name: spot.name,
        day: day.title
      })

      marker.setStyle(new Style({
        image: new Circle({
          radius: 8,
          fill: new Fill({ color: day.color }),
          stroke: new Stroke({
            color: '#fff',
            width: 2
          })
        }),
        text: new Text({
          text: (spotIndex + 1).toString(),
          fill: new Fill({ color: '#fff' }),
          font: 'bold 12px sans-serif',
          offsetY: 0
        })
      }))

      vectorSource.addFeature(marker)
    })

    // 如果有多个景点，绘制路线
    if (day.spots.length > 1) {
      const routeCoords = day.spots.map(spot => fromLonLat(spot.coords))
      const routeLine = new Feature({
        geometry: new LineString(routeCoords)
      })

      routeLine.setStyle(new Style({
        stroke: new Stroke({
          color: day.color,
          width: 3,
          lineDash: [10, 5]
        })
      }))

      vectorSource.addFeature(routeLine)
    }

    // 添加图层到地图
    const vectorLayer = new VectorLayer({
      source: vectorSource
    })
    map.addLayer(vectorLayer)
  })

  // 创建弹出层
  const popupElement = document.createElement('div')
  popupElement.className = 'ol-popup'
  popupElement.innerHTML = `
    <div class="popup-closer" id="popup-closer">×</div>
    <div id="popup-content"></div>
  `
  document.body.appendChild(popupElement)

  const popup = new Overlay({
    element: popupElement,
    positioning: 'bottom-center',
    stopEvent: false,
    offset: [0, -15]
  })
  map.addOverlay(popup)

  // 点击景点显示信息
  map.on('click', (evt) => {
    const feature = map.forEachFeatureAtPixel(evt.pixel, (feature) => feature)
    
    if (feature && feature.get('name')) {
      const coords = feature.getGeometry()?.getCoordinates()
      const contentDiv = document.getElementById('popup-content')
      if (contentDiv && coords) {
        contentDiv.innerHTML = `
          <h4>${feature.get('name')}</h4>
          <p>${feature.get('day')}</p>
        `
        popup.setPosition(coords)
        popupElement.style.display = 'block'
      }
    } else {
      popupElement.style.display = 'none'
    }
  })

  // 关闭弹出层
  const closer = document.getElementById('popup-closer')
  if (closer) {
    closer.onclick = () => {
      popupElement.style.display = 'none'
      return false
    }
  }

  // 鼠标悬停变化指针
  map.on('pointermove', (evt) => {
    const pixel = map.getEventPixel(evt.originalEvent)
    const hit = map.hasFeatureAtPixel(pixel)
    map.getTargetElement().style.cursor = hit ? 'pointer' : ''
  })
})
</script>

<style scoped>
.travel-map-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  box-sizing: border-box;
}

.map-header {
  text-align: center;
  color: white;
  margin-bottom: 15px;
}

.map-header h1 {
  margin: 0 0 10px 0;
  font-size: 2.5em;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.travel-info {
  font-size: 1.1em;
  margin: 0;
  opacity: 0.9;
}

.map-legend {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 15px 20px;
  margin-bottom: 15px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.map-legend h3 {
  margin: 0 0 10px 0;
  font-size: 1.2em;
  color: #333;
}

.legend-items {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95em;
  color: #555;
}

.legend-marker {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.map {
  flex: 1;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  margin-bottom: 15px;
  min-height: 500px;
}

.itinerary-panel {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-height: 250px;
  overflow-y: auto;
}

.itinerary-panel h3 {
  margin: 0 0 15px 0;
  font-size: 1.3em;
  color: #333;
}

.day-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.day-item {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid;
}

.day-item:nth-child(1) {
  border-left-color: #FF6B6B;
}

.day-item:nth-child(2) {
  border-left-color: #4ECDC4;
}

.day-item:nth-child(3) {
  border-left-color: #FFE66D;
}

.day-item:nth-child(4) {
  border-left-color: #95E1D3;
}

.day-item h4 {
  margin: 0 0 8px 0;
  font-size: 1.1em;
}

.day-item ul {
  margin: 0;
  padding-left: 20px;
  list-style: none;
}

.day-item li {
  margin: 4px 0;
  font-size: 0.95em;
  color: #555;
  position: relative;
  padding-left: 15px;
}

.day-item li::before {
  content: "📍";
  position: absolute;
  left: 0;
}

/* 滚动条美化 */
.itinerary-panel::-webkit-scrollbar {
  width: 8px;
}

.itinerary-panel::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.itinerary-panel::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.itinerary-panel::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>

<style>
/* 全局样式用于弹出层 */
.ol-popup {
  position: absolute;
  background-color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  padding: 15px;
  border-radius: 10px;
  border: 1px solid #cccccc;
  bottom: 12px;
  left: -50px;
  min-width: 180px;
  z-index: 1000;
}

.ol-popup:after,
.ol-popup:before {
  top: 100%;
  border: solid transparent;
  content: " ";
  height: 0;
  width: 0;
  position: absolute;
  pointer-events: none;
}

.ol-popup:after {
  border-top-color: white;
  border-width: 10px;
  left: 48px;
  margin-left: -10px;
}

.ol-popup:before {
  border-top-color: #cccccc;
  border-width: 11px;
  left: 48px;
  margin-left: -11px;
}

.popup-closer {
  text-decoration: none;
  position: absolute;
  top: 5px;
  right: 8px;
  cursor: pointer;
  font-size: 20px;
  color: #999;
  font-weight: bold;
}

.popup-closer:hover {
  color: #333;
}

#popup-content h4 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 1.1em;
}

#popup-content p {
  margin: 0;
  color: #666;
  font-size: 0.9em;
}
</style>

