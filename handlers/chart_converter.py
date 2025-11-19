"""
图表转换器
将简化的图表配置转换为ECharts格式
"""

import json
from typing import Dict, Any, List, Optional
from models.config_models import (
    ChartElement, ChartType, ChartStyle, ChartData, PRESET_STYLES
)


class ChartConverter:
    """图表转换器"""
    
    def __init__(self, preset_styles: Dict[ChartStyle, Dict[str, Any]] = None):
        self.preset_styles = preset_styles or PRESET_STYLES
    
    def convert_to_echarts(self, chart_element: ChartElement) -> Dict[str, Any]:
        """
        将ChartElement转换为ECharts配置
        
        Args:
            chart_element: 图表元素配置
            
        Returns:
            ECharts配置字典
        """
        # 获取预设样式
        style_config = self.preset_styles.get(chart_element.style, self.preset_styles[ChartStyle.DEFAULT])
        
        # 构建基础配置
        echarts_config = {
            "title": {
                "text": chart_element.title
            },
            "tooltip": {
                "trigger": "axis" if chart_element.chart_type in [ChartType.BAR, ChartType.LINE, ChartType.AREA, ChartType.SCATTER] else "item"
            }
        }
        
        # 添加图例
        if chart_element.data.series and len(chart_element.data.series) > 1:
            echarts_config["legend"] = {
                "data": [series.get("name", f"系列{i+1}") for i, series in enumerate(chart_element.data.series)]
            }
        
        # 添加网格设置
        echarts_config["grid"] = style_config["grid"]
        
        # 根据图表类型处理
        if chart_element.chart_type == ChartType.BAR:
            self._process_bar_chart(echarts_config, chart_element, style_config)
        elif chart_element.chart_type == ChartType.LINE:
            self._process_line_chart(echarts_config, chart_element, style_config)
        elif chart_element.chart_type == ChartType.PIE:
            self._process_pie_chart(echarts_config, chart_element, style_config)
        elif chart_element.chart_type == ChartType.SCATTER:
            self._process_scatter_chart(echarts_config, chart_element, style_config)
        elif chart_element.chart_type == ChartType.AREA:
            self._process_area_chart(echarts_config, chart_element, style_config)
        elif chart_element.chart_type == ChartType.HISTOGRAM:
            self._process_histogram_chart(echarts_config, chart_element, style_config)
        else:
            raise ValueError(f"不支持的图表类型: {chart_element.chart_type}")
        
        return echarts_config
    
    def validate_chart_config(self, chart_element: ChartElement) -> bool:
        """
        验证图表配置
        
        Args:
            chart_element: 图表元素配置
            
        Returns:
            验证是否通过
        """
        # 验证标题
        if not chart_element.title or not chart_element.title.strip():
            raise ValueError("图表标题不能为空")
        
        # 验证数据
        if not chart_element.data:
            raise ValueError("图表数据不能为空")
        
        # 根据图表类型验证数据
        if chart_element.chart_type == ChartType.PIE:
            if not chart_element.data.values or len(chart_element.data.values) == 0:
                raise ValueError("饼图需要数值数据")
        else:
            if not chart_element.data.categories:
                raise ValueError("柱状图、折线图等需要分类数据")
            if not chart_element.data.series:
                raise ValueError("图表需要数据系列")
        
        return True
    
    def _process_bar_chart(self, config: Dict[str, Any], chart_element: ChartElement, style_config: Dict[str, Any]):
        """处理柱状图"""
        # X轴配置
        config["xAxis"] = {
            "type": "category",
            "data": chart_element.data.categories
        }
        
        # Y轴配置
        config["yAxis"] = {
            "type": "value"
        }
        
        # 数据系列
        config["series"] = []
        for i, series in enumerate(chart_element.data.series):
            series_config = {
                "name": series.get("name", f"系列{i+1}"),
                "type": "bar",
                "data": series.get("data", [])
            }
            
            # 如果指定了堆叠，则添加堆叠属性
            if series.get("stack"):
                series_config["stack"] = series["stack"]
                
            config["series"].append(series_config)
    
    def _process_line_chart(self, config: Dict[str, Any], chart_element: ChartElement, style_config: Dict[str, Any]):
        """处理折线图"""
        # X轴配置
        config["xAxis"] = {
            "type": "category",
            "data": chart_element.data.categories,
            "boundaryGap": False
        }
        
        # Y轴配置
        config["yAxis"] = {
            "type": "value"
        }
        
        # 数据系列
        config["series"] = []
        for i, series in enumerate(chart_element.data.series):
            series_config = {
                "name": series.get("name", f"系列{i+1}"),
                "type": "line",
                "data": series.get("data", [])
            }
            
            # 如果指定了堆叠，则添加堆叠属性
            if series.get("stack"):
                series_config["stack"] = series["stack"]
                
            config["series"].append(series_config)
    
    def _process_pie_chart(self, config: Dict[str, Any], chart_element: ChartElement, style_config: Dict[str, Any]):
        """处理饼图"""
        # 饼图不需要X、Y轴
        config.pop("xAxis", None)
        config.pop("yAxis", None)
        config.pop("grid", None)
        
        # 数据系列
        if chart_element.data.categories and chart_element.data.values:
            pie_data = [
                {"name": category, "value": value}
                for category, value in zip(chart_element.data.categories, chart_element.data.values)
            ]
        else:
            # 使用简单的数值数组
            pie_data = [{"name": f"数据点{i+1}", "value": value} 
                       for i, value in enumerate(chart_element.data.values or [])]
        
        config["series"] = [{
            "name": chart_element.title,
            "type": "pie",
            "radius": "50%",
            "data": pie_data
        }]
    
    def _process_scatter_chart(self, config: Dict[str, Any], chart_element: ChartElement, style_config: Dict[str, Any]):
        """处理散点图"""
        # X轴配置
        config["xAxis"] = {
            "type": "value"
        }
        
        # Y轴配置
        config["yAxis"] = {
            "type": "value"
        }
        
        # 数据系列
        config["series"] = []
        for i, series in enumerate(chart_element.data.series):
            config["series"].append({
                "name": series.get("name", f"系列{i+1}"),
                "type": "scatter",
                "data": series.get("data", [])
            })
    
    def _process_area_chart(self, config: Dict[str, Any], chart_element: ChartElement, style_config: Dict[str, Any]):
        """处理面积图"""
        # X轴配置
        config["xAxis"] = {
            "type": "category",
            "data": chart_element.data.categories,
            "boundaryGap": False
        }
        
        # Y轴配置
        config["yAxis"] = {
            "type": "value"
        }
        
        # 数据系列
        config["series"] = []
        for i, series in enumerate(chart_element.data.series):
            series_config = {
                "name": series.get("name", f"系列{i+1}"),
                "type": "line",
                "data": series.get("data", []),
                "areaStyle": {}
            }
            
            # 如果指定了堆叠，则添加堆叠属性
            if series.get("stack"):
                series_config["stack"] = series["stack"]
                
            config["series"].append(series_config)
    
    def _process_histogram_chart(self, config: Dict[str, Any], chart_element: ChartElement, style_config: Dict[str, Any]):
        """处理直方图"""
        # 如果没有提供分组数据，需要计算直方图
        if chart_element.data.values and not chart_element.data.categories:
            # 简单的直方图分组
            values = chart_element.data.values
            min_val = min(values)
            max_val = max(values)
            num_bins = min(10, len(values))  # 最多10个分组
            
            # 计算分组边界
            bin_width = (max_val - min_val) / num_bins
            bins = []
            counts = []
            
            for i in range(num_bins):
                bin_start = min_val + i * bin_width
                bin_end = min_val + (i + 1) * bin_width
                bin_label = f"{bin_start:.1f}-{bin_end:.1f}"
                
                # 计算该分组的数量
                count = sum(1 for v in values if bin_start <= v < bin_end)
                if i == num_bins - 1:  # 最后一个分组包含最大值
                    count = sum(1 for v in values if bin_start <= v <= bin_end)
                
                bins.append(bin_label)
                counts.append(count)
            
            # 更新数据
            chart_element.data.categories = bins
            chart_element.data.series = [{"name": "频次", "data": counts}]
        
        # 使用柱状图逻辑处理
        self._process_bar_chart(config, chart_element, style_config)
    
    def convert_simple_data(self, chart_element: ChartElement) -> Dict[str, Any]:
        """
        将简单的数据格式转换为标准的图表数据格式
        
        Args:
            chart_element: 图表元素
            
        Returns:
            标准化的图表数据
        """
        data = chart_element.data
        
        # 如果只有简单数值数组，转换为标准格式
        if data.values and not data.categories:
            categories = [f"数据点{i+1}" for i in range(len(data.values))]
            data.categories = categories
        
        # 如果有分类数据但没有系列，创建一个默认系列
        if data.categories and not data.series:
            if data.values:
                data.series = [{"name": "数据", "data": data.values}]
            else:
                data.series = [{"name": "数据", "data": [1] * len(data.categories)}]
        
        return data
    
    def get_echarts_options(self, chart_element: ChartElement) -> Dict[str, Any]:
        """
        获取额外的ECharts配置选项
        
        Args:
            chart_element: 图表元素
            
        Returns:
            ECharts配置选项
        """
        options = {}
        
        # 添加动画效果
        options["animation"] = True
        options["animationDuration"] = 1000
        options["animationEasing"] = "cubicOut"
        
        # 添加工具提示
        options["tooltip"] = {
            "trigger": "axis" if chart_element.chart_type in [ChartType.BAR, ChartType.LINE, ChartType.AREA] else "item"
        }
        
        # 添加缩放功能（对于大数据集）
        if chart_element.data.categories and len(chart_element.data.categories) > 20:
            options["dataZoom"] = [
                {
                    "type": "inside",
                    "start": 0,
                    "end": 100
                }
            ]
        
        return options