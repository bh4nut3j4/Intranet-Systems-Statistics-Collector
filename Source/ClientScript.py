#!/usr/bin/python2.7
#Client Side Script

import os
#
# print os.uname()
#
import psutil
# print psutil.cpu_stats()
# print psutil.cpu_count()
# print psutil.cpu_freq()
#
# # print psutil.cpu_freq().current
# # print psutil.cpu_freq().max
# # print psutil.cpu_freq().min
#
# print psutil.boot_time()
# print psutil.sensors_battery()
# print psutil.sensors_fans()
#
# try:
#     print psutil.sensors_temperatures()
# except:
#     print ""
# print psutil.users()
#
# print psutil.pids()
#
import paramiko
from Crypto.Cipher import AES

def main():
   import psutil
   import json
   d = psutil.cpu_stats()
   print json.dumps(d)

if __name__ =='__main__':
   main()



