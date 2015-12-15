#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
    a multi-thread download tool
'''

import sys
import os
import time
import urllib
from threading import Thread
from xml.dom import minidom

class Downloader(Thread, urllib.FancyURLopener):
    def __init__(self, threadname, url, filename, ranges=0):
        Thread.__init__(self, name=threadname)
        urllib.FancyURLopener.__init__(self)
        self.name = threadname
        self.url = url
        self.filename = filename
        self.ranges = ranges
        self.downloaded = 0

    def run(self):
        try:
            self.downloaded = os.path.getsize(self.filename)
        except OSError:
            self.downloaded = 0

        self.startpoint = self.ranges[0] + self.downloaded

        if self.startpoint >= self.ranges[1]:
            print "file %s has been done." % self.filename
            return

        self.oneTimeSize = 16378
        print "task %s wil download from %d to %d" %(self.name, self.startpoint, self.ranges[1])

        self.addheader("Range", "bytes=%d-%d" %(self.startpoint, self.ranges[1]))

        self.urlhandle = self.open(self.url)

        data = self.urlhandle.read(self.oneTimeSize)
        while data:
            filehandle = open(self.filename, 'ab+')
            filehandle.write(data)
            filehandle.close()

            self.downloaded += len(data)
            data = self.urlhandle.read(self.oneTimeSize)


def GetUrlFileSize(url):
    urlHandler = urllib.urlopen(url)
    headers = urlHandler.info().headers
    length = 0
    for header in headers:
        if header.find('Length') != -1:
            length = int(header.split(':')[-1].strip())
    #print length
    return length

def GetRanges(totalsize, threadnum):
    blocksize = totalsize/threadnum
    ranges = []
    for i in range(0, threadnum-1):
        ranges.append((i*blocksize, (i+1)*blocksize-1))
    ranges.append((blocksize*(threadnum-1), totalsize-1))
    return ranges

def isalive(tasks):
    for task in tasks:
        if task.isAlive():
            return True
    return False

def start_download(url, output, threadnum=6):
    size = GetUrlFileSize(url)
    ranges = GetRanges(size, threadnum)

    threadname = [ "thread_%d" %i for i in range(0, threadnum)]
    filename = [ "_%d" %i for i in range(0, threadnum)]

    tasks = []
    for i in range(0, threadnum):
        task = Downloader(threadname[i], url, filename[i], ranges[i])
        task.setDaemon(True)
        task.start()
        tasks.append(task)

    time.sleep(2)
    while isalive(tasks):
        done = sum([task.downloaded for task in tasks])
        process = done/float(size)*100
        show = u'\rFilesize:%d have downloaded %d Completed %.2f' %(size, done, process)
        sys.stdout.write(show)
        sys.stdout.flush()
        time.sleep(0.5)

    filehandle = open(output, 'wb+')
    for i in filename:
        with open(i, 'rb') as f:
            filehandle.write(f.read())
        try:
            os.remove(i)
            pass
        except:
            pass
    filehandle.close()


def download_tv2011_201(path):
    for i in range(1, 2):
        url = "http://www-nlpir.nist.gov/projects/tv2011/pastdata/copy.detection/201/%d.mpg" %i
        output = "%d.mpg" %i
        start_download(url, os.path.join(path,output))

def parse_xml_get_filename():
    xml_file_path = '/Users/apple/Documents/pythonprogramer/pall_download/iacc.1.A.collection.xml'
    root = minidom.parse(xml_file_path).documentElement
    video_file_nodes = root.getElementsByTagName('VideoFile')
    result_list = []
    for video_file in video_file_nodes:
        raw_filename = video_file.getElementsByTagName('filename')[0].childNodes[0].nodeValue
        filename = raw_filename.split('._-o-_.')[-1]
        raw_url = video_file.getElementsByTagName('source')[0].childNodes[0].nodeValue
        url = "%s/%s" %(raw_url, filename)
        result_list.append((filename, url))
    return result_list

def download_xml_video(path):
    video_file_list = parse_xml_get_filename()
    for filename, url in video_file_list:
        #print filename, url
        start_download(url, os.path.join(path, filename))
        return


if __name__ == '__main__':
#    download_tv2011_201(sys.argv[1])
    download_xml_video(sys.argv[1])


#    url = "http://www-nlpir.nist.gov/projects/tv2011/pastdata/copy.detection/201/1.mpg"
#    output = "1.mpg"
#    start_download(url, output)


