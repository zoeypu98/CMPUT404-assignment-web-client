#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2021 Zoey Pu
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        #split the whole
        recv_response = data.split(' ') #space
        status_code = int(recv_response[1])
        return status_code

    #header + body
    def get_headers(self,data):
        get_split = data.split('\r\n\r\n')
        header = get_split[0]
        return header

    def get_body(self, data):
        get_split = data.split('\r\n\r\n')
        if len(get_split) == 2:
            body = get_split[1]
        else:
            return None
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        #method
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        my_url = urllib.parse.urlparse(url)
        net_loc = my_url.netloc
        net_loc_list = net_loc.split(':')
        if len(net_loc_list) == 2:
            port = int(net_loc_list[1])
        else:
            port = 80
        host = net_loc_list[0]

        path = my_url.path
        if path == "":
            path = '/'
        
        self.connect(host, port)

        #request body
        request_mesg = 'GET ' + path + ' HTTP/1.1\r\n'
        req_host = 'Host: ' + host + '\r\n'
        connct = 'Connection: close\r\n'
        accpt = 'Accept: text/html\r\n'
        usr_agt = 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0\r\n'
        
        request_mesg = request_mesg + req_host + connct + accpt + usr_agt + '\r\n'

        self.sendall(request_mesg)
        self.socket.shutdown(socket.SHUT_WR)

        recv = self.recvall(self.socket)

        code = self.get_code(recv)
        body = self.get_body(recv)

        self.close()
    
        return HTTPResponse(code, body)


    def POST(self, url, args=None):
        #port, host and path
        my_url = urllib.parse.urlparse(url)
        net_loc = my_url.netloc
        net_loc_list = net_loc.split(':')
        if len(net_loc_list) == 2:
            port = int(net_loc_list[1])
        else:
            port = 80
        host = net_loc_list[0]

        path = my_url.path
        if path == "":
            path = '/'

        #connect
        self.connect(host, port)

        #request body
        request_mesg = 'POST ' + path + ' HTTP/1.1\r\n'
        req_host = 'Host: ' + host + '\r\n'
        cont_type = 'Content-Type: application/x-www-form-urlencoded\r\n'
        usr_agt = 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0\r\n'
        connct = 'Connection: keep-alive\r\n'
        
        #query
        query_list = [] 
        if args != None:
            for i in args:
                string = args[i]
                value = string.replace(' ', '+') #change space to + sign
                qline = i + '=' + value  #name=Zoey
                query_list.append(qline) #append every qline in the list
        qline = '&'.join(query_list) #empty or add everything in query, ex:name=Zoey&food=potato -->string

        cont_len = 'Content-length: ' + str(len(qline)) + '\r\n'
        
        request_mesg = request_mesg + req_host + cont_type + usr_agt + connct + cont_len + '\r\n' + qline
        
        #send data
        self.sendall(request_mesg)
        self.socket.shutdown(socket.SHUT_WR)

        recv = self.recvall(self.socket)

        code = self.get_code(recv)
        body = self.get_body(recv)

        self.close()
    
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
