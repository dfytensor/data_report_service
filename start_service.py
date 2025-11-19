#!/usr/bin/env python3
"""
JSON DAG报告生成服务启动脚本
"""

import uvicorn
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """启动服务"""
    print("🚀 启动JSON DAG报告生成服务...")
    print("📚 API文档: http://localhost:8000/docs")
    print("📖 ReDoc文档: http://localhost:8000/redoc")
    print("💡 健康检查: http://localhost:8000/health")
    print("-" * 50)
    
    # 启动FastAPI服务
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()