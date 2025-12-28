from flask import Flask, render_template, request
import mysql.connector
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# MySQL连接配置
DB_CONFIG = {
    "host": "localhost",
    "user": "monitor",
    "password": "monitor123",
    "database": "monitor"
}

# 中国时区偏移量（UTC+8）
CHINA_TIMEZONE = timedelta(hours=8)

# 最大返回数据点数
MAX_DATA_POINTS = 100


def downsample_metrics(metrics):
    """
    对监控数据进行降采样，保持数据趋势特征

    Args:
        metrics: 原始监控数据列表

    Returns:
        list: 降采样后的数据列表
    """
    if len(metrics) <= MAX_DATA_POINTS:
        return metrics

    step = len(metrics) // MAX_DATA_POINTS
    downsampled = []

    for i in range(0, len(metrics), step):
        if i + step < len(metrics):
            chunk = metrics[i:i + step]
        else:
            chunk = metrics[i:]
        if chunk:
            downsampled.append(chunk[0])

    return downsampled

@app.route('/')
def index():
    # 默认时间范围为2小时
    time_range = request.args.get('time_range', '2h')
    
    # 解析时间范围
    if time_range.endswith('h'):
        hours = int(time_range[:-1])
        start_time = datetime.now() - timedelta(hours=hours)
    elif time_range.endswith('d'):
        days = int(time_range[:-1])
        start_time = datetime.now() - timedelta(days=days)
    elif time_range.endswith('w'):
        weeks = int(time_range[:-1])
        start_time = datetime.now() - timedelta(weeks=weeks)
    else:
        # 默认为2小时
        start_time = datetime.now() - timedelta(hours=2)
    
    # 查询数据库获取监控数据
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM system_metrics WHERE timestamp >= %s ORDER BY timestamp ASC"
    
    cursor.execute(query, (start_time,))
    metrics = cursor.fetchall()

    cursor.close()
    conn.close()

    # 降采样以减少数据点密度
    metrics = downsample_metrics(metrics)

    # 转换为前端所需格式，时间转换为中国时区
    timestamps = [(m['timestamp'] + CHINA_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S') for m in metrics]
    cpu_data = [m['cpu_percent'] for m in metrics]
    memory_used = [m['memory_used'] / (1024**3) for m in metrics]
    memory_total = [m['memory_total'] / (1024**3) for m in metrics]
    disk_used = [m['disk_used'] / (1024**3) for m in metrics]
    disk_total = [m['disk_total'] / (1024**3) for m in metrics]

    # 计算平均网络流量（相邻数据点的差值除以时间间隔）
    network_sent = []
    network_recv = []

    for i in range(len(metrics)):
        if i == 0:
            # 第一个数据点，设为0或使用原始值的差分估算
            network_sent.append(metrics[0]['network_sent'] / (1024**2))
            network_recv.append(metrics[0]['network_recv'] / (1024**2))
        else:
            # 计算相邻数据点的差值
            time_diff = (metrics[i]['timestamp'] - metrics[i-1]['timestamp']).total_seconds()
            if time_diff > 0:
                # 转换为MB/s（差值 / 时间间隔 / 1024^2）
                sent_rate = (metrics[i]['network_sent'] - metrics[i-1]['network_sent']) / time_diff / (1024**2)
                recv_rate = (metrics[i]['network_recv'] - metrics[i-1]['network_recv']) / time_diff / (1024**2)
                network_sent.append(max(0, sent_rate))  # 确保非负
                network_recv.append(max(0, recv_rate))
            else:
                network_sent.append(0)
                network_recv.append(0)
    
    return render_template('index.html', 
                          timestamps=json.dumps(timestamps),
                          cpu_data=json.dumps(cpu_data),
                          memory_used=json.dumps(memory_used),
                          memory_total=json.dumps(memory_total),
                          disk_used=json.dumps(disk_used),
                          disk_total=json.dumps(disk_total),
                          network_sent=json.dumps(network_sent),
                          network_recv=json.dumps(network_recv),
                          current_time_range=time_range)

if __name__ == '__main__':
    # 监听所有IP，端口8081
    app.run(host='0.0.0.0', port=8081, debug=False)