"""
数据模型定义
定义JSON DAG配置和报告生成所需的数据结构
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class ChartType(str, Enum):
    """图表类型枚举"""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    HISTOGRAM = "histogram"


class ChartStyle(str, Enum):
    """内置图表样式枚举"""
    DEFAULT = "default"
    MODERN = "modern"
    CLASSIC = "classic"
    MINIMAL = "minimal"
    COLORFUL = "colorful"
    PROFESSIONAL = "professional"


class TextElement(BaseModel):
    """文本元素模型"""
    type: str = Field(default="text", description="元素类型")
    content: str = Field(..., description="文本内容")
    style: Optional[str] = Field(default="normal", description="文本样式")


class TitleElement(BaseModel):
    """标题元素模型"""
    type: str = Field(default="title", description="元素类型")
    content: str = Field(..., description="标题内容")
    level: int = Field(default=1, ge=1, le=6, description="标题级别 (1-6)")


class ListElement(BaseModel):
    """列表元素模型"""
    type: str = Field(default="list", description="元素类型")
    items: List[str] = Field(..., description="列表项")
    ordered: bool = Field(default=False, description="是否有序列表")


class CodeElement(BaseModel):
    """代码块元素模型"""
    type: str = Field(default="code", description="元素类型")
    content: str = Field(..., description="代码内容")
    language: Optional[str] = Field(default="python", description="编程语言")


class TableElement(BaseModel):
    """表格元素模型"""
    type: str = Field(default="table", description="元素类型")
    headers: List[str] = Field(..., description="表头")
    rows: List[List[str]] = Field(..., description="表格数据")


class ChartData(BaseModel):
    """图表数据模型"""
    categories: Optional[List[str]] = Field(default=None, description="分类数据")
    series: Optional[List[Dict[str, Any]]] = Field(default=None, description="数据系列")
    values: Optional[List[float]] = Field(default=None, description="简单数值数组")


class ChartElement(BaseModel):
    """图表元素模型"""
    type: str = Field(default="chart", description="元素类型")
    chart_type: ChartType = Field(..., description="图表类型")
    title: str = Field(..., description="图表标题")
    description: Optional[str] = Field(default=None, description="图表描述")
    style: ChartStyle = Field(default=ChartStyle.DEFAULT, description="图表样式")
    data: ChartData = Field(..., description="图表数据")
    width: Optional[str] = Field(default="100%", description="图表宽度")
    height: Optional[str] = Field(default="400px", description="图表高度")


class DAGNode(BaseModel):
    """DAG节点模型"""
    id: str = Field(..., description="节点ID")
    name: str = Field(..., description="节点名称")
    description: Optional[str] = Field(default=None, description="节点描述")
    status: Optional[str] = Field(default="pending", description="节点状态")
    timestamp: Optional[str] = Field(default=None, description="时间戳")
    result: Optional[Union[str, Dict[str, Any]]] = Field(default=None, description="执行结果")
    position: Optional[Dict[str, float]] = Field(default=None, description="节点位置 (x, y)")


class DAGEdge(BaseModel):
    """DAG边模型"""
    from_node: str = Field(..., description="起始节点ID")
    to_node: str = Field(..., description="目标节点ID")
    label: Optional[str] = Field(default=None, description="边标签")


class DAGElement(BaseModel):
    """DAG流程图元素模型"""
    type: str = Field(default="dag", description="元素类型")
    title: str = Field(..., description="DAG标题")
    description: Optional[str] = Field(default=None, description="DAG描述")
    nodes: List[DAGNode] = Field(..., description="DAG节点列表")
    edges: List[DAGEdge] = Field(..., description="DAG边列表")
    layout: Optional[str] = Field(default="top-bottom", description="布局方式")


ReportElement = Union[
    TextElement, TitleElement, ListElement, CodeElement, 
    TableElement, ChartElement, DAGElement
]


class ReportConfig(BaseModel):
    """报告配置模型"""
    title: str = Field(..., description="报告标题")
    description: Optional[str] = Field(default=None, description="报告描述")
    author: Optional[str] = Field(default=None, description="作者")
    date: Optional[str] = Field(default=None, description="日期")
    version: Optional[str] = Field(default="1.0.0", description="版本号")
    elements: List[ReportElement] = Field(..., description="报告元素列表")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="额外元数据")

    @validator('date')
    def validate_date(cls, v):
        """验证日期格式"""
        if v and not isinstance(v, str):
            raise ValueError("日期必须是字符串格式")
        return v


class GenerationRequest(BaseModel):
    """生成请求模型"""
    config: ReportConfig = Field(..., description="报告配置")
    output_format: str = Field(default="markdown", description="输出格式")
    filename: Optional[str] = Field(default=None, description="输出文件名")
    options: Optional[Dict[str, Any]] = Field(default=None, description="生成选项")


class GenerationResponse(BaseModel):
    """生成响应模型"""
    success: bool = Field(..., description="是否成功")
    filename: Optional[str] = Field(default=None, description="生成的文件名")
    content: Optional[str] = Field(default=None, description="生成的内容")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="响应元数据")


# 预设的图表样式配置
PRESET_STYLES = {
    ChartStyle.DEFAULT: {
        "color": ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de", "#3ba272"],
        "backgroundColor": "transparent",
        "textStyle": {"fontSize": 14, "color": "#333"},
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True}
    },
    ChartStyle.MODERN: {
        "color": ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe", "#00f2fe"],
        "backgroundColor": "rgba(240, 248, 255, 0.8)",
        "textStyle": {"fontSize": 16, "color": "#2c3e50", "fontFamily": "Arial"},
        "grid": {"left": "5%", "right": "5%", "bottom": "5%", "containLabel": True}
    },
    ChartStyle.CLASSIC: {
        "color": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
        "backgroundColor": "#ffffff",
        "textStyle": {"fontSize": 12, "color": "#000000"},
        "grid": {"left": "10%", "right": "10%", "bottom": "15%", "containLabel": True}
    },
    ChartStyle.MINIMAL: {
        "color": ["#2c3e50", "#34495e", "#7f8c8d", "#95a5a6", "#bdc3c7", "#ecf0f1"],
        "backgroundColor": "#fafafa",
        "textStyle": {"fontSize": 14, "color": "#2c3e50", "fontWeight": "bold"},
        "grid": {"left": "8%", "right": "8%", "bottom": "8%", "containLabel": True}
    },
    ChartStyle.COLORFUL: {
        "color": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#feca57", "#ff9ff3"],
        "backgroundColor": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "textStyle": {"fontSize": 15, "color": "#2c3e50"},
        "grid": {"left": "5%", "right": "5%", "bottom": "5%", "containLabel": True}
    },
    ChartStyle.PROFESSIONAL: {
        "color": ["#2c5282", "#2b6cb0", "#3182ce", "#4299e1", "#63b3ed", "#90cdf4"],
        "backgroundColor": "#ffffff",
        "textStyle": {"fontSize": 13, "color": "#2d3748", "fontFamily": "Microsoft YaHei"},
        "grid": {"left": "3%", "right": "3%", "bottom": "3%", "containLabel": True}
    }
}