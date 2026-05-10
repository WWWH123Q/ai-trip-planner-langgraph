"""启动脚本"""

import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "app.api.main:app",  #去 app.api.main 里面找到 app，然后把它跑起来。
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower()  #日志，
    )

