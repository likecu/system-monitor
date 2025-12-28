#!/usr/bin/env python3
"""
系统资源监控采集脚本
定期采集CPU、内存、硬盘、网络等系统资源数据，并存储到MySQL数据库
"""

import psutil
import mysql.connector
import time
import os
from datetime import datetime

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'monitor'),
    'password': os.getenv('DB_PASSWORD', '!A33b3e561fec'),
    'database': os.getenv('DB_NAME', 'monitor')
}

INTERVAL = int(os.getenv('COLLECT_INTERVAL', '5'))


def collect_metrics():
    """
    采集系统资源指标

    Returns:
        dict: 包含系统资源指标的字典，采集失败时返回None
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)

        memory = psutil.virtual_memory()

        disk = psutil.disk_usage('/')

        network = psutil.net_io_counters()

        return {
            'timestamp': datetime.now(),
            'cpu_percent': cpu_percent,
            'memory_total': memory.total,
            'memory_used': memory.used,
            'memory_free': memory.free,
            'memory_percent': memory.percent,
            'disk_total': disk.total,
            'disk_used': disk.used,
            'disk_free': disk.free,
            'disk_percent': disk.percent,
            'network_sent': network.bytes_sent,
            'network_recv': network.bytes_recv
        }
    except Exception as e:
        print(f"[{datetime.now()}] 采集指标失败: {e}")
        return None


def insert_metrics(metrics):
    """
    将监控指标插入数据库

    Args:
        metrics (dict): 包含系统资源指标的字典
    """
    if not metrics:
        return

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """INSERT INTO system_metrics
                   (timestamp, cpu_percent, memory_total, memory_used,
                    memory_free, memory_percent, disk_total, disk_used,
                    disk_free, disk_percent, network_sent, network_recv)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        values = (
            metrics['timestamp'], metrics['cpu_percent'],
            metrics['memory_total'], metrics['memory_used'],
            metrics['memory_free'], metrics['memory_percent'],
            metrics['disk_total'], metrics['disk_used'],
            metrics['disk_free'], metrics['disk_percent'],
            metrics['network_sent'], metrics['network_recv']
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        print(f"[{datetime.now()}] 指标插入成功 - CPU: {metrics['cpu_percent']}%")
    except mysql.connector.Error as e:
        print(f"[{datetime.now()}] 数据库操作失败: {e}")
    except Exception as e:
        print(f"[{datetime.now()}] 插入指标失败: {e}")


def main():
    """
    主函数，定期采集并存储监控数据
    """
    print("=" * 50)
    print("系统资源监控采集脚本已启动")
    print(f"数据库: {DB_CONFIG['database']} @ {DB_CONFIG['host']}")
    print(f"采集间隔: {INTERVAL}秒")
    print("=" * 50)

    while True:
        metrics = collect_metrics()
        insert_metrics(metrics)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
