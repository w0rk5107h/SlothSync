import os
import getpass
import hashlib
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
    f = open('/opt/SlothSync/server/log/setup.log', 'a')
    now = datetime.now()
    f.write(f'[{now.strftime("%d-%m-%Y")}] -- [{now.strftime("%H:%M:%S")}] --> {message}\n')
    f.close()
            
if __name__ == '__main__':
    #printing banner
    os.system('clear')
    print(BANNER)

    setup = True

    try:
        os.system('rm -r /opt/SlothSync')
        os.system('mkdir /opt/SlothSync')
        os.system('mkdir /opt/SlothSync/server')
        os.system('mkdir /opt/SlothSync/server/log')
    except:
        pass

    #checking for root
    if os.getuid() != 0:
        print('\033[0;31;40m[-] Run this as root.\033[0;37;40m')
        exit()

    #making service
    try:
        f = open('/etc/systemd/system/slothsync.service', 'w')
        serviceContent = '''[Unit]
Description = SlothSync Server

[Service]
Type = forking
ExecStart = /opt/SlothSync/server/slothsyncserver start
ExecStop = /opt/SlothSync/server/slothsyncserver stop
ExecReload = /opt/SlothSync/server/slothsyncserver reload

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

    #initializing password
    try:
        while True:
            while True:
                password = getpass.getpass(prompt='\033[0;33;40m[+] Enter a password : \033[0;37;40m')
                if len(password) >= 8:
                    break
                else:
                    print('\033[0;31;40m[-] Enter a password with minimum 8 chars :(\033[0;37;40m')
            conf_password = getpass.getpass(prompt='\033[0;33;40m[+] Re-enter the password : \033[0;37;40m')
            if password == conf_password:
                pass_hash = hashlib.md5(password.encode())
                break
            else:
                print('\033[0;31;40m[-] Passwords don\'t match :( !!\nTry again...\n\n\033[0;37;40m')
        log('Password initialized successfully.')
    except Exception as e:
        log(f'Failed to initialize password -- {str(e)}')
        print('\033[0;31;40m[-] Failed to initialize password.\033[0;37;40m')
        setup = False

    #initializing port
    try:
        while True:
            port = int(input('\033[0;33;40m[+] Enter a port on which you want to run this service : \033[0;37;40m'))
            if port > 1000:
                break
            else:
                print('\033[0;31;40m[-] Invalid port, choose something larger than 1000.\033[0;37;40m')
        log('Port initialized successfully.')
    except Exception as e:
        log(f'Failed to initialized port -- {str(e)}')
        print('\033[0;31;40m[-] Failed to initialize port.\033[0;37;40m')
        setup = False

    #setting up the files
    try:
        os.system('cp ./slothsyncserver /opt/SlothSync/server')
        os.system('chown root:root /opt/SlothSync/server/slothsyncserver')
        os.system('chmod 755 /opt/SlothSync/server/slothsyncserver')
        os.system('cp ./slothsyncserver.py /opt/SlothSync/server')
        os.system('chown root:root /opt/SlothSync/server/slothsyncserver.py')
        os.system('chmod 755 /opt/SlothSync/server/slothsyncserver.py')
        log('File setup successfull.')
    except Exception as e:
        log(f'Failed to setup files -- {str(e)}')
        print('\033[0;31;40m[-] Failed to setup files.\033[0;37;40m')
        setup = False

    #creating config file
    try:
        f = open('/opt/SlothSync/server/config.json', 'w')
        config = {
            'pass':pass_hash,
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
        os.system('mkdir /opt/SlothSync/server/.keys')
        key = RSA.generate(4096)
        f = open('/opt/SlothSync/server/.keys/rsa_public.pem', 'wb')
        f.write(key.public_key().export_key('PEM'))
        f.close()
        f = open('/opt/SlothSync/server/.keys/rsa_private.pem', 'wb')
        f.write(key.export_key('PEM'))
        f.close()
        os.system('chown root:root /opt/SlothSync/server/.keys/rsa_private.pem')
        os.system('chmod 400 /opt/SlothSync/server/.keys/rsa_private.pem')
        os.system('chown root:root /opt/SlothSync/server/.keys/rsa_public.pem')
        os.system('chmod 444 /opt/SlothSync/server/.keys/rsa_public.pem')
        log('RSA key pair created successfully.')
    except Exception as e:
        log(f'RSA key pair generation failed -- {str(e)}')
        print('\033[0;31;40m[-] RSA key pair generation failed.\033[0;37;40m')
        setup = False

    #setup complete
    if setup == True:
        print('\033[0;33;40m[+] Setup Complete.\033[0;37;40m')
        print(f'\033[0;33;40m[+] Now you can access this server at \033[0;36;40m<your server\'s public IP>:{port}\033[0;37;40m')
    else:
        print('\033[0;31;40m[-] Setup failed check the log file.\033[0;37;40m')
