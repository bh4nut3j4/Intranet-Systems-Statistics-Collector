#!/usr/bin/python2.7
#Server Side Script

import Crypto.Cipher.AES as AES
import json
import os
import sys
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3


def decrypt_data(encrypted_data):
    global decrypted_data
    key = "Key File For Encryption!"
    iv = "16bitivkeydata!!"
    try:
        cipher = AES.new(key, AES.MODE_CFB, iv)
        decrypted_data = cipher.decrypt(encrypted_data[:-1])
        print "Decrypted Successfully !"
    except Exception as e:
        print e
    return decrypted_data


def send_mail(message, current, limit, email):
    try:
        email_configurations = json.load(open("email_config.json"))
        sender = email_configurations["email_configurations"]["username"]
        password = email_configurations["email_configurations"]["password"]
    except IOError:
        print "IOError while trying to read file! Check Whether File Exits!"
        quit()

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = email
    msg['Subject'] = 'Email from Machine Statistics Collection System'
    message = message + "\nCurrent:" + current + "\nLimit:" + limit
    msg.attach(MIMEText(message))

    mailserver = smtplib.SMTP('smtp.gmail.com', 587)
    # identify ourselves to smtp gmail client
    mailserver.ehlo()
    # secure our email with tls encryption
    mailserver.starttls()
    # re-identify ourselves as an encrypted connection
    mailserver.ehlo()
    mailserver.login(sender, password)
    mailserver.sendmail(sender, email, msg.as_string())
    print "Alert Email Sent !"
    mailserver.quit()


def connect(ip,port,username,password):
    print ip + username + password + port
    global temp_dir, command
    import paramiko
    windows = False
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
            windows = True
            print "Windows Detected"
            temp_dir = "C:\\Windows\\Temp\\"
            command = "sudo python " + temp_dir + file_name
        else:
            windows = False
            print "Linux Detected"
            temp_dir = "/tmp/"
            command = "sudo python " + temp_dir + file_name
            print command
        try:
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            secure_copy.put(pwd+file_name,temp_dir+file_name)
            print "ClientScript transfer completed !"
            stdin, stdout, stderr = ssh.exec_command(command)
            if not windows:
                stdin.write(password+'\n')
                stdin.flush()
                stdin.close()
            ssh_response = stdout.read()
            decrypted_data = decrypt_data(ssh_response)
            json_data = json.loads(decrypted_data)
            secure_copy.close()
            ssh.close()
            return json_data

        except Exception as e:
            print "Failed to copy ClientScript to the Client Computer with Ip: "+ip
            print e.message

    except Exception, e:
        print "Failed to connect to IP: "+ip
        print e.message

    except paramiko.ssh_exception.AuthenticationException:
        print "Authentication has failed!"
        quit()

    except paramiko.ssh_exception.BadHostKeyException:
        print "Server hostkey could not be verified!"
        quit()

    except paramiko.ssh_exception.socket.error:
        print "Socket error occurred while connecting!"
        quit()

    except IOError:
        print "IOError while trying to read file!"
        quit()

    except:
        print "Unknown exception: {0}!".format(str(sys.exc_info()[0]))
        quit()


def insert_into_db(data,time,ip):
    conn = sqlite3.connect('NetworkData.db')
    print "Opened database successfully."

    #  Enter system statistics into the database
    if len(conn.execute("select id from systemdetails where ip_address = '" + ip + "';").fetchall()) == 0:
        conn.execute("INSERT INTO systemdetails (ip_address, platform, date_entry) \
                              VALUES ('" + ip + "', '" + data["Platform"] + "', '" + time + "');")

    for each in data["Users"]:
        conn.execute(("INSERT INTO systemusers (name, terminal, host, started, date_entry, ip_id) \
                              VALUES ('" + data["Users"][each]["name"] + "', '" + data["Users"][each][
            "terminal"] + "', '" + data["Users"][each]["host"] + "', '" + data["Users"][each][
                          "started"] + "', '" + time + "', (select id from systemdetails where ip_address = '" + ip + "'));"))

    for each in data["DiskPartitions"]:
        conn.execute("INSERT INTO diskpartitions (fstype, device, mountpoint, opts, date_entry, ip_id) \
                              VALUES ('" + data["DiskPartitions"][each]["fstype"] + "', '" +
                     data["DiskPartitions"][each]["device"] + "', '" + data["DiskPartitions"][each][
                         "mountpoint"] + "', '" + data["DiskPartitions"][each][
                         "opts"] + "', '" + time + "', (select id from systemdetails where ip_address = '" + ip + "'));")

    conn.execute("INSERT INTO swap (used, percent, free, sin, sout, total, date_entry, ip_id) \
                          VALUES ('" + data["Swap"]["used"] + "', '" + data["Swap"]["percent"] + "', '" + data["Swap"][
        "free"] + "', '" + data["Swap"]["sin"] + "', '" + data["Swap"]["sout"] + "', '" + data["Swap"][
                     "total"] + "', '" + time + "', (select id from systemdetails where ip_address = '" + ip + "'));")

    conn.execute("INSERT INTO memory (available, used, cached, percent, free, inactive, active, shared, total, buffers, date_entry, ip_id) \
                          VALUES ('" + data["Memory"]["available"] + "', '" + data["Memory"]["used"] + "', '" +
                 data["Memory"]["cached"] + "', '" + data["Memory"]["percent"] + "', '" + data["Memory"][
                     "free"] + "', '" + data["Memory"]["inactive"] + "', '" + data["Memory"]["active"] + "', '" +
                 data["Memory"]["shared"] + "', '" + data["Memory"]["total"] + "', '" + data["Memory"][
                     "buffers"] + "', '" + time + "', (select id from systemdetails where ip_address = '" + ip + "'));")

    conn.execute("INSERT INTO diskusage (used, percent, free, total, date_entry, ip_id) \
                          VALUES ('" + data["DiskUsage"]["used"] + "', '" + data["DiskUsage"]["percent"] + "', '" +
                 data["DiskUsage"]["free"] + "', '" + data["DiskUsage"][
                     "total"] + "', '" + time + "', (select id from systemdetails where ip_address = '" + ip + "'));")

    if "logs" in data.iterkeys():
        conn.execute("INSERT INTO cpu (current_frequency, cpu_usage, soft_interrupts, min_frequency, cpu_count, max_frequency, boot_time, syscalls, interrupts, ctx_switches, logs, date_entry, ip_id) \
                              VALUES ('" + data["CPU"]["current_frequency"] + "', '" + data["CPU"][
            "cpu_usage"] + "', '" + data["CPU"]["soft_interrupts"] + "', '" + data["CPU"]["min_frequency"] + "', '" +
                     data["CPU"]["cpu_count"] + "', '" + data["CPU"]["max_frequency"] + "', '" + data["CPU"][
                         "boot_time"] + "', '" + data["CPU"]["syscalls"] + "', '" + data["CPU"]["interrupts"] + "', '" +
                     data["CPU"]["ctx_switches"] + "', '" + data[
                         "logs"] + "', '" + time + "', (select id from systemdetails where ip_address = '" + ip + "'));")
    else:
        conn.execute("INSERT INTO cpu (current_frequency, cpu_usage, soft_interrupts, min_frequency, cpu_count, max_frequency, boot_time, syscalls, interrupts, ctx_switches, date_entry, ip_id) \
                              VALUES ('" + data["CPU"]["current_frequency"] + "', '" + data["CPU"][
            "cpu_usage"] + "', '" + data["CPU"]["soft_interrupts"] + "', '" + data["CPU"]["min_frequency"] + "', '" +
                     data["CPU"]["cpu_count"] + "', '" + data["CPU"]["max_frequency"] + "', '" + data["CPU"][
                         "boot_time"] + "', '" + data["CPU"]["syscalls"] + "', '" + data["CPU"]["interrupts"] + "', '" +
                     data["CPU"][
                         "ctx_switches"] + "', '" + time + "', (select id from systemdetails where ip_address = '" + ip + "'));")

    conn.execute("INSERT INTO network (packets_sent, bytes_recv, packets_recv, dropin, dropout, bytes_sent, errout, errin, date_entry, ip_id) \
                          VALUES ('" + data["Network"]["packets_sent"] + "', '" + data["Network"][
        "bytes_recv"] + "', '" + data["Network"]["packets_recv"] + "', '" + data["Network"]["dropin"] + "', '" +
                 data["Network"]["dropout"] + "', '" + data["Network"]["bytes_sent"] + "', '" + data["Network"][
                     "errout"] + "', '" + data["Network"][
                     "errin"] + "', '" + time + "', (select id from systemdetails where ip_address = '" + ip + "'));")

    #  Make the changes requested
    conn.commit()
    print "Records created successfully."
    #  close the connection to the database after creating the table
    conn.close()


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
        mail = x.get("mail")
        data = connect(ip,port,username,password)
        time = str(datetime.now())

        print x.findall("alert")[0].get("limit")

        if data["Memory"]["percent"] > x.findall("alert")[0].get("limit"):
            print "Memory Usage is more than the Limit! \n Sending an alert Email !"
            send_mail("Memory Limit Exceeded", data["Memory"]["percent"],
                      x.findall("alert")[0].get("limit"), mail)
        if data["CPU"]["cpu_usage"] > x.findall("alert")[1].get("limit"):
            print "CPU Usage is more than the Limit! \n Sending an alert Email !"
            send_mail("CPU Limit Exceeded", data["CPU"]["cpu_usage"],  x.findall("alert")[0].get("limit"),
                      mail)

        insert_into_db(data,time,ip)

if __name__=='__main__':
    main()