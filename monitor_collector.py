#!/usr/bin/env python3
"""
系统资源监控采集脚本
定期采集CPU、内存、硬盘、网络等系统资源数据，并存储到MySQL数据库
"""

import psutil
import mysql.connector
import time
from datetime import datetime

# MySQL连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'monitor',
    'password': 'monitor123',
    'database': 'monitor'
}

# 采集间隔（秒）
INTERVAL = 60


def collect_metrics():
    """
    采集系统资源指标
    
    Returns:
        dict: 包含系统资源指标的字典
    """
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        
        # 磁盘使用情况（根目录）
        disk = psutil.disk_usage('/')
        
        # 网络IO情况
        network = psutil.net_io_counters()
        
        # 返回采集到的指标
        return {
            'timestamp': datetime.now(),
            'cpu_percent': cpu_percent,
            'memory_total': memory.total,
            'memory_used': memory.used,
            'memory_free': memory.free,
            'disk_total': disk.total,
            'disk_used': disk.used,
            'disk_free': disk.free,
            'network_sent': network.bytes_sent,
            'network_recv': network.bytes_recv
        }
    except Exception as e:
        print(f"采集指标失败: {e}")
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
        
        query = "INSERT INTO system_metrics (timestamp, cpu_percent, memory_total, memory_used, memory_free, disk_total, disk_used, disk_free, network_sent, network_recv) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        
        values = (
            metrics['timestamp'], metrics['cpu_percent'],
            metrics['memory_total'], metrics['memory_used'], metrics['memory_free'],
            metrics['disk_total'], metrics['disk_used'], metrics['disk_free'],
            metrics['network_sent'], metrics['network_recv']
        )
        
        cursor.execute(query, values)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f"[{datetime.now()}] 指标插入成功")
    except mysql.connector.Error as e:
        print(f"数据库操作失败: {e}")
    except Exception as e:
        print(f"插入指标失败: {e}")


def main():
    """
    主函数，定期采集并存储监控数据
    """
    print("系统资源监控采集脚本已启动")
    print(f"采集间隔: {INTERVAL}秒")
    
    while True:
        metrics = collect_metrics()
        insert_metrics(metrics)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()