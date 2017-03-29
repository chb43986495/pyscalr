# -*- coding:utf-8 -*-
import urllib
import urllib2
import re
import thread
import time

import logging


class Wpd:
    # 初始化方法，定义一些变量
    def __init__(self):
        # 定义一个Handler打印INFO及以上级别的日志到sys.stderr
        console = logging.StreamHandler()
        # 设置日志打印格式
        formatter = logging.Formatter('%(asctime)s-[%(name)s]-[%(funcName)s] - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        # 将定义好的console日志handler添加到root logg
        self.wpdlogger = logging.getLogger('wpd application')
        self.wpdlogger.setLevel(logging.INFO)
        self.wpdlogger.addHandler(console)

        self.pageIndex = 2
        self.hasReadPage = 0
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        # 初始化headers
        self.headers = {'User-Agent': self.user_agent}
        # 存放段子的变量，每一个元素是每一页的段子们
        self.stories = []
        # 存放程序是否继续运行的变量
        self.enable = False

    # 传入某一页的索引获得页面代码
    def getPage(self, pageIndex):
        try:
            url = 'http://www.2wpd.com/advanced-search?q=&category=2&resolution=&license=&page=' + str(pageIndex)
            # 构建请求的request
            request = urllib2.Request(url, headers=self.headers)
            # 利用urlopen获取页面代码
            response = urllib2.urlopen(request)
            # 将页面转化为UTF-8编码
            pageCode = response.read().decode('utf-8')
            return pageCode

        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                self.wpdlogger.error(u"连接原服务器失败,错误原因"+e.reason)
                self.wpdlogger.error(url)
                return None

    def getdetailPage(self, prefix):
        try:
            url = 'http://www.2wpd.com/landscape/'+prefix+'.htm'
            # 构建请求的request
            request = urllib2.Request(url, headers=self.headers)
            # 利用urlopen获取页面代码
            response = urllib2.urlopen(request)
            # 将页面转化为UTF-8编码
            pageCode = response.read().decode('utf-8')
            return pageCode

        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                self.wpdlogger.error(u"连接原服务器失败,错误原因"+e.reason)
                self.wpdlogger.error(url)
                return None

    # 获取图片并存入
    def getImg(self, html):
        flag =False
        prefix = html.lower();
        pageinfo = self.getdetailPage(prefix)

        if not pageinfo:
            return None
        # pattern = re.compile('<div.*?author">.*?<a.*?<img.*?>(.*?)</a>.*?<div.*?'+
        #                  'content">(.*?)<!--(.*?)-->.*?</div>(.*?)<div class="stats.*?class="number">(.*?)</i>',re.S)
        pattern = re.compile('<a href="/preview/(.*?).htm".*?</a>',
                             re.S)
        items = re.findall(pattern, pageinfo)
        for item in items:
            #仅爬取1280*800图片
            if re.search('1280x800',item):
                if len(items)>0:
                    imagesrc = 'http://www.2wpd.com/images/%s.jpg' % item
                    flag = self.download(imagesrc,prefix)
                    break
        return flag
    def download(self,imagesrc,prefix):
        return urllib.urlretrieve(imagesrc, 'D:\wpd\%s.jpg' % prefix)

    # 传入某一页代码
    def getPageItems(self,pageindex):
        pi =self.hasReadPage+1
        for pagenumber in range(pi,pageindex):
            self.hasReadPage=pi
            pageCode = self.getPage(pagenumber)
            pageStories = []
            if not pageCode:
                self.wpdlogger.error(u"页面加载失败,错误原因")
                return None
            pattern = re.compile('<img itemprop=".*?src="/uploads/wallpapers/.*?/.*?/.*?/(.*?)/.*?alt="(.*?)" .*?>',re.S)
            items = re.findall(pattern, pageCode)

            # 用来存储每页图片alt
            pageAlt = []
            # 遍历正则表达式匹配的信息
            for item in items:
                # 是否含有图片
                # haveImg = re.search("img",item[3])
                # #如果不含有图片，把它加入list中
                text = re.sub("\s+", "-", item[1])
                text = re.sub("-Wallpaper", "", text)
                text = text + '-' + item[0]
                # self.getImg(text)
                pageStories.append(text);
                # replaceBR = re.compile('<br/>')

        return pageStories

    # 开始方法
    def start(self):
        return self.getPageItems()