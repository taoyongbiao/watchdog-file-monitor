import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from nicegui import app, events, ui

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

# 尝试导入监控模块
try:
    from file_monitor import FileChangeHandler
    from git_manager import get_git_manager

    MONITOR_AVAILABLE = True
except ImportError as e:
    print(f"警告: 无法导入监控模块: {e}")
    MONITOR_AVAILABLE = False


class FileMonitorUI:
    def __init__(self):
        self.handler = None
        self.git_manager = None
        self.is_monitoring = False
        self.monitor_thread = None
        self.file_changes = []

        # 如果监控模块可用，初始化它们
        if MONITOR_AVAILABLE:
            try:
                self.handler = FileChangeHandler()
                self.git_manager = get_git_manager()
            except Exception as e:
                print(f"初始化监控模块时出错: {e}")

        # 创建UI
        self.create_ui()

    def create_ui(self):
        @ui.page("/")
        def main_page():
            '''
            主页面UI布局
            '''
            with ui.column().classes("w-full items-center p-4"):
                ui.label("文件监控系统").classes("text-2xl font-bold")

                # 状态面板
                with ui.card().classes("w-full max-w-3xl"):
                    with ui.row().classes("w-full justify-between items-center"):
                        self.status_label = ui.label("监控状态: 未运行").classes("text-lg")
                        with ui.row():
                            self.start_button = ui.button(
                                "开始监控", on_click=self.start_monitoring
                            ).classes("mx-1")
                            self.stop_button = (
                                ui.button("停止监控", on_click=self.stop_monitoring)
                                .classes("mx-1")
                                .disable()
                            )

                    # 文件变化表格
                    ui.label("文件变化记录").classes("text-lg mt-4")
                    self.changes_table = ui.table(
                        columns=[
                            {
                                "name": "time",
                                "label": "时间",
                                "field": "time",
                                "align": "left",
                            },
                            {
                                "name": "file",
                                "label": "文件",
                                "field": "file",
                                "align": "left",
                            },
                            {
                                "name": "type",
                                "label": "类型",
                                "field": "type",
                                "align": "left",
                            },
                        ],
                        rows=[],
                        pagination=10,
                    ).classes("w-full")

                    # 控制按钮
                    with ui.row().classes("w-full justify-center mt-4"):
                        ui.button("生成报告", on_click=self.generate_report).classes("mx-2")
                        ui.button("查看Git状态", on_click=self.check_git_status).classes(
                            "mx-2"
                        )

                # 自动刷新数据
                ui.timer(1.0, self.update_ui)

        # 添加一些样式
        ui.add_head_html(
            """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
            }
            .q-table th {
                font-weight: bold;
            }
        </style>
        """,
            shared=True,
        )

    def start_monitoring(self):
        """启动文件监控"""
        if not MONITOR_AVAILABLE or not self.handler:
            ui.notify("监控模块不可用，请检查安装")
            return

        if not self.is_monitoring:
            self.is_monitoring = True
            self.status_label.set_text("监控状态: 运行中")
            self.start_button.disable()
            self.stop_button.enable()

            # 在单独线程中运行监控
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop, daemon=True
            )
            self.monitor_thread.start()

            ui.notify("文件监控已启动")

    def stop_monitoring(self):
        """停止文件监控"""
        if self.is_monitoring:
            self.is_monitoring = False
            self.status_label.set_text("监控状态: 已停止")
            self.start_button.enable()
            self.stop_button.disable()
            ui.notify("文件监控已停止")

    def _monitor_loop(self):
        """监控循环"""
        # 这里应该实现实际的文件监控逻辑
        # 由于我们没有真实的文件监控实现，我们模拟一些变化
        counter = 0
        while self.is_monitoring:
            time.sleep(2)  # 每2秒检查一次
            counter += 1

            # 模拟文件变化
            if counter % 3 == 0:
                change_type = "MODIFIED" if counter % 2 == 0 else "CREATED"
                file_name = f"test_file_{counter}.txt"

                change_record = {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "file": file_name,
                    "type": change_type,
                }

                # 添加到变化记录中
                self.file_changes.append(change_record)

                # 限制记录数量
                if len(self.file_changes) > 50:
                    self.file_changes.pop(0)

                # 如果有Git管理器，模拟提交
                if self.git_manager:
                    # 这里可以调用Git管理器的方法
                    pass

    def update_ui(self):
        """更新UI显示"""
        # 更新表格数据
        self.changes_table.rows = list(reversed(self.file_changes))
        self.changes_table.update()

    def generate_report(self):
        """生成报告"""
        if not MONITOR_AVAILABLE:
            ui.notify("监控模块不可用，请检查安装")
            return

        try:
            # 调用file_monitor.py中的全量扫描功能
            from file_monitor import full_scan

            scan_report = full_scan()
            ui.notify(f"报告已生成: 共检测到 {scan_report.get('file_count', 0)} 个文件")
        except Exception as e:
            ui.notify(f"生成报告时出错: {str(e)}")

    def check_git_status(self):
        """检查Git状态"""
        if not MONITOR_AVAILABLE or not self.git_manager:
            ui.notify("Git管理器不可用")
            return

        try:
            # 检查Git状态
            import subprocess

            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=os.path.dirname(__file__),
                capture_output=True,
                text=True,
            )

            if result.stdout.strip():
                ui.notify(f"有 {len(result.stdout.strip().split('\\n'))} 个文件未提交")
            else:
                ui.notify("工作区干净，没有未提交的更改")
        except Exception as e:
            ui.notify(f"检查Git状态时出错: {str(e)}")


# 创建应用实例
app_instance = FileMonitorUI()

if __name__ == "__main__":
    ui.run(title="文件监控系统", reload=False, port=8080)
