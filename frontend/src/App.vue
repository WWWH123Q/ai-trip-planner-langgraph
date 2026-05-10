<template>
  <div id="app">
    <a-layout class="app-layout">
      <!-- 顶部导航 -->
      <a-layout-header class="app-header">
        <div class="app-header-inner">
          <div class="brand" @click="router.push('/')">
            <div class="brand-icon">🌍</div>

            <div class="brand-text">
              <div class="brand-title">智能旅行助手</div>
              <div class="brand-subtitle">Multi-Agent Travel Planner</div>
            </div>
          </div>

          <div class="nav-actions">
            <button
              class="nav-link"
              :class="{ active: route.path === '/' }"
              @click="router.push('/')"
            >
              开始规划
            </button>

            <button
              class="nav-link"
              :class="{ active: route.path === '/result' }"
              @click="router.push('/result')"
            >
              查看结果
            </button>
          </div>
        </div>
      </a-layout-header>

      <a-layout-content class="app-content">
        <router-view />
      </a-layout-content>

      <a-layout-footer class="app-footer">
        智能旅行助手 · 基于 HelloAgents / LangGraph / 高德地图工具构建
      </a-layout-footer>
    </a-layout>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
</script>

<style>
* {
  box-sizing: border-box;
}

html,
body,
#app {
  margin: 0;
  min-height: 100%;
}

body {
  background: #eef8fb;
}

#app {
  font-family:
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    'Helvetica Neue',
    Arial,
    'Noto Sans',
    sans-serif;
}

.app-layout {
  min-height: 100vh;
  background: linear-gradient(180deg, #e8f8ff 0%, #effdf8 46%, #ffffff 100%);
}

/* 顶部导航 */
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  height: 72px;
  padding: 0 28px;
  line-height: normal !important;
  background: rgba(255, 255, 255, 0.9) !important;
  border-bottom: 1px solid rgba(203, 213, 225, 0.75);
  backdrop-filter: blur(18px);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
}

.app-header-inner {
  max-width: 1280px;
  height: 72px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.brand-icon {
  width: 42px;
  height: 42px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  background: linear-gradient(135deg, #dff7ff, #e7fff8);
  border: 1px solid rgba(14, 165, 233, 0.18);
  box-shadow: 0 10px 24px rgba(14, 165, 233, 0.12);
}

.brand-text {
  display: flex;
  flex-direction: column;
  justify-content: center;
  line-height: 1.2;
}

.brand-title {
  color: #0f172a;
  font-size: 19px;
  font-weight: 900;
}

.brand-subtitle {
  margin-top: 3px;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
}

/* 右侧导航 */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-link {
  height: 40px;
  min-width: 92px;
  padding: 0 18px;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: #475569;
  font-size: 15px;
  font-weight: 850;
  cursor: pointer;

  display: inline-flex;
  align-items: center;
  justify-content: center;

  line-height: 1 !important;
  transition: all 0.22s ease;
}

.nav-link:hover {
  color: #0891b2;
  background: rgba(14, 165, 233, 0.1);
}

.nav-link.active {
  color: #ffffff;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  box-shadow: 0 12px 24px rgba(20, 184, 166, 0.24);
}

/* 内容区 */
.app-content {
  padding: 0;
  background: transparent;
}

/* 底部 */
.app-footer {
  padding: 22px 16px;
  text-align: center;
  color: #64748b;
  font-size: 14px;
  font-weight: 600;
  background: #ffffff;
  border-top: 1px solid rgba(226, 232, 240, 0.95);
}

@media (max-width: 768px) {
  .app-header {
    height: auto;
    padding: 12px 14px;
  }

  .app-header-inner {
    height: auto;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .brand-title {
    font-size: 17px;
  }

  .brand-subtitle {
    display: none;
  }

  .nav-actions {
    width: 100%;
  }

  .nav-link {
    flex: 1;
  }
}
</style>