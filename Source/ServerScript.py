#!/usr/bin/python2.7
#Server Side Script

import os
import re
import json
import logging
import sys

def connect(ip,port,username,password):
    print ip + username + password + port
    global temp_dir, command
    import paramiko
    pwd = os.getcwd()+'/'
    file_name = "ClientScript.py"
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, 22, username, password)

        print "Successfully Connected to IP: "+ip
        secure_copy = ssh.open_sftp()
        stdin, stdout, stderr = ssh.exec_command('echo "cmd" ')
        stdin.close()
        cmd_op = str(stdout.read())
        if cmd_op.__contains__('"'):
            print "Windows Detected"
            temp_dir = "C:\\Windows\\Temp\\"
            command = "sudo python " + temp_dir + file_name
        else:
            print "Linux Detected"
            temp_dir = "/tmp/"
            command = "sudo python " + temp_dir + file_name
            print command
        try:
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            secure_copy.put(pwd+file_name,temp_dir+file_name)
            stdin, stdout, stderr = ssh.exec_command(command)
            stdin.close()
            d = stdout.read()
            print d


        except Exception as e:
            print "Failed to copy ClientScript to the Client Computer with Ip: "+ip
            logging.error(e)
            print format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e

    except Exception, e:
        print "Failed to connect to IP: "+ip
        logging.error(e)
        print format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e



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


