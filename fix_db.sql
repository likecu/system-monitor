-- 检查monitor用户
SELECT user, host FROM mysql.user WHERE user = 'monitor';

-- 重新授权
GRANT ALL PRIVILEGES ON monitor.* TO 'monitor'@'localhost' IDENTIFIED BY '!A33b3e561fec';
GRANT ALL PRIVILEGES ON monitor.* TO 'monitor'@'%' IDENTIFIED BY '!A33b3e561fec';
FLUSH PRIVILEGES;
