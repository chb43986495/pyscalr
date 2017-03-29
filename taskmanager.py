# -*- coding:utf-8 -*-

#################分布式爬虫demo，manager###########################
from spider import wpd
import threading
import random, time, Queue,logging
import dill
from multiprocessing.managers import BaseManager

# 定义一个Handler打印INFO及以上级别的日志到sys.stderr
console = logging.StreamHandler()
# 设置日志打印格式
formatter = logging.Formatter('%(asctime)s -[%(threadName)s] - %(levelname)s - %(message)s')
console.setFormatter(formatter)
# 将定义好的console日志handler添加到root logg
logger = logging.getLogger('manager')
logger.setLevel(logging.INFO)
logger.addHandler(console)

# 从BaseManager继承的QueueManager:
class QueueManager(BaseManager):
    pass
def make_server_manager():

    # 发送任务的队列:
    task_queue = Queue.Queue()
    # 接收结果的队列:
    result_queue = Queue.Queue()

    # 把两个Queue都注册到网络上, callable参数关联了Queue对象:
    QueueManager.register('get_task_queue', callable=lambda: task_queue)
    QueueManager.register('get_result_queue', callable=lambda: result_queue)
    # 绑定端口5000, 设置验证码'abc':
    manager = QueueManager(address=('127.0.0.1', 5000), authkey='abc')
    # 启动Queue:
    manager.start()
    t1 = threading.Thread(target=startTask, name='TaskQueue',args=(manager,))
    t2 = threading.Thread(target=startresultQueue, name='ResultQueue',args=(manager,))
    t1.start()
    t2.start()
    # t1.join()
    # t2.join()

def startTask(manager):

    # 初始化爬虫
    spider1 = wpd.Wpd()
    # 获得通过网络访问的Queue对象:
    task = manager.get_task_queue()
    # 爬取页数:
    page =10
    n=1
    while page>=n:

        logger.info(u'读取第 %d页....' % n)
        n += 1
        imgs = spider1.getPageItems(n)
        for v in imgs:
            # n = random.randint(0, 10000)
            logger.info(u'下载任务放入队列 %s...' % v)
            task.put(v)
# 从result队列读取结果:
def startresultQueue(manager):
    result = manager.get_result_queue()
    logger.info(u'尝试获取下次结果...')
    while True:
        try:
            r = result.get(timeout=10)
            logger.info(u'结果: %s' % r)
        except Queue.Empty:
            logger.warning('task queue is empty.')
    # 关闭:
    manager.shutdown()

if __name__=='__main__':
    make_server_manager()
