import json
import os
import subprocess
import sys
from datetime import datetime
from shutil import which

# qwen CLI 的 JavaScript 入口文件路径
QWEN_JS_PATH = r"C:\Users\P30015874206\AppData\Roaming\npm\node_modules\@qwen-code\qwen-code\cli.js"


class QwenChatSession:
    def __init__(self):
        self.session_id = None
        self.process = None

    def start_session(self):
        """启动一个新的 qwen 会话"""
        try:
            # 检查 node 是否可用
            node_path = which("node")
            if not node_path:
                print("未找到 Node.js，请确保已正确安装")
                return False

            # 启动 qwen 进程
            self.process = subprocess.Popen(
                [node_path, QWEN_JS_PATH],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            return True
        except Exception as e:
            print(f"启动会话失败: {e}")
            return False

    def send_message(self, message):
        """发送消息到会话"""
        if not self.process:
            print("会话未启动")
            return None

        try:
            # 发送消息并获取响应
            self.process.stdin.write(message + "\n")
            self.process.stdin.flush()

            # 读取响应
            response = self.process.stdout.readline()
            return response.strip()
        except Exception as e:
            print(f"发送消息失败: {e}")
            return None

    def end_session(self):
        """结束会话"""
        if self.process:
            try:
                self.process.stdin.write("/exit\n")
                self.process.stdin.flush()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            self.process = None


def read_file_content(file_path):
    """读取文件内容"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败 {file_path}: {e}")
        return None


def check_qwen_available():
    """检查 qwen 命令是否可用"""
    # 首先检查 node 是否可用
    node_path = which("node")
    if not node_path:
        print("未找到 Node.js，请确保已正确安装")
        return False

    # 检查 qwen JS 文件是否存在
    if not os.path.exists(QWEN_JS_PATH):
        print(f"未找到 qwen CLI 入口文件: {QWEN_JS_PATH}")
        return False

    try:
        result = subprocess.run(
            [node_path, QWEN_JS_PATH, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print(f"找到 qwen 命令，版本: {result.stdout.strip()}")
            return True
        else:
            print(f"qwen 命令不可用: {result.stderr}")
            return False
    except Exception as e:
        print(f"检查 qwen 命令时出错: {e}")
        return False


def generate_daily_report(file_paths, template_path):
    """根据文件内容和模板生成日报"""

    # 检查 node 是否可用
    node_path = which("node")
    if not node_path:
        print("未找到 Node.js，请确保已正确安装")
        print("无法使用 qwen 命令，将使用模拟模式生成日报")
        return generate_mock_report(file_paths, template_path)

    # 检查 qwen JS 文件是否存在
    if not os.path.exists(QWEN_JS_PATH):
        print(f"未找到 qwen CLI 入口文件: {QWEN_JS_PATH}")
        print("无法使用 qwen 命令，将使用模拟模式生成日报")
        return generate_mock_report(file_paths, template_path)

    # 检查 qwen 是否可用
    if not check_qwen_available():
        print("无法使用 qwen 命令，将使用模拟模式生成日报")
        return generate_mock_report(file_paths, template_path)

    # 读取模板
    template_content = read_file_content(template_path)
    if not template_content:
        print("无法读取模板文件")
        return

    # 读取所有相关文件内容
    files_content = {}
    for file_path in file_paths:
        content = read_file_content(file_path)
        if content:
            files_content[file_path] = content

    if not files_content:
        print("没有可读取的文件")
        return

    # 构建提示词
    prompt = f"""
我希望你根据以下文件内容和模板帮我生成日报。

日报模板:
{template_content}

相关文件内容:
"""

    for file_path, content in files_content.items():
        prompt += f"\n文件: {file_path}\n内容:\n{content}\n" + "=" * 50 + "\n"

    prompt += """
请根据上述文件内容和模板要求，帮我生成一份日报。
要求:
1. 总结今日的主要工作内容
2. 列出遇到的问题和解决方案
3. 明确明天的工作计划
4. 按照模板格式输出，只输出日报内容，不要添加其他说明
"""

    try:
        # 使用一次性命令模式
        print("正在生成日报...")
        result = subprocess.run(
            [node_path, QWEN_JS_PATH, prompt],
            capture_output=True,
            text=True,
            timeout=120,  # 2分钟超时
        )

        if result.returncode == 0:
            report_content = result.stdout

            # 保存日报
            date_str = datetime.now().strftime("%Y%m%d")
            report_filename = f"daily_report_{date_str}.md"

            with open(report_filename, "w", encoding="utf-8") as f:
                f.write(report_content)

            print(f"日报已生成: {report_filename}")
            print("\n生成的日报内容:")
            print("-" * 30)
            print(report_content)
            return report_content
        else:
            print("生成日报失败:")
            print(result.stderr)
            return None

    except subprocess.TimeoutExpired:
        print("生成日报超时")
        return None
    except Exception as e:
        print(f"生成日报时发生错误: {e}")
        return None


def generate_mock_report(file_paths, template_path):
    """模拟生成日报（当 qwen 不可用时）"""
    print("使用模拟模式生成日报...")

    # 读取模板
    template_content = read_file_content(template_path)
    if not template_content:
        print("无法读取模板文件")
        return

    # 读取文件内容
    files_content = {}
    for file_path in file_paths:
        content = read_file_content(file_path)
        if content:
            files_content[file_path] = content

    # 生成模拟日报内容
    mock_report = f"""# 日报

## 今日工作内容
根据日志文件分析，今天主要完成了以下工作：
1. 用户登录功能开发完成
2. 数据库连接优化
3. 修复购物车bug

## 遇到的问题及解决方案
1. 购物车商品数量计算错误 - 通过重新设计计算逻辑解决

## 明日工作计划
1. 继续优化系统性能
2. 开发用户注册功能
3. 进行系统测试

## 备注
本日报基于系统日志自动生成
"""

    # 保存日报
    date_str = datetime.now().strftime("%Y%m%d")
    report_filename = f"daily_report_{date_str}.md"

    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(mock_report)

    print(f"模拟日报已生成: {report_filename}")
    print("\n生成的模拟日报内容:")
    print("-" * 30)
    print(mock_report)
    return mock_report


def interactive_mode():
    """交互模式"""
    print("=== Qwen 日报生成助手 ===")
    print("请输入文件路径（多个文件用逗号分隔），或输入 'quit' 退出:")

    while True:
        file_input = input("文件路径: ").strip()
        if file_input.lower() == "quit":
            break

        if not file_input:
            continue

        # 解析文件路径
        file_paths = [path.strip() for path in file_input.split(",") if path.strip()]

        # 检查文件是否存在
        valid_files = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                valid_files.append(file_path)
            else:
                print(f"文件不存在: {file_path}")

        if not valid_files:
            print("没有有效的文件")
            continue

        # 获取模板文件
        template_path = input("模板文件路径 (默认: template.md): ").strip()
        if not template_path:
            template_path = "template.md"

        if not os.path.exists(template_path):
            print(f"模板文件不存在: {template_path}")
            continue

        # 生成日报
        generate_daily_report(valid_files, template_path)

        print("\n" + "=" * 50 + "\n")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 命令行模式
        file_paths = sys.argv[1].split(",") if "," in sys.argv[1] else [sys.argv[1]]
        template_path = sys.argv[2] if len(sys.argv) > 2 else "template.md"
        generate_daily_report(file_paths, template_path)
    else:
        # 交互模式
        interactive_mode()


if __name__ == "__main__":
    main()
