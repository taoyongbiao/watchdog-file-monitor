#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务主线检查脚本
用于检查当前任务是否符合项目主线目标
"""

import os
import sys
import re
from typing import Dict, List, Tuple, Optional
from rapidfuzz import fuzz, process


class TaskChecker:
    def __init__(self, task_file_path: str = "task.md"):
        """
        初始化任务检查器
        
        Args:
            task_file_path: 任务文件路径，默认为"task.md"
        """
        self.task_file_path = task_file_path
        self.task_content = ""
        self.versions = {}
        
    def read_task_file(self) -> bool:
        """
        读取任务文件内容
        
        Returns:
            bool: 读取成功返回True，否则返回False
        """
        try:
            with open(self.task_file_path, 'r', encoding='utf-8') as file:
                self.task_content = file.read()
            return True
        except FileNotFoundError:
            print(f"错误: 找不到任务文件 {self.task_file_path}")
            return False
        except Exception as e:
            print(f"错误: 读取任务文件时发生异常: {e}")
            return False
    
    def parse_task_content(self) -> None:
        """
        解析任务文件内容，提取各个版本信息
        """
        # 清空之前的数据
        self.versions = {}
        
        # 按章节分割内容
        sections = re.split(r'^##\s+', self.task_content, flags=re.MULTILINE)
        
        # 第一个是标题，跳过
        for section in sections[1:]:
            lines = section.strip().split('\n')
            if not lines:
                continue
                
            # 获取版本标题
            version_title = lines[0].strip()
            
            # 提取版本状态（进行中、计划中、规划中、已完成）
            status_match = re.search(r'\(([^)]+)\)', version_title)
            status = status_match.group(1) if status_match else "未知"
            
            # 提取版本名称
            version_name = re.sub(r'\s*\([^)]+\)\s*$', '', version_title).strip()
            
            # 存储版本信息
            self.versions[version_name] = {
                "status": status,
                "tasks": lines[1:] if len(lines) > 1 else []
            }
    
    def get_current_version(self) -> Optional[str]:
        """
        获取当前进行中的版本
        
        Returns:
            str: 当前版本名称，如果没有找到则返回None
        """
        for version, info in self.versions.items():
            if info["status"] == "进行中":
                return version
        return None
    
    def check_task_against_main_line(self, task_description: str) -> Tuple[bool, str, str]:
        """
        检查任务是否符合主线目标
        
        Args:
            task_description: 任务描述
            
        Returns:
            tuple: (是否符合主线, 当前版本, 任务归属版本)
        """
        current_version = self.get_current_version()
        if not current_version:
            return False, "未知", "未知"
        
        # 收集所有版本的任务，建立任务字典
        version_tasks = {}
        for version, info in self.versions.items():
            tasks = []
            for task in info["tasks"]:
                # 移除任务前面的状态标记(- [ ])以进行比较
                clean_task = re.sub(r'^-\s*\[[\sx]\]\s*', '', task.strip())
                if clean_task:
                    tasks.append(clean_task)
            version_tasks[version] = tasks
        
        # 使用rapidfuzz进行模糊匹配
        # 设置相似度阈值为75%
        similarity_threshold = 75
        
        # 首先尝试精确匹配
        for version, tasks in version_tasks.items():
            for task in tasks:
                if task and (task in task_description or task_description in task):
                    # 如果是未来版本的任务且当前版本未完成，则判定为偏离主线
                    if version != current_version and self.versions[version]["status"] in ["计划中", "规划中"]:
                        return False, current_version, version
                    # 如果是当前版本的任务，则判定为符合主线
                    elif version == current_version:
                        return True, current_version, current_version
        
        # 如果没有精确匹配，使用模糊匹配
        all_tasks_with_versions = []
        for version, tasks in version_tasks.items():
            for task in tasks:
                if task:
                    all_tasks_with_versions.append((task, version))
        
        if all_tasks_with_versions:
            # 使用多种评分器进行匹配，提高准确性
            matches_partial = process.extract(
                task_description, 
                [task for task, _ in all_tasks_with_versions], 
                scorer=fuzz.partial_ratio,
                limit=3
            )
            
            matches_token_sort = process.extract(
                task_description, 
                [task for task, _ in all_tasks_with_versions], 
                scorer=fuzz.token_sort_ratio,
                limit=3
            )
            
            # 合并匹配结果
            all_matches = matches_partial + matches_token_sort
            best_match = None
            best_score = 0
            best_version = None
            
            for match_task, score, idx in all_matches:
                if score > best_score:
                    best_score = score
                    best_match = match_task
                    # 找到对应的版本
                    for task, version in all_tasks_with_versions:
                        if task == match_task:
                            best_version = version
                            break
            
            # 如果最佳匹配分数超过阈值
            if best_match and best_score >= similarity_threshold and best_version:
                # 如果是未来版本的任务且当前版本未完成，则判定为偏离主线
                if best_version != current_version and self.versions[best_version]["status"] in ["计划中", "规划中"]:
                    return False, current_version, best_version
                # 如果是当前版本的任务，则判定为符合主线
                elif best_version == current_version:
                    return True, current_version, current_version
        
        # 检查是否提及未来版本关键词
        for version, info in self.versions.items():
            if info["status"] in ["计划中", "规划中"] and version in task_description:
                # 如果任务提及未来版本且当前版本未完成，则判定为偏离主线
                return False, current_version, version
        
        # 默认认为属于当前版本（宽松匹配）
        return True, current_version, current_version
    
    def run_check(self, task_description: str = "") -> int:
        """
        运行主线任务检查
        
        Args:
            task_description: 任务描述（可选）
            
        Returns:
            int: 检查结果状态码
                0: 符合主线
                1: 偏离主线
                2: 读取任务文件失败
        """
        # 读取任务文件
        if not self.read_task_file():
            return 2
        
        # 解析任务内容
        self.parse_task_content()
        
        # 如果提供了任务描述，则进行检查
        if task_description:
            is_main_line, current_version, task_version = self.check_task_against_main_line(task_description)
            
            if is_main_line:
                print(f"检查通过: 任务符合当前主线版本 ({current_version})")
                return 0
            else:
                print(f"检查不通过: 任务偏离主线")
                print(f"当前主线版本: {current_version}")
                print(f"任务归属版本: {task_version}")
                return 1
        
        # 如果没有提供任务描述，只显示当前版本信息
        current_version = self.get_current_version()
        if current_version:
            print(f"当前进行中版本: {current_version}")
        else:
            print("未找到标记为'进行中'的版本")
        
        return 0


def main():
    """主函数"""
    # 创建任务检查器实例
    checker = TaskChecker()
    
    # 获取命令行参数
    task_description = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    
    # 运行检查
    result = checker.run_check(task_description)
    
    # 根据结果返回相应的退出码
    sys.exit(result)


if __name__ == "__main__":
    main()