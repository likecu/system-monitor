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
    
    # 转换为前端所需格式
    timestamps = [m['timestamp'].strftime('%Y-%m-%d %H:%M:%S') for m in metrics]
    cpu_data = [m['cpu_percent'] for m in metrics]
    memory_used = [m['memory_used'] / (1024**3) for m in metrics]  # 转换为GB
    memory_total = [m['memory_total'] / (1024**3) for m in metrics]  # 转换为GB
    disk_used = [m['disk_used'] / (1024**3) for m in metrics]  # 转换为GB
    disk_total = [m['disk_total'] / (1024**3) for m in metrics]  # 转换为GB
    network_sent = [m['network_sent'] / (1024**2) for m in metrics]  # 转换为MB
    network_recv = [m['network_recv'] / (1024**2) for m in metrics]  # 转换为MB
    
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
    # 监听所有IP，端口8080
    app.run(host='0.0.0.0', port=8080, debug=False)