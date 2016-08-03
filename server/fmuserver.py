# -*- coding: utf-8 -*-
"""
Created on Wed Jun 08 10:48:29 2016

@author: Amane Tanaka
"""

import SocketServer

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
        for i in range(0,self.nitem):
            print self.itemName[i]+": "+self.itemValue[i]
        for i in range(0,self.ninput):
            print self.inputName[i]+" = "+str(self.itemValue[i])
        for i in range(0,self.noutput):
            print self.outputName[i]+" = "+str(self.outputValue[i])
    
    def toolDoStep(self):
        print "t = "+str(self.ctime) + " dt = "+str(self.cstep)
        for i in range(0,self.ninput):
            print self.inputName[i]+" = "+str(self.inputValue[i])
        for i in range(0, self.noutput):
            if self.ctime <= 1e-6:
                self.outputValue[i] = self.inputValue[i]
            else:	
                self.outputValue[i] +=  self.inputValue[i] * self.cstep
            print self.outputName[i]+" = "+str(self.outputValue[i])
    
    def toolTerminate(self):
        print "Terminate tool!"
           
if __name__ == "__main__":
    server = SocketServer.ThreadingTCPServer((HOST, PORT), SampleHandler)
    server.serve_forever()
    
