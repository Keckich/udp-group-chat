import socket 
import threading
import string
import random

host = '127.0.0.1'
port = 5107
clients = []
clients_addr = []
want_to_connect = []
groups = []
group_client = []
id_group = 0


class Client(object):
    def __init__(self, id_group, addres, create, status):
        self.id_group = id_group
        self.addres = addres
        self.create = create
        self.status = status


def server():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,  socket.IPPROTO_UDP)    
        sock.bind((host, port))
        
        print('Server online...')
        
        while True:
            create, status = False, False
            data, addres = sock.recvfrom(1024)
            print(addres[0], addres[1])
            message = data.decode('utf-8')
            print(message)
            if message[-2:] == '#y' and addres in clients_addr:
                for client in want_to_connect:
                    for c in clients:
                        if c.addres == addres:
                            id_group = c.id_group
                    if client.id_group == id_group:
                        status = True
                        msg = str(status) + ': you can connect to the server with group_id = ' + str(id_group)
                        client.status = status
                        group_client.append(client)
                        want_to_connect.remove(client)
                        sock.sendto(msg.encode('utf-8'), client.addres)
                        break
                continue
            elif message[-2:] == '#n' and addres in clients_addr:
                for client in want_to_connect:
                    for c in clients:
                        if c.addres == addres:
                            id_group = c.id_group
                    if client.id_group == id_group:
                        status = False
                        msg = str(status) + ': you can\'t connect to the server with group_id = ' + str(id_group)
                        client.status = status
                        clients_addr.remove(client.addres)
                        want_to_connect.remove(client)
                        sock.sendto(msg.encode('utf-8'), client.addres)
                        break
                continue               
                    

            if addres not in clients_addr:
                id_group = message[-10:]
                clients_addr.append(addres) 

                if message[:7] == 'creator':
                    create = True
                    status = True
                else:     
                    creator = ''                         
                    msg = '\n####Only you see this message####\n'+message+'\nDo you agree?[#y/#n]'
                    for c in group_client:
                        if c.id_group == id_group and c.create:
                            creator = c.addres
                    guest_client = Client(id_group, addres, False, False)
                    want_to_connect.append(guest_client)                   
                    sock.sendto(msg.encode('utf-8'), creator)        
                    create = False    
                    continue     
                
                
                if id_group not in groups:
                    groups.append(id_group)
                cur_client = Client(id_group, addres, create, status)  
                if cur_client not in group_client:
                    group_client.append(cur_client)
            print(groups)
            broadcast(group_client, sock, data, id_group)
        sock.close()
        return True
    except OSError:
        return False


def broadcast(clients, sock, data, id_group):
    for client in clients:
        if client.id_group == id_group:
            sock.sendto(data, client.addres)


def read_socket(client):
    while True:
        data = client.recv(1024)
        print(data.decode('utf-8'))


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def client():
    print('Your nickname: ', end='', flush=True)
    nickname = input()
    if nickname == '':
        print('nickname can\'t be emty!')
        exit(0)
    user = ''
    status = False
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,  socket.IPPROTO_UDP)
    client.bind(('', 0))
    
    server = (host, port) 
    print('You want to create new group?[y/n]', end='', flush=True)
    answer = input()
    if answer == 'y':
        user = 'creator ' 
        group = id_generator()
        print('Your group id: '+group)
        status = True        
        client.sendto((user+nickname+' connected to server with group_id = '+group).encode('utf-8'), server)
    elif answer == 'n':
        user = 'guest '
        print('enter group id you want to connect: ', end='', flush=True)
        group = input()
        print('Trying to connect...')
        client.sendto((user+nickname+' trying to connect to server with group_id = '+group).encode('utf-8'), server)
        data = client.recv(1024)
        msg = data.decode('utf-8')
        print('Data to guest: '+ msg)
        if msg[:4] == 'True':
            status = True
        else:
            status = False
    else:
        print('Wrong input')
        exit(0)

    if status:
        thrd = threading.Thread(target=read_socket, args=(client,))
        thrd.start()
        while True:
            message = input()
            client.sendto(('['+nickname+']'+message).encode('utf-8'), server)

def main():
    connect_server = server()
    if not connect_server:
        client()
    else:
        pass



if __name__ == '__main__':
    main()