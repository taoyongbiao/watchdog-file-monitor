#!/usr/bin/env python3
"""
代码检查脚本
运行代码格式化、导入排序和风格检查
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


def check_file_exists(filepath):
    """检查文件是否存在"""
    return os.path.exists(filepath)


def main():
    print("🔍 开始代码检查...")

    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"项目路径: {project_root}")

    # 1. 运行Black代码格式化检查
    print("\n1. 运行Black代码格式化检查...")
    returncode, stdout, stderr = run_command("black --check .", project_root)
    if returncode == 0:
        print("   ✅ Black检查通过")
    else:
        print("   ⚠️  Black检查发现问题:")
        print(stderr)
        print("   💡 运行 'black .' 来自动格式化代码")

    # 2. 运行isort导入排序检查
    print("\n2. 运行isort导入排序检查...")
    returncode, stdout, stderr = run_command("isort --check-only .", project_root)
    if returncode == 0:
        print("   ✅ isort检查通过")
    else:
        print("   ⚠️  isort检查发现问题:")
        print(stderr)
        print("   💡 运行 'isort .' 来自动排序导入")

    # 3. 运行flake8代码风格检查
    print("\n3. 运行flake8代码风格检查...")
    returncode, stdout, stderr = run_command("flake8 .", project_root)
    if returncode == 0:
        print("   ✅ flake8检查通过")
    else:
        print("   ⚠️  flake8检查发现问题:")
        print(stdout)

    # 4. 检查重要文件是否存在
    print("\n4. 检查重要文件...")
    important_files = [
        "ui_app.py",
        "file_monitor.py",
        "git_manager.py",
        "requirements.txt",
    ]

    missing_files = []
    for file in important_files:
        if not check_file_exists(os.path.join(project_root, file)):
            missing_files.append(file)

    if missing_files:
        print(f"   ❌ 缺少重要文件: {missing_files}")
    else:
        print("   ✅ 所有重要文件都存在")

    print("\n✅ 代码检查完成!")


if __name__ == "__main__":
    main()
