#!/usr/bin/env python3
"""
文件监控系统综合测试
可用于持续集成和单元测试
"""

import os
import subprocess
import sys
import time
import unittest

import requests


class TestFileMonitoringSystem(unittest.TestCase):
    """文件监控系统测试套件"""

    def setUp(self):
        """测试前准备"""
        self.base_dir = os.path.dirname(__file__)

    def test_ui_connectivity(self):
        """测试UI界面连通性"""
        try:
            response = requests.get("http://localhost:8080", timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.skipTest("UI服务器未运行，跳过此测试")
        except Exception as e:
            self.fail(f"UI连通性测试失败: {e}")

    def test_git_status(self):
        """测试Git状态功能"""
        try:
            # 检查当前Git状态
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, f"Git命令执行失败: {result.stderr}")
            # 注意：我们不检查是否有未提交的文件，因为这取决于当前工作区状态
            print(f"Git状态检查成功，未提交文件数: {len(result.stdout.strip().split())}")
        except Exception as e:
            self.fail(f"Git状态测试失败: {e}")

    def test_file_monitor_module(self):
        """测试文件监控模块"""
        try:
            # 导入监控模块
            from file_monitor import FileChangeHandler, full_scan

            # 模块导入成功即视为通过
            self.assertTrue(True)

            # 测试全量扫描（不验证结果，只确保不抛出异常）
            scan_result = full_scan()
            self.assertIsInstance(scan_result, dict)
            self.assertIn("file_count", scan_result)
        except ImportError as e:
            self.fail(f"无法导入文件监控模块: {e}")
        except Exception as e:
            self.fail(f"文件监控模块测试失败: {e}")

    def test_git_manager(self):
        """测试Git管理器"""
        try:
            from git_manager import get_git_manager

            git_manager = get_git_manager()
            self.assertIsNotNone(git_manager, "Git管理器初始化失败")
            # 检查是否有repo_path属性
            self.assertTrue(hasattr(git_manager, "repo_path"), "Git管理器缺少repo_path属性")
        except Exception as e:
            self.fail(f"Git管理器测试失败: {e}")


def run_comprehensive_test():
    """运行综合测试"""
    print("=== 文件监控系统综合测试 ===")

    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFileMonitoringSystem)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    # 如果作为脚本直接运行，则执行综合测试
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
