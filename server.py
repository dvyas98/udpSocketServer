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
         if 'heartbeat' in dataString: #if data string has heartbeat in it , then set the last beat.
            clients[addr]['lastBeat'] = datetime.now()
         else:
            positionData = json.loads(data) #else get the positions.
            clients[addr]['position'] = positionData['position']

      else:
         if 'connect' in dataString: # if it has connect in it then start intializin  my cube with last beat, position and ID.
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now() #set the last beat.
          #  clients[addr]['color'] = 0
            clients[addr]['position'] = 0 #init the pos
            message = {"cmd": 0,"player":{"id":str(addr)}}  #NewClient
            m = json.dumps(message)
            
            for c in clients:
               
               sock.sendto(bytes(m,'utf8'), (c[0],c[1]))
               player = {}
               player['id'] = str(c)
               PlayerList['players'].append(player)
                
            sock.sendto(bytes(json.dumps(PlayerList), 'utf8'), (addr[0],addr[1]))  #lets start sending.
 
         

def cleanClients(sock):  #cleaning clients
  while True:
     
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5: #if the last heart beat was five seconds ago then drop theplayer.
            print('Dropped Client: ', c) #lets print who we dropped.


            for cl in list(clients.keys()):
               dmessage = {"cmd": 2, "id":str(c)} #cmd 2 is drop list.
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
      for c in clients:    # if we already have a cube in scene then we need to get the positions and ids.
         player = {}
         player['position'] = clients[c]['position']
         player['id'] = str(c)
         GameState['players'].append(player)
      s=json.dumps(GameState)
      print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()

      time.sleep(0.03)#ms.  #30 packets every seconds.

def main(): 
   
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))  #lets start our threads.
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while True:
      time.sleep(1) # 1 second

if __name__ == '__main__':
   main()
