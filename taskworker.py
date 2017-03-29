# -*- coding:utf-8 -*-
#################分布式爬虫demo，worker###########################3
import time, sys, Queue
from multiprocessing.managers import BaseManager
from multiprocessing import Process
import logging

from spider import wpd

# 创建类似的QueueManager:
class QueueManager(BaseManager):
    pass

def start_client():
    # 定义一个Handler打印INFO及以上级别的日志到sys.stderr
    console = logging.StreamHandler()
    # 设置日志打印格式
    formatter = logging.Formatter('%(asctime)s -[%(name)s] - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    # 将定义好的console日志handler添加到root logg
    logger = logging.getLogger('client')
    logger.setLevel(logging.INFO)
    logger.addHandler(console)

    # 由于这个QueueManager只从网络上获取Queue，所以注册时只提供名字:
    QueueManager.register('get_task_queue')
    QueueManager.register('get_result_queue')

    # 连接到服务器，也就是运行taskmanager.py的机器:
    server_addr = '127.0.0.1'
    logger.info('Connect to server %s...' % server_addr)
    # 端口和验证码注意保持与taskmanager.py设置的完全一致:
    m = QueueManager(address=(server_addr, 5000), authkey='abc')
    # 从网络连接:
    m.connect()
    # 获取Queue的对象:
    task = m.get_task_queue()
    result = m.get_result_queue()

    spider1 = wpd.Wpd()
    # 从task队列取任务,并把结果写入result队列:
    while True:
        try:
            n = task.get()
            logger.info(u'开始下载图片 %s...' % n)
            flag = spider1.getImg(n)
            #result.put('cuck')
            r = u'图片 '+ n +u' 下载 失败'
            if flag:
                r = u'图片 ' + n + u' 下载 成功'
                logger.info(u'下载图片完成 %s.............finish' % n)
            result.put(r)
        except Queue.Empty:
            logger.info('task queue is empty.')

if __name__ == '__main__':
    #启动10个进程做这个事情
    for n in range(10):
        p1 = Process(target=start_client)
        p1.start()