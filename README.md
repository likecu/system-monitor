# 系统监控面板

一个基于Python和Flask的远程服务器监控系统，用于实时监控和展示CPU、内存、硬盘、网络等系统资源使用情况。

## 系统架构

1. **数据采集层**：使用`psutil`库定期采集系统资源数据
2. **数据存储层**：MariaDB数据库存储历史监控数据
3. **数据展示层**：基于Flask的Web应用，提供实时和历史数据查询、图表展示

## 快速开始

### SSH连接到远程服务器

```bash
ssh -i ~/.ssh/milk milk@34.29.5.105
```

### 进入项目目录

```bash
cd ~/system-monitor
```

### 管理监控脚本

```bash
# 启动监控采集
./run_monitor.sh start

# 查看运行状态
./run_monitor.sh status

# 查看实时日志
./run_monitor.sh logs

# 停止监控
./run_monitor.sh stop

# 重启监控
./run_monitor.sh restart
```

### 查看监控数据

直接查询数据库：

```bash
sudo mysql -u root -e "USE monitor; SELECT timestamp, cpu_percent, memory_percent, disk_percent FROM system_metrics ORDER BY timestamp DESC LIMIT 10;"
```

查看最新记录：

```bash
sudo mysql -u root -e "USE monitor; SELECT COUNT(*) as total, AVG(cpu_percent) as avg_cpu, AVG(memory_percent) as avg_mem FROM system_metrics;"
```

## 项目结构

```
.
├── monitor_collector.py      # 数据采集脚本
├── run_monitor.sh            # 启动管理脚本
├── init_db.sql               # 数据库初始化脚本
├── requirements.txt          # Python依赖列表
├── monitor-web/              # Web应用目录
│   ├── app.py               # Flask应用主程序
│   ├── templates/           # HTML模板目录
│   │   └── index.html       # 监控面板页面
│   └── static/              # 静态资源目录
│       └── css/             # CSS样式目录
│           └── style.css    # 样式文件
└── README.md                # 项目说明文档
```

## 本地开发环境搭建

### 1. 安装依赖

```bash
# 安装Python依赖
pip install psutil mysql-connector-python flask
```

### 2. 配置MySQL/MariaDB

在本地或远程服务器上创建数据库和用户：

```sql
-- 创建监控数据库
CREATE DATABASE monitor;

-- 创建监控用户并授权
CREATE USER 'monitor'@'localhost' IDENTIFIED BY '!A33b3e561fec';
GRANT ALL PRIVILEGES ON monitor.* TO 'monitor'@'localhost';
FLUSH PRIVILEGES;

-- 切换到监控数据库
USE monitor;

-- 创建系统资源监控表
CREATE TABLE system_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    cpu_percent FLOAT NOT NULL,
    memory_total BIGINT NOT NULL,
    memory_used BIGINT NOT NULL,
    memory_free BIGINT NOT NULL,
    memory_percent FLOAT NOT NULL,
    disk_total BIGINT NOT NULL,
    disk_used BIGINT NOT NULL,
    disk_free BIGINT NOT NULL,
    disk_percent FLOAT NOT NULL,
    network_sent BIGINT NOT NULL,
    network_recv BIGINT NOT NULL
);
```

### 3. 运行采集脚本

```bash
# 启动监控采集
python3 monitor_collector.py

# 或使用管理脚本
chmod +x run_monitor.sh
./run_monitor.sh start
```

## GitHub同步方案

### 1. 本地代码更新

```bash
# 添加文件
git add .

# 提交代码
git commit -m "描述信息"

# 推送到GitHub
git push origin master
```

### 2. 远程服务器更新

```bash
# SSH连接到服务器
ssh -i ~/.ssh/milk milk@34.29.5.105

# 进入项目目录
cd ~/system-monitor

# 拉取最新代码
git pull origin master
```

## 远程服务器部署

### 1. 安装依赖

```bash
# 安装系统依赖
sudo apt update
sudo apt install -y python3-pip

# 安装Python依赖
sudo pip3 install --break-system-packages psutil mysql-connector-python flask
```

### 2. 初始化数据库

```bash
# 执行数据库初始化脚本
sudo mysql -u root < init_db.sql
```

### 3. 启动数据采集服务

#### 方式一：使用管理脚本（推荐）

```bash
chmod +x run_monitor.sh
./run_monitor.sh start
```

#### 方式二：直接运行

```bash
python3 monitor_collector.py &
```

#### 方式三：使用系统服务

```bash
# 设置执行权限
chmod +x monitor_collector.py

# 创建系统服务
sudo cat > /etc/systemd/system/monitor-collector.service << 'EOF'
[Unit]
Description=System Monitor Collector
After=mysql.service

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /root/monitor_collector.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动并启用服务
sudo systemctl daemon-reload
sudo systemctl start monitor-collector
sudo systemctl enable monitor-collector
```

### 4. 启动Web监控服务（可选）

```bash
# 复制Web应用到指定目录
cp -r monitor-web ~/

# 创建系统服务
sudo cat > /etc/systemd/system/monitor-web.service << 'EOF'
[Unit]
Description=System Monitor Web Panel
After=mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=~/monitor-web
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动并启用Web服务
sudo systemctl daemon-reload
sudo systemctl start monitor-web
sudo systemctl enable monitor-web
```

### 5. 配置防火墙

```bash
# 允许8080端口访问
sudo ufw allow 8080/tcp
sudo ufw reload
```

## 访问监控面板

监控面板可以通过以下URL访问：

```
http://34.29.5.105:8080
```

## 服务管理

### 查看服务状态

```bash
# 查看数据采集服务状态
ps aux | grep monitor_collector

# 或使用管理脚本
./run_monitor.sh status
```

### 查看实时日志

```bash
./run_monitor.sh logs

# 或直接查看日志文件
tail -f monitor.log
```

### 重启服务

```bash
./run_monitor.sh restart
```

### 停止服务

```bash
./run_monitor.sh stop
```

## 数据管理

### 查看数据统计

```bash
# 查看总记录数
sudo mysql -u root -e "USE monitor; SELECT COUNT(*) as total FROM system_metrics;"

# 查看最近24小时数据
sudo mysql -u root -e "USE monitor; SELECT * FROM system_metrics WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR);"

# 查看平均使用率
sudo mysql -u root -e "USE monitor; SELECT AVG(cpu_percent) as avg_cpu, AVG(memory_percent) as avg_mem, AVG(disk_percent) as avg_disk FROM system_metrics;"
```

### 清理旧数据

```bash
# 保留最近30天的数据
sudo mysql -u root -e "USE monitor; DELETE FROM system_metrics WHERE timestamp < DATE_SUB(NOW(), INTERVAL 30 DAY);"

# 调用存储过程清理数据
sudo mysql -u root -e "USE monitor; CALL cleanup_old_data(30);"
```

### 备份数据

```bash
# 备份整个监控数据库
sudo mysqldump -u root monitor > monitor_backup_$(date +%Y%m%d).sql

# 备份最近7天数据
sudo mysql -u root -e "USE monitor; SELECT * INTO OUTFILE '/tmp/monitor_backup.csv' FROM system_metrics WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY);"
```

## 自定义配置

### 环境变量配置

支持通过环境变量配置（推荐）：

```bash
export DB_HOST='localhost'
export DB_USER='monitor'
export DB_PASSWORD='!A33b3e561fec'
export DB_NAME='monitor'
export COLLECT_INTERVAL='60'
```

### 修改采集间隔

在`monitor_collector.py`中修改`INTERVAL`变量：

```python
# 采集间隔（秒）
INTERVAL = 60  # 修改为其他值，如300表示5分钟
```

### 修改数据库配置

在`monitor_collector.py`中修改`DB_CONFIG`变量：

```python
# MySQL连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'monitor',
    'password': '!A33b3e561fec',
    'database': 'monitor'
}
```

## 监控指标说明

| 指标 | 说明 | 单位 |
|------|------|------|
| cpu_percent | CPU使用率 | 百分比 |
| memory_total | 内存总大小 | bytes |
| memory_used | 已用内存 | bytes |
| memory_free | 可用内存 | bytes |
| memory_percent | 内存使用率 | 百分比 |
| disk_total | 磁盘总大小 | bytes |
| disk_used | 已用磁盘 | bytes |
| disk_free | 可用磁盘 | bytes |
| disk_percent | 磁盘使用率 | 百分比 |
| network_sent | 网络发送字节数 | bytes |
| network_recv | 网络接收字节数 | bytes |

## 技术栈

- **后端**：Python 3.9+, Flask
- **数据库**：MariaDB/MySQL
- **前端**：HTML, CSS, JavaScript, Chart.js
- **系统监控**：psutil

## 功能特点

- ✅ 实时监控CPU使用率
- ✅ 实时监控内存使用情况
- ✅ 实时监控磁盘使用情况
- ✅ 实时监控网络流量
- ✅ 支持多种时间范围查询（2小时、24小时、7天、30天）
- ✅ 图表化展示历史数据趋势
- ✅ 自动启动和故障恢复
- ✅ 支持GitHub同步部署
- ✅ 支持后台运行和日志管理

## 注意事项

1. 定期备份数据库，防止数据丢失
2. 根据服务器性能调整数据采集间隔
3. 考虑使用Nginx作为反向代理，提高Web应用的性能和安全性
4. 监控Web应用本身的资源使用情况
5. 定期更新依赖库，确保安全性
6. 数据库密码已配置为`!A33b3e561fec`，建议定期更换

## License

MIT
