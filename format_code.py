#!/usr/bin/env python3
"""
代码格式化脚本
自动格式化代码、排序导入
"""

import os
import subprocess
import sys


def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def main():
    print("🎨 开始代码格式化...")

    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"项目路径: {project_root}")

    # 1. 运行Black代码格式化
    print("\n1. 运行Black代码格式化...")
    returncode, stdout, stderr = run_command("black .", project_root)
    if returncode == 0:
        print("   ✅ Black格式化完成")
    else:
        print("   ❌ Black格式化失败:")
        print(stderr)

    # 2. 运行isort导入排序
    print("\n2. 运行isort导入排序...")
    returncode, stdout, stderr = run_command("isort .", project_root)
    if returncode == 0:
        print("   ✅ isort排序完成")
    else:
        print("   ❌ isort排序失败:")
        print(stderr)

    print("\n✅ 代码格式化完成! 你的代码现在更加整洁了!")


if __name__ == "__main__":
    main()
