-- 更新 system_metrics 表，添加 memory_percent 和 disk_percent 字段
USE monitor;

-- 添加新字段
ALTER TABLE system_metrics
ADD COLUMN memory_percent FLOAT NOT NULL DEFAULT 0 COMMENT '内存使用率(%)' AFTER memory_free,
ADD COLUMN disk_percent FLOAT NOT NULL DEFAULT 0 COMMENT '磁盘使用率(%)' AFTER disk_free;

-- 更新现有记录的字段值
UPDATE system_metrics SET memory_percent = (memory_used * 100.0 / memory_total) WHERE memory_total > 0;
UPDATE system_metrics SET disk_percent = (disk_used * 100.0 / disk_total) WHERE disk_total > 0;

-- 验证更新
DESCRIBE system_metrics;
SELECT COUNT(*) as total_records, AVG(memory_percent) as avg_memory, AVG(disk_percent) as avg_disk FROM system_metrics;
