import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

clients = {}
def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      dataString = str(data)

      PlayerList ={"cmd": 3, "players": []} 

      if addr in clients:
         if 'heartbeat' in dataString:
            clients[addr]['lastBeat'] = datetime.now()
         else:
            positionData = json.loads(data)
            clients[addr]['position'] = positionData['position']

      else:
         if 'connect' in dataString:
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['color'] = 0
            clients[addr]['position'] = 0
            message = {"cmd": 0,"player":{"id":str(addr)}}  #NewClient
            m = json.dumps(message)
            
            for c in clients:
               
               sock.sendto(bytes(m,'utf8'), (c[0],c[1]))
               player = {}
               player['id'] = str(c)
               PlayerList['players'].append(player)
                
            sock.sendto(bytes(json.dumps(PlayerList), 'utf8'), (addr[0],addr[1]))
 
         

def cleanClients(sock):
  while True:
     
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Dropped Client: ', c)


            for cl in list(clients.keys()):
               dmessage = {"cmd": 2, "id":str(c)}
               m = json.dumps(dmessage)
               sock.sendto(bytes(m,'utf8'), (cl[0],cl[1]))
            clients_lock.acquire() 
            del clients[c]
            clients_lock.release()   
      time.sleep(1)
      
def gameLoop(sock):
   while True:
      GameState = {"cmd": 1, "players": []}  #Update CLient
      clients_lock.acquire()
      #print (clients)
      for c in clients:
         player = {}
         player['position'] = clients[c]['position']
         player['id'] = str(c)
         GameState['players'].append(player)
      s=json.dumps(GameState)
      print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()

      time.sleep(0.33)#ms.

def main(): 
   
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()
