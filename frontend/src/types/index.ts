// 类型定义
// 类似后端的：backend/app/models/schemas.py
// types/index.ts
// 告诉前端：
// 我要发出去的数据是什么格式；
// 我要接收回来的数据是什么格式；
// 旅行计划里面有哪些字段。
// export 的意思是：把当前文件里的变量、函数、类型“暴露出去”，让其他文件可以导入使用。
// 你可以把一个 .ts 文件理解成一个“房间”。默认情况下，房间里的东西只能自己用。
// 加了 export，就相当于把这个东西放到门口，允许别的文件拿走用。
export interface Location {
  longitude: number
  latitude: number
}

export interface Attraction {
  name: string
  address: string
  location: Location
  visit_duration: number
  description: string
  category?: string
  rating?: number
  image_url?: string
  ticket_price?: number
}

export interface Meal {
  type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  name: string
  address?: string
  location?: Location
  description?: string
  estimated_cost?: number
}

export interface Hotel {
  name: string
  address: string
  location?: Location
  price_range: string
  rating: string
  distance: string
  type: string
  estimated_cost?: number
}

export interface Budget {
  total_attractions: number
  total_hotels: number
  total_meals: number
  total_transportation: number
  total: number
}

export interface DayPlan {
  date: string
  day_index: number
  description: string
  transportation: string
  accommodation: string
  hotel?: Hotel
  attractions: Attraction[]
  meals: Meal[]
}

export interface WeatherInfo {
  date: string
  day_weather: string
  night_weather: string
  day_temp: number
  night_temp: number
  wind_direction: string
  wind_power: string
}

export interface TripPlan { //这个是结果页要展示的完整旅行计划。
  city: string
  start_date: string
  end_date: string
  days: DayPlan[]
  weather_info: WeatherInfo[]
  overall_suggestions: string
  budget?: Budget
}

export interface TripFormData { //这个就对应后端的 TripRequest。
  // TripFormData= 前端准备发给后端的表单数据格式= 后端 TripRequest 的前端版本
  // 也就是说，前端最后要发给后端的数据就是这种形状：
  //   {
  //   "city": "南京",
  //   "start_date": "2026-06-01",
  //   "end_date": "2026-06-03",
  //   "travel_days": 3,
  //   "transportation": "公共交通",
  //   "accommodation": "经济型酒店",
  //   "preferences": ["历史文化", "美食"],
  //   "free_text_input": "希望多安排一些博物馆"
  // }
  city: string
  start_date: string
  end_date: string
  travel_days: number
  transportation: string
  accommodation: string
  preferences: string[]
  free_text_input: string
}

export interface TripPlanResponse {
  // TripPlanResponse= 后端返回给前端的响应外壳
// 这个对应后端返回的：
//   TripPlanResponse(
//     success=True,
//     message="旅行计划生成成功",
//     data=trip_plan
// )
  success: boolean//success 一定有
  message: string//message 一定有
  data?: TripPlan  //不一定有
  //问号是 TypeScript 里的“可选属性”标记。
  // data 这个字段可以有，也可以没有。
  // 如果有，它的类型必须是 TripPlan。
  // 如果没有，它就是 undefined。
  // 等价理解成：
  // data: TripPlan | undefined
}

// 所以前端期待后端返回：
//   {
//     "success": true,
//     "message": "旅行计划生成成功",
//     "data": {
//       "city": "南京",
//       "days": [...]
//     }
//   }

