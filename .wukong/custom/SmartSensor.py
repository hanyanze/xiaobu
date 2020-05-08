# -*- coding:utf-8 -*-
import requests
import json
import re
import os
import datetime
import yaml
import sys
import threading
from robot import logging
from robot import config
from robot.sdk.AbstractPlugin import AbstractPlugin
from local_socket import client
logger = logging.getLogger(__name__)


class Plugin(AbstractPlugin):
    SLUG = "SmartSensor"
    YAML_FLAG = False
    DATA_POSITION = 22
    profile = config.get()
    if profile[SLUG]['sensor_response'] or profile[SLUG]['supervise_response']:
        t1 = threading.Thread(target=client.client.recv_from_server)
        t1.start()
    try:
        with open("/home/pi/.wukong/sensor.yaml", "r") as f:
            file = f.read()
            data = yaml.load(file, Loader=yaml.FullLoader)
            YAML_FLAG = True
    except Exception as e:
        logger.error(e)

    def match(self, text, patterns):
        for pattern in patterns:
            if re.match(pattern, text):
                return pattern
        return ''

    def match_dict(self, text, patterns_dict):
        for pattern in patterns_dict:
            if re.match(list(pattern.keys())[0], text):
                return list(pattern.values())[0]
        return ''

    def handle(self, text, parsed):
        if isinstance(text, bytes):
            text = text.decode('utf8')
        if self.YAML_FLAG:
            command = self.match_dict(text, self.data['control'])
            if command != "":
                client.client.send2server(command)
                if self.profile[self.SLUG]['sensor_response']:
                    self.control_response()
                else:
                     self.say("指令已下发", cache=True)
            else:
                command = self.match_dict(text, self.data['supervise'])
                if command != "":
                    client.client.send2server(command)
                    client.client.recvData = ""
                    if self.profile[self.SLUG]['supervise_response']:
                        self.supervise_response()
                    else:
                       self.say("检查配置文件是否开启传感点回复功能", cache=True)
                else:
                    self.say("未找到相应指令，请检查配置文件", cache=True)
        else:
            self.say("未找到传感器配置文件", cache=True)
            return
        
    def control_response(self):  # 控制类的节点反馈后作出响应，一般节点不返回反馈
        time_start = datetime.datetime.now()
        while True:
            if client.client.recvData:
                rcv = client.client.recvData
                if rcv == list(self.data['sensor_response'][0].keys())[0]:
                    self.say(list(self.data['sensor_response'][0].values())[0], cache=True)
                client.client.recvData = ""
                break
            if (datetime.datetime.now() - time_start).seconds >= 3:
                if self.profile[self.SLUG]['sensor_response']: 
                    self.say("数据不通畅，请重试", cache=True)
                else:
                    self.say("指令已下发", cache=True)
                break

    def supervise_response(self):  # 传感类的节点反馈后作出响应，每个if都是不同的节点
        time_start = datetime.datetime.now()
        while True:
            if client.client.recvData:
                rcv = client.client.recvData
                print("rcv:", rcv)
                rcv_data = rcv[self.DATA_POSITION:self.DATA_POSITION + 2]
                if rcv_data == list(self.data['supervise_response'][0].keys())[0]:  # 温湿度
                    tem = rcv[self.DATA_POSITION + 2:self.DATA_POSITION + 4]
                    hum = rcv[self.DATA_POSITION + 4:self.DATA_POSITION + 6]
                    self.say(list(self.data['supervise_response'][0].values())[0].split("-")[0] + 
                        str(int(tem, 16)) + "摄氏度，" + 
                        list(self.data['supervise_response'][0].values())[0].split("-")[1] +
                        "百分之" + str(int(hum, 16)), cache=True)
                elif rcv_data == list(self.data['supervise_response'][1].keys())[0]:
                    lx = rcv[self.DATA_POSITION + 2:self.DATA_POSITION + 6]
                    self.say(list(self.data['supervise_response'][1].values())[0] + 
                        str(int(lx, 16)) + "勒克斯，", cache=True)
                client.client.recvData = ""
                break
            if (datetime.datetime.now() - time_start).seconds >= 3:
                if self.profile[self.SLUG]['supervise_response']: 
                    self.say("数据不通畅，请重试", cache=True)
                else:
                    self.say("配置文件未开启查询传感点标志", cache=True)
                break

    def isValid(self, text, parsed):
        if isinstance(text, bytes):
            text = text.decode('utf8')
        # 根据配置中的正则式来匹配
        if (not self.profile[self.SLUG]['enable']) and (self.match(text, self.profile[self.SLUG]['patterns']) != ""):
            return True
        return False
