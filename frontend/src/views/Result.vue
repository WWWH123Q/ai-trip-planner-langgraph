<template>
  <div class="result-container">
    <!-- 背景装饰 -->
    <div class="result-bg" aria-hidden="true">
      <div class="result-orb orb-a"></div>
      <div class="result-orb orb-b"></div>
      <div class="result-grid"></div>
    </div>

    <!-- 页面头部 -->
    <div class="page-header">
      <a-button class="back-button" size="large" @click="goBack">
        ← 返回首页
      </a-button>

      <a-space size="middle" wrap>
        <a-button v-if="!editMode" class="soft-action-button" @click="toggleEditMode" type="default">
          ✏️ 编辑行程
        </a-button>
        <a-button v-else class="primary-action-button" @click="saveChanges" type="primary">
          💾 保存修改
        </a-button>
        <a-button v-if="editMode" class="soft-action-button" @click="cancelEdit" type="default">
          ❌ 取消编辑
        </a-button>

        <!-- 导出按钮 -->
        <a-dropdown v-if="!editMode">
          <template #overlay>
            <a-menu>
              <a-menu-item key="image" @click="exportAsImage">
                📷 导出为图片
              </a-menu-item>
              <a-menu-item key="pdf" @click="exportAsPDF">
                📄 导出为PDF
              </a-menu-item>
            </a-menu>
          </template>
          <a-button class="soft-action-button" type="default">
            📥 导出行程 <DownOutlined />
          </a-button>
        </a-dropdown>
      </a-space>
    </div>

    <div v-if="tripPlan" class="content-wrapper">
      <!-- 侧边导航 -->
      <div class="side-nav">
        <a-affix :offset-top="90">
          <a-menu mode="inline" :selected-keys="[activeSection]" @click="scrollToSection">
            <a-menu-item key="overview">
              <span>📋 行程概览</span>
            </a-menu-item>
            <a-menu-item key="budget" v-if="tripPlan.budget">
              <span>💰 预算明细</span>
            </a-menu-item>
            <a-menu-item key="map">
              <span>📍 景点地图</span>
            </a-menu-item>
            <a-sub-menu key="days" title="📅 每日行程">
              <a-menu-item v-for="(day, index) in tripPlan.days" :key="`day-${index}`">
                第{{ day.day_index + 1 }}天
              </a-menu-item>
            </a-sub-menu>
            <a-menu-item key="weather" v-if="tripPlan.weather_info && tripPlan.weather_info.length > 0">
              <span>🌤️ 天气信息</span>
            </a-menu-item>
          </a-menu>
        </a-affix>
      </div>

      <!-- 主内容区 -->
      <div class="main-content">
        <!-- 新增：结果页 Hero 看板 -->
        <section class="result-hero-card">
          <div class="result-hero-left">
            <div class="hero-kicker">
              <span class="kicker-dot"></span>
              AI Travel Plan Ready
            </div>
            <h1>{{ tripPlan.city }}旅行计划</h1>
            <p>
              {{ tripPlan.start_date }} 至 {{ tripPlan.end_date }} ·
              共 {{ tripPlan.days.length }} 天 ·
              已为你整理景点、天气、预算、地图路线和每日行程。
            </p>

            <div class="fun-actions">
              <button type="button" class="fun-button primary" @click="randomSpotlight">
                <span>🎲</span>
                景点盲盒
              </button>
              <button type="button" class="fun-button" @click="showBudgetTip">
                <span>💰</span>
                预算小算盘
              </button>
              <button type="button" class="fun-button" @click="showTravelCard">
                <span>✨</span>
                旅行氛围卡
              </button>
              <button type="button" class="fun-button" @click="showAllRoute">
                <span>🗺️</span>
                路线总览
              </button>
              <button type="button" class="fun-button" @click="expandAllDays">
                <span>📖</span>
                展开全部
              </button>
              <button type="button" class="fun-button" @click="collapseAllDays">
                <span>🧺</span>
                收起行程
              </button>
              <button type="button" class="fun-button" @click="copyTripSummary">
                <span>📋</span>
                复制摘要
              </button>
              <button type="button" class="fun-button" @click="showPackingList">
                <span>🎒</span>
                出行清单
              </button>
              <button type="button" class="fun-button" @click="showFoodMission">
                <span>🍜</span>
                美食任务
              </button>
              <button type="button" class="fun-button" @click="showIntensityReport">
                <span>🚦</span>
                强度分析
              </button>
            </div>
          </div>

          <div class="result-hero-right">
            <div class="summary-grid">
              <div class="summary-tile">
                <span>📅</span>
                <strong>{{ tripPlan.days.length }}</strong>
                <p>旅行天数</p>
              </div>
              <div class="summary-tile">
                <span>📍</span>
                <strong>{{ attractionCount }}</strong>
                <p>景点数量</p>
              </div>
              <div class="summary-tile">
                <span>🍽️</span>
                <strong>{{ mealCount }}</strong>
                <p>餐饮安排</p>
              </div>
              <div class="summary-tile">
                <span>💰</span>
                <strong>{{ budgetTotalText }}</strong>
                <p>预估费用</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 顶部信息区:左侧概览+预算,右侧地图 -->
        <div class="top-info-section">
          <!-- 左侧:行程概览和预算明细 -->
          <div class="left-info">
            <!-- 行程概览 -->
            <a-card id="overview" :title="`${tripPlan.city}旅行计划`" :bordered="false" class="overview-card">
              <div class="overview-content">
                <div class="info-item">
                  <span class="info-label">📅 日期:</span>
                  <span class="info-value">{{ tripPlan.start_date }} 至 {{ tripPlan.end_date }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">💡 建议:</span>
                  <span class="info-value">{{ tripPlan.overall_suggestions }}</span>
                </div>
              </div>
            </a-card>

            <!-- 预算明细 -->
            <a-card id="budget" v-if="tripPlan.budget" title="💰 预算明细" :bordered="false" class="budget-card">
              <div class="budget-grid">
                <div class="budget-item">
                  <div class="budget-label">景点门票</div>
                  <div class="budget-value">¥{{ tripPlan.budget.total_attractions }}</div>
                </div>
                <div class="budget-item">
                  <div class="budget-label">酒店住宿</div>
                  <div class="budget-value">¥{{ tripPlan.budget.total_hotels }}</div>
                </div>
                <div class="budget-item">
                  <div class="budget-label">餐饮费用</div>
                  <div class="budget-value">¥{{ tripPlan.budget.total_meals }}</div>
                </div>
                <div class="budget-item">
                  <div class="budget-label">交通费用</div>
                  <div class="budget-value">¥{{ tripPlan.budget.total_transportation }}</div>
                </div>
              </div>
              <div class="budget-total">
                <span class="total-label">预估总费用</span>
                <span class="total-value">¥{{ tripPlan.budget.total }}</span>
              </div>
            </a-card>
          </div>

          <!-- 右侧:地图 -->
          <div class="right-map">
            <a-card id="map" title="📍 景点地图" :bordered="false" class="map-card">
              <div class="map-toolbar">
                <button
                  class="map-day-button"
                  :class="{ active: activeMapDay === 'all' }"
                  @click="setActiveMapDay('all')"
                >
                  全部路线
                </button>
                <button
                  v-for="day in tripPlan.days"
                  :key="`map-day-${day.day_index}`"
                  class="map-day-button"
                  :class="{ active: activeMapDay === day.day_index }"
                  @click="setActiveMapDay(day.day_index)"
                >
                  第{{ day.day_index + 1 }}天
                </button>
              </div>
              <div id="amap-container"></div>
            </a-card>
          </div>
        </div>

        <!-- 每日行程:可折叠 -->
        <a-card title="📅 每日行程" :bordered="false" class="days-card">
          <a-collapse v-model:activeKey="activeDays">
            <a-collapse-panel
              v-for="(day, index) in tripPlan.days"
              :key="index"
              :id="`day-${index}`"
            >
              <template #header>
                <div class="day-header">
                  <span class="day-title">第{{ day.day_index + 1 }}天</span>
                  <span class="day-date">{{ day.date }}</span>
                </div>
              </template>

              <!-- 行程基本信息 -->
              <div class="day-info">
                <div class="info-row">
                  <span class="label">📝 行程描述:</span>
                  <span class="value">{{ day.description }}</span>
                </div>
                <div class="info-row">
                  <span class="label">🚗 交通方式:</span>
                  <span class="value">{{ day.transportation }}</span>
                </div>
                <div class="info-row">
                  <span class="label">🏨 住宿:</span>
                  <span class="value">{{ day.accommodation }}</span>
                </div>
              </div>

              <!-- 景点安排 -->
              <a-divider orientation="left">🎯 景点安排</a-divider>
              <a-list
                :data-source="day.attractions"
                :grid="{ gutter: 16, column: 2 }"
              >
                <template #renderItem="{ item, index }">
                  <a-list-item>
                    <a-card :title="item.name" size="small" class="attraction-card">
                      <!-- 编辑模式下的操作按钮 -->
                      <template #extra v-if="editMode">
                        <a-space>
                          <a-button
                            size="small"
                            @click="moveAttraction(day.day_index, index, 'up')"
                            :disabled="index === 0"
                          >
                            ↑
                          </a-button>
                          <a-button
                            size="small"
                            @click="moveAttraction(day.day_index, index, 'down')"
                            :disabled="index === day.attractions.length - 1"
                          >
                            ↓
                          </a-button>
                          <a-button
                            size="small"
                            danger
                            @click="deleteAttraction(day.day_index, index)"
                          >
                            🗑️
                          </a-button>
                        </a-space>
                      </template>

                      <!-- 景点图片 -->
                      <div class="attraction-image-wrapper">
                        <img
                          :src="getAttractionImage(item.name, index)"
                          :alt="item.name"
                          class="attraction-image"
                          @error="handleImageError"
                        />
                        <div class="attraction-badge">
                          <span class="badge-number">{{ index + 1 }}</span>
                        </div>
                        <div v-if="item.ticket_price" class="price-tag">
                          ¥{{ item.ticket_price }}
                        </div>
                      </div>

                      <!-- 编辑模式下可编辑的字段 -->
                      <div v-if="editMode">
                        <p><strong>地址:</strong></p>
                        <a-input v-model:value="item.address" size="small" style="margin-bottom: 8px" />

                        <p><strong>游览时长(分钟):</strong></p>
                        <a-input-number v-model:value="item.visit_duration" :min="10" :max="480" size="small" style="width: 100%; margin-bottom: 8px" />

                        <p><strong>描述:</strong></p>
                        <a-textarea v-model:value="item.description" :rows="2" size="small" style="margin-bottom: 8px" />
                      </div>

                      <!-- 查看模式 -->
                      <div v-else>
                        <p><strong>地址:</strong> {{ item.address }}</p>
                        <p><strong>游览时长:</strong> {{ item.visit_duration }}分钟</p>
                        <p><strong>描述:</strong> {{ item.description }}</p>
                        <p v-if="item.rating"><strong>评分:</strong> {{ item.rating }}⭐</p>
                      </div>
                    </a-card>
                  </a-list-item>
                </template>
              </a-list>

              <!-- 酒店推荐 -->
              <a-divider v-if="day.hotel" orientation="left">🏨 住宿推荐</a-divider>
              <a-card v-if="day.hotel" size="small" class="hotel-card">
                <template #title>
                  <span class="hotel-title">{{ day.hotel.name }}</span>
                </template>
                <a-descriptions :column="2" size="small">
                  <a-descriptions-item label="地址">{{ day.hotel.address }}</a-descriptions-item>
                  <a-descriptions-item label="类型">{{ day.hotel.type }}</a-descriptions-item>
                  <a-descriptions-item label="价格范围">{{ day.hotel.price_range }}</a-descriptions-item>
                  <a-descriptions-item label="评分">{{ day.hotel.rating }}⭐</a-descriptions-item>
                  <a-descriptions-item label="距离" :span="2">{{ day.hotel.distance }}</a-descriptions-item>
                </a-descriptions>
              </a-card>

              <!-- 餐饮安排 -->
              <a-divider orientation="left">🍽️ 餐饮安排</a-divider>
              <a-descriptions :column="1" bordered size="small">
                <a-descriptions-item
                  v-for="meal in day.meals"
                  :key="meal.type"
                  :label="getMealLabel(meal.type)"
                >
                  {{ meal.name }}
                  <span v-if="meal.description"> - {{ meal.description }}</span>
                </a-descriptions-item>
              </a-descriptions>
            </a-collapse-panel>
          </a-collapse>
        </a-card>

        <a-card id="weather" v-if="tripPlan.weather_info && tripPlan.weather_info.length > 0" title="🌤️ 天气信息" style="margin-top: 20px" :bordered="false">
          <a-list
            :data-source="tripPlan.weather_info"
            :grid="{ gutter: 16, column: 3 }"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <a-card size="small" class="weather-card">
                  <div class="weather-date">{{ item.date }}</div>
                  <div class="weather-info-row">
                    <span class="weather-icon">☀️</span>
                    <div>
                      <div class="weather-label">白天</div>
                      <div class="weather-value">{{ item.day_weather }} {{ item.day_temp }}°C</div>
                    </div>
                  </div>
                  <div class="weather-info-row">
                    <span class="weather-icon">🌙</span>
                    <div>
                      <div class="weather-label">夜间</div>
                      <div class="weather-value">{{ item.night_weather }} {{ item.night_temp }}°C</div>
                    </div>
                  </div>
                  <div class="weather-wind">
                    💨 {{ item.wind_direction }} {{ item.wind_power }}
                  </div>
                </a-card>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </div>
    </div>

    <a-empty v-else description="没有找到旅行计划数据" class="empty-panel">
      <template #image>
        <div style="font-size: 80px;">🗺️</div>
      </template>
      <template #description>
        <span style="color: #999;">暂无旅行计划数据,请先创建行程</span>
      </template>
      <a-button type="primary" @click="goBack">返回首页创建行程</a-button>
    </a-empty>

    <!-- 回到顶部按钮 -->
    <a-back-top :visibility-height="300">
      <div class="back-top-button">
        ↑
      </div>
    </a-back-top>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { DownOutlined } from '@ant-design/icons-vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import type { TripPlan } from '@/types'

const router = useRouter()
const tripPlan = ref<TripPlan | null>(null)
const editMode = ref(false)
const originalPlan = ref<TripPlan | null>(null)
const attractionPhotos = ref<Record<string, string>>({})
const activeSection = ref('overview')
const activeDays = ref<number[]>([0]) // 默认展开第一天
let map: any = null
type MapDayFilter = 'all' | number
const activeMapDay = ref<MapDayFilter>('all')
let AMapInstance: any = null

const attractionCount = computed(() => {
  if (!tripPlan.value) return 0
  return tripPlan.value.days.reduce((sum, day) => sum + day.attractions.length, 0)
})

const mealCount = computed(() => {
  if (!tripPlan.value) return 0
  return tripPlan.value.days.reduce((sum, day) => sum + day.meals.length, 0)
})

const budgetTotalText = computed(() => {
  if (!tripPlan.value?.budget?.total) return '—'
  return `¥${tripPlan.value.budget.total}`
})

type ModalCardItem = {
  icon: string
  title: string
  value: string
  desc?: string
}

const openCardModal = (options: {
  type?: 'info' | 'success'
  title: string
  items: ModalCardItem[]
  footer?: string
  okText?: string
}) => {
  const modalFn = options.type === 'success' ? Modal.success : Modal.info

  modalFn({
    title: options.title,
    width: 640,
    centered: true,
    okText: options.okText || '知道了',
    class: 'trip-card-modal',
    content: h('div', { class: 'trip-modal-card' }, [
      h(
        'div',
        { class: 'trip-modal-grid' },
        options.items.map(item =>
          h('div', { class: 'trip-modal-item' }, [
            h('div', { class: 'trip-modal-icon' }, item.icon),
            h('div', { class: 'trip-modal-main' }, [
              h('div', { class: 'trip-modal-title' }, item.title),
              h('div', { class: 'trip-modal-value' }, item.value),
              item.desc ? h('div', { class: 'trip-modal-desc' }, item.desc) : null
            ])
          ])
        )
      ),
      options.footer
        ? h('div', { class: 'trip-modal-footer' }, options.footer)
        : null
    ])
  })
}

onMounted(async () => {
  const data = sessionStorage.getItem('tripPlan')
  if (data) {
    tripPlan.value = JSON.parse(data)
    // 加载景点图片
    await loadAttractionPhotos()
    // 等待DOM渲染完成后初始化地图
    await nextTick()
    initMap()
  }
})

const goBack = () => {
  router.push('/')
}

// 滚动到指定区域
const scrollToSection = ({ key }: { key: string }) => {
  activeSection.value = key

  if (key.startsWith('day-')) {
    const index = Number(key.replace('day-', ''))
    activeDays.value = Array.from(new Set([...activeDays.value, index]))
    nextTick(() => {
      const element = document.getElementById(key)
      element?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
    return
  }

  const element = document.getElementById(key)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// 新增：景点盲盒
const randomSpotlight = () => {
  if (!tripPlan.value) return

  const pool: Array<{ dayIndex: number; attrIndex: number; name: string }> = []
  tripPlan.value.days.forEach((day, dayIndex) => {
    day.attractions.forEach((attraction, attrIndex) => {
      pool.push({ dayIndex, attrIndex, name: attraction.name })
    })
  })

  if (pool.length === 0) {
    message.warning('当前行程里还没有景点')
    return
  }

  const target = pool[Math.floor(Math.random() * pool.length)]
  activeDays.value = Array.from(new Set([...activeDays.value, target.dayIndex]))
  setActiveMapDay(tripPlan.value.days[target.dayIndex].day_index)

  nextTick(() => {
    const element = document.getElementById(`day-${target.dayIndex}`)
    element?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  })

  message.success(`今日盲盒景点：第${target.dayIndex + 1}天 · ${target.name}`)
}

// 新增：预算提示
const showBudgetTip = () => {
  const budget = tripPlan.value?.budget
  if (!budget) {
    message.info('当前行程暂时没有预算数据')
    return
  }

  const items = [
    { name: '景点门票', value: budget.total_attractions, icon: '🎫' },
    { name: '酒店住宿', value: budget.total_hotels, icon: '🏨' },
    { name: '餐饮费用', value: budget.total_meals, icon: '🍽️' },
    { name: '交通费用', value: budget.total_transportation, icon: '🚗' }
  ]

  const maxItem = items.reduce((max, item) => item.value > max.value ? item : max, items[0])
  const dayCount = Math.max(tripPlan.value?.days.length || 1, 1)
  const average = Math.round((budget.total || 0) / dayCount)

  openCardModal({
    title: '💰 预算小算盘',
    items: [
      { icon: '💵', title: '预估总费用', value: `¥${budget.total}`, desc: '当前行程的整体预算估算' },
      { icon: '📆', title: '日均花费', value: `¥${average}/天`, desc: `按 ${dayCount} 天平均计算` },
      { icon: maxItem.icon, title: '最高支出项', value: maxItem.name, desc: `约 ¥${maxItem.value}` },
      { icon: '🧾', title: '预算结构', value: `${items.length} 类费用`, desc: '门票、住宿、餐饮、交通' }
    ],
    footer: '预算只是估算值，真实花费会受到酒店价格、餐饮选择、交通方式和景区票价变化影响。',
    okText: '我会控制预算'
  })
}

// 新增：旅行氛围卡
const showTravelCard = () => {
  if (!tripPlan.value) return

  const firstDay = tripPlan.value.days[0]
  const firstSpot = firstDay?.attractions?.[0]?.name || '第一站'
  const lastDay = tripPlan.value.days[tripPlan.value.days.length - 1]
  const lastSpot = lastDay?.attractions?.[lastDay.attractions.length - 1]?.name || '最后一站'

  openCardModal({
    type: 'success',
    title: '✨ 旅行氛围卡',
    items: [
      { icon: '🏙️', title: '目的地', value: tripPlan.value.city, desc: `${tripPlan.value.start_date} 至 ${tripPlan.value.end_date}` },
      { icon: '🚩', title: '建议起点', value: firstSpot, desc: '从第一站开始进入旅行节奏' },
      { icon: '🌙', title: '收尾地点', value: lastSpot, desc: '适合作为最后的记忆点' },
      { icon: '📍', title: '行程密度', value: `${attractionCount.value} 个景点`, desc: `${tripPlan.value.days.length} 天内完成主要游览` }
    ],
    footer: `这趟旅行的关键词：${tripPlan.value.days.length}天、${attractionCount.value}个景点、${mealCount.value}项餐饮安排。建议保持轻松节奏，边走边调整。`,
    okText: '出发！'
  })
}

// 新增：地图路线总览
const showAllRoute = () => {
  activeMapDay.value = 'all'
  scrollToSection({ key: 'map' })
  nextTick(() => {
    refreshMapOverlays()
  })
  message.success('已切换到全部路线视图')
}

// 新增：展开全部每日行程
const expandAllDays = () => {
  if (!tripPlan.value) return
  activeDays.value = tripPlan.value.days.map((_, index) => index)
  message.success('已展开全部每日行程')
}

// 新增：收起全部每日行程
const collapseAllDays = () => {
  activeDays.value = []
  message.info('已收起每日行程')
}

// 新增：复制行程摘要
const copyTripSummary = async () => {
  if (!tripPlan.value) return

  const lines = [
    `【${tripPlan.value.city}旅行计划】`,
    `日期：${tripPlan.value.start_date} 至 ${tripPlan.value.end_date}`,
    `天数：${tripPlan.value.days.length}天`,
    `景点：${attractionCount.value}个`,
    `餐饮：${mealCount.value}项`,
    tripPlan.value.budget?.total ? `预算：约 ¥${tripPlan.value.budget.total}` : '',
    '',
    '每日安排：',
    ...tripPlan.value.days.map(day => {
      const spots = day.attractions.map(item => item.name).join(' → ')
      return `第${day.day_index + 1}天：${spots}`
    })
  ].filter(Boolean)

  try {
    await navigator.clipboard.writeText(lines.join(String.fromCharCode(10)))
    message.success('行程摘要已复制，可以发给朋友啦')
  } catch (error) {
    console.error('复制失败:', error)
    message.error('复制失败，请检查浏览器权限')
  }
}

// 新增：出行清单
const showPackingList = () => {
  if (!tripPlan.value) return

  const weatherText = (tripPlan.value.weather_info || [])
    .map(item => `${item.day_weather || ''}${item.night_weather || ''}`)
    .join(' ')

  const maxTemp = Math.max(
    ...((tripPlan.value.weather_info || []).map(item => Number(item.day_temp)).filter(num => !Number.isNaN(num))),
    0
  )

  const list = ['身份证/学生证', '充电宝和充电线', '舒服的鞋', '纸巾和湿巾', '常用药', '少量现金']

  if (/雨|阵雨|雷/.test(weatherText)) {
    list.push('雨伞或轻便雨衣')
  }

  if (maxTemp >= 28) {
    list.push('防晒霜', '遮阳帽', '便携水杯')
  }

  if (tripPlan.value.days.length >= 3) {
    list.push('换洗衣物', '收纳袋')
  }

  openCardModal({
    title: '🎒 出行清单',
    items: list.map((item, index) => ({
      icon: index < 6 ? ['🪪', '🔋', '👟', '🧻', '💊', '💵'][index] : '✅',
      title: `清单 ${index + 1}`,
      value: item,
      desc: index < 6 ? '基础必备' : '根据天气和天数补充'
    })),
    footer: '可以截图保存，也可以点击「复制摘要」把行程一起发给同行的人。',
    okText: '收好啦'
  })
}

// 新增：随机美食任务
const showFoodMission = () => {
  if (!tripPlan.value) return

  const meals: Array<{ day: number; label: string; name: string; desc?: string }> = []
  tripPlan.value.days.forEach(day => {
    day.meals.forEach(meal => {
      meals.push({
        day: day.day_index + 1,
        label: getMealLabel(meal.type),
        name: meal.name,
        desc: meal.description || ''
      })
    })
  })

  if (meals.length === 0) {
    message.info('当前行程还没有餐饮安排')
    return
  }

  const target = meals[Math.floor(Math.random() * meals.length)]
  openCardModal({
    type: 'success',
    title: '🍜 今日美食任务',
    items: [
      { icon: '📅', title: '日期位置', value: `第${target.day}天`, desc: '把它当作当天的小任务' },
      { icon: '🍽️', title: '餐饮类型', value: target.label, desc: '行程里的用餐节点' },
      { icon: '🥢', title: '任务目标', value: target.name, desc: target.desc || '去尝一尝这家推荐' },
      { icon: '📸', title: '隐藏玩法', value: '拍照打卡', desc: '给这顿饭留下一个记忆点' }
    ],
    footer: '美食任务是从当前行程餐饮安排中随机抽取的，可以多点几次刷新灵感。',
    okText: '我去吃！'
  })
}

// 新增：行程强度分析
const showIntensityReport = () => {
  if (!tripPlan.value) return

  const dayReports = tripPlan.value.days.map(day => {
    const spotCount = day.attractions.length
    const totalMinutes = day.attractions.reduce((sum, item) => sum + (Number(item.visit_duration) || 0), 0)
    let level = '轻松'
    let icon = '🟢'

    if (spotCount >= 4 || totalMinutes >= 420) {
      level = '偏紧凑'
      icon = '🔴'
    } else if (spotCount >= 3 || totalMinutes >= 300) {
      level = '适中'
      icon = '🟡'
    }

    return {
      icon,
      title: `第${day.day_index + 1}天`,
      value: level,
      desc: `${spotCount}个景点，约${totalMinutes || '未知'}分钟`
    }
  })

  const tightDays = dayReports.filter(item => item.value === '偏紧凑').length

  openCardModal({
    title: '🚦 行程强度分析',
    items: dayReports,
    footer: tightDays > 0
      ? `有 ${tightDays} 天偏紧凑，可以考虑减少景点或增加休息时间。`
      : '整体节奏比较舒服，可以按这个强度出行。',
    okText: '收到'
  })
}

// 切换编辑模式
const toggleEditMode = () => {
  editMode.value = true
  // 保存原始数据用于取消编辑
  originalPlan.value = JSON.parse(JSON.stringify(tripPlan.value))
  message.info('进入编辑模式')
}

// 保存修改
const saveChanges = () => {
  editMode.value = false
  // 更新sessionStorage
  if (tripPlan.value) {
    sessionStorage.setItem('tripPlan', JSON.stringify(tripPlan.value))
  }
  message.success('修改已保存')

  // 重新初始化地图以反映更改
  if (map) {
    map.destroy()
  }
  nextTick(() => {
    initMap()
  })
}

// 取消编辑
const cancelEdit = () => {
  if (originalPlan.value) {
    tripPlan.value = JSON.parse(JSON.stringify(originalPlan.value))
  }
  editMode.value = false
  message.info('已取消编辑')
}

// 删除景点
const deleteAttraction = (dayIndex: number, attrIndex: number) => {
  if (!tripPlan.value) return

  const day = tripPlan.value.days[dayIndex]
  if (day.attractions.length <= 1) {
    message.warning('每天至少需要保留一个景点')
    return
  }

  day.attractions.splice(attrIndex, 1)
  message.success('景点已删除')
}

// 移动景点顺序
const moveAttraction = (dayIndex: number, attrIndex: number, direction: 'up' | 'down') => {
  if (!tripPlan.value) return

  const day = tripPlan.value.days[dayIndex]
  const attractions = day.attractions

  if (direction === 'up' && attrIndex > 0) {
    [attractions[attrIndex], attractions[attrIndex - 1]] = [attractions[attrIndex - 1], attractions[attrIndex]]
  } else if (direction === 'down' && attrIndex < attractions.length - 1) {
    [attractions[attrIndex], attractions[attrIndex + 1]] = [attractions[attrIndex + 1], attractions[attrIndex]]
  }
}

const getMealLabel = (type: string): string => {
  const labels: Record<string, string> = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    snack: '小吃'
  }
  return labels[type] || type
}

// 加载所有景点图片
const loadAttractionPhotos = async () => {
  if (!tripPlan.value) return

  const promises: Promise<void>[] = []

  tripPlan.value.days.forEach(day => {
    day.attractions.forEach(attraction => {
      const promise = fetch(`http://localhost:8000/api/poi/photo?name=${encodeURIComponent(attraction.name)}`)
        .then(res => res.json())
        .then(data => {
          if (data.success && data.data.photo_url) {
            attractionPhotos.value[attraction.name] = data.data.photo_url
          }
        })
        .catch(err => {
          console.error(`获取${attraction.name}图片失败:`, err)
        })

      promises.push(promise)
    })
  })

  await Promise.all(promises)
}

// 获取景点图片
const getAttractionImage = (name: string, index: number): string => {
  // 如果已加载真实图片,返回真实图片
  if (attractionPhotos.value[name]) {
    return attractionPhotos.value[name]
  }

  // 返回一个纯色占位图(避免跨域问题)
  const colors = [
    { start: '#0ea5e9', end: '#14b8a6' },
    { start: '#06b6d4', end: '#22c55e' },
    { start: '#2dd4bf', end: '#84cc16' },
    { start: '#38bdf8', end: '#0f766e' },
    { start: '#22c55e', end: '#0284c7' }
  ]
  const colorIndex = index % colors.length
  const { start, end } = colors[colorIndex]

  // 使用base64编码避免中文问题
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">
    <defs>
      <linearGradient id="grad${index}" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:${start};stop-opacity:1" />
        <stop offset="100%" style="stop-color:${end};stop-opacity:1" />
      </linearGradient>
    </defs>
    <rect width="400" height="300" fill="url(#grad${index})"/>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="24" font-weight="bold" fill="white">${name}</text>
  </svg>`

  return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svg)))}`
}

// 图片加载失败时的处理
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  // 使用灰色占位图
  img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="400" height="300" fill="%23f0f0f0"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="18" fill="%23999"%3E图片加载失败%3C/text%3E%3C/svg%3E'
}

// 导出为图片
const exportAsImage = async () => {
  try {
    message.loading({ content: '正在生成图片...', key: 'export', duration: 0 })

    const element = document.querySelector('.main-content') as HTMLElement
    if (!element) {
      throw new Error('未找到内容元素')
    }

    // 创建一个独立的容器
    const exportContainer = document.createElement('div')
    exportContainer.style.width = element.offsetWidth + 'px'
    exportContainer.style.backgroundColor = '#f5f7fa'
    exportContainer.style.padding = '20px'

    // 复制所有内容
    exportContainer.innerHTML = element.innerHTML

    // 处理地图截图
    const mapContainer = document.getElementById('amap-container')
    if (mapContainer && map) {
      const mapCanvas = mapContainer.querySelector('canvas')
      if (mapCanvas) {
        const mapSnapshot = mapCanvas.toDataURL('image/png')
        const exportMapContainer = exportContainer.querySelector('#amap-container')
        if (exportMapContainer) {
          exportMapContainer.innerHTML = `<img src="${mapSnapshot}" style="width:100%;height:100%;object-fit:cover;" />`
        }
      }
    }

    // 移除所有ant-card类,替换为纯div
    const cards = exportContainer.querySelectorAll('.ant-card')
    cards.forEach((card) => {
      const cardEl = card as HTMLElement
      try {
        cardEl.className = ''
        cardEl.style.setProperty('background-color', '#ffffff')
        cardEl.style.setProperty('border-radius', '12px')
        cardEl.style.setProperty('box-shadow', '0 4px 12px rgba(0, 0, 0, 0.1)')
        cardEl.style.setProperty('margin-bottom', '20px')
        cardEl.style.setProperty('overflow', 'hidden')
      } catch (err) {
        console.error('设置卡片样式失败:', err)
      }
    })

    // 处理卡片头部
    const cardHeads = exportContainer.querySelectorAll('.ant-card-head')
    cardHeads.forEach((head) => {
      const headEl = head as HTMLElement
      try {
        headEl.style.setProperty('background-color', '#0ea5e9')
        headEl.style.setProperty('color', '#ffffff')
        headEl.style.setProperty('padding', '16px 24px')
        headEl.style.setProperty('font-size', '18px')
        headEl.style.setProperty('font-weight', '600')
      } catch (err) {
        console.error('设置卡片头部样式失败:', err)
      }
    })

    // 处理卡片内容
    const cardBodies = exportContainer.querySelectorAll('.ant-card-body')
    cardBodies.forEach((body) => {
      const bodyEl = body as HTMLElement
      bodyEl.style.setProperty('background-color', '#ffffff')
      bodyEl.style.setProperty('padding', '24px')
    })

    // 处理酒店卡片头部
    const hotelCards = exportContainer.querySelectorAll('.hotel-card')
    hotelCards.forEach((card) => {
      const head = card.querySelector('.ant-card-head') as HTMLElement
      if (head) {
        head.style.setProperty('background-color', '#1976d2')
      }
      ;(card as HTMLElement).style.setProperty('background-color', '#e3f2fd')
    })

    // 处理天气卡片
    const weatherCards = exportContainer.querySelectorAll('.weather-card')
    weatherCards.forEach((card) => {
      ;(card as HTMLElement).style.setProperty('background-color', '#e0f7fa')
    })

    // 处理预算总计
    const budgetTotal = exportContainer.querySelector('.budget-total')
    if (budgetTotal) {
      const el = budgetTotal as HTMLElement
      el.style.setProperty('background-color', '#0ea5e9')
      el.style.setProperty('color', '#ffffff')
      el.style.setProperty('padding', '20px')
      el.style.setProperty('border-radius', '12px')
      el.style.setProperty('margin-bottom', '20px')
    }

    // 处理预算项
    const budgetItems = exportContainer.querySelectorAll('.budget-item')
    budgetItems.forEach((item) => {
      const el = item as HTMLElement
      el.style.setProperty('background-color', '#f5f7fa')
      el.style.setProperty('padding', '16px')
      el.style.setProperty('border-radius', '8px')
      el.style.setProperty('margin-bottom', '12px')
    })

    // 添加到body(隐藏)
    exportContainer.style.position = 'absolute'
    exportContainer.style.left = '-9999px'
    document.body.appendChild(exportContainer)

    const canvas = await html2canvas(exportContainer, {
      backgroundColor: '#f5f7fa',
      scale: 2,
      logging: false,
      useCORS: true,
      allowTaint: true
    })

    // 移除容器
    document.body.removeChild(exportContainer)

    // 转换为图片并下载
    const link = document.createElement('a')
    link.download = `旅行计划_${tripPlan.value?.city}_${new Date().getTime()}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()

    message.success({ content: '图片导出成功!', key: 'export' })
  } catch (error: any) {
    console.error('导出图片失败:', error)
    message.error({ content: `导出图片失败: ${error.message}`, key: 'export' })
  }
}

// 导出为PDF
const exportAsPDF = async () => {
  try {
    message.loading({ content: '正在生成PDF...', key: 'export', duration: 0 })

    const element = document.querySelector('.main-content') as HTMLElement
    if (!element) {
      throw new Error('未找到内容元素')
    }

    // 创建一个独立的容器
    const exportContainer = document.createElement('div')
    exportContainer.style.width = element.offsetWidth + 'px'
    exportContainer.style.backgroundColor = '#f5f7fa'
    exportContainer.style.padding = '20px'

    // 复制所有内容
    exportContainer.innerHTML = element.innerHTML

    // 处理地图截图
    const mapContainer = document.getElementById('amap-container')
    if (mapContainer && map) {
      const mapCanvas = mapContainer.querySelector('canvas')
      if (mapCanvas) {
        const mapSnapshot = mapCanvas.toDataURL('image/png')
        const exportMapContainer = exportContainer.querySelector('#amap-container')
        if (exportMapContainer) {
          exportMapContainer.innerHTML = `<img src="${mapSnapshot}" style="width:100%;height:100%;object-fit:cover;" />`
        }
      }
    }

    // 移除所有ant-card类,替换为纯div
    const cards = exportContainer.querySelectorAll('.ant-card')
    cards.forEach((card) => {
      const cardEl = card as HTMLElement
      try {
        cardEl.className = ''
        cardEl.style.setProperty('background-color', '#ffffff')
        cardEl.style.setProperty('border-radius', '12px')
        cardEl.style.setProperty('box-shadow', '0 4px 12px rgba(0, 0, 0, 0.1)')
        cardEl.style.setProperty('margin-bottom', '20px')
        cardEl.style.setProperty('overflow', 'hidden')
      } catch (err) {
        console.error('设置卡片样式失败:', err)
      }
    })

    // 处理卡片头部
    const cardHeads = exportContainer.querySelectorAll('.ant-card-head')
    cardHeads.forEach((head) => {
      const headEl = head as HTMLElement
      try {
        headEl.style.setProperty('background-color', '#0ea5e9')
        headEl.style.setProperty('color', '#ffffff')
        headEl.style.setProperty('padding', '16px 24px')
        headEl.style.setProperty('font-size', '18px')
        headEl.style.setProperty('font-weight', '600')
      } catch (err) {
        console.error('设置卡片头部样式失败:', err)
      }
    })

    // 处理卡片内容
    const cardBodies = exportContainer.querySelectorAll('.ant-card-body')
    cardBodies.forEach((body) => {
      const bodyEl = body as HTMLElement
      bodyEl.style.setProperty('background-color', '#ffffff')
      bodyEl.style.setProperty('padding', '24px')
    })

    // 处理酒店卡片头部
    const hotelCards = exportContainer.querySelectorAll('.hotel-card')
    hotelCards.forEach((card) => {
      const head = card.querySelector('.ant-card-head') as HTMLElement
      if (head) {
        head.style.setProperty('background-color', '#1976d2')
      }
      ;(card as HTMLElement).style.setProperty('background-color', '#e3f2fd')
    })

    // 处理天气卡片
    const weatherCards = exportContainer.querySelectorAll('.weather-card')
    weatherCards.forEach((card) => {
      ;(card as HTMLElement).style.setProperty('background-color', '#e0f7fa')
    })

    // 处理预算总计
    const budgetTotal = exportContainer.querySelector('.budget-total')
    if (budgetTotal) {
      const el = budgetTotal as HTMLElement
      el.style.setProperty('background-color', '#0ea5e9')
      el.style.setProperty('color', '#ffffff')
      el.style.setProperty('padding', '20px')
      el.style.setProperty('border-radius', '12px')
      el.style.setProperty('margin-bottom', '20px')
    }

    // 处理预算项
    const budgetItems = exportContainer.querySelectorAll('.budget-item')
    budgetItems.forEach((item) => {
      const el = item as HTMLElement
      el.style.setProperty('background-color', '#f5f7fa')
      el.style.setProperty('padding', '16px')
      el.style.setProperty('border-radius', '8px')
      el.style.setProperty('margin-bottom', '12px')
    })

    // 添加到body(隐藏)
    exportContainer.style.position = 'absolute'
    exportContainer.style.left = '-9999px'
    document.body.appendChild(exportContainer)

    const canvas = await html2canvas(exportContainer, {
      backgroundColor: '#f5f7fa',
      scale: 2,
      logging: false,
      useCORS: true,
      allowTaint: true
    })

    // 移除容器
    document.body.removeChild(exportContainer)

    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    })

    const imgWidth = 210 // A4宽度(mm)
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    // 如果内容高度超过一页,分页处理
    let heightLeft = imgHeight
    let position = 0

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= 297 // A4高度

    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= 297
    }

    pdf.save(`旅行计划_${tripPlan.value?.city}_${new Date().getTime()}.pdf`)

    message.success({ content: 'PDF导出成功!', key: 'export' })
  } catch (error: any) {
    console.error('导出PDF失败:', error)
    message.error({ content: `导出PDF失败: ${error.message}`, key: 'export' })
  }
}

// 截取地图图片
const captureMapImage = async () => {
  if (!map) return

  try {
    // 获取地图容器
    const mapContainer = document.getElementById('amap-container')
    if (!mapContainer) return

    // 使用高德地图的截图功能
    const mapCanvas = mapContainer.querySelector('canvas')
    if (mapCanvas) {
      // 创建一个img元素替换地图容器
      const img = document.createElement('img')
      img.src = mapCanvas.toDataURL('image/png')
      img.style.width = '100%'
      img.style.height = '500px'
      img.style.objectFit = 'cover'
      img.id = 'map-snapshot'

      // 隐藏原地图,显示截图
      mapContainer.style.display = 'none'
      mapContainer.parentElement?.appendChild(img)
    }
  } catch (error) {
    console.error('截取地图失败:', error)
  }
}

// 恢复地图
const restoreMap = () => {
  const mapContainer = document.getElementById('amap-container')
  const snapshot = document.getElementById('map-snapshot')

  if (mapContainer) {
    mapContainer.style.display = 'block'
  }

  if (snapshot) {
    snapshot.remove()
  }
}

// 切换地图显示的日期
const setActiveMapDay = (day: MapDayFilter) => {
  activeMapDay.value = day
  refreshMapOverlays()
}

// 重新绘制地图覆盖物
const refreshMapOverlays = () => {
  if (!map || !AMapInstance || !tripPlan.value) return
  map.clearMap()
  addAttractionMarkers(AMapInstance)
}

// 初始化地图
const initMap = async () => {
  try {
    const AMap = await AMapLoader.load({
      key: import.meta.env.VITE_AMAP_WEB_JS_KEY,
      version: '2.0',
      plugins: ['AMap.Marker', 'AMap.Polyline', 'AMap.InfoWindow']
    })

    AMapInstance = AMap

    if (map) {
      map.destroy()
      map = null
    }

    map = new AMap.Map('amap-container', {
      zoom: 12,
      center: [116.397128, 39.916527],
      viewMode: '3D',
      mapStyle: 'amap://styles/normal'
    })

    addAttractionMarkers(AMap)
    message.success('地图加载成功')
  } catch (error) {
    console.error('地图加载失败:', error)
    message.error('地图加载失败')
  }
}

// 根据当前地图筛选条件收集景点
const getVisibleAttractions = () => {
  if (!tripPlan.value) return []

  const attractions: any[] = []

  tripPlan.value.days.forEach((day, dayIndex) => {
    if (activeMapDay.value !== 'all' && day.day_index !== activeMapDay.value) {
      return
    }

    day.attractions.forEach((attraction, attrIndex) => {
      if (attraction.location && attraction.location.longitude && attraction.location.latitude) {
        attractions.push({
          ...attraction,
          dayIndex,
          attrIndex,
          dayNumber: day.day_index + 1,
          orderNumber: attrIndex + 1
        })
      }
    })
  })

  return attractions
}

// 添加景点标记
const addAttractionMarkers = (AMap: any) => {
  if (!tripPlan.value || !map) return

  const markers: any[] = []
  const visibleAttractions = getVisibleAttractions()

  visibleAttractions.forEach((attraction) => {
    const markerLabel = activeMapDay.value === 'all'
      ? `${attraction.dayNumber}-${attraction.orderNumber}`
      : `${attraction.orderNumber}`

    const marker = new AMap.Marker({
      position: [attraction.location.longitude, attraction.location.latitude],
      title: attraction.name,
      label: {
        content: `<div class="map-marker-label">${markerLabel}</div>`,
        offset: new AMap.Pixel(0, -36)
      }
    })

    const infoWindow = new AMap.InfoWindow({
      content: `
        <div class="map-info-window">
          <div class="map-info-title">${attraction.name}</div>
          <div class="map-info-row"><strong>地址：</strong>${attraction.address || '暂无地址'}</div>
          <div class="map-info-row"><strong>游览时长：</strong>${attraction.visit_duration || 120} 分钟</div>
          <div class="map-info-row"><strong>行程：</strong>第${attraction.dayNumber}天 · 第${attraction.orderNumber}站</div>
          <div class="map-info-desc">${attraction.description || ''}</div>
        </div>
      `,
      offset: new AMap.Pixel(0, -32)
    })

    marker.on('click', () => {
      infoWindow.open(map, marker.getPosition())
    })

    markers.push(marker)
  })

  if (markers.length > 0) {
    map.add(markers)
    map.setFitView(markers, false, [80, 80, 80, 80])
  }

  drawRoutes(AMap, visibleAttractions)
}

// 绘制路线：按天分组绘制，不把不同天强行连成一条线
const drawRoutes = (AMap: any, attractions: any[]) => {
  if (!map || attractions.length < 2) return

  const dayGroups: Record<number, any[]> = {}

  attractions.forEach(attr => {
    if (!dayGroups[attr.dayIndex]) {
      dayGroups[attr.dayIndex] = []
    }
    dayGroups[attr.dayIndex].push(attr)
  })

  Object.values(dayGroups).forEach((dayAttractions: any[]) => {
    if (dayAttractions.length < 2) return

    const sortedAttractions = [...dayAttractions].sort((a, b) => a.attrIndex - b.attrIndex)

    const path = sortedAttractions.map((attr: any) => [
      attr.location.longitude,
      attr.location.latitude
    ])

    const polyline = new AMap.Polyline({
      path,
      strokeColor: '#0ea5e9',
      strokeWeight: 6,
      strokeOpacity: 0.9,
      strokeStyle: 'solid',
      lineJoin: 'round',
      lineCap: 'round',
      showDir: true
    })

    map.add(polyline)
  })
}
</script>

<style scoped>
.result-container {
  min-height: 100vh;
  padding: 32px 24px 56px;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 8% 10%, rgba(14, 165, 233, 0.16), transparent 28%),
    radial-gradient(circle at 90% 4%, rgba(20, 184, 166, 0.14), transparent 24%),
    linear-gradient(180deg, #e8f8ff 0%, #effdf8 46%, #ffffff 100%);
}

.result-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.result-orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(8px);
  opacity: 0.72;
}

.orb-a {
  width: 360px;
  height: 360px;
  top: -130px;
  left: -120px;
  background: rgba(14, 165, 233, 0.16);
}

.orb-b {
  width: 300px;
  height: 300px;
  right: -110px;
  top: 260px;
  background: rgba(20, 184, 166, 0.14);
}

.result-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(14, 165, 233, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(14, 165, 233, 0.05) 1px, transparent 1px);
  background-size: 38px 38px;
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.52), transparent 62%);
}

.page-header {
  position: relative;
  z-index: 1;
  max-width: 1440px;
  margin: 0 auto 26px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  animation: fadeInDown 0.45s ease-out;
}

.back-button,
.soft-action-button,
.primary-action-button {
  border-radius: 999px;
  font-weight: 850;
  border: none;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
}

.back-button,
.soft-action-button {
  background: rgba(255, 255, 255, 0.9);
  color: #334155;
}

.primary-action-button {
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
}

.content-wrapper {
  position: relative;
  z-index: 1;
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  gap: 24px;
}

.side-nav {
  width: 240px;
  flex-shrink: 0;
}

.side-nav :deep(.ant-menu) {
  border-radius: 22px;
  padding: 12px 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
}

.side-nav :deep(.ant-menu-item) {
  height: 46px;
  margin: 4px 6px;
  border-radius: 14px;
  color: #475569;
  font-weight: 700;
  transition: all 0.2s ease;
}

.side-nav :deep(.ant-menu-item:hover) {
  background: #f1f5f9;
  color: #0ea5e9;
}

.side-nav :deep(.ant-menu-item-selected) {
  background: linear-gradient(135deg, #0ea5e9, #14b8a6) !important;
  color: #ffffff !important;
  box-shadow: 0 10px 22px rgba(14, 165, 233, 0.25);
}

.side-nav :deep(.ant-menu-submenu-title) {
  border-radius: 14px;
  font-weight: 700;
  color: #475569;
}

.main-content {
  flex: 1;
  min-width: 0;
}

.result-hero-card {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(360px, 0.75fr);
  gap: 24px;
  margin-bottom: 22px;
  padding: 30px;
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(226, 232, 240, 0.95);
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(18px);
  animation: fadeInUp 0.5s ease-out;
}

.hero-kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  margin-bottom: 16px;
  border-radius: 999px;
  color: #0891b2;
  font-size: 13px;
  font-weight: 900;
  background: rgba(236, 254, 255, 0.9);
  border: 1px solid rgba(14, 165, 233, 0.18);
}

.kicker-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  box-shadow: 0 0 14px rgba(14, 165, 233, 0.7);
}

.result-hero-left h1 {
  margin: 0;
  color: #0f172a;
  font-size: 42px;
  line-height: 1.16;
  font-weight: 950;
  letter-spacing: -1px;
}

.result-hero-left p {
  max-width: 760px;
  margin: 14px 0 0;
  color: #64748b;
  font-size: 16px;
  line-height: 1.85;
}

.fun-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 22px;
}

.fun-button {
  height: 42px;
  padding: 0 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 1px solid rgba(226, 232, 240, 0.95);
  border-radius: 999px;
  color: #334155;
  background: rgba(255, 255, 255, 0.88);
  font-size: 14px;
  font-weight: 900;
  cursor: pointer;
  transition: all 0.22s ease;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.045);
}

.fun-button:hover {
  transform: translateY(-2px);
  color: #0891b2;
  border-color: rgba(14, 165, 233, 0.26);
  box-shadow: 0 16px 36px rgba(14, 165, 233, 0.12);
}

.fun-button.primary {
  color: #ffffff;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  border-color: transparent;
  box-shadow: 0 16px 34px rgba(20, 184, 166, 0.26);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.summary-tile {
  min-height: 118px;
  padding: 18px;
  border-radius: 22px;
  background: linear-gradient(135deg, rgba(236, 254, 255, 0.9), rgba(240, 253, 250, 0.88));
  border: 1px solid rgba(14, 165, 233, 0.14);
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.055);
}

.summary-tile span {
  display: block;
  font-size: 24px;
  margin-bottom: 8px;
}

.summary-tile strong {
  display: block;
  color: #0f172a;
  font-size: 28px;
  font-weight: 950;
}

.summary-tile p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 13px;
  font-weight: 800;
}

.top-info-section {
  display: flex;
  gap: 22px;
  margin-bottom: 22px;
}

.left-info {
  flex: 0 0 410px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.right-map {
  flex: 1;
  min-width: 0;
}

:deep(.ant-card) {
  border-radius: 24px;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.08);
  margin-bottom: 20px;
  overflow: hidden;
  background: #ffffff;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: fadeInUp 0.5s ease-out;
}

:deep(.ant-card:hover) {
  transform: translateY(-2px);
  box-shadow: 0 22px 46px rgba(15, 23, 42, 0.12);
}

:deep(.ant-card-head) {
  min-height: 58px;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6) !important;
  color: white !important;
  border-bottom: none;
}

:deep(.ant-card-head-title) {
  color: white !important;
  font-size: 18px;
  font-weight: 900;
}

:deep(.ant-card-body) {
  padding: 22px;
}

.overview-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.info-item,
.day-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px;
  border-radius: 18px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.info-label,
.info-row .label {
  font-size: 14px;
  font-weight: 900;
  color: #334155;
}

.info-value,
.info-row .value {
  font-size: 15px;
  color: #475569;
  line-height: 1.7;
}

.budget-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  margin-bottom: 16px;
}

.budget-item {
  text-align: center;
  padding: 16px 12px;
  background: #f8fafc;
  border-radius: 18px;
  border: 1px solid #e2e8f0;
}

.budget-label {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
  font-weight: 700;
}

.budget-value {
  font-size: 22px;
  font-weight: 900;
  color: #0ea5e9;
}

.budget-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  border-radius: 18px;
  color: white;
  box-shadow: 0 14px 28px rgba(14, 165, 233, 0.22);
}

.total-label {
  font-size: 16px;
  font-weight: 900;
}

.total-value {
  font-size: 30px;
  font-weight: 900;
}

.map-card {
  height: 100%;
  min-height: 620px;
}

.map-card :deep(.ant-card-body) {
  height: calc(100% - 58px);
  min-height: 560px;
  padding: 14px;
  display: flex;
  flex-direction: column;
}

.map-toolbar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  padding: 2px 2px 12px;
  flex-shrink: 0;
}

.map-day-button {
  border: none;
  padding: 8px 16px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-weight: 900;
  cursor: pointer;
  transition: all 0.2s ease;
}

.map-day-button:hover {
  background: #bae6fd;
  color: #0f766e;
}

.map-day-button.active {
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  color: #ffffff;
  box-shadow: 0 10px 22px rgba(14, 165, 233, 0.25);
}

#amap-container {
  width: 100%;
  flex: 1;
  min-height: 500px;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid #dbeafe;
  background: #eaf5ff;
}

.days-card {
  margin-top: 22px;
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.day-title {
  font-size: 18px;
  font-weight: 900;
  color: #0f172a;
}

.day-date {
  font-size: 14px;
  color: #64748b;
  font-weight: 700;
}

.info-row {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  min-width: 110px;
}

:deep(.ant-collapse) {
  border: none;
  background: transparent;
}

:deep(.ant-collapse-item) {
  margin-bottom: 16px;
  border: 1px solid #e2e8f0 !important;
  border-radius: 20px !important;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
}

:deep(.ant-collapse-header) {
  background: #f8fafc;
  padding: 18px 22px !important;
  font-weight: 900;
}

:deep(.ant-collapse-content) {
  border-top: 1px solid #e2e8f0;
}

:deep(.ant-collapse-content-box) {
  padding: 22px;
}

.attraction-card {
  border-radius: 22px !important;
  overflow: hidden;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08) !important;
}

.attraction-card :deep(.ant-card-head) {
  background: #ffffff !important;
  border-bottom: 1px solid #e2e8f0;
}

.attraction-card :deep(.ant-card-head-title) {
  color: #0f172a !important;
  font-size: 17px;
  font-weight: 900;
}

.attraction-card :deep(.ant-card-body) {
  padding: 16px;
}

.attraction-image-wrapper {
  position: relative;
  margin-bottom: 14px;
  border-radius: 18px;
  overflow: hidden;
  background: linear-gradient(135deg, #dbeafe, #ccfbf1);
}

.attraction-image {
  width: 100%;
  height: 210px;
  object-fit: cover;
  display: block;
  transition: transform 0.35s ease;
}

.attraction-image-wrapper:hover .attraction-image {
  transform: scale(1.05);
}

.attraction-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  border: 3px solid #ffffff;
  box-shadow: 0 8px 18px rgba(14, 165, 233, 0.35);
}

.badge-number {
  font-size: 18px;
}

.price-tag {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(245, 158, 11, 0.95);
  color: white;
  padding: 5px 13px;
  border-radius: 999px;
  font-weight: 900;
  font-size: 14px;
  box-shadow: 0 8px 18px rgba(245, 158, 11, 0.28);
}

:deep(.ant-list-item) {
  transition: all 0.25s ease;
}

:deep(.ant-list-item:hover) {
  transform: translateY(-3px);
}

.hotel-card {
  background: #f8fafc !important;
  border: 1px solid #dbeafe !important;
}

.hotel-card :deep(.ant-card-head) {
  background: linear-gradient(135deg, #0ea5e9, #14b8a6) !important;
}

.hotel-title {
  color: white !important;
  font-weight: 900;
}

.weather-card {
  background: linear-gradient(135deg, #ecfeff, #eff6ff);
  border: 1px solid #bfdbfe !important;
  transition: all 0.25s ease;
}

.weather-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 32px rgba(14, 165, 233, 0.15);
}

.weather-date {
  font-size: 16px;
  font-weight: 900;
  color: #0f766e;
  margin-bottom: 14px;
  text-align: center;
}

.weather-info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.weather-icon {
  font-size: 25px;
}

.weather-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 800;
}

.weather-value {
  font-size: 16px;
  font-weight: 900;
  color: #0f766e;
}

.weather-wind {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(15, 118, 110, 0.18);
  text-align: center;
  color: #0f766e;
  font-size: 14px;
  font-weight: 800;
}

:deep(.ant-divider-inner-text) {
  font-weight: 900;
  color: #334155;
}

.empty-panel {
  position: relative;
  z-index: 1;
  margin-top: 80px;
}

.back-top-button {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  color: white;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 900;
  box-shadow: 0 12px 26px rgba(14, 165, 233, 0.35);
  cursor: pointer;
  transition: all 0.25s ease;
}

.back-top-button:hover {
  transform: scale(1.08);
}

:global(.trip-card-modal .ant-modal-content) {
  border-radius: 26px;
  overflow: hidden;
  padding: 0;
  background:
    radial-gradient(circle at 12% 0%, rgba(14, 165, 233, 0.13), transparent 34%),
    linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 28px 80px rgba(15, 23, 42, 0.22);
}

:global(.trip-card-modal .ant-modal-header) {
  margin: 0;
  padding: 22px 26px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.95);
  background: transparent;
}

:global(.trip-card-modal .ant-modal-title) {
  color: #0f172a;
  font-size: 22px;
  font-weight: 950;
}

:global(.trip-card-modal .ant-modal-body) {
  padding: 24px 26px;
}

:global(.trip-card-modal .ant-modal-footer) {
  margin: 0;
  padding: 0 26px 24px;
}

:global(.trip-card-modal .ant-btn-primary) {
  border: none;
  border-radius: 999px;
  font-weight: 900;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  box-shadow: 0 12px 24px rgba(20, 184, 166, 0.24);
}

:global(.trip-modal-card) {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

:global(.trip-modal-grid) {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

:global(.trip-modal-item) {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(226, 232, 240, 0.95);
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.055);
}

:global(.trip-modal-icon) {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 44px;
  width: 44px;
  height: 44px;
  border-radius: 16px;
  font-size: 23px;
  background: linear-gradient(135deg, #ecfeff, #e7fff8);
  border: 1px solid rgba(14, 165, 233, 0.14);
}

:global(.trip-modal-main) {
  min-width: 0;
}

:global(.trip-modal-title) {
  color: #64748b;
  font-size: 12px;
  font-weight: 850;
}

:global(.trip-modal-value) {
  margin-top: 3px;
  color: #0f172a;
  font-size: 17px;
  font-weight: 950;
  line-height: 1.4;
}

:global(.trip-modal-desc) {
  margin-top: 5px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.55;
  font-weight: 650;
}

:global(.trip-modal-footer) {
  padding: 14px 16px;
  border-radius: 18px;
  color: #0f766e;
  font-size: 14px;
  line-height: 1.7;
  font-weight: 750;
  background: linear-gradient(135deg, rgba(236, 254, 255, 0.92), rgba(240, 253, 250, 0.92));
  border: 1px solid rgba(20, 184, 166, 0.16);
}

@media (max-width: 640px) {
  :global(.trip-modal-grid) {
    grid-template-columns: 1fr;
  }
}

:deep(.map-marker-label) {
  min-width: 36px;
  height: 36px;
  padding: 0 8px;
  border-radius: 999px;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  color: #ffffff;
  border: 3px solid #ffffff;
  box-shadow: 0 8px 20px rgba(14, 165, 233, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 900;
  line-height: 1;
}

:deep(.map-info-window) {
  width: 260px;
  padding: 4px;
  color: #1e293b;
}

:deep(.map-info-title) {
  font-size: 16px;
  font-weight: 900;
  color: #0f172a;
  margin-bottom: 8px;
}

:deep(.map-info-row) {
  font-size: 13px;
  line-height: 1.7;
  color: #475569;
}

:deep(.map-info-desc) {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
  font-size: 13px;
  line-height: 1.6;
  color: #64748b;
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-16px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 1200px) {
  .result-hero-card {
    grid-template-columns: 1fr;
  }

  .summary-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 1100px) {
  .content-wrapper {
    flex-direction: column;
  }

  .side-nav {
    display: none;
  }

  .top-info-section {
    flex-direction: column;
  }

  .left-info {
    flex: auto;
  }

  .map-card {
    min-height: 560px;
  }
}

@media (max-width: 768px) {
  .result-container {
    padding: 20px 10px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .result-hero-card {
    padding: 22px;
    border-radius: 24px;
  }

  .result-hero-left h1 {
    font-size: 32px;
  }

  .summary-grid,
  .budget-grid {
    grid-template-columns: 1fr;
  }

  .fun-button {
    flex: 1 1 100%;
  }

  :deep(.ant-list-grid .ant-col) {
    max-width: 100% !important;
    flex: 0 0 100% !important;
  }
}
</style>
