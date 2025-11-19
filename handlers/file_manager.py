"""
文件管理器
处理文件的保存、下载、清理等操作
"""

import os
import shutil
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FileManager:
    """文件管理器"""
    
    def __init__(self, base_dir: str = "generated_reports"):
        self.base_dir = base_dir
        self.temp_dir = "temp_reports"
        
        # 确保目录存在
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # 清理文件的任务记录
        self.cleanup_tasks = []
    
    def save_file(self, filename: str, content: str, temp: bool = False) -> str:
        """
        保存文件
        
        Args:
            filename: 文件名
            content: 文件内容
            temp: 是否为临时文件
            
        Returns:
            文件路径
        """
        if temp:
            directory = self.temp_dir
        else:
            directory = self.base_dir
        
        file_path = os.path.join(directory, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"文件保存成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"文件保存失败: {e}")
            raise
    
    def read_file(self, filename: str) -> str:
        """
        读取文件内容
        
        Args:
            filename: 文件名
            
        Returns:
            文件内容
        """
        # 首先检查主目录
        file_path = os.path.join(self.base_dir, filename)
        
        if not os.path.exists(file_path):
            # 检查临时目录
            file_path = os.path.join(self.temp_dir, filename)
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件 {filename} 不存在")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
            
        except Exception as e:
            logger.error(f"文件读取失败: {e}")
            raise
    
    def get_file_path(self, filename: str) -> Optional[str]:
        """
        获取文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            文件路径，如果文件不存在返回None
        """
        # 检查主目录
        file_path = os.path.join(self.base_dir, filename)
        if os.path.exists(file_path):
            return file_path
        
        # 检查临时目录
        file_path = os.path.join(self.temp_dir, filename)
        if os.path.exists(file_path):
            return file_path
        
        return None
    
    def file_exists(self, filename: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            filename: 文件名
            
        Returns:
            文件是否存在
        """
        return self.get_file_path(filename) is not None
    
    def list_files(self, temp: bool = False) -> List[Dict[str, Any]]:
        """
        列出文件
        
        Args:
            temp: 是否列出临时文件
            
        Returns:
            文件信息列表
        """
        if temp:
            directory = self.temp_dir
        else:
            directory = self.base_dir
        
        files = []
        
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    
                    files.append({
                        "filename": filename,
                        "path": file_path,
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "temp": temp
                    })
        
        # 按修改时间排序
        files.sort(key=lambda x: x["modified"], reverse=True)
        
        return files
    
    def delete_file(self, filename: str) -> bool:
        """
        删除文件
        
        Args:
            filename: 文件名
            
        Returns:
            删除是否成功
        """
        file_path = self.get_file_path(filename)
        if not file_path:
            return False
        
        try:
            os.remove(file_path)
            logger.info(f"文件删除成功: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"文件删除失败: {e}")
            return False
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        清理临时文件
        
        Args:
            max_age_hours: 文件最大保留时间（小时）
            
        Returns:
            清理的文件数量
        """
        if not os.path.exists(self.temp_dir):
            return 0
        
        cutoff_time = time.time() - (max_age_hours * 3600)
        cleaned_count = 0
        
        try:
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                
                if os.path.isfile(file_path):
                    file_mtime = os.path.getmtime(file_path)
                    
                    if file_mtime < cutoff_time:
                        try:
                            os.remove(file_path)
                            cleaned_count += 1
                            logger.info(f"清理临时文件: {filename}")
                        except Exception as e:
                            logger.error(f"清理文件失败 {filename}: {e}")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理临时文件过程发生错误: {e}")
            return cleaned_count
    
    def schedule_cleanup(self, file_path: str, ttl_hours: int = 24):
        """
        安排文件清理任务
        
        Args:
            file_path: 文件路径
            ttl_hours: 生存时间（小时）
        """
        cleanup_time = time.time() + (ttl_hours * 3600)
        
        self.cleanup_tasks.append({
            "file_path": file_path,
            "cleanup_time": cleanup_time,
            "ttl_hours": ttl_hours
        })
    
    def process_cleanup_tasks(self):
        """处理清理任务"""
        current_time = time.time()
        
        # 过滤出已到清理时间的任务
        due_tasks = [task for task in self.cleanup_tasks if task["cleanup_time"] <= current_time]
        
        for task in due_tasks:
            try:
                if os.path.exists(task["file_path"]):
                    os.remove(task["file_path"])
                    logger.info(f"清理定时任务文件: {task['file_path']}")
            except Exception as e:
                logger.error(f"清理定时任务文件失败 {task['file_path']}: {e}")
        
        # 移除已处理的任务
        self.cleanup_tasks = [task for task in self.cleanup_tasks if task["cleanup_time"] > current_time]
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """
        获取磁盘使用情况
        
        Returns:
            磁盘使用统计
        """
        def get_directory_size(directory):
            """获取目录大小"""
            total_size = 0
            file_count = 0
            
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except OSError:
                        pass
            
            return total_size, file_count
        
        base_size, base_count = get_directory_size(self.base_dir)
        temp_size, temp_count = get_directory_size(self.temp_dir)
        
        return {
            "generated_reports": {
                "size_bytes": base_size,
                "size_mb": round(base_size / 1024 / 1024, 2),
                "file_count": base_count
            },
            "temp_reports": {
                "size_bytes": temp_size,
                "size_mb": round(temp_size / 1024 / 1024, 2),
                "file_count": temp_count
            },
            "total": {
                "size_bytes": base_size + temp_size,
                "size_mb": round((base_size + temp_size) / 1024 / 1024, 2),
                "file_count": base_count + temp_count
            }
        }
    
    def export_files(self, output_dir: str, temp: bool = False) -> bool:
        """
        导出所有文件到指定目录
        
        Args:
            output_dir: 输出目录
            temp: 是否导出临时文件
            
        Returns:
            导出是否成功
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            source_dir = self.temp_dir if temp else self.base_dir
            
            if not os.path.exists(source_dir):
                return False
            
            for filename in os.listdir(source_dir):
                source_path = os.path.join(source_dir, filename)
                dest_path = os.path.join(output_dir, filename)
                
                if os.path.isfile(source_path):
                    shutil.copy2(source_path, dest_path)
            
            logger.info(f"文件导出成功到: {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"文件导出失败: {e}")
            return False
    
    def backup_files(self, backup_dir: str) -> bool:
        """
        备份所有文件
        
        Args:
            backup_dir: 备份目录
            
        Returns:
            备份是否成功
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
            
            os.makedirs(backup_path, exist_ok=True)
            
            # 备份生成的文件
            if os.path.exists(self.base_dir):
                backup_base = os.path.join(backup_path, "generated_reports")
                shutil.copytree(self.base_dir, backup_base)
            
            # 备份临时文件
            if os.path.exists(self.temp_dir):
                backup_temp = os.path.join(backup_path, "temp_reports")
                shutil.copytree(self.temp_dir, backup_temp)
            
            logger.info(f"文件备份成功到: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"文件备份失败: {e}")
            return False
    
    def create_file_info(self, filename: str) -> Dict[str, Any]:
        """
        创建文件信息
        
        Args:
            filename: 文件名
            
        Returns:
            文件信息字典
        """
        file_path = self.get_file_path(filename)
        if not file_path:
            return {"error": f"文件 {filename} 不存在"}
        
        try:
            stat = os.stat(file_path)
            
            return {
                "filename": filename,
                "path": file_path,
                "size": stat.st_size,
                "size_mb": round(stat.st_size / 1024 / 1024, 2),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "exists": True
            }
            
        except Exception as e:
            return {"error": f"获取文件信息失败: {str(e)}"}
    
    def validate_filename(self, filename: str) -> bool:
        """
        验证文件名是否有效
        
        Args:
            filename: 文件名
            
        Returns:
            文件名是否有效
        """
        # 检查非法字符
        illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        
        for char in illegal_chars:
            if char in filename:
                return False
        
        # 检查长度
        if len(filename) > 255:
            return False
        
        # 检查保留名称
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                         'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                         'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        
        name_without_ext = filename.split('.')[0].upper()
        if name_without_ext in reserved_names:
            return False
        
        return True
    
    def ensure_safe_filename(self, filename: str) -> str:
        """
        确保文件名安全
        
        Args:
            filename: 原始文件名
            
        Returns:
            安全的文件名
        """
        # 替换非法字符
        safe_filename = filename
        illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        
        for char in illegal_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # 限制长度
        if len(safe_filename) > 200:
            name, ext = os.path.splitext(safe_filename)
            safe_filename = name[:200-len(ext)] + ext
        
        return safe_filename