<template>
  <div class="home-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration" aria-hidden="true">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
      <div class="grid-mask"></div>
      <div class="route-dash dash-1"></div>
      <div class="route-dash dash-2"></div>
    </div>

    <!-- Hero 区域 -->
    <section class="home-hero">
      <div class="hero-left">
<h1 class="page-title">AI 智能旅行规划助手</h1>

        <p class="page-subtitle">
          基于多 Agent 协作、高德地图 MCP 工具、天气查询与路线优化，
          为每一次出行生成更顺路、更清晰、更个性化的旅行计划。
        </p>

        <div class="hero-actions">
          <button class="primary-hero-btn" type="button" @click="scrollToForm">
            <span>🚀</span>
            开始填写需求
          </button>
          <button class="ghost-hero-btn" type="button" @click="randomInspiration">
            <span>🎲</span>
            随机旅行灵感
          </button>
        </div>

        <div class="hero-tags">
          <span>多 Agent 协作</span>
          <span>高德地图工具</span>
          <span>路线顺路优化</span>
          <span>天气辅助决策</span>
        </div>
      </div>

      <div class="hero-panel">
        <div class="plane-card">
          <div class="plane-icon">✈️</div>
          <div>
            <p>Smart Route</p>
            <strong>更顺路的每日行程</strong>
          </div>
        </div>

        <div class="agent-console">
          <div class="console-header">
            <span></span>
            <span></span>
            <span></span>
            <strong>Agent 协作中</strong>
          </div>
          <div class="console-line active">Attraction Agent → 搜索景点</div>
          <div class="console-line">Weather Tool → 检查天气</div>
          <div class="console-line">Route Tool → 优化顺路程度</div>
        </div>

        <div class="mini-map">
          <svg class="route-svg" viewBox="0 0 520 180" aria-hidden="true">
            <defs>
              <linearGradient id="routeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#0ea5e9" />
                <stop offset="22%" stop-color="#06b6d4" />
                <stop offset="44%" stop-color="#14b8a6" />
                <stop offset="66%" stop-color="#22c55e" />
                <stop offset="100%" stop-color="#84cc16" />
              </linearGradient>

              <linearGradient id="pointGradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#38bdf8" />
                <stop offset="100%" stop-color="#0284c7" />
              </linearGradient>
              <linearGradient id="pointGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#22d3ee" />
                <stop offset="100%" stop-color="#0891b2" />
              </linearGradient>
              <linearGradient id="pointGradient3" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#2dd4bf" />
                <stop offset="100%" stop-color="#0f766e" />
              </linearGradient>
              <linearGradient id="pointGradient4" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#34d399" />
                <stop offset="100%" stop-color="#059669" />
              </linearGradient>
              <linearGradient id="pointGradient5" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#4ade80" />
                <stop offset="100%" stop-color="#16a34a" />
              </linearGradient>
              <linearGradient id="pointGradient6" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#a3e635" />
                <stop offset="100%" stop-color="#65a30d" />
              </linearGradient>

              <filter id="routeShadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="8" stdDeviation="7" flood-color="#0ea5e9" flood-opacity="0.22" />
              </filter>
            </defs>

            <path
              class="route-path route-path-shadow"
              d="M54 130 C92 104 112 96 140 92 C180 86 194 118 230 112 C270 106 280 78 312 70 C354 60 362 94 392 96 C424 100 440 70 466 58"
            />
            <path
              class="route-path"
              d="M54 130 C92 104 112 96 140 92 C180 86 194 118 230 112 C270 106 280 78 312 70 C354 60 362 94 392 96 C424 100 440 70 466 58"
            />

            <circle class="route-ring" cx="54" cy="130" r="24" />
            <circle class="route-dot" cx="54" cy="130" r="19" fill="url(#pointGradient1)" />
            <text x="54" y="136" text-anchor="middle">1</text>

            <circle class="route-ring" cx="140" cy="92" r="24" />
            <circle class="route-dot" cx="140" cy="92" r="19" fill="url(#pointGradient2)" />
            <text x="140" y="98" text-anchor="middle">2</text>

            <circle class="route-ring" cx="230" cy="112" r="24" />
            <circle class="route-dot" cx="230" cy="112" r="19" fill="url(#pointGradient3)" />
            <text x="230" y="118" text-anchor="middle">3</text>

            <circle class="route-ring" cx="312" cy="70" r="24" />
            <circle class="route-dot" cx="312" cy="70" r="19" fill="url(#pointGradient4)" />
            <text x="312" y="76" text-anchor="middle">4</text>

            <circle class="route-ring" cx="392" cy="96" r="24" />
            <circle class="route-dot" cx="392" cy="96" r="19" fill="url(#pointGradient5)" />
            <text x="392" y="102" text-anchor="middle">5</text>

            <circle class="route-ring" cx="466" cy="58" r="24" />
            <circle class="route-dot" cx="466" cy="58" r="19" fill="url(#pointGradient6)" />
            <text x="466" y="64" text-anchor="middle">6</text>
          </svg>
        </div>

        <div class="hero-stats">
          <div>
            <strong>6+</strong>
            <span>工具能力</span>
          </div>
          <div>
            <strong>5 步</strong>
            <span>规划流程</span>
          </div>
          <div>
            <strong>AI</strong>
            <span>个性化生成</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 主体内容 -->
    <section class="content-shell" ref="formAnchor">
      <!-- 好玩的快捷按钮 -->
      <section class="quick-playground">
        <div class="quick-header">
          <div>
            <p class="section-eyebrow">Quick Play</p>
            <h2>一键开启旅行玩法</h2>
          </div>
        </div>

        <div class="quick-grid">
          <button
            v-for="preset in presetButtons"
            :key="preset.key"
            type="button"
            class="quick-card"
            :class="{ active: activePreset === preset.key }"
            @click="applyPreset(preset.key)"
          >
            <span class="quick-icon">{{ preset.icon }}</span>
            <span class="quick-content">
              <strong>{{ preset.title }}</strong>
              <em>{{ preset.desc }}</em>
            </span>
          </button>
        </div>

        <div class="city-row">
          <span class="city-label">热门目的地：</span>
          <button
            v-for="city in quickCities"
            :key="city"
            type="button"
            class="city-chip"
            :class="{ active: formData.city === city }"
            @click="setCity(city)"
          >
            {{ city }}
          </button>
        </div>
      </section>

      <a-card class="form-card" :bordered="false">
        <a-form
          :model="formData"
          layout="vertical"
          @finish="handleSubmit"
        >
          <!-- 第一步:目的地和日期 -->
          <div class="form-section">
            <div class="section-header">
              <div class="section-title-group">
                <span class="section-icon">📍</span>
                <div>
                  <span class="section-title">目的地与日期</span>
                  <p>告诉系统你要去哪里，以及什么时候出发。</p>
                </div>
              </div>
              <span class="section-index">01</span>
            </div>

            <a-row :gutter="[24, 16]">
              <a-col :xs="24" :sm="24" :md="12" :lg="8">
                <a-form-item name="city" :rules="[{ required: true, message: '请输入目的地城市' }]">
                  <template #label>
                    <span class="form-label">目的地城市</span>
                  </template>
                  <a-input
                    v-model:value="formData.city"
                    placeholder="例如：北京 / 上海 / 南京"
                    size="large"
                    class="custom-input"
                  >
                    <template #prefix>
                      <span class="input-prefix">🏙️</span>
                    </template>
                  </a-input>
                </a-form-item>
              </a-col>

              <a-col :xs="24" :sm="12" :md="6" :lg="6">
                <a-form-item name="start_date" :rules="[{ required: true, message: '请选择开始日期' }]">
                  <template #label>
                    <span class="form-label">开始日期</span>
                  </template>
                  <a-date-picker
                    v-model:value="formData.start_date"
                    style="width: 100%"
                    size="large"
                    class="custom-date-picker"
                    placeholder="选择日期"
                  />
                </a-form-item>
              </a-col>

              <a-col :xs="24" :sm="12" :md="6" :lg="6">
                <a-form-item name="end_date" :rules="[{ required: true, message: '请选择结束日期' }]">
                  <template #label>
                    <span class="form-label">结束日期</span>
                  </template>
                  <a-date-picker
                    v-model:value="formData.end_date"
                    style="width: 100%"
                    size="large"
                    class="custom-date-picker"
                    placeholder="选择日期"
                  />
                </a-form-item>
              </a-col>

              <a-col :xs="24" :sm="24" :md="24" :lg="4">
                <a-form-item>
                  <template #label>
                    <span class="form-label">旅行天数</span>
                  </template>
                  <div class="days-display-compact">
                    <span class="days-value">{{ formData.travel_days }}</span>
                    <span class="days-unit">天</span>
                  </div>
                </a-form-item>
              </a-col>
            </a-row>
          </div>

          <!-- 第二步:偏好设置 -->
          <div class="form-section">
            <div class="section-header">
              <div class="section-title-group">
                <span class="section-icon">⚙️</span>
                <div>
                  <span class="section-title">偏好设置</span>
                  <p>设置交通、住宿和旅行兴趣，让行程更贴近你的习惯。</p>
                </div>
              </div>
              <span class="section-index">02</span>
            </div>

            <a-row :gutter="[24, 16]">
              <a-col :xs="24" :md="8">
                <a-form-item name="transportation">
                  <template #label>
                    <span class="form-label">交通方式</span>
                  </template>
                  <a-select v-model:value="formData.transportation" size="large" class="custom-select">
                    <a-select-option value="公共交通">🚇 公共交通</a-select-option>
                    <a-select-option value="自驾">🚗 自驾</a-select-option>
                    <a-select-option value="步行">🚶 步行</a-select-option>
                    <a-select-option value="混合">🔀 混合</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>

              <a-col :xs="24" :md="8">
                <a-form-item name="accommodation">
                  <template #label>
                    <span class="form-label">住宿偏好</span>
                  </template>
                  <a-select v-model:value="formData.accommodation" size="large" class="custom-select">
                    <a-select-option value="经济型酒店">💰 经济型酒店</a-select-option>
                    <a-select-option value="舒适型酒店">🏨 舒适型酒店</a-select-option>
                    <a-select-option value="豪华酒店">⭐ 豪华酒店</a-select-option>
                    <a-select-option value="民宿">🏡 民宿</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>

              <a-col :xs="24" :md="8">
                <a-form-item name="preferences">
                  <template #label>
                    <span class="form-label">旅行偏好</span>
                  </template>
                  <a-checkbox-group v-model:value="formData.preferences" class="custom-checkbox-group">
                    <a-checkbox value="历史文化" class="preference-tag">🏛️ 历史文化</a-checkbox>
                    <a-checkbox value="自然风光" class="preference-tag">🏞️ 自然风光</a-checkbox>
                    <a-checkbox value="美食" class="preference-tag">🍜 美食</a-checkbox>
                    <a-checkbox value="购物" class="preference-tag">🛍️ 购物</a-checkbox>
                    <a-checkbox value="艺术" class="preference-tag">🎨 艺术</a-checkbox>
                    <a-checkbox value="休闲" class="preference-tag">☕ 休闲</a-checkbox>
                  </a-checkbox-group>
                </a-form-item>
              </a-col>
            </a-row>
          </div>

          <!-- 第三步:额外要求 -->
          <div class="form-section">
            <div class="section-header">
              <div class="section-title-group">
                <span class="section-icon">💬</span>
                <div>
                  <span class="section-title">额外要求</span>
                  <p>补充你的特殊需求，系统会在生成行程时一并考虑。</p>
                </div>
              </div>
              <span class="section-index">03</span>
            </div>

            <a-form-item name="free_text_input">
              <a-textarea
                v-model:value="formData.free_text_input"
                placeholder="例如：想去看升旗、不要太赶、需要无障碍设施、对海鲜过敏、第一天希望离酒店近一点……"
                :rows="4"
                size="large"
                class="custom-textarea"
              />
            </a-form-item>
          </div>

          <!-- 提交按钮 -->
          <a-form-item>
            <a-button
              type="primary"
              html-type="submit"
              :loading="loading"
              size="large"
              block
              class="submit-button"
            >
              <template v-if="!loading">
                <span class="button-icon">🚀</span>
                <span>开始规划我的旅行</span>
              </template>
              <template v-else>
                <span>正在生成中...</span>
              </template>
            </a-button>
          </a-form-item>

          <!-- 加载进度条 -->
          <a-form-item v-if="loading">
            <div class="loading-container">
              <a-progress
                :percent="loadingProgress"
                status="active"
                :stroke-color="{
                  '0%': '#0ea5e9',
                  '100%': '#14b8a6',
                }"
                :stroke-width="10"
              />
              <p class="loading-status">
                {{ loadingStatus }}
              </p>
            </div>
          </a-form-item>
        </a-form>
      </a-card>

      <!-- 后端工具能力展示 -->
      <section class="tool-section">
        <div class="section-heading">
          <div>
            <p class="section-eyebrow">Backend Capabilities</p>
            <h2>系统背后的智能工具链</h2>
          </div>
          <p class="section-desc">
            后端不是简单拼接文本，而是通过多个 Agent 和地图工具协同完成旅行规划。
          </p>
        </div>

        <div class="tool-grid">
          <div
            v-for="tool in toolCards"
            :key="tool.title"
            class="tool-card"
          >
            <div class="tool-icon">{{ tool.icon }}</div>
            <div class="tool-info">
              <div class="tool-title-row">
                <h3>{{ tool.title }}</h3>
                <span>{{ tool.tag }}</span>
              </div>
              <p>{{ tool.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 智能规划流程 -->
      <section class="process-section">
        <div class="process-card">
          <div class="process-title">
            <span>⚙️</span>
            <div>
              <h2>智能规划流程</h2>
              <p>从用户输入到最终行程，后端会逐步完成搜索、分析、优化与生成。</p>
            </div>
          </div>

          <div class="process-steps">
            <div
              v-for="(step, index) in processSteps"
              :key="step"
              class="process-step"
            >
              <div class="step-index">{{ index + 1 }}</div>
              <span>{{ step }}</span>
            </div>
          </div>
        </div>
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { generateTripPlan } from '@/services/api'
import type { TripFormData } from '@/types'
import type { Dayjs } from 'dayjs'

const router = useRouter()
const loading = ref(false)
const loadingProgress = ref(0)
const loadingStatus = ref('')
const formAnchor = ref<HTMLElement | null>(null)
const activePreset = ref('')

const toolCards = [
  {
    icon: '🧭',
    title: '景点搜索 Agent',
    desc: '根据城市、偏好和关键词，调用高德地图搜索相关景点。',
    tag: 'Attraction Agent'
  },
  {
    icon: '🍜',
    title: '美食推荐 Agent',
    desc: '结合目的地和旅行偏好，推荐适合的餐饮与特色美食。',
    tag: 'Food Agent'
  },
  {
    icon: '🌦️',
    title: '天气查询工具',
    desc: '根据出行日期与城市，查询天气并辅助行程安排。',
    tag: 'Weather Tool'
  },
  {
    icon: '🚗',
    title: '路线规划工具',
    desc: '基于景点位置计算路线距离，让每天行程更顺路。',
    tag: 'Route Tool'
  },
  {
    icon: '🧠',
    title: '多 Agent 协作',
    desc: '多个智能体分别负责搜索、分析、规划和整合结果。',
    tag: 'Multi-Agent'
  },
  {
    icon: '📍',
    title: '行程顺路优化',
    desc: '按照区域聚类和距离排序，减少景点之间的无效绕路。',
    tag: 'Optimization'
  }
]

const processSteps = [
  '解析旅行需求',
  '搜索景点与美食',
  '查询天气与路线',
  '优化每日顺序',
  '生成完整行程'
]

const quickCities = ['北京', '上海', '南京', '杭州', '苏州', '成都', '重庆', '厦门']

type PresetKey = 'route' | 'food' | 'weather' | 'culture' | 'relax' | 'budget'

type PresetButton = {
  key: PresetKey
  icon: string
  title: string
  desc: string
  preferences: string[]
  transportation?: string
  accommodation?: string
  freeText: string
}

const presetButtons: PresetButton[] = [
  {
    key: 'route',
    icon: '📍',
    title: '少走回头路',
    desc: '优先调用路线优化思路',
    preferences: ['休闲'],
    transportation: '公共交通',
    freeText: '请优先按照地理位置和路线顺路程度安排行程，减少折返、跨区绕路和无效通勤。'
  },
  {
    key: 'food',
    icon: '🍜',
    title: '美食优先局',
    desc: '让美食推荐更突出',
    preferences: ['美食'],
    freeText: '请把当地特色美食和餐饮地点安排进每天行程中，尽量让用餐地点靠近当天景点。'
  },
  {
    key: 'weather',
    icon: '🌦️',
    title: '天气友好模式',
    desc: '根据天气调整室内外',
    preferences: ['休闲', '艺术'],
    freeText: '请结合天气情况安排室内外活动，如果遇到雨天或高温，优先安排博物馆、展馆、商圈等室内或半室内地点。'
  },
  {
    key: 'culture',
    icon: '🏛️',
    title: '文化深度游',
    desc: '历史文化景点更靠前',
    preferences: ['历史文化', '艺术'],
    freeText: '请优先安排历史文化、博物馆、古迹、艺术展馆等地点，并在行程描述中补充简短看点。'
  },
  {
    key: 'relax',
    icon: '☕',
    title: '慢游不特种兵',
    desc: '降低强度，留出休息',
    preferences: ['休闲', '自然风光'],
    transportation: '混合',
    freeText: '请不要安排得太赶，每天保留休息和自由活动时间，优先选择节奏舒适、体验感强的路线。'
  },
  {
    key: 'budget',
    icon: '💰',
    title: '省钱但好玩',
    desc: '偏公共交通和免费景点',
    preferences: ['自然风光', '历史文化'],
    transportation: '公共交通',
    accommodation: '经济型酒店',
    freeText: '请尽量选择公共交通方便、门票较低或免费的景点，并控制餐饮和交通成本。'
  }
]

// 页面上用户填写的城市、日期、交通、住宿、偏好、额外要求，都会存在 formData 里。
// formData = 前端临时保存用户输入的对象。
type HomeFormData = Omit<TripFormData, 'start_date' | 'end_date'> & {
  start_date: Dayjs | null
  end_date: Dayjs | null
}

const formData = reactive<HomeFormData>({
  city: '',
  start_date: null,
  end_date: null,
  travel_days: 1,
  transportation: '公共交通',
  accommodation: '经济型酒店',
  preferences: [],
  free_text_input: ''
})

const scrollToForm = () => {
  formAnchor.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const setCity = (city: string) => {
  formData.city = city
  message.success(`目的地已设置为：${city}`)
}

const addPreferences = (preferences: string[]) => {
  formData.preferences = Array.from(new Set([...formData.preferences, ...preferences]))
}

const appendFreeText = (text: string) => {
  const current = formData.free_text_input.trim()
  formData.free_text_input = current ? `${current}\n${text}` : text
}

const applyPreset = (key: PresetKey) => {
  const preset = presetButtons.find((item) => item.key === key)
  if (!preset) return

  activePreset.value = key

  if (preset.transportation) {
    formData.transportation = preset.transportation
  }

  if (preset.accommodation) {
    formData.accommodation = preset.accommodation
  }

  addPreferences(preset.preferences)
  appendFreeText(preset.freeText)
  message.success(`已开启：${preset.title}`)
}

const randomInspiration = () => {
  const city = quickCities[Math.floor(Math.random() * quickCities.length)]
  const preset = presetButtons[Math.floor(Math.random() * presetButtons.length)]

  formData.city = city
  applyPreset(preset.key)
  message.success(`灵感已生成：${city} · ${preset.title}`)
  scrollToForm()
}

// 监听日期变化，自动计算旅行天数
watch([() => formData.start_date, () => formData.end_date], ([start, end]) => {
  if (start && end) {
    const days = end.diff(start, 'day') + 1
    if (days > 0 && days <= 30) {
      formData.travel_days = days
    } else if (days > 30) {
      message.warning('旅行天数不能超过30天')
      formData.end_date = null
    } else {
      message.warning('结束日期不能早于开始日期')
      formData.end_date = null
    }
  }
})

const handleSubmit = async () => {
  if (!formData.start_date || !formData.end_date) {
    message.error('请选择日期')
    return
  }

  loading.value = true
  loadingProgress.value = 0
  loadingStatus.value = '正在初始化智能规划流程...'

  // 模拟进度更新
  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 90) {
      loadingProgress.value += 10

      // 更新状态文本
      if (loadingProgress.value <= 20) {
        loadingStatus.value = '🔍 正在解析旅行需求...'
      } else if (loadingProgress.value <= 40) {
        loadingStatus.value = '🧭 正在搜索景点与美食...'
      } else if (loadingProgress.value <= 60) {
        loadingStatus.value = '🌤️ 正在查询天气与路线...'
      } else if (loadingProgress.value <= 80) {
        loadingStatus.value = '📍 正在优化每日游玩顺序...'
      } else {
        loadingStatus.value = '📋 正在生成完整行程计划...'
      }
    }
  }, 500)

  try {
    const requestData: TripFormData = {
      city: formData.city,
      start_date: formData.start_date.format('YYYY-MM-DD'),
      end_date: formData.end_date.format('YYYY-MM-DD'),
      travel_days: formData.travel_days,
      transportation: formData.transportation,
      accommodation: formData.accommodation,
      preferences: formData.preferences,
      free_text_input: formData.free_text_input
    }

    const response = await generateTripPlan(requestData)

    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingStatus.value = '✅ 完成！正在进入结果页...'

    if (response.success && response.data) {
      // 保存到 sessionStorage
      sessionStorage.setItem('tripPlan', JSON.stringify(response.data))

      message.success('旅行计划生成成功！')

      // 短暂延迟后跳转
      setTimeout(() => {
        router.push('/result')
      }, 500)
    } else {
      message.error(response.message || '生成失败')
    }
  } catch (error: any) {
    clearInterval(progressInterval)
    message.error(error.message || '生成旅行计划失败，请稍后重试')
  } finally {
    setTimeout(() => {
      loading.value = false
      loadingProgress.value = 0
      loadingStatus.value = ''
    }, 1000)
  }
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  padding: 32px 24px 56px;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 8% 10%, rgba(14, 165, 233, 0.16), transparent 28%),
    radial-gradient(circle at 90% 4%, rgba(20, 184, 166, 0.16), transparent 24%),
    linear-gradient(180deg, #e8f8ff 0%, #effdf8 46%, #ffffff 100%);
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(8px);
  opacity: 0.72;
  animation: floatOrb 18s infinite ease-in-out;
}

.orb-1 {
  width: 360px;
  height: 360px;
  top: -120px;
  left: -120px;
  background: rgba(14, 165, 233, 0.16);
}

.orb-2 {
  width: 300px;
  height: 300px;
  right: -110px;
  top: 260px;
  background: rgba(20, 184, 166, 0.14);
  animation-delay: 4s;
}

.orb-3 {
  width: 220px;
  height: 220px;
  left: 18%;
  bottom: 120px;
  background: rgba(45, 212, 191, 0.11);
  animation-delay: 8s;
}

.grid-mask {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(14, 165, 233, 0.055) 1px, transparent 1px),
    linear-gradient(90deg, rgba(14, 165, 233, 0.055) 1px, transparent 1px);
  background-size: 38px 38px;
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.55), transparent 62%);
}

.route-dash {
  position: absolute;
  height: 2px;
  border-radius: 999px;
  background: linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.35), rgba(20, 184, 166, 0.4), transparent);
  transform: rotate(-12deg);
}

.dash-1 {
  width: 420px;
  right: 8%;
  top: 160px;
}

.dash-2 {
  width: 320px;
  left: 6%;
  top: 580px;
  transform: rotate(10deg);
}

@keyframes floatOrb {
  0%, 100% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  50% {
    transform: translate3d(24px, -18px, 0) scale(1.04);
  }
}

/* Hero 区域 */
.home-hero {
  position: relative;
  z-index: 1;
  max-width: 1280px;
  margin: 0 auto 28px;
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(360px, 0.9fr);
  gap: 28px;
  align-items: stretch;
}

.hero-left,
.hero-panel,
.quick-playground,
.form-card,
.tool-card {
  border: 1px solid rgba(226, 232, 240, 0.92);
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(18px);
}

.hero-left {
  padding: 64px 52px 56px;
  border-radius: 30px;
}

.page-title {
  margin: 0;
  font-size: 52px;
  line-height: 1.12;
  font-weight: 900;
  letter-spacing: -1.6px;
  color: #0f172a;
}

.page-subtitle {
  max-width: 760px;
  margin: 22px 0 0;
  font-size: 18px;
  line-height: 1.9;
  color: #5b6475;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 28px;
}

.primary-hero-btn,
.ghost-hero-btn,
.quick-card,
.city-chip {
  border: none;
  cursor: pointer;
  transition: all 0.22s ease;
  font-family: inherit;
}

.primary-hero-btn,
.ghost-hero-btn {
  height: 44px;
  padding: 0 18px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 850;
}

.primary-hero-btn {
  color: #ffffff;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  box-shadow: 0 16px 34px rgba(20, 184, 166, 0.28);
}

.primary-hero-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 44px rgba(20, 184, 166, 0.34);
}

.ghost-hero-btn {
  color: #0f766e;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(20, 184, 166, 0.22);
}

.ghost-hero-btn:hover {
  color: #0891b2;
  background: #ecfeff;
  transform: translateY(-2px);
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 28px;
}

.hero-tags span {
  padding: 9px 14px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 750;
  color: #334155;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(226, 232, 240, 0.95);
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.055);
}

.hero-panel {
  padding: 26px;
  border-radius: 30px;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 15% 15%, rgba(14, 165, 233, 0.22), transparent 34%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(236, 254, 255, 0.9));
}

.plane-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.06);
}

.plane-icon {
  width: 54px;
  height: 54px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
  font-size: 28px;
  background: linear-gradient(135deg, #ecfeff, #e7fff8);
}

.plane-card p {
  margin: 0 0 4px;
  color: #0891b2;
  font-size: 13px;
  font-weight: 850;
}

.plane-card strong {
  color: #0f172a;
  font-size: 17px;
}

.agent-console {
  margin-top: 16px;
  padding: 14px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.9);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.console-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
}

.console-header span {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #22c55e;
}

.console-header span:nth-child(2) {
  background: #f59e0b;
}

.console-header span:nth-child(3) {
  background: #ef4444;
}

.console-header strong {
  margin-left: 6px;
  color: rgba(255, 255, 255, 0.72);
  font-size: 12px;
}

.console-line {
  padding: 7px 10px;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.68);
  font-size: 13px;
  font-weight: 700;
}

.console-line.active {
  color: #67e8f9;
  background: rgba(14, 165, 233, 0.12);
}

.mini-map {
  position: relative;
  height: 180px;
  margin-top: 16px;
  border-radius: 24px;
  background:
    linear-gradient(rgba(14, 165, 233, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(14, 165, 233, 0.06) 1px, transparent 1px),
    rgba(255, 255, 255, 0.62);
  background-size: 26px 26px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  overflow: hidden;
}

.route-svg {
  display: block;
  width: 100%;
  height: 100%;
}

.route-path {
  fill: none;
  stroke: url(#routeGradient);
  stroke-width: 5;
  stroke-linecap: round;
  stroke-linejoin: round;
  filter: url(#routeShadow);
}

.route-path-shadow {
  stroke: rgba(14, 165, 233, 0.16);
  stroke-width: 14;
  filter: none;
}

.route-ring {
  fill: rgba(14, 165, 233, 0.09);
  stroke: rgba(14, 165, 233, 0.18);
  stroke-width: 1;
}

.route-dot {
  stroke: #ffffff;
  stroke-width: 4;
}

.route-svg text {
  fill: #ffffff;
  font-size: 17px;
  font-weight: 900;
  dominant-baseline: middle;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 16px;
}

.hero-stats div {
  padding: 16px 12px;
  border-radius: 18px;
  text-align: center;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(226, 232, 240, 0.9);
}

.hero-stats strong {
  display: block;
  color: #0f172a;
  font-size: 22px;
  font-weight: 900;
}

.hero-stats span {
  display: block;
  margin-top: 4px;
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
}

/* 主体外壳 */
.content-shell {
  position: relative;
  z-index: 1;
  max-width: 1280px;
  margin: 0 auto;
  scroll-margin-top: 92px;
}

/* 快捷玩法 */
.quick-playground {
  margin-bottom: 28px;
  padding: 26px;
  border-radius: 30px;
}

.quick-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px;
  margin-bottom: 18px;
}

.quick-header h2 {
  margin: 0;
  color: #0f172a;
  font-size: 26px;
  font-weight: 900;
  letter-spacing: -0.4px;
}

.quick-header p:last-child {
  max-width: 520px;
  margin: 0;
  color: #64748b;
  line-height: 1.8;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.quick-card {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 16px;
  border-radius: 22px;
  text-align: left;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(226, 232, 240, 0.96);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.045);
}

.quick-card:hover,
.quick-card.active {
  transform: translateY(-3px);
  border-color: rgba(14, 165, 233, 0.3);
  box-shadow: 0 18px 46px rgba(14, 165, 233, 0.13);
}

.quick-card.active {
  background: linear-gradient(135deg, rgba(236, 254, 255, 0.94), rgba(240, 253, 250, 0.94));
}

.quick-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 46px;
  width: 46px;
  height: 46px;
  border-radius: 16px;
  font-size: 23px;
  background: linear-gradient(135deg, #ecfeff, #e7fff8);
  border: 1px solid rgba(14, 165, 233, 0.14);
}

.quick-content strong,
.quick-content em {
  display: block;
}

.quick-content strong {
  color: #0f172a;
  font-size: 15px;
  font-weight: 900;
}

.quick-content em {
  margin-top: 4px;
  color: #64748b;
  font-size: 13px;
  font-style: normal;
  font-weight: 650;
}

.city-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid rgba(226, 232, 240, 0.88);
}

.city-label {
  color: #334155;
  font-size: 14px;
  font-weight: 850;
}

.city-chip {
  height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  color: #475569;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(226, 232, 240, 0.96);
  font-size: 14px;
  font-weight: 800;
}

.city-chip:hover,
.city-chip.active {
  color: #ffffff;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  box-shadow: 0 12px 24px rgba(20, 184, 166, 0.22);
}

/* 表单卡片 */
.form-card {
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.92) !important;
}

.form-card :deep(.ant-card-body) {
  padding: 30px;
}

/* 表单分区 */
.form-section {
  margin-bottom: 26px;
  padding: 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 24px;
  border: 1px solid rgba(226, 232, 240, 0.95);
  transition: all 0.24s ease;
}

.form-section:hover {
  transform: translateY(-2px);
  border-color: rgba(14, 165, 233, 0.3);
  box-shadow: 0 18px 44px rgba(14, 165, 233, 0.08);
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 22px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.95);
}

.section-title-group {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.section-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  flex: 0 0 42px;
  border-radius: 15px;
  font-size: 22px;
  background: #ecfeff;
  border: 1px solid rgba(14, 165, 233, 0.16);
}

.section-title {
  display: block;
  font-size: 19px;
  font-weight: 850;
  color: #0f172a;
}

.section-title-group p {
  margin: 5px 0 0;
  color: #64748b;
  line-height: 1.6;
}

.section-index {
  color: #bae6fd;
  font-size: 28px;
  font-weight: 900;
  letter-spacing: -1px;
}

/* 表单标签 */
.form-label {
  font-size: 14px;
  font-weight: 750;
  color: #344054;
}

.input-prefix {
  color: #0891b2;
}

/* 输入框 */
.custom-input :deep(.ant-input-affix-wrapper),
.custom-date-picker,
.custom-textarea :deep(.ant-input) {
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  transition: all 0.24s ease;
}

.custom-input :deep(.ant-input-affix-wrapper:hover),
.custom-date-picker:hover,
.custom-textarea :deep(.ant-input:hover) {
  border-color: #67e8f9;
}

.custom-input :deep(.ant-input-affix-wrapper-focused),
.custom-date-picker.ant-picker-focused,
.custom-textarea :deep(.ant-input:focus) {
  border-color: #0ea5e9;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1);
}

/* 选择框 */
.custom-select :deep(.ant-select-selector) {
  border-radius: 14px !important;
  border: 1px solid #e2e8f0 !important;
  transition: all 0.24s ease !important;
}

.custom-select:hover :deep(.ant-select-selector) {
  border-color: #67e8f9 !important;
}

.custom-select.ant-select-focused :deep(.ant-select-selector) {
  border-color: #0ea5e9 !important;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1) !important;
}

/* 天数显示 */
.days-display-compact {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  padding: 8px 16px;
  border-radius: 14px;
  color: #ffffff;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  box-shadow: 0 14px 28px rgba(20, 184, 166, 0.22);
}

.days-value {
  font-size: 24px;
  font-weight: 900;
  margin-right: 4px;
}

.days-unit {
  font-size: 14px;
  font-weight: 700;
}

/* 偏好标签 */
.custom-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  width: 100%;
}

.preference-tag {
  margin-inline-start: 0 !important;
  margin-right: 0 !important;
  padding: 8px 13px;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  background: #ffffff;
  color: #475569;
  font-size: 14px;
  font-weight: 700;
  transition: all 0.22s ease;
}

.preference-tag:hover {
  border-color: #67e8f9;
  background: #ecfeff;
  color: #0891b2;
}

.preference-tag :deep(.ant-checkbox) {
  display: none;
}

.preference-tag :deep(span:last-child) {
  padding-inline-start: 0;
  padding-inline-end: 0;
}

.preference-tag.ant-checkbox-wrapper-checked {
  border-color: transparent;
  color: #ffffff;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  box-shadow: 0 12px 24px rgba(20, 184, 166, 0.22);
}

/* 提交按钮 */
.submit-button {
  height: 58px;
  border-radius: 18px;
  font-size: 18px;
  font-weight: 850;
  border: none;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  box-shadow: 0 18px 38px rgba(20, 184, 166, 0.26);
  transition: all 0.24s ease;
}

.submit-button:hover {
  transform: translateY(-2px);
  background: linear-gradient(135deg, #0284c7, #0f766e) !important;
  box-shadow: 0 22px 46px rgba(20, 184, 166, 0.34);
}

.submit-button:active {
  transform: translateY(0);
}

.button-icon {
  margin-right: 8px;
  font-size: 20px;
}

/* 加载容器 */
.loading-container {
  text-align: center;
  padding: 24px;
  border-radius: 20px;
  background: #f8fafc;
  border: 1px dashed #67e8f9;
}

.loading-status {
  margin: 16px 0 0;
  color: #0891b2;
  font-size: 16px;
  font-weight: 800;
}

/* 工具展示区 */
.tool-section,
.process-section {
  margin-top: 30px;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px;
  margin-bottom: 18px;
}

.section-eyebrow {
  margin: 0 0 8px;
  color: #0891b2;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.section-heading h2 {
  margin: 0;
  color: #0f172a;
  font-size: 28px;
  font-weight: 900;
  letter-spacing: -0.6px;
}

.section-desc {
  max-width: 460px;
  margin: 0;
  color: #64748b;
  line-height: 1.8;
}

.tool-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.tool-card {
  display: flex;
  gap: 16px;
  min-height: 148px;
  padding: 22px;
  border-radius: 24px;
  transition: all 0.24s ease;
}

.tool-card:hover {
  transform: translateY(-4px);
  border-color: rgba(14, 165, 233, 0.3);
  box-shadow: 0 22px 60px rgba(14, 165, 233, 0.11);
}

.tool-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 48px;
  width: 48px;
  height: 48px;
  border-radius: 17px;
  font-size: 24px;
  background: linear-gradient(135deg, #ecfeff, #e7fff8);
  border: 1px solid rgba(14, 165, 233, 0.14);
}

.tool-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.tool-title-row h3 {
  margin: 0;
  color: #172033;
  font-size: 17px;
  font-weight: 850;
}

.tool-title-row span {
  padding: 4px 9px;
  border-radius: 999px;
  color: #0891b2;
  font-size: 12px;
  font-weight: 800;
  background: #ecfeff;
}

.tool-info p {
  margin: 12px 0 0;
  color: #667085;
  line-height: 1.75;
  font-size: 14px;
}

/* 流程区域 */
.process-card {
  padding: 28px;
  border-radius: 28px;
  color: #ffffff;
  background:
    radial-gradient(circle at 12% 20%, rgba(14, 165, 233, 0.35), transparent 34%),
    linear-gradient(135deg, #0f172a, #0f766e);
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.22);
}

.process-title {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 26px;
}

.process-title > span {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 17px;
  font-size: 24px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.process-title h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 900;
}

.process-title p {
  margin: 6px 0 0;
  color: rgba(255, 255, 255, 0.68);
}

.process-steps {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.process-step {
  padding: 18px 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.09);
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.step-index {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  width: 30px;
  height: 30px;
  margin-bottom: 10px;
  border-radius: 999px;
  color: #0f172a;
  font-weight: 900;
  background: #ffffff;
}

.process-step span {
  display: block;
  font-size: 14px;
  font-weight: 800;
}

@media (max-width: 1100px) {
  .home-hero {
    grid-template-columns: 1fr;
  }

  .hero-panel {
    display: none;
  }

  .quick-grid,
  .tool-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .process-steps {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .home-container {
    padding: 20px 12px 36px;
  }

  .hero-left {
    padding: 38px 24px;
    border-radius: 24px;
  }

  .page-title {
    font-size: 36px;
  }

  .page-subtitle {
    font-size: 16px;
  }

  .hero-actions {
    flex-direction: column;
  }

  .primary-hero-btn,
  .ghost-hero-btn {
    width: 100%;
  }

  .form-card :deep(.ant-card-body) {
    padding: 18px;
  }

  .form-section,
  .quick-playground {
    padding: 18px;
  }

  .section-header,
  .section-heading,
  .quick-header {
    display: block;
  }

  .section-index {
    display: none;
  }

  .section-desc,
  .quick-header p:last-child {
    margin-top: 10px;
  }

  .quick-grid,
  .tool-grid,
  .process-steps {
    grid-template-columns: 1fr;
  }
}
</style>
