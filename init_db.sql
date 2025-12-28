-- 系统监控数据库初始化脚本
-- 创建监控数据库、表和用户

-- 创建监控数据库
CREATE DATABASE IF NOT EXISTS monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建监控专用用户（允许远程连接）
CREATE USER IF NOT EXISTS 'monitor'@'%' IDENTIFIED BY '!A33b3e561fec';

-- 授予用户权限
GRANT ALL PRIVILEGES ON monitor.* TO 'monitor'@'%';
FLUSH PRIVILEGES;

-- 切换到监控数据库
USE monitor;

-- 创建系统资源监控表
CREATE TABLE IF NOT EXISTS system_metrics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL COMMENT '数据采集时间',
    cpu_percent FLOAT NOT NULL COMMENT 'CPU使用率(%)',
    memory_total BIGINT NOT NULL COMMENT '内存总大小(bytes)',
    memory_used BIGINT NOT NULL COMMENT '已用内存(bytes)',
    memory_free BIGINT NOT NULL COMMENT '可用内存(bytes)',
    memory_percent FLOAT NOT NULL COMMENT '内存使用率(%)',
    disk_total BIGINT NOT NULL COMMENT '磁盘总大小(bytes)',
    disk_used BIGINT NOT NULL COMMENT '已用磁盘(bytes)',
    disk_free BIGINT NOT NULL COMMENT '可用磁盘(bytes)',
    disk_percent FLOAT NOT NULL COMMENT '磁盘使用率(%)',
    network_sent BIGINT NOT NULL COMMENT '网络发送字节数',
    network_recv BIGINT NOT NULL COMMENT '网络接收字节数',
    INDEX idx_timestamp (timestamp),
    INDEX idx_cpu_percent (cpu_percent),
    INDEX idx_memory_percent (memory_percent),
    INDEX idx_disk_percent (disk_percent)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统资源监控数据表';

-- 创建监控配置表（可选，用于存储配置信息）
CREATE TABLE IF NOT EXISTS monitor_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键',
    config_value TEXT COMMENT '配置值',
    description VARCHAR(255) COMMENT '配置说明',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='监控配置表';

-- 插入默认配置
INSERT INTO monitor_config (config_key, config_value, description) VALUES
('collect_interval', '5', '数据采集间隔(秒)'),
('data_retention_days', '30', '数据保留天数'),
('enabled', 'true', '监控是否启用')
ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;

-- 创建数据清理存储过程（可选）
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS cleanup_old_data(IN retention_days INT)
BEGIN
    DELETE FROM system_metrics
    WHERE timestamp < DATE_SUB(NOW(), INTERVAL retention_days DAY);
END //
DELIMITER ;

-- 验证表创建成功
SELECT TABLE_NAME, TABLE_COMMENT, ENGINE, CREATE_TIME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'monitor'
ORDER BY TABLE_NAME;
