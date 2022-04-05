import socket
import select
import threading
import random
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from random import shuffle
import DL_related
from enum import Enum

class State(Enum):
    INIT = 0
    TRAINING = 1
    STUDYING = 2

hint = '####################################################################\n# s: start study session and send target seq to hololens\n# t: start test session and send target seq to hololens\n# z: start trial\n# a: stop test or study. If you were in study session, you HAVE TO clean nod_data and result manually.\n'
send_seq = ['9', '11', '13', '17', '18', '19', '20', '21', '22', '23', '24', '33', '34', '35', 
                '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50',
                '51', '52', '53', '54', '55', '56']
s = socket.socket()

userID = 's'
host = socket.gethostname() # ip
port = 8000 # port
state = State.INIT
nod_model = DL_related.nod_model()
target_list = list()


def client_listener():
    res = list()
    buffer = ''
    print('current target index:', target_list[0], '--', len(target_list), 'remain')
    while(state is State.TRAINING or state is State.STUDYING):
        r, _, _ = select.select([conn], [], [])
        if r:
            data = conn.recv(1024).decode()
        else:
            continue
        data = (buffer + str(data)).split('\n')
        buffer = ''
        if('finish' in data):
            print(data)
            break
        if(data[-1] != ''):
            buffer = data[-1]
        del data[-1]
        res += data
        r = nod_model.predict(data)
        if(r != -1):
            # print(str(r))
            client_writer(conn, 't' + str(r))
            break
    if(state is State.STUDYING):
        while(True):
            r, _, _ = select.select([conn], [], [])
            if r:
                data = conn.recv(1024).decode()
            else:
                continue
            data = str(data).strip('\n')
            print(data, len(data))

            data = data.split('\n')
            if(len(data) > 0):
                for i in range(len(data)):
                    if(data[i][0] == 'r'):
                        data = data[i]
                        break
            if(data[0] == 'r'):
                print(data[1:])
                f = open('./result/result' + userID, 'a')
                f.write(data[1:]+'\n')
                if(len(target_list) == 0):
                    f.write('\n\n')
                f.close()
                f = open('./result/nod_data' + userID, 'a')       
                for item in res:
                    f.write(item + '\n')
                if(len(target_list) == 0):
                    f.write('\n\n')
                f.close()
                break
    
    nod_model.data.clear()
    nod_model.check.clear()
    del target_list[0]

def client_writer(con, msg):
    con.sendall(msg.encode('utf-8'))

if __name__ == "__main__":
    
    s.bind((host, port))
    print('Wait for client ....')
    s.listen(1)
    conn, addr = s.accept()
    s.setblocking(False)
    print('connected')
    userID = input('User id: ')
    print(hint)
    while(True):
        key = input()
        
        if(key == 's' and state == State.INIT):
            state = State.STUDYING
            # generate order and send to client
            shuffle(send_seq)
            target_list = send_seq
            rnd = '0,' + (','.join(send_seq))
            client_writer(conn, rnd)
            pass
        elif(key == 't' and state == State.INIT):
            state = State.TRAINING
            shuffle(send_seq)
            target_list = send_seq
            rnd = '0,' + (','.join(send_seq))
            # generate order and send to client
            client_writer(conn, rnd)
            pass
        elif(key == 'z' and state is not State.INIT):   
            if(len(target_list) == 0):
                print('session complete')
                state = State.INIT
                continue   
            # send start trial signal to client
            client_writer(conn, 'start')
            # start recording data and identify if nodding
            t = threading.Thread(target=client_listener)
            t.start()
            pass
        elif(key == 'a' and (state is State.STUDYING or state is State.TRAINING)):
            client_writer(conn, 'stop')
            state = State.INIT
        
        
    

    
    
