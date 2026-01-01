import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import config_manager
from app.core.dependencies import get_config
from app.core.exceptions import setup_exception_handlers


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="PPT2Audio Backend",
        description="Backend for PPT2Audio",
        version="0.1.0",
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 在生产环境中应该设置具体的域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 加载配置
    config = config_manager.get_config()
    
    # 设置异常处理器
    setup_exception_handlers(app)
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {"status": "healthy"}
    
    # 包含路由
    from app.api import projects, pdf, scripts, tasks, audio, export, config
    app.include_router(projects.projects_router)
    app.include_router(pdf.pdf_router)
    app.include_router(scripts.scripts_router)
    app.include_router(scripts.dialogue_router)
    app.include_router(audio.audio_router)
    app.include_router(tasks.tasks_router)
    app.include_router(export.export_router)
    app.include_router(config.config_router)
    
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.__main__:app",
        port=8000,
        host="0.0.0.0",
        reload=False,
    )