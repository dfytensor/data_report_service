"""
FastAPI应用入口
JSON DAG报告生成服务
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
import os
import json
import uuid
from datetime import datetime
from typing import Optional

from models.config_models import (
    ReportConfig, GenerationRequest, GenerationResponse,
    PRESET_STYLES, ChartType, ChartStyle
)
from handlers.report_generator import ReportGenerator
from handlers.chart_converter import ChartConverter
from handlers.dag_handler import DAGHandler
from handlers.file_manager import FileManager

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="JSON DAG报告生成服务",
    description="基于JSON配置的DAG报告生成服务，支持ECharts图表和Markdown输出",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建组件实例
report_generator = ReportGenerator()
chart_converter = ChartConverter(PRESET_STYLES)
dag_handler = DAGHandler()
file_manager = FileManager()


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    # 创建必要的目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("generated_reports", exist_ok=True)
    os.makedirs("temp_reports", exist_ok=True)
    os.makedirs("examples", exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/service.log'),
            logging.StreamHandler()
        ]
    )
    global logger
    logger = logging.getLogger(__name__)
    
    logger.info("JSON DAG报告生成服务启动中...")
    logger.info("服务启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("JSON DAG报告生成服务关闭中...")
    file_manager.cleanup_temp_files()
    logger.info("服务关闭完成")


@app.get("/")
async def root():
    """根路径，返回服务信息"""
    return {
        "service": "JSON DAG报告生成服务",
        "version": "1.0.0",
        "description": "基于JSON配置的DAG报告生成服务",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/styles")
async def get_chart_styles():
    """获取支持的图表样式"""
    styles = {}
    for style_enum in ChartStyle:
        styles[style_enum.value] = PRESET_STYLES[style_enum]
    return {
        "chart_types": [chart_type.value for chart_type in ChartType],
        "chart_styles": [style.value for style in ChartStyle],
        "preset_styles": PRESET_STYLES
    }


@app.get("/examples")
async def list_examples():
    """获取示例列表"""
    examples = []
    examples_dir = "examples"
    
    if os.path.exists(examples_dir):
        for filename in os.listdir(examples_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(examples_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                        examples.append({
                            "filename": filename,
                            "title": config_data.get("config", {}).get("title", "未知标题"),
                            "description": config_data.get("config", {}).get("description", ""),
                            "elements_count": len(config_data.get("config", {}).get("elements", []))
                        })
                except Exception as e:
                    logger.warning(f"读取示例文件失败 {filename}: {e}")
    
    return {"examples": examples}


@app.get("/examples/{filename}")
async def get_example(filename: str):
    """获取指定示例"""
    examples_dir = "examples"
    file_path = os.path.join(examples_dir, f"{filename}.json")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"示例文件 {filename} 不存在")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return JSONResponse(
            content=json.loads(content),
            media_type="application/json"
        )
    except Exception as e:
        logger.error(f"读取示例文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"读取示例文件失败: {str(e)}")


@app.post("/generate", response_model=GenerationResponse)
async def generate_report(request: GenerationRequest, background_tasks: BackgroundTasks):
    """生成报告的主端点"""
    try:
        logger.info(f"收到报告生成请求: {request.config.title}")
        
        # 生成唯一标识符
        report_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 构建文件名
        base_filename = request.filename or request.config.title.replace(" ", "_")
        filename = f"{base_filename}_{timestamp}_{report_id}.md"
        
        # 生成报告内容
        try:
            markdown_content = report_generator.generate_report(
                request.config,
                request.options
            )
        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            raise HTTPException(status_code=400, detail=f"报告生成失败: {str(e)}")
        
        # 保存文件
        try:
            file_path = file_manager.save_file(filename, markdown_content)
            logger.info(f"报告已保存: {file_path}")
        except Exception as e:
            logger.error(f"文件保存失败: {e}")
            raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
        
        # 添加清理任务
        background_tasks.add_task(
            file_manager.schedule_cleanup,
            file_path,
            ttl_hours=24  # 24小时后自动删除
        )
        
        response = GenerationResponse(
            success=True,
            filename=filename,
            content=markdown_content,
            metadata={
                "report_id": report_id,
                "timestamp": timestamp,
                "file_size": len(markdown_content),
                "elements_count": len(request.config.elements)
            }
        )
        
        logger.info(f"报告生成成功: {filename}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"报告生成过程发生未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")


@app.get("/download/{filename}")
async def download_report(filename: str):
    """下载生成的报告文件"""
    file_path = file_manager.get_file_path(filename)
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"文件 {filename} 不存在")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/markdown"
    )


@app.post("/validate")
async def validate_config(request: GenerationRequest):
    """验证配置"""
    try:
        # 检查基本配置
        config = request.config
        
        # 验证标题
        if not config.title or not config.title.strip():
            return JSONResponse(
                status_code=400,
                content={
                    "valid": False,
                    "errors": ["标题不能为空"]
                }
            )
        
        # 验证元素
        if not config.elements:
            return JSONResponse(
                status_code=400,
                content={
                    "valid": False,
                    "errors": ["报告至少需要一个元素"]
                }
            )
        
        # 验证图表元素
        chart_errors = []
        for i, element in enumerate(config.elements):
            if element.type == "chart":
                try:
                    chart_converter.validate_chart_config(element)
                except Exception as e:
                    chart_errors.append(f"图表元素 {i+1}: {str(e)}")
        
        if chart_errors:
            return JSONResponse(
                status_code=400,
                content={
                    "valid": False,
                    "errors": chart_errors
                }
            )
        
        # 验证DAG元素
        dag_errors = []
        for i, element in enumerate(config.elements):
            if element.type == "dag":
                try:
                    dag_handler.validate_dag_config(element)
                except Exception as e:
                    dag_errors.append(f"DAG元素 {i+1}: {str(e)}")
        
        if dag_errors:
            return JSONResponse(
                status_code=400,
                content={
                    "valid": False,
                    "errors": dag_errors
                }
            )
        
        return {
            "valid": True,
            "message": "配置验证通过"
        }
        
    except Exception as e:
        logger.error(f"配置验证失败: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "valid": False,
                "errors": [f"验证过程发生错误: {str(e)}"]
            }
        )


@app.delete("/cleanup")
async def cleanup_files():
    """清理临时文件"""
    try:
        count = file_manager.cleanup_temp_files()
        return {
            "message": f"清理完成，删除了 {count} 个临时文件"
        }
    except Exception as e:
        logger.error(f"清理文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理文件失败: {str(e)}")


@app.get("/files")
async def list_generated_files():
    """列出已生成的文件"""
    try:
        files = file_manager.list_files()
        return {"files": files}
    except Exception as e:
        logger.error(f"列出文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"列出文件失败: {str(e)}")


# 异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "detail": "内部服务器错误"
        }
    )


if __name__ == "__main__":
    # 开发模式启动
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )