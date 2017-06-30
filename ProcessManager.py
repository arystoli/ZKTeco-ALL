import zk,DeviceManager
import win32com.client,ctypes,datetime,sys,pika
import json,multiprocessing,os,pickle,logging
import smtplib,time,threading

class Process_Controller(DeviceManager.Device):
    process = []
    ip = []
    def __init__(self):
        self.idnum = 0
        self.pickle_file_position = 'ipstore.pkl'
        self.OpenProcess()
        
    def WritePickle(self,ip,port,id,position,brand):
        obj = {"ip":ip,"port":port,"id":id,"position":position,"brand":brand}
        with open(self.pickle_file_position,'wb') as myfile:
            pickle.dump(obj,myfile)
        
    def CreateProcess(self,ip,port,n,brand):
        if brand == 'zk':
            selfdevice = zk.zk(ip,port,n,brand)
        else:
            return

    def AddIP(self,info_deel):
        logging.warning( "AddIP")
        ip = info_deel["ip"]
        port = info_deel["port"]
        id = info_deel["id"]
        position = info_deel["position"]
        brand = info_deel["brand"]
        port = int(port)
        id = int(id)
        self.WritePickle(ip,port,id,position,brand)
        self.ip.append(ip);
        self.process.insert(self.processCount,multiprocessing.Process(target = self.CreateProcess,args = (ip,port,id,brand,)) )
        self.process[self.processCount].start()
        self.processCount = self.processCount + 1

    def OpenRecvMessageThread(self):
        logging.warning("new thread")
        self.MQ(1,"MainProcess")

    def OpenProcess(self):
        self.WriteLogInit()
        threads = threading.Thread(target = self.OpenRecvMessageThread,args=())
        threads.start()
#        self.WritePickle('10.0.1.136',4370,1,'hsdjklsfsdf','zk')
        self.processCount = 0
        while 1:
            while 1:
                try:
                    with open(self.pickle_file_position,'rb') as self.pickle_file:
                        dic_ip_port_id_info_brand = pickle.load(self.pickle_file)
                except EOFError:
                    break
                ip = dic_ip_port_id_info_brand["ip"]
                port = dic_ip_port_id_info_brand["port"]
                id = dic_ip_port_id_info_brand["id"]
                position = dic_ip_port_id_info_brand["position"]
                brand = dic_ip_port_id_info_brand["brand"]
                if ip not in self.ip:
                    self.ip.append(ip)
                    self.process.insert(self.processCount,multiprocessing.Process(target = self.CreateProcess,args = (ip,port,id,brand,)))
                    self.process[self.processCount].start()
                    logging.warning("process.id " + str(self.process[self.processCount].pid))
                    logging.warning("process.name " + str(self.process[self.processCount].pid))
                    logging.warning("process.is_alive " + str(self.process[self.processCount].is_alive()))
                    self.process[self.processCount].join()
                    self.processCount = self.processCount + 1
                time.sleep(2)

    def WriteLogInit(self):
        logging.basicConfig(level = logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename= 'manager.log',
                filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)


