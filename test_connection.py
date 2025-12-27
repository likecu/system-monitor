#!/usr/bin/env python3
"""
测试数据库连接和psutil
"""

import mysql.connector
import psutil
import os

def test_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'monitor'),
            password=os.getenv('DB_PASSWORD', '!A33b3e561fec'),
            database=os.getenv('DB_NAME', 'monitor')
        )
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM system_metrics')
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f'数据库连接成功! 当前有 {count} 条记录')
        return True
    except Exception as e:
        print(f'数据库连接失败: {e}')
        return False

def test_psutil():
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        print(f'psutil测试成功!')
        print(f'  CPU: {cpu}%')
        print(f'  内存: {memory.percent}%')
        print(f'  磁盘: {disk.percent}%')
        return True
    except Exception as e:
        print(f'psutil测试失败: {e}')
        return False

if __name__ == "__main__":
    print("=" * 40)
    print("系统监控测试脚本")
    print("=" * 40)
    test_connection()
    print()
    test_psutil()
