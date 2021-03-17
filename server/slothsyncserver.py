import socket

def log(message):
    f = open('/opt/SlothSync/server/log/server.log', 'a')
    now = datetime.now()
    f.write(f'[{now.strftime("%d-%m-%Y")}] -- [{now.strftime("%H:%M:%S")}] --> {message}\n')
    f.close()
