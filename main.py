import os
import can
import time
import datetime
import logging

class HATD():
    def __init__(self, test='clear_dtc'):
        print("Iniciando test con variable ", test)
        #logging.info("Iniciando test con variable "+test)
        self.lst_results = [] #lista para guardar los resultados
        #ids y mensajes recurrentes
        self.req_id=0x773
        self.resp_id=0x7DD
        #self.resp_id=0x773
        #self.req_id=0x7DD
        
        self.diag_session=[0x10,0x03]
        self.extended_session=[0x10,0x40]
        self.tester_present=[0x3E,0X00]
        self.reset_dtc=[0x14,0xFF,0xFF,0xFF]
        #paths
        self.project_path = "/home/pi/Desktop/HATD"
        self.recursos_path = self.project_path+'/recursos'
        self.especificacion_path = self.project_path+'/especificacion'
        self.resultados_path = self.project_path+'/resultados'
        self.logs_path = self.project_path+'/logs'
        #configuracion del log
        self.logpath = self.logs_path+'/log_'+str(datetime.datetime.now())+'.log'
        logfilename='log_'+str(datetime.datetime.now())+'.log'
        print(self.logpath.replace(" ","_"))
        self.FORMAT = '%(asctime)s--%(levelname)s:%(message)s'
        logging.basicConfig(filename=self.logpath.replace(" ","_"), level=logging.DEBUG, format=self.FORMAT)
        logging.info("Iniciando test con variable "+test)
        #diccionarios
        self.id = {}
        self.msg = {}
        self.expected = {}
        self.response = {}
        #lista de resultados finales
        self.result = []
        #switch de tests
        self.test = test
        if self.test == 'dtc_mem': self.datapath = self.especificacion_path+'/dtc_mem.csv'
        elif self.test == 'meas_val': self.datapath =  self.especificacion_path+'/meas_values.csv'
        elif self.test == 'clear_dtc':
            print ('Manda comando de borrar los dtcs')
            #logging.info('Manda comando de borrar los dtcs')
        
    def can_up(self):
        result = False
        #configuracion del puerto can de la shield
        os.system('sudo ip link set can1 up type can bitrate 500000   dbitrate 8000000 restart-ms 1000 berr-reporting on fd on')
        os.system('sudo ifconfig can1 txqueuelen 65536')
        self.can0 = can.interface.Bus(channel = 'can1', bustype = 'socketcan_ctypes')# socketcan_native
        
        result = True
        return result
             
    def timestamp(self):
        return str(datetime.datetime.now())
    
    def loadData(self):
        result = False
        with open(self.datapath, mode='rb') as fin:
                cnt = [i.split(b';') for i in fin.read().split(b'\r\n')]
                             
                for row in cnt[1:]:
                    self.id[row[0].decode('utf8')] = row[0].decode('utf8')
                    self.msg[row[0].decode('utf8')] = row[1].decode('utf8')
                    self.expected [row[0].decode('utf8')] = row[3].decode('utf8')
        
        result = True
        return result

    def send(self, msg_id=0x773, msg_data =[0x10,0x03]):
        msg = can.Message(arbitration_id=msg_id, data=msg_data, extended_id=False)
        self.can0.send(msg)
        print("send: ", msg)
        logging.info("send: "+str(msg.data))
        time.sleep(0.1)
        resp_aux = self.recive(self.resp_id)
        if resp_aux != None:
            resp = resp_aux.data
            return resp_aux
        else: return None
        
    def recive(self, msg_id=0x7DD):
                
        resp_received = False
        attemps = 0

        if (resp_received == False and attemps < 10):
            msg = self.can0.recv(8)          

            if msg is None:
                print('Timeout occurred, no message.Trying Again.')
                logging.warning('Timeout occurred, no message.Trying Again.')
                          
            elif msg.arbitration_id == 0x7DD and msg.data[0] != 0x3E:
                print('diag_message arrived: ')
                print ("recive: ",msg)
                logging.info('diag_message arrived: '+str(msg.data))
                resp_received = True
                print (resp_received)
                return msg
                #attemps = 11
    #           print('id: ', hex(msg.arbitration_id))
    #           print('size: ',msg.dlc)
    #           print('data: ',msg.data)
            else:
                print("Other message ID received: ", hex(msg.arbitration_id))
                print ("recive: ",msg)
                logging.warning("Other message ID received: "+str(hex(msg.arbitration_id)))
                
            attemps+=1
            print("Attemp ", attemps)
            
        if resp_received == True: return msg
        else: return None
        

    def write(self,msg_id,msg_data):
        
        self.lst_results =[]
        msg_bytes =[None, None, None, None, None, None, None, None]
        size = len(msg_data)
##        print(size)
        
        size_hex = int(hex(size),0)
        
        if size <= 6:
            print("Single frame")
            
            msg_bytes[0] = 0x10 #indicate FF
            msg_bytes[1]= size_hex #datalenght
            for byte in range(0,size_hex):
                msg_bytes[byte+2] = int(msg_data[byte])
            for byte in range(size_hex+2, 8):
                msg_bytes[byte] = int('0x55',0) 
            
            #print("msg: ",msg_bytes)
            
            resp_aux = self.send(self.req_id, msg_bytes)
            
            #resp_aux = self.recive(self.resp_id)
            #print("resp_aux:", resp_aux.data)
            if resp_aux != None: resp = resp_aux.data
            else: resp = None
            
            self.lst_results.append(resp)
            
        elif size > 6:

            print("Large frame")
            byte = 0
            header_first_frame = 2
            header_other_frames = 1
            nframes = round((size + header_first_frame + (round(size/8)))/8)
            print("Num. de frames: ",nframes)
            
            print("First frame")
            frame =0xff
            if size < 256:
                msg_bytes[0] = 0x10 #indicate FF
                msg_bytes[1]= size_hex #datalenght
            else:
                msg_bytes[0] = 0x10+round((size/256)) #indicate FF
                msg_bytes[1] = size_hex-256 #datalenght

            for byte in range(0,6):
                #acaba de montar First frame con 5bytes de data(original version)
                msg_bytes[byte+2] = int(msg_data[byte])
                #print('0x'+str(msg_data[byte]))
            
            resp_aux = self.send(self.req_id, msg_bytes) #envia frame

            #resp_aux = self.recive(self.resp_id)
            
            if resp_aux != None: resp = resp_aux.data
            else: resp = None
 
            bs = int(resp[1])
            bs_count = 1
            print("blocksize:",bs)

            sn = 1
            for frame in range(1,nframes+1): #el caso en que la secuencia es mayor a 15 (F) el byte 0 sera 2F en ese caso   
                print("Continuous frame")
                #print(hex(0x20+sn))
                
                msg_bytes[0]=0x20+sn #indicate SM
                
                for cont in range(1,8):
                    if byte < size-1:
                        byte+=1
                        msg_bytes[cont]=int('0x'+str(msg_data[byte]),0)
##                        print('0x'+data[byte])
                    else:
                        msg_bytes[cont]=0x00
##                        print("0x00")

                resp_aux = self.send(self.req_id, msg_bytes)

                if sn<15: sn=sn+1
                else: sn = 0
##
                if bs_count < bs: bs_count+=1
                else:
                    print("Espera CF tras frame ", frame)
                    bs_count = 1
                    time.sleep(0.5)              

                time.sleep(0.2)

            #resp_aux = self.recive(self.resp_id)
            resp = resp_aux.data

            self.lst_results.append(resp)

        return self.lst_results
    
    def steps(self):
        
        result = False
        i = 0
        for identification,message in zip(self.id, self.msg):
            i +=1
            print ("step: "+str(i))
            logging.info("step: "+str(i))
            print("tester_present")
            logging.info("tester_present")
            self.write(self.req_id,self.tester_present)
            time.sleep(0.1)
            print("diag_session")
            logging.info("diag_session")
            #self.write(self.req_id,self.diag_session)
            #time.sleep(1)
            print("extended_session")
            logging.info("extended_session")
            #self.write(self.req_id,self.extended_session)
            #time.sleep(1)
            msg_data_aux= self.msg[message].split(" ")
            msg_data = []
            for byte in msg_data_aux: msg_data.append(int(('0x'+byte),16))
            print (self.id[identification], ":", msg_data,":", len(msg_data))
            print("message_data")
            #if len(msg_data) <= 8: self.send(self.req_id,msg_data)
            #else: self.write(self.req_id,msg_data)
            resp = self.write(self.req_id,msg_data)
            time.sleep(0.1)

            if resp[0] != None:
                self.response[identification] = resp
                logging.info(str(resp))
            else:
                self.response[identification] = 'No se ha recibido respuesta'
                logging.error('No se ha recibido respuesta')
            
            if i%30 ==0:
                self.deinit()
                self.can_up()
      
            time.sleep(0.2)
            
        result = True
            
        return result
        
    def report(self):
        result =  True
        
        str_fileName = self.resultados_path+'//'+self.test+'_'+self.timestamp()[0:16].replace('-','').replace(' ','').replace(':','').replace('.','')+'.csv'
        
        for el1,el2,el3,el4 in zip(self.id,self.msg,self.expected,self.response):
            el2_aux=self.msg[el2]
            el3_aux=self.expected[el3]
            el4_aux=self.response[el4][:len(el3_aux)]
            lst_aux = list(el4_aux[0])
            resp =''
            for el in lst_aux:
                byte_mod =''
                if type(el) != str:
                    byte = hex(el).replace('0x','')
                    if len(byte) == 1: byte_mod = '0'+byte
                    else: byte_mod = byte
                else: byte_mod = 'None'
                resp = resp + byte_mod + ' '

            print("id: ",el1)
            print("message: ", el2_aux)
            print("expected: ", el3_aux)
            print("response: ", resp)
            
            if (resp[0:len(el3_aux)]).upper() == (el3_aux): result = "OK"
            else: result = "ERROR"
        
            self.result.append(el1+";"+el2_aux+";"+resp+";"+el3_aux+";"+result)

        str_out = 'Identificator;Data sended;Response;Expected;Result\n'+'\n'.join(self.result)
    
        
        with open(str_fileName,'w') as fout:
            fout.write(str_out)

        print ("Report finished and saved in path: " , str_fileName)
        logging.info("Report finished and saved in path: "+str_fileName)
        
        result = False
        return result
    
    def deinit(self):
        os.system('sudo ifconfig can1 down')
        
    def run(self):
        result = False

        if self.test in("dtc_mem","meas_val"):
            self.loadData()
            self.can_up()
            self.steps()   
            self.deinit()
            self.report()
        elif self.test == "clear_dtc":
            self.can_up()
            print("tester_present")
            self.write(self.req_id,self.tester_present)
            time.sleep(2)
            self.write(self.req_id,self.diag_session)
            time.sleep(2)
            self.write(self.req_id,self.extended_session)
            time.sleep(2)
            print("clear_dtc")
            self.write(self.req_id,self.reset_dtc)
            time.sleep(15)
            self.deinit()
            
        print("Test finished")
              
        result = True
        return result
    
if __name__ == '__main__':
    HATD().run()
