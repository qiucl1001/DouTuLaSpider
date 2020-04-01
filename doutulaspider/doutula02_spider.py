# coding: utf-8
# author: QCL
# software: PyCharm Professional Edition 2018.2.8

import requests
from lxml import etree
import re
import os
from urllib import request
from queue import Queue
import threading


class Producer(threading.Thread):
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/72.0.3626.109 Safari/537.36"
        }

    def __init__(self, page_queue, image_queue, *args, **kwargs):
        """
        初始化
        :param page_queue: 列表页队列
        :param image_queue: 图片url即图片名称队列
        :param args: 非键值对的可变参数类表， 位置参数
        :param kwargs: 以键值对形式的可变参数类表，关键字参数
        """
        super(Producer, self).__init__(*args, **kwargs)
        self.page_queue = page_queue
        self.image_queue = image_queue

        self.proxy_url = "http://127.0.0.1:5000/random"

    def use_free_proxy(self, current_url, proxy):
        """
        使用免费代理获取网页源代码
        :param current_url: 目标网页url连接
        :param proxy: 免费代理ip
        :return:
        """
        response = requests.get(
            url=current_url,
            headers=self.headers,
            proxies={
                "http": "http://" + proxy,
                "https": "https://" + proxy
            }
        )

        return response

    def run(self):
        while True:
            if self.page_queue.empty():
                break
            current_url = self.page_queue.get()

            try:
                # 次循环目的请求一个url连接10次机会，如果连续调用10次免费的ip没有一个可用
                # 则通过捕获异常的方式将次url重新放回url队列，等待下一轮的调度
                for i in range(10):
                    # 获取代理ip
                    proxy = requests.get(self.proxy_url).text
                    response = self.use_free_proxy(current_url, proxy)
                    if response.status_code == 200:
                        self.parse_page(response)
                    break
            except Exception as e:
                print(e.args)
                self.page_queue.put(current_url)
                continue

    def parse_page(self, response):
        """
        获取网页源码中的斗图url连接
        :param response: 网页源代码
        :return:
        """
        text = response.text
        html = etree.HTML(text)
        images = html.xpath("//div[@class='page-content text-center']//img[@class!='gif']")
        for image in images:
            # print(etree.tostring(image, encoding="utf-8").decode("utf-8"))
            image_url = image.get("data-original")
            alt = image.get("alt")
            alt = re.sub(r'[\?？，。！!\*]', "", alt)
            suffix = os.path.splitext(image_url)[1].split("!")[0]
            filename = alt + suffix
            self.image_queue.put((image_url, filename))


class Consumer(threading.Thread):
    def __init__(self, page_queue, image_queue, *args, **kwargs):
        """
        初始化
        :param page_queue: 列表页队列
        :param image_queue: 图片url即图片名称队列
        :param args: 非键值对的可变参数类表， 位置参数
        :param kwargs: 以键值对形式的可变参数类表，关键字参数
        """
        super(Consumer, self).__init__(*args, **kwargs)
        self.page_queue = page_queue
        self.image_queue = image_queue

    def run(self):
        while True:
            if self.image_queue.empty() and self.page_queue.empty():
                break
            image_url, filename = self.image_queue.get()
            request.urlretrieve(image_url, "images/" + filename)
            print(filename + "------下载完成！------")


def main():
    page_queue = Queue(100)
    image_queue = Queue(1024)
    base_url = "https://www.doutula.com/photo/list/?page={}"
    for x in range(1, 101):
        url = base_url.format(x)
        page_queue.put(url)

    for x in range(5):
        t = Producer(page_queue, image_queue)
        t.start()

    for x in range(5):
        t = Consumer(page_queue, image_queue)
        t.start()


if __name__ == '__main__':
    main()
