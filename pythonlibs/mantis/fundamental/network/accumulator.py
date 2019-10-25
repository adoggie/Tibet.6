#coding:utf-8

import json
import message

class JsonDataAccumulator(object):
    def __init__(self):
        self.buff = ''
        self.user = None

    def enqueue(self,data):
        self.buff += data

        lines = []

        while True:
            p = self.buff.find(message.JsonMessageSplitter)
            if p == -1:
                break
            lines.append(self.buff[:p])
            self.buff = self.buff[p+1:]

        # lines = self.buff.split(message.JsonMessageSplitter)
        # self.buff = ''
        # if lines[-1]=='':
        #     lines= lines[:-1]
        # else:
        #     self.buff = lines[-1]

        result =[]
        for line  in lines:
            # print line
            # print '-'*20
            data = json.loads(line)
            # msg = message.JsonMessage()
            result.append(data)
        return result