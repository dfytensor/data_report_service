"""
DAG处理器
处理DAG (有向无环图) 流程的配置和可视化
"""

from typing import List, Dict, Any, Optional
from collections import deque
from models.config_models import DAGElement, DAGNode, DAGEdge


class DAGHandler:
    """DAG流程图处理器"""
    
    def __init__(self):
        self.validation_errors = []
    
    def convert_to_mermaid(self, dag_element: DAGElement) -> str:
        """
        将DAG元素转换为Mermaid流程图代码
        
        Args:
            dag_element: DAG元素配置
            
        Returns:
            Mermaid流程图代码
        """
        mermaid_lines = []
        
        # 选择合适的图表类型
        if len(dag_element.nodes) <= 10 and len(dag_element.edges) <= 15:
            # 使用简单的flowchart
            mermaid_lines.append("flowchart TD")
        else:
            # 使用更强大的graph
            mermaid_lines.append("graph TD")
        
        # 添加节点
        for node in dag_element.nodes:
            status_style = self._get_node_status_style(node.status)
            node_content = self._escape_mermaid_text(node.name)
            if node.description:
                node_content += f"\\n\\n*{node.description}*"
            
            mermaid_lines.append(f'    {node.id}["{node_content}"]{status_style}')
        
        # 添加边
        for edge in dag_element.edges:
            arrow_text = f'|{edge.label}|' if edge.label else ''
            mermaid_lines.append(f'    {edge.from_node} -->{arrow_text} {edge.to_node}')
        
        return '\n'.join(mermaid_lines)
    
    def validate_dag_config(self, dag_element: DAGElement) -> bool:
        """
        验证DAG配置
        
        Args:
            dag_element: DAG元素配置
            
        Returns:
            验证是否通过
        """
        self.validation_errors = []
        
        # 验证节点列表
        if not dag_element.nodes:
            self.validation_errors.append("DAG必须包含至少一个节点")
            return False
        
        # 检查节点ID的唯一性
        node_ids = [node.id for node in dag_element.nodes]
        if len(node_ids) != len(set(node_ids)):
            self.validation_errors.append("节点ID必须唯一")
            return False
        
        # 验证边
        for edge in dag_element.edges:
            # 检查边是否引用存在的节点
            if edge.from_node not in node_ids:
                self.validation_errors.append(f"边引用了不存在的起始节点: {edge.from_node}")
                return False
            
            if edge.to_node not in node_ids:
                self.validation_errors.append(f"边引用了不存在的目标节点: {edge.to_node}")
                return False
        
        # 检查是否有环
        if not self._check_acyclic(dag_element.nodes, dag_element.edges):
            self.validation_errors.append("DAG不能包含环")
            return False
        
        return True
    
    def _check_acyclic(self, nodes: List[DAGNode], edges: List[DAGEdge]) -> bool:
        """
        检查DAG是否有环
        
        Args:
            nodes: 节点列表
            edges: 边列表
            
        Returns:
            是否无环
        """
        # 构建邻接表
        adjacency = {}
        in_degree = {}
        
        # 初始化
        for node in nodes:
            adjacency[node.id] = []
            in_degree[node.id] = 0
        
        # 构建图
        for edge in edges:
            adjacency[edge.from_node].append(edge.to_node)
            in_degree[edge.to_node] += 1
        
        # Kahn算法检查环
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        processed_count = 0
        
        while queue:
            current = queue.popleft()
            processed_count += 1
            
            for neighbor in adjacency[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return processed_count == len(nodes)
    
    def get_topological_order(self, dag_element: DAGElement) -> List[DAGNode]:
        """
        获取DAG的拓扑排序
        
        Args:
            dag_element: DAG元素配置
            
        Returns:
            按拓扑顺序排列的节点列表
        """
        # 构建邻接表和入度表
        adjacency = {}
        in_degree = {}
        
        # 初始化
        for node in dag_element.nodes:
            adjacency[node.id] = []
            in_degree[node.id] = 0
        
        # 构建图
        for edge in dag_element.edges:
            adjacency[edge.from_node].append(edge.to_node)
            in_degree[edge.to_node] += 1
        
        # Kahn算法拓扑排序
        queue = deque([node for node in dag_element.nodes if in_degree[node.id] == 0])
        topo_order = []
        
        while queue:
            current = queue.popleft()
            topo_order.append(current)
            
            for neighbor_id in adjacency[current.id]:
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    # 找到对应的节点对象
                    neighbor_node = next((n for n in dag_element.nodes if n.id == neighbor_id), None)
                    if neighbor_node:
                        queue.append(neighbor_node)
        
        return topo_order
    
    def get_dag_statistics(self, dag_element: DAGElement) -> Dict[str, Any]:
        """
        获取DAG统计信息
        
        Args:
            dag_element: DAG元素配置
            
        Returns:
            统计信息字典
        """
        # 构建邻接表
        adjacency = {}
        in_degree = {}
        out_degree = {}
        
        # 初始化
        for node in dag_element.nodes:
            adjacency[node.id] = []
            in_degree[node.id] = 0
            out_degree[node.id] = 0
        
        # 统计入度和出度
        for edge in dag_element.edges:
            adjacency[edge.from_node].append(edge.to_node)
            in_degree[edge.to_node] += 1
            out_degree[edge.from_node] += 1
        
        # 统计节点状态
        status_counts = {}
        for node in dag_element.nodes:
            status = node.status or "unknown"
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 找出起始节点和结束节点
        start_nodes = [node for node in dag_element.nodes if in_degree[node.id] == 0]
        end_nodes = [node for node in dag_element.nodes if out_degree[node.id] == 0]
        
        return {
            "total_nodes": len(dag_element.nodes),
            "total_edges": len(dag_element.edges),
            "density": len(dag_element.edges) / max(1, len(dag_element.nodes) * (len(dag_element.nodes) - 1)),
            "start_nodes": [node.id for node in start_nodes],
            "end_nodes": [node.id for node in end_nodes],
            "status_distribution": status_counts,
            "avg_in_degree": sum(in_degree.values()) / len(dag_element.nodes) if dag_element.nodes else 0,
            "avg_out_degree": sum(out_degree.values()) / len(dag_element.nodes) if dag_element.nodes else 0
        }
    
    def generate_execution_order(self, dag_element: DAGElement, start_nodes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        生成DAG执行顺序
        
        Args:
            dag_element: DAG元素配置
            start_nodes: 指定的起始节点列表
            
        Returns:
            执行顺序列表
        """
        # 获取拓扑排序
        topo_order = self.get_topological_order(dag_element)
        
        if not start_nodes:
            # 如果没有指定起始节点，使用所有入度为0的节点
            start_nodes = []
            # 构建入度表
            in_degree = {}
            for node in dag_element.nodes:
                in_degree[node.id] = 0
            for edge in dag_element.edges:
                in_degree[edge.to_node] += 1
            
            start_nodes = [node.id for node in dag_element.nodes if in_degree[node.id] == 0]
        
        execution_order = []
        
        for i, node in enumerate(topo_order):
            # 查找依赖此节点的边
            dependencies = []
            for edge in dag_element.edges:
                if edge.to_node == node.id and edge.label:
                    dependencies.append(edge.label)
            
            execution_order.append({
                "step": i + 1,
                "node_id": node.id,
                "node_name": node.name,
                "dependencies": dependencies,
                "status": node.status or "pending"
            })
        
        return execution_order
    
    def _get_node_status_style(self, status: Optional[str]) -> str:
        """
        根据节点状态获取Mermaid样式
        
        Args:
            status: 节点状态
            
        Returns:
            Mermaid样式代码
        """
        if not status:
            return ""
        
        if status == "completed":
            return ':::success'
        elif status == "failed":
            return ':::danger'
        elif status == "running":
            return ':::warning'
        elif status == "pending":
            return ':::info'
        else:
            return ':::info'
    
    def _escape_mermaid_text(self, text: str) -> str:
        """
        转义Mermaid文本中的特殊字符
        
        Args:
            text: 原始文本
            
        Returns:
            转义后的文本
        """
        # 转义特殊字符
        special_chars = ['"', "'", '\\', '[', ']', '{', '}', '(', ')', '#', '*', '+', '-', '.', '/', ':']
        escaped_text = text
        
        for char in special_chars:
            escaped_text = escaped_text.replace(char, f'\\{char}')
        
        return escaped_text
    
    def optimize_dag_layout(self, dag_element: DAGElement, layout_type: str = "hierarchical") -> DAGElement:
        """
        优化DAG布局
        
        Args:
            dag_element: DAG元素配置
            layout_type: 布局类型 (hierarchical, circular, force)
            
        Returns:
            优化布局后的DAG元素
        """
        if layout_type == "hierarchical":
            return self._hierarchical_layout(dag_element)
        elif layout_type == "circular":
            return self._circular_layout(dag_element)
        elif layout_type == "force":
            return self._force_layout(dag_element)
        else:
            return dag_element
    
    def _hierarchical_layout(self, dag_element: DAGElement) -> DAGElement:
        """层次布局"""
        # 计算每个节点的层级
        node_levels = {}
        
        # 找到起始节点（入度为0）
        in_degree = {}
        for node in dag_element.nodes:
            in_degree[node.id] = 0
        for edge in dag_element.edges:
            in_degree[edge.to_node] += 1
        
        start_nodes = [node for node in dag_element.nodes if in_degree[node.id] == 0]
        
        # BFS计算层级
        queue = [(node, 0) for node in start_nodes]
        visited = set()
        
        while queue:
            current_node, level = queue.pop(0)
            if current_node.id in visited:
                continue
            
            visited.add(current_node.id)
            node_levels[current_node.id] = level
            
            # 添加子节点到队列
            for edge in dag_element.edges:
                if edge.from_node == current_node.id:
                    child_node = next((n for n in dag_element.nodes if n.id == edge.to_node), None)
                    if child_node and child_node.id not in visited:
                        queue.append((child_node, level + 1))
        
        # 分配位置
        nodes_at_level = {}
        for node_id, level in node_levels.items():
            if level not in nodes_at_level:
                nodes_at_level[level] = []
            nodes_at_level[level].append(node_id)
        
        # 为每个节点分配位置
        for node in dag_element.nodes:
            if node.id in node_levels:
                level = node_levels[node.id]
                level_nodes = nodes_at_level[level]
                index = level_nodes.index(node.id)
                
                # 水平分布
                x = (index - len(level_nodes) / 2) * 150
                y = level * 100
                
                node.position = {"x": x, "y": y}
        
        return dag_element
    
    def _circular_layout(self, dag_element: DAGElement) -> DAGElement:
        """圆形布局"""
        n = len(dag_element.nodes)
        radius = max(200, n * 50)
        
        for i, node in enumerate(dag_element.nodes):
            angle = 2 * 3.14159 * i / n
            x = radius * 1.2 * (1 + 0.3 * n * 0.1) * (0.6 + 0.4 * (angle % 1))
            y = radius * 1.2 * (1 + 0.3 * n * 0.1) * (0.6 + 0.4 * ((angle + 0.5) % 1))
            
            node.position = {"x": x, "y": y}
        
        return dag_element
    
    def _force_layout(self, dag_element: DAGElement) -> DAGElement:
        """力导向布局（简化版）"""
        # 简化的力导向布局
        import random
        
        # 初始化随机位置
        for node in dag_element.nodes:
            node.position = {
                "x": random.uniform(-300, 300),
                "y": random.uniform(-200, 200)
            }
        
        # 简单的力导向调整
        for _ in range(5):  # 迭代次数
            for node in dag_element.nodes:
                # 计算斥力（简化）
                force_x = 0
                force_y = 0
                
                for other_node in dag_element.nodes:
                    if node.id != other_node.id:
                        dx = node.position["x"] - other_node.position["x"]
                        dy = node.position["y"] - other_node.position["y"]
                        dist = (dx * dx + dy * dy) ** 0.5
                        if dist > 0:
                            force_x += dx / dist * 100 / dist
                            force_y += dy / dist * 100 / dist
                
                # 应用力
                node.position["x"] += force_x * 0.1
                node.position["y"] += force_y * 0.1
        
        return dag_element