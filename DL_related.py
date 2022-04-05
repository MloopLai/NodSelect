import csv
import math
import numpy as np
import random
from collections import deque
import tensorflow as tf

from ml_model import CNN_model
from keras.models import load_model

def change360(degree):
    # return degree/360
    if(degree>180):
        return -1 * (degree-360)
    else:
        return -1 * degree
def changetoarray(datalist):
    modellist = []
    for x in range(1,len(datalist)):
       time = float(datalist[x][1]) - float(datalist[x-1][1])
       rot_x = float(change360(float(datalist[x][5])))
       rot_y = float(change360(float(datalist[x][6])))
       angspd_x = (rot_x - change360(float(datalist[x-1][5])))/time * 1000
       angspd_y = (rot_y - change360(float(datalist[x-1][6])))/time * 1000
       modellist.append([rot_x,rot_y,angspd_x,angspd_y])
    mydatalist = np.asarray(modellist)
    return mydatalist

class nod_model():
    def __init__(self):
        self.model = load_model("./model/best_model_705.h5")
        self.data = list()
        self.buffer = ''
        self.continuous = 0
        self.graph = tf.get_default_graph()
        self.check = deque(maxlen=10)

    # def add_data(self, offered):
        
    #     # for line in offered:
    #     #     self.data.append(line.split(','))
    #     #     if(self.data[-1][0] != self.data[0][0]):
    #     #         self.data = []
    #     # lines = (self.buffer + offered).split('\n')
    #     # self.buffer = ''
    #     # if(len(lines) == 1):
    #     #     self.data.append(lines[0].split(','))
    #     # else:
    #     #     self.buffer = lines[-1]
    #     #     for line in lines[:-1]:
    #     #         self.data.append(line.split(','))
        
    def predict(self, offered):
        # print(line)
        for line in offered:
            self.data.append(line.split(','))
            if(self.data[-1][0] != self.data[0][0]):
                self.data.clear()
                self.check.clear()
                continue
            if(len(self.data) > 80):
                cur = changetoarray(self.data[-71:])
                cur = cur[np.newaxis, :, :]
                with self.graph.as_default():
                    result = self.model.predict(cur)
                    # print('predict result: ' + str(result) + "@ " + str(self.data[-71][1]))
                result = 1 if result > 0.5 else 0
                self.check.append(result)
                # if(result == 1):
                #     print('nod at ' + self.data[-71][1])
                if(self.check.count(1) > 4):
                    p = self.check.index(1)
                    nod_data = self.data[p-111:p-10]
                    nod_dataP = changetoarray(nod_data)
                    ref = 25
                    for i, c in enumerate(nod_dataP[25:]):
                        if(nod_dataP[ref][2] > c[2]):
                            ref = i + 25
                    tmp = 0
                    curmin = (0, 10000000)
                    for i, c in enumerate(reversed(range(ref-25, ref))):
                        tmp = tmp + abs(nod_dataP[c][2]) + abs(nod_dataP[c][3])
                        if(i % 5 == 4):
                            if(tmp < curmin[1]):
                                curmin = (c, tmp)
                                tmp = 0
                            else:
                                break
                    data = self.data[-106+curmin[0]]
                    print(data[0] + " " + data[1])
                    return data[1]
        return -1