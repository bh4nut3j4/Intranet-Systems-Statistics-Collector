#!/usr/bin/python2.7
# Client Side Script
import os
import json
import sys
from time import time



def install_and_import(packageName, importName=None, submoduleName=None):
    if importName is None:
        importName = packageName
    import importlib
    try:
        importlib.import_module(importName, submoduleName)
    except ImportError:
        import pip
        pip.main(['install', packageName])

    return

install_and_import('psutil')

import Crypto.Cipher.AES as AES

def encrypt_jsondata(data):
    global encrypted_data
    key = "Key File For Encryption!"
    iv = "16bitivkeydata!!"
    try:
        cipher = AES.new(key, AES.MODE_CFB, iv)
        encrypted_data = cipher.encrypt(data)
    except Exception as e:
        print e
    return encrypted_data

def main():
    global CPU
    result = {}
    import psutil
    memory = psutil.virtual_memory().__dict__
    swap = psutil.swap_memory().__dict__
    disk_partitions = {}
    for each in psutil.disk_partitions():
        """
        Converts the named tuple of disk partion properties into a dictionary
        and assigns to disk partitions dictionary with key as partition name
        """
        disk_partitions[each[0]] = each._asdict()

    try:
        disk_usage = psutil.disk_usage('/').__dict__
        #  If not successful, C:// directory disk usage statistics are obtained
    except:
        disk_usage = psutil.disk_usage('C:\\').__dict__

    network = psutil.net_io_counters().__dict__

    users = {}


    for each in psutil.users():
        """
        Converts the named tuple of user details into a dictionary
        and assigns to users dictionary with key as username
        Each value is converted to a string first
        """
        users[each[0]] = dict([(k, str(v)) for k, v in each._asdict().items()])

    try:
        CPU = {}
        CPU["cpu_usage"] = psutil.cpu_percent()
        CPU["cpu_count"] = psutil.cpu_count()
        CPU["boot_time"] = time() - psutil.boot_time()
        # CPU["min_frequency"] = psutil.cpu_freq().min
        # CPU["max_frequency"] = psutil.cpu_freq().max
        CPU["ctx_switches"] = psutil.cpu_stats().ctx_switches
        CPU["interrupts"] = psutil.cpu_stats().interrupts
        CPU["soft_interrupts"] = psutil.cpu_stats().soft_interrupts
        CPU["syscalls"] = psutil.cpu_stats().syscalls

        result = {"Platform": sys.platform, "Memory": dict([(k, str(v)) for k, v in memory.items()]),
                  "Swap": dict([(k, str(v)) for k, v in swap.items()]), "DiskPartitions": disk_partitions,
                  "DiskUsage": dict([(k, str(v)) for k, v in disk_usage.items()]),
                  "Network": dict([(k, str(v)) for k, v in network.items()]), "Users": users,
                  "CPU": dict([(k, str(v)) for k, v in CPU.items()])}
    except Exception as e:
        print e.message

    if os.name == 'nt':
        import win32evtlog
        host = 'localhost'
        type_of_log = 'Security'
        hand = win32evtlog.OpenEventLog(host, type_of_log)
        readbck = win32evtlog.EVENTLOG_BACKWARDS_READ
        readsqntl = win32evtlog.EVENTLOG_SEQUENTIAL_READ
        flags = readbck | readsqntl
        total = win32evtlog.GetNumberOfEventLogRecords(hand)
        events = win32evtlog.ReadEventLog(hand, flags, 0)
        if events:
            formatedEvents = ''
            for event in events:
                formatedEvents += 'Event Category: ' + str(event.EventCategory)
                formatedEvents += '\nTime Generated: ' + str(event.TimeGenerated)
                formatedEvents += '\nSource Name: ' + event.SourceName
                formatedEvents += '\nEvent ID: ' + str(event.EventID)
                formatedEvents += '\nEvent Type:' + str(event.EventType) + '\n'
            # Adds Logs to the result dictionary
            result["logs"] = str(formatedEvents)

    json_result = json.dumps(result)
    encrypted_data = encrypt_jsondata(json_result)
    print encrypted_data


if __name__ == '__main__':
    main()
