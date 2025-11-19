# JSON DAG报告生成服务

基于Python FastAPI的JSON配置报告生成服务，支持ECharts图表和DAG流程可视化，生成vditor兼容的Markdown报告。

## 🚀 功能特性

### 核心功能
- **JSON配置驱动**: 通过JSON配置文件定义报告结构和内容
- **多元素支持**: 文本、标题、列表、代码块、表格、图表、DAG流程图
- **图表可视化**: 支持柱状图、折线图、饼图、散点图、面积图、直方图
- **内置样式**: 6种预设图表样式 (default, modern, classic, minimal, colorful, professional)
- **DAG可视化**: 支持工作流程图的可视化展示
- **vditor兼容**: 生成的Markdown文件完美兼容vditor编辑器
- **纯Python实现**: 无外部依赖，符合您的要求

### 技术特性
- **FastAPI框架**: 高性能异步API服务
- **Pydantic验证**: 强类型数据模型验证
- **自动文档**: 集成Swagger UI和ReDoc文档
- **错误处理**: 完善的错误处理和日志记录
- **文件管理**: 自动文件保存、下载、清理功能

## 📁 项目结构

```
dag-report-service/
├── main.py                     # FastAPI应用入口
├── models/
│   └── config_models.py        # 数据模型定义
├── handlers/
│   ├── report_generator.py     # 报告生成器
│   ├── chart_converter.py      # 图表转换器
│   ├── dag_handler.py          # DAG处理器
│   └── file_manager.py         # 文件管理器
├── examples/                   # 示例配置
│   ├── basic_text_report.json  # 基础文本报告
│   ├── chart_reports.json      # 图表报告
│   ├── dag_flow_report.json    # DAG流程报告
│   └── edge_cases_report.json  # 边界情况测试
├── requirements.txt            # 依赖包列表
├── start_service.py            # 服务启动脚本
└── README.md                   # 项目文档
```

## 🛠️ 安装和使用

### 环境要求
- Python 3.7+
- pip包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd dag-report-service
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动服务**
```bash
python start_service.py
```

或者使用传统的启动方式:
```bash
python main.py
```

4. **访问API文档**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📊 API端点

### 主要端点

#### 1. 生成报告
```http
POST /generate
Content-Type: application/json

{
  "config": {
    "title": "报告标题",
    "description": "报告描述",
    "author": "作者",
    "elements": [...]
  },
  "output_format": "markdown",
  "filename": "optional_filename"
}
```

#### 2. 验证配置
```http
POST /validate
Content-Type: application/json

{
  "config": { ... },
  "options": { ... }
}
```

#### 3. 下载报告
```http
GET /download/{filename}
```

#### 4. 获取示例
```http
GET /examples                    # 列出所有示例
GET /examples/{filename}         # 获取指定示例
GET /styles                      # 获取支持的图表样式
```

### 健康检查和状态
```http
GET /                           # 服务信息
GET /health                     # 健康检查
GET /files                      # 列出生成的文件
DELETE /cleanup                 # 清理临时文件
```

## 📝 配置说明

### 支持的元素类型

#### 1. 文本元素
```json
{
  "type": "text",
  "content": "文本内容",
  "style": "normal"  // normal, bold, italic, quote, highlight
}
```

#### 2. 标题元素
```json
{
  "type": "title",
  "content": "标题内容",
  "level": 1  // 1-6级标题
}
```

#### 3. 列表元素
```json
{
  "type": "list",
  "items": ["列表项1", "列表项2"],
  "ordered": false  // false: 无序列表, true: 有序列表
}
```

#### 4. 代码块元素
```json
{
  "type": "code",
  "content": "代码内容",
  "language": "python"
}
```

#### 5. 表格元素
```json
{
  "type": "table",
  "headers": ["列1", "列2", "列3"],
  "rows": [
    ["数据1", "数据2", "数据3"],
    ["数据4", "数据5", "数据6"]
  ]
}
```

#### 6. 图表元素
```json
{
  "type": "chart",
  "chart_type": "bar",           // bar, line, pie, scatter, area, histogram
  "title": "图表标题",
  "description": "图表描述",
  "style": "default",            // default, modern, classic, minimal, colorful, professional
  "data": {
    "categories": ["A", "B", "C", "D"],
    "series": [
      {
        "name": "数据系列名称",
        "data": [10, 20, 30, 40],
        "stack": "总量"           // 可选: 用于创建堆叠图表
      }
    ]
  },
  "width": "100%",
  "height": "400px"
}
```

#### 7. DAG流程图元素
```json
{
  "type": "dag",
  "title": "DAG标题",
  "description": "DAG描述",
  "nodes": [
    {
      "id": "node1",
      "name": "节点名称",
      "description": "节点描述",
      "status": "completed",     // pending, running, completed, failed
      "timestamp": "2025-11-17 10:00:00",
      "result": "节点结果",
      "position": {"x": 0, "y": 0}
    }
  ],
  "edges": [
    {
      "from_node": "node1",
      "to_node": "node2",
      "label": "连接条件"
    }
  ],
  "layout": "hierarchical"
}
```

### 内置图表样式

1. **default**: 默认样式，通用性强
2. **modern**: 现代风格，渐变色彩
3. **classic**: 经典风格，传统配色
4. **minimal**: 简约风格，低饱和度
5. **colorful**: 彩色风格，鲜艳配色
6. **professional**: 专业风格，商务配色

## 📋 使用示例

### 1. 基础文本报告
```json
{
  "config": {
    "title": "数据分析报告",
    "description": "这是一个数据分析示例报告",
    "author": "MiniMax Agent",
    "elements": [
      {
        "type": "title",
        "content": "项目概述",
        "level": 2
      },
      {
        "type": "text",
        "content": "本报告分析了数据处理的主要步骤和结果。",
        "style": "normal"
      }
    ]
  }
}
```

### 2. 包含图表的报告
```json
{
  "config": {
    "title": "销售数据报告",
    "elements": [
      {
        "type": "chart",
        "chart_type": "bar",
        "title": "月度销售额",
        "style": "modern",
        "data": {
          "categories": ["1月", "2月", "3月", "4月"],
          "series": [
            {
              "name": "销售额",
              "data": [100, 120, 150, 180]
            }
          ]
        }
      }
    ]
  }
}
```

### 3. DAG流程报告
```json
{
  "config": {
    "title": "机器学习流程",
    "elements": [
      {
        "type": "dag",
        "title": "ML项目流程",
        "nodes": [
          {
            "id": "data_collection",
            "name": "数据收集",
            "status": "completed"
          },
          {
            "id": "data_processing",
            "name": "数据处理",
            "status": "running"
          }
        ],
        "edges": [
          {
            "from_node": "data_collection",
            "to_node": "data_processing"
          }
        ]
      }
    ]
  }
}
```

## 📥 JSON配置教程

### 基础结构
JSON配置文件必须包含以下基本结构：

```json
{
  "config": {
    "title": "报告标题",
    "description": "报告描述（可选）",
    "author": "作者（可选）",
    "date": "日期（可选）",
    "version": "版本（可选，默认1.0.0）",
    "elements": [
      // 报告元素列表
    ]
  },
  "output_format": "markdown",
  "filename": "可选的文件名"
}
```

### 创建文本元素
文本元素是最基本的元素类型：

```json
{
  "type": "text",
  "content": "这是文本内容",
  "style": "normal"  // 可选值: normal, bold, italic, quote, highlight
}
```

### 创建标题元素
标题元素用于创建不同级别的标题：

```json
{
  "type": "title",
  "content": "这是标题",
  "level": 1  // 1-6级标题，1为最高级
}
```

### 创建列表元素
列表元素可以创建有序或无序列表：

```json
{
  "type": "list",
  "items": [
    "列表项1",
    "列表项2",
    "列表项3"
  ],
  "ordered": false  // false为无序列表，true为有序列表
}
```

### 创建代码块元素
代码块元素用于展示代码：

```json
{
  "type": "code",
  "content": "print('Hello World')",
  "language": "python"  // 编程语言，如python, javascript, java等
}
```

### 创建表格元素
表格元素用于展示结构化数据：

```json
{
  "type": "table",
  "headers": ["列1", "列2", "列3"],
  "rows": [
    ["数据1", "数据2", "数据3"],
    ["数据4", "数据5", "数据6"]
  ]
}
```

### 创建图表元素
图表元素用于可视化数据：

```json
{
  "type": "chart",
  "chart_type": "bar",  // 图表类型: bar, line, pie, scatter, area, histogram
  "title": "图表标题",
  "description": "图表描述（可选）",
  "style": "default",   // 样式: default, modern, classic, minimal, colorful, professional
  "data": {
    // 数据结构根据图表类型有所不同
  },
  "width": "100%",      // 图表宽度
  "height": "400px"     // 图表高度
}
```

#### 柱状图/折线图/面积图数据格式
```json
{
  "categories": ["类别1", "类别2", "类别3"],
  "series": [
    {
      "name": "系列1",
      "data": [10, 20, 30],
      "stack": "总量"  // 可选，用于创建堆叠图表
    }
  ]
}
```

#### 饼图/直方图数据格式
```json
{
  "categories": ["类别1", "类别2", "类别3"],
  "values": [25, 35, 40]
}
```

### 创建DAG流程图元素
DAG元素用于可视化工作流程：

```json
{
  "type": "dag",
  "title": "流程图标题",
  "description": "流程图描述（可选）",
  "nodes": [
    {
      "id": "unique_id",
      "name": "节点名称",
      "description": "节点描述（可选）",
      "status": "pending",  // 状态: pending, running, completed, failed
      "timestamp": "2025-11-17 10:00:00（可选）",
      "result": "节点结果（可选）"
    }
  ],
  "edges": [
    {
      "from_node": "node_id_1",
      "to_node": "node_id_2",
      "label": "连接标签（可选）"
    }
  ]
}
```

### 完整示例
以下是一个包含多种元素的完整配置示例：

```json
{
  "config": {
    "title": "项目报告示例",
    "description": "这是一个完整的项目报告示例",
    "author": "MiniMax Agent",
    "date": "2025-11-17",
    "version": "1.0.0",
    "elements": [
      {
        "type": "title",
        "content": "项目概述",
        "level": 1
      },
      {
        "type": "text",
        "content": "本报告详细介绍了项目的各个方面。",
        "style": "normal"
      },
      {
        "type": "title",
        "content": "关键指标",
        "level": 2
      },
      {
        "type": "chart",
        "chart_type": "bar",
        "title": "月度销售数据",
        "description": "展示过去几个月的销售情况",
        "style": "modern",
        "data": {
          "categories": ["1月", "2月", "3月", "4月"],
          "series": [
            {
              "name": "销售额",
              "data": [120, 150, 180, 200]
            }
          ]
        }
      },
      {
        "type": "title",
        "content": "实施步骤",
        "level": 2
      },
      {
        "type": "list",
        "items": [
          "数据收集",
          "数据分析",
          "结果展示",
          "报告生成"
        ],
        "ordered": true
      }
    ]
  },
  "output_format": "markdown",
  "filename": "project_report"
}
```

## 🔧 配置选项

### 生成选项
```json
{
  "config": { ... },
  "options": {
    "add_toc": false,        // 是否添加目录
    "add_styles": false,     // 是否添加样式
    "output_format": "markdown"
  }
}
```

### 图表配置选项

#### 支持的图表类型
- `bar`: 柱状图
- `line`: 折线图
- `pie`: 饼图
- `scatter`: 散点图
- `area`: 面积图
- `histogram`: 直方图

#### 数据格式

**分类数据图表** (bar, line, area, scatter):
```json
{
  "categories": ["A", "B", "C", "D"],
  "series": [
    {
      "name": "系列1",
      "data": [10, 20, 30, 40]
    }
  ]
}
```

**简单数值图表** (pie, histogram):
```json
{
  "categories": ["类别1", "类别2", "类别3"],
  "values": [25, 35, 40]
}
```

## 🧪 测试

### 运行示例
服务提供了4个预置示例用于测试：

1. **basic_text_report.json** - 基础文本报告
2. **chart_reports.json** - 包含多种图表的报告
3. **dag_flow_report.json** - DAG流程图报告
4. **edge_cases_report.json** - 边界情况测试

### 测试步骤
```bash
# 启动服务
python start_service.py

# 在另一个终端测试
curl -X POST http://localhost:8000/examples/basic_text_report.json | curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d @-
```

在Windows PowerShell中，可以使用以下命令发送JSON文件:
```powershell
# 方法1: 使用PowerShell的Invoke-WebRequest
$Body = [System.IO.File]::ReadAllBytes("examples/basic_text_report.json")
Invoke-WebRequest -Uri http://localhost:8000/generate -Method POST -Headers @{ 'Content-Type' = 'application/json' } -Body $Body

# 方法2: 使用curl (如果已安装)
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d (Get-Content examples/basic_text_report.json | ConvertTo-Json -Depth 100)
```

## 📈 性能特性

- **并发处理**: 支持多并发报告生成
- **内存优化**: 自动清理临时文件
- **错误恢复**: 图表生成失败时自动降级为数据表格
- **大文件处理**: 支持大量数据元素的处理
- **快速响应**: 典型报告生成时间 < 5秒

## 🔒 错误处理

### 常见错误类型
1. **配置验证错误**: JSON格式错误、必填字段缺失
2. **数据验证错误**: 图表数据不完整、格式错误
3. **DAG验证错误**: 循环引用、节点ID重复
4. **文件操作错误**: 权限问题、磁盘空间不足

### 错误响应格式
```json
{
  "success": false,
  "error_message": "详细错误信息",
  "errors": ["具体错误列表"],
  "metadata": {}
}
```

## 📚 vditor集成

生成的Markdown文件完全兼容vditor编辑器，支持：
- ✅ 文本格式渲染
- ✅ 表格渲染
- ✅ 代码高亮
- ✅ 标题层级
- ✅ 列表格式
- ⚠️ 图表显示 (需要JavaScript环境)

### 图表在vditor中的显示
图表会以HTML/JavaScript代码块形式出现，需要在支持JavaScript的环境中才能正常显示图表，否则会降级显示为数据表格。

## 🤝 贡献指南

欢迎提交问题报告和功能请求！

### 开发流程
1. Fork项目
2. 创建功能分支
3. 提交代码更改
4. 创建Pull Request

### 代码规范
- 遵循PEP 8代码风格
- 添加必要的文档字符串
- 包含单元测试
- 更新相关文档

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 支持

如有问题或建议，请通过以下方式联系：
- 创建GitHub Issue
- 发送邮件到开发团队

---
