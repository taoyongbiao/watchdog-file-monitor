import os
import time
import logging
from datetime import datetime
import schedule
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import http.server
import socketserver
import json
import urllib.parse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_changes.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 配置变量
MONITOR_DIR = "."  # 默认监控当前目录
AI_API_URL = "http://example.com/api/report"  # AI接口URL（请替换为实际地址）
REPORT_SAVE_PATH = "daily_reports/"  # 日报保存路径
WEB_PORT = 8080  # Web服务端口


class FileChangeHandler(FileSystemEventHandler):
    """文件变化处理器"""
    
    def on_created(self, event):
        """处理文件创建事件"""
        if not event.is_directory:
            self.log_change("CREATED", event.src_path)
            
    def on_modified(self, event):
        """处理文件修改事件"""
        if not event.is_directory:
            self.log_change("MODIFIED", event.src_path)
            
    def on_deleted(self, event):
        """处理文件删除事件"""
        if not event.is_directory:
            self.log_change("DELETED", event.src_path)
            
    def log_change(self, action, file_path):
        """记录文件变化到日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        relative_path = os.path.relpath(file_path, MONITOR_DIR)
        logger.info(f"{action}: {relative_path}")
        
        # 如果是定时任务触发条件，调用AI接口
        if self.should_trigger_ai(action):
            self.call_ai_api(action, relative_path, timestamp)
    
    def should_trigger_ai(self, action):
        """判断是否应该触发AI接口调用"""
        # 这里可以添加更复杂的触发条件逻辑
        # 当前简单实现：任何文件变化都可能触发
        return True
    
    def call_ai_api(self, action, file_path, timestamp):
        """调用AI接口生成日报"""
        try:
            # 准备发送给AI接口的数据
            data = {
                "action": action,
                "file_path": file_path,
                "timestamp": timestamp
            }
            
            # 调用AI接口（这里只是示例，请替换为实际的API调用）
            # response = requests.post(AI_API_URL, json=data)
            # ai_response = response.json()
            
            # 模拟AI返回结果
            ai_response = {
                "summary": f"在{timestamp}检测到文件{file_path}被{action}",
                "details": f"文件 {file_path} 的{action.lower()}操作已被记录"
            }
            
            # 保存AI生成的日报
            self.save_daily_report(ai_response, timestamp)
            
            logger.info("AI日报已生成并保存")
        except Exception as e:
            logger.error(f"调用AI接口失败: {e}")
    
    def save_daily_report(self, ai_response, timestamp):
        """保存AI生成的日报"""
        # 确保保存目录存在
        os.makedirs(REPORT_SAVE_PATH, exist_ok=True)
        
        # 创建日报文件名
        date_str = datetime.now().strftime("%Y%m%d")
        report_filename = f"daily_report_{date_str}.txt"
        report_path = os.path.join(REPORT_SAVE_PATH, report_filename)
        
        # 写入日报内容
        with open(report_path, 'a', encoding='utf-8') as f:
            f.write(f"\n--- {timestamp} ---\n")
            f.write(f"摘要: {ai_response.get('summary', '')}\n")
            f.write(f"详情: {ai_response.get('details', '')}\n")
            f.write("-" * 30 + "\n")


def full_scan():
    """全量扫描目录并与日志记录对比"""
    logger.info("开始执行全量扫描...")
    
    # 获取当前目录下所有文件
    current_files = []
    for root, dirs, files in os.walk(MONITOR_DIR):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), MONITOR_DIR)
            # 排除日志文件和报告文件
            if not relative_path.startswith("file_changes.log") and not relative_path.startswith(REPORT_SAVE_PATH):
                current_files.append(relative_path)
    
    logger.info(f"当前目录中共有 {len(current_files)} 个文件")
    
    # 这里可以添加与历史记录对比的逻辑
    # 为了简化，我们只记录扫描完成
    logger.info("全量扫描完成")


def setup_schedule():
    """设置定时任务"""
    # 设置每天7:00和17:00执行全量扫描
    schedule.every().day.at("07:00").do(full_scan)
    schedule.every().day.at("17:00").do(full_scan)
    
    logger.info("定时任务已设置: 每天07:00和17:00执行全量扫描")


def start_monitoring():
    """启动文件监控"""
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, MONITOR_DIR, recursive=True)
    observer.start()
    
    logger.info(f"开始监控目录: {os.path.abspath(MONITOR_DIR)}")
    
    try:
        while True:
            # 运行定时任务
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("监控已停止")
    finally:
        observer.join()


if __name__ == "__main__":
    # 创建必要的目录
    os.makedirs(REPORT_SAVE_PATH, exist_ok=True)
    
    # 设置定时任务
    setup_schedule()
    
    # 启动监控
    start_monitoring()