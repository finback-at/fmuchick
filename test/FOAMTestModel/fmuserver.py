# -*- coding: utf-8 -*-
"""
Created on Wed Jun 08 10:48:29 2016

@author: Amane Tanaka
"""

import SocketServer
import subprocess
import os
import time
import signal

HOST, PORT = "", 9999
BSIZE = 512

class SampleHandler(SocketServer.BaseRequestHandler):
    state = 0
    
    ctime = 0.0
    cstep = 0.0
    
    nitem = 0
    ninput = 0
    noutput = 0
    
    itemName = []
    itemValue = []
    inputName = []
    inputValue = []
    outputName = []
    outputValue = []
    
    # solver time
    stime = 0.0
    proc = None    
    
    def handle(self):
        cmd = False
        print "connect from:", self.client_address
        while True:
            data = self.request.recv(BSIZE)
            if len(data) == 0:
                break
            data = data.rstrip('\0')
            if not cmd:
                if data == "end":
                    data = "end"
                    self.request.send(data)
                    break
                elif data == "shutdown":
                    self.server.shutdown()
                    self.request.send("end")
                    self.request.close()
                    break
                elif data == "instantiate":
                    self.instantiate()
                    self.state = 1
                elif data == "initialize":
                    self.initialize()
                    self.state = 2
                elif data == "dostep":
                    self.doStep()
                    self.state =3
                elif data == "terminate":
                    self.terminate()
                    self.state = 1
                    break;
                else:    
                    self.request.send(data)
        self.request.close()        
        print "closed! "

    def instantiate(self):
        self.request.send("ok")
        # receive number of items
        data = self.request.recv(BSIZE)
        data = data.rstrip('\0')
        self.nitem = int(data)
        # receive items                     
        for i in range(0,self.nitem):
            # item name
            self.request.send("ok")
            data = self.request.recv(BSIZE)
            if len(data) == 0:
                break
            data = data.rstrip('\0')
            self.itemName.append(data)
            # item value
            self.request.send("ok")
            data = self.request.recv(BSIZE)
            if len(data) == 0:
                break
            data = data.rstrip('\0')
            self.itemValue.append(data)
        # receive number of input variables
        self.request.send("ok")
        data = self.request.recv(BSIZE)
        data = data.rstrip('\0')
        self.ninput = int(data)
        # receive input variables                    
        for i in range(0,self.ninput):
            # item name
            self.request.send("ok")
            data = self.request.recv(BSIZE)
            if len(data) == 0:
                break
            data = data.rstrip('\0')
            self.request.send("ok")
            self.inputName.append(data)
            # item value
            data = self.request.recv(BSIZE)
            if len(data) == 0:
                break
            data = data.rstrip('\0')
            value = float(data)                        
            self.inputValue.append(value)
        # receive number of output variables
        self.request.send("ok")
        data = self.request.recv(BSIZE)
        data = data.rstrip('\0')
        self.noutput = int(data)
        # receive output variables                    
        for i in range(0,self.noutput):
            # item name
            self.request.send("ok")
            data = self.request.recv(BSIZE)
            if len(data) == 0:
                break
            data = data.rstrip('\0')
            self.outputName.append(data)
            # item value
            self.request.send("ok")
            data = self.request.recv(BSIZE)
            if len(data) == 0:
                break
            data = data.rstrip('\0')
            value = float(data)                        
            self.outputValue.append(value)
        self.request.send("ok")
        print "instantiated\n"        

    def initialize(self):
        self.toolInitialize()
        self.request.send("ok")
        print "initialized\n"

    def doStep(self):
        self.request.send("ok")
        # recieve communication point and step
        data = self.request.recv(BSIZE)
        data = data.rstrip('\0')
        self.ctime = float(data)
        self.request.send("ok")
        data = self.request.recv(BSIZE)
        data = data.rstrip('\0')
        self.cstep = float(data)
        # recieve input variables
        for i in range(0,self.ninput):
            self.request.send("ok")
            data = self.request.recv(BSIZE)
            data = data.rstrip('\0')
            self.inputValue[i] = float(data)
        # user customize section
        self.request.send("ok")
        data = self.request.recv(BSIZE)
        self.toolDoStep()
        self.request.send("ok")
        # send output variables
        for i in range(0,self.noutput):
            data = self.request.recv(BSIZE)
            data = data.rstrip('\0')
            self.request.send(str(self.outputValue[i]))
    
    def terminate(self):
        self.toolTerminate()       
        self.request.send("ok")
        self.request.close()
                    
    def toolInitialize(self):
        self.proc = subprocess.Popen('./Run', shell=True)
        time.sleep(10)
        print "pid = "+str(self.proc.pid)
        self.stime = 0.0        
    
    def toolDoStep(self):
        t = self.ctime + self.cstep
        print str(self.stime)+" "+str(t)
        while self.stime < t:
            self.doSolverStep()
        print "t = "+str(self.ctime) + " dt = "+str(self.cstep)
    
    def toolTerminate(self):
        subprocess.check_call('./Post', shell=True)
        if not (self.proc is None):
            os.killpg(os.getpgid(self.proc.pid), signal.SIGKILL)
        print "Terminate tool!"

    def doSolverStep(self):
        grad0 = 0
        ratio0 = 1
        grad1 = 0
        ratio1 = 1
        f = open("comms/heater_topAir/coupleGroup/T.in","w")
        for i in range(0,8):
            f.write(str(self.inputValue[0])+" "+str(grad0)+" "+str(ratio0)+"\n")
        for i in range(8,48):
            f.write(str(self.inputValue[1])+" "+str(grad1)+" "+str(ratio1)+"\n")
        f.close()
        # generate lock file
        f = open("comms/OpenFOAM.lock","w")
        f.close()
        while (os.path.isfile("comms/OpenFOAM.lock")):
            time.sleep(0.02)
        cmd = "tail -n1 postProcessing/topAir/volAvgT/0/cellSource.dat"
        a = subprocess.check_output( cmd.split(" ") ).rstrip("\n").split("\t")
        self.stime = float(a[0].rstrip())
        self.outputValue[0] = float(a[1])
        print "t="+str(self.stime)+" Tavr="+str(self.outputValue[0])
           
if __name__ == "__main__":
    server = SocketServer.ThreadingTCPServer((HOST, PORT), SampleHandler)
    server.serve_forever()
    
