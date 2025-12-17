#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 file_monitor.py Web 服务功能的脚本
"""

import time

import requests


def test_service():
    """测试 Web 服务功能"""
    base_url = "http://localhost:8080"

    print("测试文件监控服务...")

    # 测试服务状态
    print("\n1. 测试服务状态接口:")
    try:
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"   服务状态: {status_data['status']}")
            print(f"   监控目录: {status_data['monitor_dir']}")
            print(f"   时间戳: {status_data['timestamp']}")
        else:
            print(f"   错误: HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   错误: 无法连接到服务，请确保服务正在运行")
        return

    # 测试手动扫描
    print("\n2. 测试手动扫描接口:")
    try:
        response = requests.get(f"{base_url}/scan")
        if response.status_code == 200:
            scan_data = response.json()
            print(f"   扫描状态: {scan_data['status']}")
            print(f"   消息: {scan_data['message']}")
            print(f"   文件数: {scan_data['report']['file_count']}")
            print(f"   时间戳: {scan_data['timestamp']}")
        else:
            print(f"   错误: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   错误: {e}")

    # 测试不存在的接口
    print("\n3. 测试不存在的接口:")
    try:
        response = requests.get(f"{base_url}/nonexistent")
        if response.status_code == 404:
            error_data = response.json()
            print(f"   错误状态: {error_data['status']}")
            print(f"   消息: {error_data['message']}")
            print(f"   可用接口: {', '.join(error_data['available_endpoints'])}")
        else:
            print(f"   意外响应: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   错误: {e}")


if __name__ == "__main__":
    test_service()
