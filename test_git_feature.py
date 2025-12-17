#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件差异比较和 Git 管理功能的脚本
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

# 添加项目目录到 Python 路径
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))


def test_file_diff_and_git():
    """测试文件差异比较和 Git 管理功能"""
    print("开始测试文件差异比较和 Git 管理功能...")

    # 创建临时测试目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"使用临时目录: {temp_path}")

        # 复制 file_monitor.py 到临时目录
        monitor_file = project_dir / "file_monitor.py"
        if monitor_file.exists():
            shutil.copy2(monitor_file, temp_path)
            print("已复制 file_monitor.py 到临时目录")

        # 创建测试文件
        test_file = temp_path / "test_file.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("这是测试文件的第一版内容。\n")
        print("已创建测试文件")

        # 模拟文件修改
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("这是测试文件的修改后内容。\n添加了一行新内容。\n")
        print("已修改测试文件")

        print("测试完成。请手动运行 file_monitor.py 来检查差异报告生成功能。")


def main():
    """主函数"""
    test_file_diff_and_git()


if __name__ == "__main__":
    main()
