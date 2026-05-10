"""高德地图 Web 服务 API 封装：不依赖 hello_agents / MCP"""

from typing import List, Dict, Any, Optional
import requests

from ..config import get_settings
from ..models.schemas import Location, POIInfo, WeatherInfo, RouteInfo


class AmapService:
    """高德地图服务封装类：直接调用高德 Web 服务 HTTP API"""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.amap_api_key
        self.base_url = "https://restapi.amap.com/v3"

        if not self.api_key:
            raise ValueError("高德地图 API Key 未配置，请在 .env 文件中设置 AMAP_API_KEY")

    def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """统一 GET 请求"""
        url = f"{self.base_url}{path}"
        params = {
            **params,
            "key": self.api_key,
            "output": "JSON",
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "1":
            raise RuntimeError(f"高德 API 调用失败: {data}")

        return data

    def geocode(self, address: str, city: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        地址转经纬度，同时可拿到 adcode。
        """
        try:
            params = {"address": address}
            if city:
                params["city"] = city

            data = self._get("/geocode/geo", params)
            geocodes = data.get("geocodes", [])

            if not geocodes:
                return None

            item = geocodes[0]
            location_str = item.get("location", "")

            longitude = 116.397128
            latitude = 39.916527

            if "," in location_str:
                lon, lat = location_str.split(",", 1)
                longitude = float(lon)
                latitude = float(lat)

            return {
                "formatted_address": item.get("formatted_address", address),
                "adcode": item.get("adcode", ""),
                "location": Location(longitude=longitude, latitude=latitude),
            }

        except Exception as e:
            print(f"❌ 地理编码失败: {e}")
            return None

    def search_poi(self, keywords: str, city: str, citylimit: bool = True, limit: int = 10) -> List[POIInfo]:
        """
        搜索 POI：景点 / 酒店 / 餐厅等。
        """
        try:
            data = self._get(
                "/place/text",
                {
                    "keywords": keywords,
                    "city": city,
                    "citylimit": "true" if citylimit else "false",
                    "extensions": "base",
                    "offset": limit,
                    "page": 1,
                },
            )

            pois = []

            for item in data.get("pois", []):
                location_str = item.get("location", "")
                if "," not in location_str:
                    continue

                lon, lat = location_str.split(",", 1)

                address = item.get("address") or ""
                if isinstance(address, list):
                    address = ""

                poi = POIInfo(
                    id=item.get("id", ""),
                    name=item.get("name", ""),
                    type=item.get("type", ""),
                    address=address,
                    location=Location(
                        longitude=float(lon),
                        latitude=float(lat),
                    ),
                    tel=item.get("tel") or None,
                )

                pois.append(poi)

            return pois

        except Exception as e:
            print(f"❌ POI 搜索失败: {e}")
            return []

    def get_weather(self, city: str) -> List[WeatherInfo]:
        """
        查询天气。先用 geocode 拿 adcode，再查天气。
        """
        try:
            geo = self.geocode(city, city)
            adcode = geo.get("adcode") if geo else city

            data = self._get(
                "/weather/weatherInfo",
                {
                    "city": adcode,
                    "extensions": "all",
                },
            )

            forecasts = data.get("forecasts", [])
            if not forecasts:
                return []

            casts = forecasts[0].get("casts", [])

            weather_list = []
            for item in casts:
                weather_list.append(
                    WeatherInfo(
                        date=item.get("date", ""),
                        day_weather=item.get("dayweather", ""),
                        night_weather=item.get("nightweather", ""),
                        day_temp=item.get("daytemp", 0),
                        night_temp=item.get("nighttemp", 0),
                        wind_direction=item.get("daywind", ""),
                        wind_power=item.get("daypower", ""),
                    )
                )

            return weather_list

        except Exception as e:
            print(f"❌ 天气查询失败: {e}")
            return []

    def _location_to_str(self, location: Location) -> str:
        """把 Location 转成高德 API 需要的 lon,lat 字符串"""
        return f"{location.longitude:.6f},{location.latitude:.6f}"

    def _normalize_list(self, value):
        """高德返回有时是 list，有时是 dict，这里统一成 list"""
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def get_route_between_locations(
        self,
        origin: Location,
        destination: Location,
        city: str,
        route_type: str = "walking"
    ) -> Dict[str, Any]:
        """
        调用高德路径规划 API，计算两个经纬度之间的真实路线距离和耗时。

        route_type:
        - walking: 步行
        - driving: 驾车
        - transit: 公共交通
        """
        origin_str = self._location_to_str(origin)
        destination_str = self._location_to_str(destination)

        route_type = route_type or "walking"

        try:
            if route_type == "driving":
                data = self._get(
                    "/direction/driving",
                    {
                        "origin": origin_str,
                        "destination": destination_str,
                        "extensions": "base",
                    }
                )

                route = data.get("route", {})
                paths = self._normalize_list(route.get("paths"))

                if not paths:
                    raise ValueError("高德驾车路线无 paths")

                path = paths[0]

                distance_m = int(float(path.get("distance") or 0))
                duration_s = int(float(path.get("duration") or 0))

                return {
                    "success": True,
                    "route_type": "driving",
                    "distance_m": distance_m,
                    "duration_s": duration_s,
                    "distance_km": round(distance_m / 1000, 2),
                    "duration_min": round(duration_s / 60),
                    "summary": f"驾车约 {round(distance_m / 1000, 1)} 公里，约 {round(duration_s / 60)} 分钟"
                }

            if route_type == "transit":
                data = self._get(
                    "/direction/transit/integrated",
                    {
                        "origin": origin_str,
                        "destination": destination_str,
                        "city": city,
                        "cityd": city,
                        "strategy": "0",
                    }
                )

                route = data.get("route", {})
                transits = self._normalize_list(route.get("transits"))

                if not transits:
                    print("⚠️ 公共交通无结果，自动改用步行路线")
                    return self.get_route_between_locations(
                        origin=origin,
                        destination=destination,
                        city=city,
                        route_type="walking"
                    )
                transit = transits[0]

                distance_m = int(float(transit.get("distance") or 0))
                duration_s = int(float(transit.get("duration") or 0))
                cost = transit.get("cost", "")

                return {
                    "success": True,
                    "route_type": "transit",
                    "distance_m": distance_m,
                    "duration_s": duration_s,
                    "distance_km": round(distance_m / 1000, 2),
                    "duration_min": round(duration_s / 60),
                    "cost": cost,
                    "summary": f"公共交通约 {round(distance_m / 1000, 1)} 公里，约 {round(duration_s / 60)} 分钟"
                }

            # 默认步行
            data = self._get(
                "/direction/walking",
                {
                    "origin": origin_str,
                    "destination": destination_str,
                }
            )

            route = data.get("route", {})
            paths = self._normalize_list(route.get("paths"))

            if not paths:
                raise ValueError("高德步行路线无 paths")

            path = paths[0]

            distance_m = int(float(path.get("distance") or 0))
            duration_s = int(float(path.get("duration") or 0))

            return {
                "success": True,
                "route_type": "walking",
                "distance_m": distance_m,
                "duration_s": duration_s,
                "distance_km": round(distance_m / 1000, 2),
                "duration_min": round(duration_s / 60),
                "summary": f"步行约 {round(distance_m / 1000, 1)} 公里，约 {round(duration_s / 60)} 分钟"
            }

        except Exception as e:
            print(f"⚠️ 高德路线规划失败: {origin_str} -> {destination_str}, {e}")
            return {
                "success": False,
                "route_type": route_type,
                "distance_m": 999999,
                "duration_s": 999999,
                "distance_km": 999.0,
                "duration_min": 9999,
                "summary": "路线规划失败，已使用兜底距离"
            }

    def get_route_between_pois(
        self,
        origin_poi: POIInfo,
        destination_poi: POIInfo,
        city: str,
        route_type: str = "walking"
    ) -> Dict[str, Any]:
        """计算两个 POI 之间的真实路线"""
        return self.get_route_between_locations(
            origin=origin_poi.location,
            destination=destination_poi.location,
            city=city,
            route_type=route_type
        )

    def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        """
        根据 POI ID 获取详情。
        """
        try:
            data = self._get(
                "/place/detail",
                {
                    "id": poi_id,
                },
            )

            pois = data.get("pois", [])
            if not pois:
                return {}

            return pois[0]

        except Exception as e:
            print(f"❌ 获取 POI 详情失败: {e}")
            return {}

    def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking",
    ) -> Optional[RouteInfo]:
        """
        先保留一个简化版路线规划，后面可以继续增强。
        """
        try:
            return RouteInfo(
                distance=0,
                duration=0,
                route_type=route_type,
                description=f"建议从 {origin_address} 前往 {destination_address}，可使用高德地图进一步导航。",
            )
        except Exception as e:
            print(f"❌ 路线规划失败: {e}")
            return None


_amap_service = None


def get_amap_service() -> AmapService:
    """获取高德地图服务实例，单例模式"""
    global _amap_service

    if _amap_service is None:
        _amap_service = AmapService()

    return _amap_service