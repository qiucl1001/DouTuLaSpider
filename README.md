# DouTuLaSpider

备注：本项目有2个子项目
1. 斗图啦：[https://www.doutula.com]
2. 百思不得姐段子：[http://www.budejie.com] 
两个自子项目主要演示了---> 采用多线程 + Queue队列做生产者消费者模式 + ip代理池 进行抓取。

# 环境安装
1. python3+以上版本
2. 安装并配置好redis数据库，启动redis数据库

# 三方库安装
```
pip install -r requirements.txt
```

# 启动程序 
### 注意： 启动本项目前，需先下载本地项目<IP_PROXY_POOL> 详细配置信息请看里面的readme.md文件
```
cd doutulaspider
python doutula02_spider.py
```

