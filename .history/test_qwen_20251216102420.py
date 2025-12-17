where qwenwhere qwenimport subprocess

def check_qwen_available():
    """检查 qwen 命令是否可用"""
    try:
        result = subprocess.run(['qwen', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"找到 qwen 命令，版本: {result.stdout.strip()}")
            return True
        else:
            print(f"qwen 命令不可用: {result.stderr}")
            return False
    except FileNotFoundError:
        print("未找到 qwen 命令，请确保已正确安装")
        return False
    except Exception as e:
        print(f"检查 qwen 命令时出错: {e}")
        return False

# 测试函数
if __name__ == "__main__":
    available = check_qwen_available()
    print(f"Qwen 可用性: {available}")