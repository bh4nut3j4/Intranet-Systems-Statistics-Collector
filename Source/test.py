import paramiko

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    s.connect('192.168.0.105',22,'bhanu','Bhanuteja12345')
    secure_copy = s.open_sftp()
    stdin, stdout, stderr = s.exec_command('echo "cmd" ')
    # stdin.close()
    # cmd_op = str(stdout.read())
    # print cmd_op
except Exception as e:
    print 'exp'
    print e