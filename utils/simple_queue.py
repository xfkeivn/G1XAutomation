#!/usr/bin/env python
# encoding: utf-8
"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSCUDSStudio
@file: simple_queue.py
@time: 2023/3/26 22:00
@desc:
"""
import threading
import copy

class LightQueue():
    def __init__(self, max_size=None):
        self.buffer = []
        self.lock = threading.Lock()
        self.max_size = max_size

    def put(self, item):
        self.lock.acquire()
        if isinstance(item, list):
            for i in item:
                self.buffer.append(i)
        else:
            self.buffer.append(item)
        self.lock.release()
        if self.max_size is not None and self.size() > self.max_size:
            self.get()

    def empty(self):
        self.lock.acquire()
        isempty = (len(self.buffer) == 0)
        self.lock.release()
        return isempty

    def size(self):
        return len(self.buffer)

    def get(self):
        if self.empty():
            return None
        self.lock.acquire()
        returnvalue = self.buffer[0]
        del self.buffer[0]
        self.lock.release()
        return returnvalue

    def get_all(self):
        self.lock.acquire()
        if len(self.buffer) == 0:
            self.lock.release()
            return []
        else:
            return_value = self.buffer
            self.buffer = []
            self.lock.release()
            return return_value

    def get_all_retain(self):
        self.lock.acquire()
        if len(self.buffer) == 0:
            self.lock.release()
            return []
        else:
            tempbuffer = copy.deepcopy(self.buffer)
            self.lock.release()
            return tempbuffer

    def clear(self):
        self.lock.acquire()
        self.buffer = []
        self.lock.release()


class MessageDictQueue:
    def __init__(self, buffersize = 100000):
        self._msgqueue_dict = {}
        self.lock = threading.Lock()
        self.buffersize = buffersize
        self.seq = 0

    def put(self, message_id, message):
        self.lock.acquire()
        if self._msgqueue_dict.get(message_id) is None:
            self._msgqueue_dict[message_id] = LightQueue()

        self._msgqueue_dict[message_id].put((self.seq,message))
        if self._msgqueue_dict[message_id].size() > self.buffersize:
            self._msgqueue_dict[message_id].get()

        self.lock.release()

    def count(self):
        self.lock.acquire()
        count = 0
        for key, value in list(self._msgqueue_dict.items()):
            count = value.size() + count
        self.lock.release()
        return count

    def empty_specific(self, messageid):
        self.lock.acquire()
        msgqueue = self._msgqueue_dict.get(messageid)
        self.lock.release()
        if msgqueue is None:
            return True
        return msgqueue.empty()

    def get_all_specific(self, messageid):
        self.lock.acquire()
        msgqueue = self._msgqueue_dict.get(messageid)
        msgs = []
        if msgqueue is not None:
            msgs = msgqueue.get_all()
        self.lock.release()
        return msgs

    def get_all_retain_specific(self, messageid):
        self.lock.acquire()
        msgqueue = self._msgqueue_dict.get(messageid)
        tempbuffer = []
        if msgqueue is not None:
            tempbuffer = copy.deepcopy(msgqueue.buffer)
        self.lock.release()
        return tempbuffer

    def clear(self):
        self.seq = 0
        self.lock.acquire()
        self._msgqueue_dict.clear()
        self.lock.release()