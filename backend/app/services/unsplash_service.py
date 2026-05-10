"""Unsplash图片服务
这个文件是用来从 Unsplash 图片网站/API 搜索图片的。"""

import requests
from typing import List, Optional
from ..config import get_settings

class UnsplashService:
    """Unsplash图片服务类"""
    
    def __init__(self):
        """初始化服务"""
        settings = get_settings() #读配置
        self.access_key = settings.unsplash_access_key  #
        self.base_url = "https://api.unsplash.com" #设置API根地址，后面请求图片搜索时，会拼成：https://api.unsplash.com/search/photos
    
    def search_photos(self, query: str, per_page: int = 5) -> List[dict]:
        """
        搜索多张图片：根据关键词 query 搜索图片，默认返回 5 张。
        Args:
            query: 搜索关键词
            per_page: 每页数量
        Returns:
            图片列表
        """
        try:
            url = f"{self.base_url}/search/photos" #构造url，这是 Unsplash 的图片搜索接口地址。
            params = { #构造请求参数
                "query": query,
                "per_page": per_page,
                "client_id": self.access_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            #发送请求，这句是真正向 Unsplash 发送 HTTP GET 请求。最多等10秒
            response.raise_for_status() #检查请求是否成功
            
            data = response.json()#Unsplash 返回的是 JSON。response.json() 会把返回内容转成 Python 字典。
            #Unsplash 搜图结果一般在：data["results"] 所以：
            results = data.get("results", []) #从返回数据中取出图片列表。如果没有 results，就用空列表。
            
            # 提取图片URL：这里是把 Unsplash 返回的一大堆复杂信息，整理成项目需要的简单格式。
            #每张图片提取这些字段：
                    # id：图片 ID
                    # url：正常尺寸图片 URL
                    # thumb：缩略图 URL
                    # description：图片描述
                    # photographer：摄影师名字
         # 最后整理成：[
                #     {
                #         "id": "abc123",
                #         "url": "https://images.unsplash.com/xxx",
                #         "thumb": "https://images.unsplash.com/thumb_xxx",
                #         "description": "A museum building",
                #         "photographer": "John Smith"
                #     }
                # ]
            photos = []
            for photo in results:
                photos.append({
                    "id": photo.get("id"),
                    "url": photo.get("urls", {}).get("regular"),
                    "thumb": photo.get("urls", {}).get("thumb"),
                    "description": photo.get("description") or photo.get("alt_description"),
                    "photographer": photo.get("user", {}).get("name")
                })
            
            return photos
            
        except Exception as e:
            print(f"❌ Unsplash搜索失败: {str(e)}")
            return []
    
    def get_photo_url(self, query: str) -> Optional[str]:
        """
        获取单张图片URL

        Args:
            query: 搜索关键词

        Returns:
            图片URL
        """
        photos = self.search_photos(query, per_page=1) #返回第一张图片的url
        if photos:
            return photos[0].get("url")
        return None
        #比如：photo_url = service.get_photo_url("南京博物院 China landmark")
        #如果成功，返回：https://images.unsplash.com/xxxx

# 全局服务实例
_unsplash_service = None


def get_unsplash_service() -> UnsplashService:
    """获取Unsplash服务实例(单例模式)"""
    global _unsplash_service
    
    if _unsplash_service is None:
        _unsplash_service = UnsplashService()
    
    return _unsplash_service

