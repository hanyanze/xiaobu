#!/usr/bin/env python3
import os
import sys
import time
import signal

def sh_process_info(process_name):
        command = "ps aux | grep " + process_name
        out = os.popen(command).read()
        for line in out.splitlines():
            print(line)
            if "sh " + process_name in line:
                pid = int(line.split()[1])
                print("pid = ", pid)
                return pid, True
        return 1, False

def py_process_info(process_name):
        command = "ps aux | grep " + process_name
        out = os.popen(command).read()
        for line in out.splitlines():
            if "python3 " + process_name in line:
                pid = int(line.split()[1])
                # print("pid = ", pid)
                return pid, True
        return 1, False

def process_info_stop(processId):
    try:
        os.kill(processId, signal.SIGKILL)
        # print('已杀死pid为%s的进程,　返回值是:%s' % (processId, a))
    except OSError:
        # print('没有如此进程!!!')
        return False
    return True


if __name__ == "__main__":
    print('''****************************
    (1)开启语音模块
    (2)关闭语音模块
    (3)训练唤醒词
    (4)退出
****************************''')
    status = input("输入：")
    if status == "1":
        #command = "./run.sh"
        #out = os.popen(command).read()
        os.system("./wukong-robot/run.sh")
    elif status == "2":
        try:
            process_result = py_process_info('main.py')
            if process_result[0] != 1:
                process_info_stop(process_result[0])
        except Exception as e:
            print(e)
        try:
            process_result = py_process_info('wukong.py')
            if process_result[0] != 1:
                process_info_stop(process_result[0])
        except Exception as e:
            print(e)
        try:
            process_result = py_process_info('LocalGateway.py')
            if process_result[0] != 1:
                process_info_stop(process_result[0])
        except Exception as e:
            print(e)
    elif status == "3":
        num = 3
        i = 0
        name = input("输入训练模型名称：")
        if name != "":
            while i < num:
                print("开始录音......")
                os.system("python3 ./train/recoder.py " + str(i) + " > /dev/null 2>&1")
                print("完成录音")
                status = input("输入d删除，按下回车继续：")
                if status == "d":
                    path = "./train/test{}.wav".format(i)
                    os.system("rm " + path)
                    i -= 1
                i += 1
                time.sleep(2)
            print("开始训练......")
            os.system("python3 ./wukong-robot/wukong.py train ~/train/test0.wav ~/train/test1.wav ~/train/test2.wav ~/.wukong/" + name + ".pmdl")
    else:
        pass
