import socket 
import threading
import random
import struct

host = '127.0.0.1'
multicast_host = '224.3.22.71'
clients_addr = []

def read_server(sock):
    while True:    
        data, addres = sock.recvfrom(1024)
        message = data.decode('utf-8')
        if addres not in clients_addr:
            if message[:7] == 'creator':
                create = True
                status = True
            else:     
                creator = ''                         
                msg = '\n####Only you see this message####\n'+message+'\nDo you agree?[#y/#n] '
                print(msg, addres)
                answer = input()
                if answer == '#y':
                    clients_addr.append(addres)                 
                sock.sendto(answer.encode('utf-8'), addres)          
                                 
                

def server(creator=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,  socket.IPPROTO_UDP)    
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    port = random.randint(2000,5000)
    sock.bind((host, port))

    print(f'Server online with port: {port}...')

    thrd = threading.Thread(target=read_server,args=(sock,))
    thrd.start()
    client(port, creator)



def read_client(sock):
    while True:
        try:
            data, server = sock.recvfrom(1024)
            print(data.decode('utf-8')) 
        except socket.timeout:
            print('timed out, no more responses')
            break        
            

def client(group_port, creator):
    status = False
    server = (host, int(group_port))
    multicast_group = (multicast_host , int(group_port))
    #socket1
    group_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,  socket.IPPROTO_UDP)    
    group_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    group_sock.bind(('', int(group_port)))

    group = socket.inet_aton(multicast_host)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    group_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    #socket2
    client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    client.bind((host, 0))

    #socket3 
    send_group_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    send_group_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    print('Your nickname: ', end='', flush=True)
    nickname = input()   
    if creator:
        status = True
        client.sendto(('creator '+nickname+' connected to server with group_id = '+str(group_port)).encode('utf-8'), server)
    else:
        client.sendto(('guest '+nickname+' trying to connect to server with group_id = '+str(group_port)).encode('utf-8'), server)
        print('Trying to connect...')
        data = client.recv(1024)
        msg = data.decode('utf-8')
        print('Data to guest: '+ msg)
        if msg[-2:] == '#y':
            status = True
            message = nickname + ' connected!'
            send_group_sock.sendto(message.encode('utf-8'), multicast_group)
        else:
            status = False    

    if status:
        thrd = threading.Thread(target=read_client, args=(group_sock,))
        thrd.start()
        while True:
            message = input()
            send_group_sock.sendto(('['+nickname+']'+message).encode('utf-8'), multicast_group)


if __name__ == '__main__':
    creator = False
    print('You want to create new group?[y/n]', end='', flush=True)
    answer = input()
    if answer == 'y':
        creator = True
        server(creator)
    else:
        print('Enter group id:', end='', flush=True)
        g_port = input()
        client(g_port, creator)
