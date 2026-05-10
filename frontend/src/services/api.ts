// 前端怎么请求后端，是前端专门封装接口请求的文件。
//把“请求后端”这件事封装成一个函数

import axios from 'axios'
import type { TripFormData, TripPlanResponse } from '@/types'

// // #重点：
// 如果 .env 里配置了 VITE_API_BASE_URL，就用配置的地址；
// 如果没配置，就默认请求 http://localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

//apiClient 是 axios 请求对象：创建一个专门用来请求后端的对象。 创建一个提前配置好的 axios 请求对象。
// 以后你不用每次都写完整地址：axios.post('http://localhost:8000/api/trip/plan', formData)
//而是写：apiClient.post('/api/trip/plan', formData) 因为 baseURL 已经提前设置好了。
//apiClient = 一个已经知道后端地址、超时时间、请求格式的 axios 工具：
// 前端把用户填写的旅行需求，打包成 JSON，发送给后端 FastAPI 的工具。
// 后端处理完后，axios 再把返回的旅行计划 JSON 带回前端。
const apiClient = axios.create({  //const 是“声明一个变量/常量名字，并且这个名字不能重新指向别的值 相对的 let能重新赋值
  baseURL: API_BASE_URL, //baseURL: 后端基础地址
  timeout: 120000, // 2分钟超时，最多寻找120s
  headers: {
    'Content-Type': 'application/json'  //发送 JSON 数据
  }
})
//所以以后请求时不用每次都写完整地址，只写这个就行了：
// apiClient.post('/api/trip/plan', formData)
// 实际请求的是：
// http://localhost:8000/api/trip/plan

// 请求拦截器：主要是打印日志
//每次前端准备向后端发送请求之前，
// 先自动经过这里，
// 打印一下请求信息，
// 然后再真正发出去。
apiClient.interceptors.request.use(
    //interceptors 拦截器 ：让请求在发出去之前，先经过一段统一处理逻辑。
    //request.use(...) ：给 apiClient 注册一个“请求发出前要执行的函数”。
    //request 表示：拦截“请求发出前”的过程  use() 表示：注册一个拦截函数
    //给 apiClient 注册一个“请求发出前要执行的函数”。
  (config) => {
    console.log('发送请求:', config.method?.toUpperCase(), config.url)  //请求发出去前打印：
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器:主要是打印日志
apiClient.interceptors.response.use(
  (response) => {
    console.log('收到响应:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('响应错误:', error.response?.status, error.message)
    return Promise.reject(error)
  }
)

/**
 * 生成旅行计划-->核心函数：这就是前端调用后端主接口的函数。
   * 接收 formData
   * ↓
   * 发送 POST 请求到 /api/trip/plan
   * ↓
   * 把 formData 作为 JSON 请求体发给后端
   * ↓
   * 等待后端返回 TripPlanResponse
   * ↓
   * 返回 response.data
 *
 */
export async function generateTripPlan(formData: TripFormData): Promise<TripPlanResponse> {
  // 定义一个异步函数 generateTripPlan并且把它导出，让别的文件可以使用它
  // 所以 Home.vue 里才能写：import { generateTripPlan } from '@/services/api'。
  // async function:定义一个“异步函数”. 这个函数里面通常会做一些需要等待结果的事情  async function 会自动返回 Promise
  //export:把当前文件里的东西“暴露出去”，让别的文件可以 import 使用。
  try {
    const response = await apiClient.post<TripPlanResponse>('/api/trip/plan', formData)
    //apiClient.post<TripPlanResponse>('/api/trip/plan', formData) --> 它对应后端：@router.post("/plan") async def plan_trip(request: TripRequest):

    return response.data
  } catch (error: any) {
    console.error('生成旅行计划失败:', error)
    throw new Error(error.response?.data?.detail || error.message || '生成旅行计划失败')
  }
}

/**
 * 健康检查
 */
export async function healthCheck(): Promise<any> {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error: any) {
    console.error('健康检查失败:', error)
    throw new Error(error.message || '健康检查失败')
  }
}

export default apiClient


// api.ts
// export async function generateTripPlan() {}
// export async function healthCheck() {}
// export default apiClient
//
// 导入方式：
// import apiClient from '@/services/api'
// import { generateTripPlan, healthCheck } from '@/services/api'
//
// 也可以写在一起：
// import apiClient, { generateTripPlan, healthCheck } from '@/services/api'