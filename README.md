# 系统监控面板

一个基于Python和Flask的远程服务器监控系统，用于实时监控和展示CPU、内存、硬盘、网络等系统资源使用情况。

## 系统架构

1. **数据采集层**：使用`psutil`库定期采集系统资源数据
2. **数据存储层**：MariaDB数据库存储历史监控数据
3. **数据展示层**：基于Flask的Web应用，提供实时和历史数据查询、图表展示

## 项目结构

```
.
├── monitor_collector.py      # 数据采集脚本
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
CREATE USER 'monitor'@'localhost' IDENTIFIED BY 'monitor123';
GRANT ALL PRIVILEGES ON monitor.* TO 'monitor'@'localhost';
FLUSH PRIVILEGES;

-- 创建系统资源监控表
USE monitor;
CREATE TABLE system_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    cpu_percent FLOAT NOT NULL,
    memory_total BIGINT NOT NULL,
    memory_used BIGINT NOT NULL,
    memory_free BIGINT NOT NULL,
    disk_total BIGINT NOT NULL,
    disk_used BIGINT NOT NULL,
    disk_free BIGINT NOT NULL,
    network_sent BIGINT NOT NULL,
    network_recv BIGINT NOT NULL
);
```

## GitHub同步方案

### 1. 在本地初始化Git仓库

```bash
# 初始化Git仓库
git init

# 添加文件
git add .

# 提交代码
git commit -m "Initial commit"
```

### 2. 创建GitHub仓库

在GitHub上创建一个新的仓库，然后将本地代码推送到GitHub：

```bash
# 添加远程仓库
git remote add origin https://github.com/likecu/system-monitor.git

# 推送到GitHub
git push -u origin main
```

### 3. 在远程服务器上拉取代码

```bash
# 克隆GitHub仓库
cd /root
git clone https://github.com/likecu/system-monitor.git
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

### 2. 启动数据采集服务

```bash
# 复制采集脚本到指定目录
sudo cp /root/system-monitor/monitor_collector.py /root/

# 设置执行权限
sudo chmod +x /root/monitor_collector.py

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

### 3. 启动Web监控服务

```bash
# 复制Web应用到指定目录
sudo cp -r /root/system-monitor/monitor-web /root/

# 创建系统服务
sudo cat > /etc/systemd/system/monitor-web.service << 'EOF'
[Unit]
Description=System Monitor Web Panel
After=mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/monitor-web
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动并启用服务
sudo systemctl daemon-reload
sudo systemctl start monitor-web
sudo systemctl enable monitor-web
```

### 4. 配置防火墙

```bash
# 允许8080端口访问
sudo ufw allow 8080/tcp
sudo ufw reload
```

## 访问监控面板

监控面板可以通过以下URL访问：

```
http://服务器IP:8080
```

## 服务管理

### 查看服务状态

```bash
# 查看数据采集服务状态
sudo systemctl status monitor-collector

# 查看Web服务状态
sudo systemctl status monitor-web
```

### 重启服务

```bash
# 重启数据采集服务
sudo systemctl restart monitor-collector

# 重启Web服务
sudo systemctl restart monitor-web
```

### 停止服务

```bash
# 停止数据采集服务
sudo systemctl stop monitor-collector

# 停止Web服务
sudo systemctl stop monitor-web
```

## 数据保留策略

建议定期清理旧的监控数据，以避免数据库过大。可以使用以下SQL语句定期清理：

```sql
-- 保留最近30天的数据
DELETE FROM system_metrics WHERE timestamp < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

## 自定义配置

### 修改采集间隔

在`monitor_collector.py`中修改`INTERVAL`变量：

```python
# 采集间隔（秒）
INTERVAL = 60  # 修改为其他值，如300表示5分钟
```

### 修改数据库配置

在`monitor_collector.py`和`monitor-web/app.py`中修改`DB_CONFIG`变量：

```python
# MySQL连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'monitor',
    'password': 'monitor123',
    'database': 'monitor'
}
```

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

## 注意事项

1. 定期备份数据库，防止数据丢失
2. 根据服务器性能调整数据采集间隔
3. 考虑使用Nginx作为反向代理，提高Web应用的性能和安全性
4. 监控Web应用本身的资源使用情况
5. 定期更新依赖库，确保安全性

## License

MIT