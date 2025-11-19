"""
报告生成器处理器
将JSON配置转换为Markdown格式
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.config_models import (
    ReportConfig, ReportElement, TextElement, TitleElement,
    ListElement, CodeElement, TableElement, ChartElement,
    DAGElement, ChartType, ChartStyle
)
from handlers.chart_converter import ChartConverter
from handlers.dag_handler import DAGHandler


class ReportGenerator:
    """报告生成器主类"""
    
    def __init__(self):
        self.chart_converter = ChartConverter()
        self.dag_handler = DAGHandler()
        
    def generate_report(self, config: ReportConfig, options: Optional[Dict[str, Any]] = None) -> str:
        """
        生成Markdown报告
        
        Args:
            config: 报告配置
            options: 生成选项
            
        Returns:
            生成的Markdown内容
        """
        if options is None:
            options = {}
            
        markdown_parts = []
        
        # 添加报告头部信息
        markdown_parts.append(self._generate_header(config))
        
        # 生成报告内容元素
        for element in config.elements:
            content = self._generate_element(element, options)
            if content:
                markdown_parts.append(content)
        
        # 添加报告尾部信息
        markdown_parts.append(self._generate_footer(config))
        
        # 合并所有内容
        markdown_content = "\n\n".join(markdown_parts)
        
        # 后处理
        markdown_content = self._post_process(markdown_content, options)
        
        return markdown_content
    
    def _generate_header(self, config: ReportConfig) -> str:
        """生成报告头部"""
        header_parts = []
        
        # 报告标题
        header_parts.append(f"# {config.title}")
        
        # 报告描述
        if config.description:
            header_parts.append(f"\n{config.description}")
        
        # 元数据信息
        metadata_lines = []
        if config.author:
            metadata_lines.append(f"**作者**: {config.author}")
        if config.date:
            metadata_lines.append(f"**日期**: {config.date}")
        if config.version:
            metadata_lines.append(f"**版本**: {config.version}")
            
        if metadata_lines:
            header_parts.append("\n## 报告信息")
            header_parts.extend(metadata_lines)
        
        return "\n".join(header_parts)
    
    def _generate_footer(self, config: ReportConfig) -> str:
        """生成报告尾部"""
        footer_parts = []
        
        # 添加生成时间
        footer_parts.append(f"\n---\n*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        # 添加自定义元数据
        if config.metadata:
            footer_parts.append("\n## 元数据")
            for key, value in config.metadata.items():
                footer_parts.append(f"- **{key}**: {value}")
        
        return "\n".join(footer_parts)
    
    def _generate_element(self, element: ReportElement, options: Dict[str, Any]) -> Optional[str]:
        """生成单个元素的Markdown内容"""
        element_type = element.type
        
        if element_type == "text":
            return self._generate_text_element(element, options)
        elif element_type == "title":
            return self._generate_title_element(element, options)
        elif element_type == "list":
            return self._generate_list_element(element, options)
        elif element_type == "code":
            return self._generate_code_element(element, options)
        elif element_type == "table":
            return self._generate_table_element(element, options)
        elif element_type == "chart":
            return self._generate_chart_element(element, options)
        elif element_type == "dag":
            return self._generate_dag_element(element, options)
        else:
            return f"<!-- 未支持的元素类型: {element_type} -->"
    
    def _generate_text_element(self, element: TextElement, options: Dict[str, Any]) -> str:
        """生成文本元素"""
        content = element.content
        
        # 应用样式
        if element.style == "bold":
            content = f"**{content}**"
        elif element.style == "italic":
            content = f"*{content}*"
        elif element.style == "quote":
            content = f"> {content}"
        elif element.style == "highlight":
            content = f"**{content}**"
            
        return content
    
    def _generate_title_element(self, element: TitleElement, options: Dict[str, Any]) -> str:
        """生成标题元素"""
        level = element.level
        content = element.content
        
        # 构建标题
        if 1 <= level <= 6:
            return f"{'#' * level} {content}"
        else:
            return f"## {content}"  # 默认二级标题
    
    def _generate_list_element(self, element: ListElement, options: Dict[str, Any]) -> str:
        """生成列表元素"""
        lines = []
        
        if element.ordered:
            # 有序列表
            for i, item in enumerate(element.items, 1):
                lines.append(f"{i}. {item}")
        else:
            # 无序列表
            for item in element.items:
                lines.append(f"- {item}")
        
        return "\n".join(lines)
    
    def _generate_code_element(self, element: CodeElement, options: Dict[str, Any]) -> str:
        """生成代码块元素"""
        language = element.language or "python"
        content = element.content
        
        # 清理内容，避免格式问题
        content = content.strip()
        
        return f"``{language}\n{content}\n```"
    
    def _generate_table_element(self, element: TableElement, options: Dict[str, Any]) -> str:
        """生成表格元素"""
        lines = []
        
        # 表头
        header = "| " + " | ".join(element.headers) + " |"
        separator = "| " + " | ".join(["---"] * len(element.headers)) + " |"
        lines.append(header)
        lines.append(separator)
        
        # 表格数据
        for row in element.rows:
            row_line = "| " + " | ".join(str(cell) for cell in row) + " |"
            lines.append(row_line)
        
        return "\n".join(lines)
    
    def _generate_chart_element(self, element: ChartElement, options: Dict[str, Any]) -> str:
        """生成图表元素"""
        lines = []
        
        # 图表标题和描述
        lines.append(f"## {element.title}")
        if element.description:
            lines.append(f"\n{element.description}")
        
        # 生成ECharts配置
        try:
            echarts_config = self.chart_converter.convert_to_echarts(element)
            
            # 添加简化格式的ECharts配置
            lines.append(f'\n```echarts\n{json.dumps(echarts_config, ensure_ascii=False, indent=2)}\n```')
            
        except Exception as e:
            # 降级处理，显示数据表格
            lines.append("\n*图表生成失败，显示数据表格:*")
            lines.append(self._generate_fallback_table(element))
        
        return "\n".join(lines)
    
    def _generate_dag_element(self, element: DAGElement, options: Dict[str, Any]) -> str:
        """生成DAG元素"""
        lines = []
        
        # DAG标题和描述
        lines.append(f"## {element.title}")
        if element.description:
            lines.append(f"\n{element.description}")
        
        # 生成DAG可视化
        try:
            mermaid_code = self.dag_handler.convert_to_mermaid(element)
            lines.append(f"\n```mermaid\n{mermaid_code}\n```")
            lines.append("\n*注: DAG流程图需要在支持Mermaid的环境中查看*")
            
        except Exception as e:
            # 降级处理，显示节点列表
            lines.append("\n*DAG生成失败，显示节点列表:*")
            lines.extend(self._generate_dag_list(element))
        
        return "\n".join(lines)
    
    def _generate_fallback_table(self, element: ChartElement) -> str:
        """生成图表降级表格"""
        lines = []
        lines.append("\n| 数据项 | 值 |")
        lines.append("|---------|---------|")
        
        # 根据图表类型生成表格
        if element.data.categories and element.data.series:
            for i, category in enumerate(element.data.categories):
                value = None
                if element.data.series and len(element.data.series) > 0:
                    series_data = element.data.series[0].get('data', [])
                    if i < len(series_data):
                        value = series_data[i]
                if value is not None:
                    lines.append(f"| {category} | {value} |")
        elif element.data.values:
            for i, value in enumerate(element.data.values):
                lines.append(f"| 数据点 {i+1} | {value} |")
        
        return "\n".join(lines)
    
    def _generate_dag_list(self, element: DAGElement) -> List[str]:
        """生成DAG降级列表"""
        lines = []
        
        lines.append("\n### 节点列表")
        for node in element.nodes:
            status_indicator = "⏳" if node.status == "pending" else "✅" if node.status == "completed" else "❌"
            lines.append(f"- {status_indicator} **{node.name}** ({node.id})")
            if node.description:
                lines.append(f"  - 描述: {node.description}")
            if node.result:
                if isinstance(node.result, str):
                    lines.append(f"  - 结果: {node.result}")
                else:
                    lines.append(f"  - 结果: {json.dumps(node.result, ensure_ascii=False)}")
        
        lines.append("\n### 流程连接")
        for edge in element.edges:
            lines.append(f"- {edge.from_node} → {edge.to_node}")
            if edge.label:
                lines.append(f"  - 条件: {edge.label}")
        
        return lines
    
    def _post_process(self, content: str, options: Dict[str, Any]) -> str:
        """后处理Markdown内容"""
        # 移除多余的空行
        content = content.replace("\n\n\n", "\n\n")
        
        # 添加TOC (Table of Contents) 如果需要
        if options.get('add_toc', False):
            toc = self._generate_toc(content)
            content = f"{toc}\n\n{content}"
        
        # 添加样式如果需要
        if options.get('add_styles', False):
            content = self._add_styles(content, options)
        
        return content
    
    def _generate_toc(self, content: str) -> str:
        """生成目录"""
        lines = content.split('\n')
        toc_lines = ["## 目录"]
        
        for line in lines:
            if line.startswith('#') and line[1] != '#':
                # 只添加一级和二级标题
                level = len(line) - len(line.lstrip('#'))
                if level <= 2:
                    title = line.lstrip('#').strip()
                    anchor = title.lower().replace(' ', '-').replace('.', '').replace(',', '')
                    toc_lines.append(f"- [{title}](#{anchor})")
        
        return "\n".join(toc_lines)
    
    def _add_styles(self, content: str, options: Dict[str, Any]) -> str:
        """添加样式（预留接口）"""
        # 这里可以添加CSS样式或Markdown扩展
        # 目前返回原内容
        return content