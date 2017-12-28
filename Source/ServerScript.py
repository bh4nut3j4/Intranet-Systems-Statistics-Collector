#!/usr/bin/python2.7
#Server Side Script

import os
import re
import json

def connect(ip,port,username,password):
    import paramiko
    print ip + username + password + port
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,port,username,password)
        print "Successfully Connected to IP: "+ip
        secure_copy = ssh.open_sftp()
        stdin, stdout, stderr = ssh.exec_command('echo "cmd" ')
        cmd_op = str(stdout.read())
        if cmd_op.__contains__('"'):
            print "Windows Detected"
        else:
            print "Linux Detected"

    except:
        print "Failed to connect to IP: "+ip
        exit(0)



def main():
    global root
    import xml.etree.ElementTree as ET
    print "Initializing...!"

    try:
        xmldata = ET.parse("clients.xml")
        root = xmldata.getroot()
        print "Parsing the XML File"
    except IOError:
        print "File Not Found"
        exit(0)

    for x in root.findall("client"):
        ip = x.get("ip")
        username = x.get("username")
        password = x.get("password")
        port = x.get("port")
        connect(ip,port,username,password)
        # print ip + username + password + port

if __name__=='__main__':
    main()


