# coding: utf-8
# author: QCL
# software: PyCharm Professional Edition 2018.2.8

import requests
from lxml import etree
from queue import Queue
import threading
import csv


class Producer(threading.Thread):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
         Chrome/72.0.3626.109 Safari/537.36"
    }

    def __init__(self, page_queue, content_queue, *args, **kwargs):
        super(Producer, self).__init__(*args, **kwargs)
        self.base_url = "http://www.budejie.com"
        self.page_queue = page_queue
        self.content_queue = content_queue

    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()
            self.parse_page(url)

    def parse_page(self, url):
        response = requests.get(url, headers=self.headers)
        text = response.text
        html = etree.HTML(text)
        descs = html.xpath("//div[@class='j-r-list-c-desc']")
        for desc in descs:
            joke = "".join(desc.xpath(".//a/text()"))
            link = self.base_url + desc.xpath(".//a/@href")[0]
            self.content_queue.put((joke, link))


class Consumer(threading.Thread):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
             Chrome/72.0.3626.109 Safari/537.36"
    }

    def __init__(self, page_queue, content_queue, mutex, writer, *args, **kwargs):
        super(Consumer, self).__init__(*args, **kwargs)
        self.page_queue = page_queue
        self.content_queue = content_queue
        self.mutex = mutex
        self.writer = writer

    def run(self):
        while True:
            if self.content_queue.empty() and self.page_queue.empty():
                break
            content_info = self.content_queue.get()
            joke, link = content_info
            self.mutex.acquire()
            self.writer.writerow((joke, link))
            self.mutex.release()
            print("写入完成一条")


def main():
    page_queue = Queue(20)
    content_queue = Queue(1024)
    mutex = threading.Lock()

    f = open("bsbdj.csv", "a", encoding="utf-8", newline="")
    writer = csv.writer(f)
    writer.writerow(("content", "link"))

    for x in range(20):
        url = "http://www.budejie.com/text/{}".format(x)
        page_queue.put(url)

    for x in range(5):
        t = Producer(page_queue, content_queue)
        t.start()

    for x in range(5):
        t = Consumer(page_queue, content_queue, mutex, writer)
        t.start()


if __name__ == '__main__':
    main()
