BigLog
======
INTRODUCTION
-------------
BigLog is an open source nginx access log analyzer provides fast and
valuable HTTP statistics for system administrators .

DEMAND
------
nginx access log format
log_format  access  '$remote_addr - $remote_user [$time_local] "$request" ' '$status $body_bytes_sent "$http_referer" '   '"$http_user_agent" "$http_x_forwarded_for" ' '"$upstream_cache_status"' &@&$host;

日志接收:
udp 515 端口

RUN
---
./biglog.sh


版本更新说明
------------
BigLog2增加了gearman模块，各个模块的通信都通过gearman来实现,主要模块如下：

BigLogCollect 单条日志信息（字典）接收

BigLogDomain  Mysql域名数据库创建（一个域名一个库，包含统计信息）

BigLogMysql   一段时间日志统计信息导入数据库

BigLogGeo     ip对应地理位置查询

--------------
新增加 redis 队列缓存

