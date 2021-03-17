import os
import getpass
import json
from Crypto.PublicKey import RSA
from datetime import datetime

BANNER = '''
Welcome to \033[0;33;40m
   _____ __      __  __   _____                 
  / ___// /___  / /_/ /_ / ___/__  ______  _____
  \__ \/ / __ \/ __/ __ \\__ \/ / / / __ \/ ___/
 ___/ / / /_/ / /_/ / / /__/ / /_/ / / / / /__  
/____/_/\____/\__/_/ /_/____/\__, /_/ /_/\___/  
                            /____/   
\033[0;37;40m               
'''

def log(message):
    f = open('/opt/SlothSync/client/log/setup.log', 'a')
    now = datetime.now()
    f.write(f'[{now.strftime("%d-%m-%Y")}] -- [{now.strftime("%H:%M:%S")}] --> {message}\n')
    f.close()

if __name__ == '__main__':
    #printing banner
    os.system('clear')
    print(BANNER)

    #checking for root
    if os.getuid() != 0:
        print('\033[0;31;40m[-] Run this as root.\n\033[0;37;40m')
        exit()

    setup = True

    #setting up log folder
    try:
        os.system('rm -r /opt/SlothSync/client 2>/dev/null')
        os.system('mkdir /opt/SlothSync 2>/dev/null')
        os.system('mkdir /opt/SlothSync/client 2>/dev/null')
        os.system('mkdir /opt/SlothSync/client/log 2>/dev/null')
    except:
        print('\033[0;31;40m[-] Failed to setup log folder.\033[0;37;40m')

    #making service
    try:
        f = open('/etc/systemd/system/slothsync-client.service', 'w')
        serviceContent = '''[Unit]
Description = SlothSync client

[Service]
Type = forking
ExecStart = /opt/SlothSync/client/slothsyncclient start
ExecStop = /opt/SlothSync/client/slothsyncclient stop
ExecReload = /opt/SlothSync/client/slothsyncclient reload
ExecStatus = /opt/SlothSync/client/slothsyncclient status

[Install]
WantedBy = multi-user.target
'''    
        f.write(serviceContent)
        f.close()
        log('Service created successfully.')
    except Exception as e:
        log(f'Failed to create service -- {str(e)}')
        print('\033[0;31;40m[-] Failed to create service.\033[0;37;40m')
        setup = False

    #collecting creds
    try:
        print('\n\n\033[0;33;40m[+] Credentials [+]\033[0;37;40m')
        username = input('\033[0,33,40m[+] Username : \033[0;37;40m')
        password = getpass.getpass(prompt='\033[0,33,40m[+] Passowrd : \033[0;37;40m')
        server = input('\033[0,33,40m[+] Server Ip/hostname : \033[0;37;40m')
        while True:
            try:
                port = int(input('\033[0,33,40m[+] Service port : \033[0;37;40m'))
                break
            except:
                print('\033[0;31;40m[-] Port shoud be a number.\033[0;37;40m')
        log('Creds collected successfully.')
    except Exception as e:
        log(f'Collecting creds failed -- {str(e)}')
        print('\033[0;31;40m[-] Failed to collect creds.\033[0;37;40m')
        setup = False


    #setting up the files
    try:
        os.system('cp ./slothsyncclient /opt/SlothSync/client 2>/dev/null')
        os.system('chown root:root /opt/SlothSync/client/slothsyncclient 2>/dev/null')
        os.system('chmod 755 /opt/SlothSync/client/slothsyncclient 2>/dev/null')
        os.system('cp ./slothsyncclient.py /opt/SlothSync/client 2>/dev/null')
        os.system('chown root:root /opt/SlothSync/client/slothsyncclient.py 2>/dev/null')
        os.system('chmod 755 /opt/SlothSync/client/slothsyncclient.py 2>/dev/null')
        log('File setup successfull.')
    except Exception as e:
        log(f'Failed to setup files -- {str(e)}')
        print('\033[0;31;40m[-] Failed to setup files.\033[0;37;40m')
        setup = False

    #creating config file
    try:
        f = open('/opt/SlothSync/client/config.json', 'w')
        config = {
            'username':username,
            'password':password,
            'server':server,
            'port':port
        }
        json.dump(config, f)
        f.close()
        log('Config file created.')
    except Exception as e:
        log(f'Config file creation failed -- {str(e)}')
        print('\033[0;31;40m[-] Failed to create config.\033[0;37;40m')
        setup = False

    #generating RSA key pair
    try:
        os.system('mkdir /opt/SlothSync/client/.keys 2>/dev/null')
        key = RSA.generate(4096)
        f = open('/opt/SlothSync/client/.keys/rsa_public.pem', 'wb')
        f.write(key.publickey().exportKey('PEM'))
        f.close()
        f = open('/opt/SlothSync/client/.keys/rsa_private.pem', 'wb')
        f.write(key.exportKey('PEM'))
        f.close()
        os.system('chown root:root /opt/SlothSync/client/.keys/rsa_private.pem 2>/dev/null')
        os.system('chmod 400 /opt/SlothSync/client/.keys/rsa_private.pem 2>/dev/null')
        os.system('chown root:root /opt/SlothSync/client/.keys/rsa_public.pem 2>/dev/null')
        os.system('chmod 444 /opt/SlothSync/client/.keys/rsa_public.pem 2>/dev/null')
        log('RSA key pair created successfully.')
    except Exception as e:
        log(f'RSA key pair generation failed -- {str(e)}')
        print('\033[0;31;40m[-] RSA key pair generation failed.\033[0;37;40m')
        setup = False

    #setup complete
    if setup == True:
        print('\033[0;33;40m[+] Setup Complete.\033[0;37;40m')
        print(f'\033[0;33;40m[+] Now you can connect to your server.\033[0;37;40m')
        log('Setup completed successfully.')
    else:
        print('\033[0;31;40m[-] Setup failed check the log file.\033[0;37;40m')
        log('Setup failed.')