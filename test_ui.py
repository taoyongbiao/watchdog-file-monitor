import sys
import time

import requests


def test_ui_connectivity():
    """测试UI基本连通性"""
    print("测试UI基本连通性...")

    # 测试主页是否可访问
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("✓ UI主页可访问")
            return True
        else:
            print(f"✗ UI主页访问失败，状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到UI服务器，请确保应用正在运行")
        return False
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {e}")
        return False


if __name__ == "__main__":
    success = test_ui_connectivity()
    sys.exit(0 if success else 1)
