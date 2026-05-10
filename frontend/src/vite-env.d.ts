/// <reference types="vite/client" />

interface ImportMetaEnv {
  /**
   * 后端接口地址
   * 例如：http://localhost:8000
   */
  readonly VITE_API_BASE_URL?: string

  /**
   * 高德地图 Web 端 JS API Key
   */
  readonly VITE_AMAP_WEB_JS_KEY: string

  /**
   * 高德地图安全密钥
   * 如果你没有配置安全密钥，可以先不填
   */
  readonly VITE_AMAP_SECURITY_CODE?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

/**
 * 防止 @amap/amap-jsapi-loader 在 TypeScript 里爆红
 */
declare module '@amap/amap-jsapi-loader' {
  const AMapLoader: {
    load(options: {
      key: string
      version?: string
      plugins?: string[]
      AMapUI?: {
        version?: string
        plugins?: string[]
      }
      Loca?: {
        version?: string
      }
      securityJsCode?: string
    }): Promise<any>
  }

  export default AMapLoader
}

/**
 * 声明浏览器 window 上可能出现的高德地图对象
 */
declare global {
  interface Window {
    AMap?: any
    _AMapSecurityConfig?: {
      securityJsCode: string
    }
  }
}

export {}