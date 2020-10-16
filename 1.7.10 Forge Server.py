from shutil import copy
from shutil import copytree
from exceptions import LostResources
from datetime import datetime
import os
import subprocess
import socket


def log(server_files_path, log_msg):

    # Logs an action from the program into the program logs.

    with open(os.path.join(server_files_path, 'creator_logs'), 'a+') as logs:
        now = datetime.now()
        logs.write(f'[{now.day}/{now.month}/{now.year} - {now.hour}:{now.minute}]{log_msg}\n')


def agree_eula(eula):

    # Agrees with the eula.

    with open(eula, 'r') as file:
        # Reads the eula.txt file.
        data = file.readlines()

        # Pops the third line. "eula=false" and replaces it with "eula=true"

        data.pop(2)
        data.append('eula=true')

    with open(eula, 'w') as agreed:

        # Writes each new line into the file. (eula agreed)

        for i in data:
            agreed.write(i)


def run(server_files_path):

    # Runs the server on preset args.

    subprocess.run(
        ['java', '-Xmx1024M', '-Xms1024M', '-jar', 'forge-1.7.10-10.13.4.1614-1.7.10-universal.jar', 'nogui'],
        cwd=server_files_path
    )


def send_resources(server_files_path):

    # Tries to get the resources from the "resources" folder. If except; Raises a LostResources error.
    # Tries to copy the resources to the server_files folder. If except; Raises a LostResources error.
    # Logs every action

    try:
        forge = os.path.join(os.getcwd(), 'resources', 'forge-1.7.10-10.13.4.1614-1.7.10-universal.jar')
        log(server_files_path, f'[-MCSM] Loaded resource {forge.title()}.')

        server = os.path.join(os.getcwd(), 'resources', 'minecraft_server.1.7.10.jar')
        log(server_files_path, f'[-MCSM] Loaded resource {server.title()}.')

        libs = os.path.join(os.getcwd(), 'resources', 'libraries')
        log(server_files_path, f'[-MCSM] Loaded resource {libs.title()}.')

        copytree(libs, os.path.join(server_files_path, 'libraries'), dirs_exist_ok=True)
        log(server_files_path, f'[-MCSM] Sent resource {libs.title()} to ({server_files_path})')

        copy(forge, server_files_path)
        log(server_files_path, f'[-MCSM] Sent resource {forge.title()} to ({server_files_path})')

        copy(server, server_files_path)
        log(server_files_path, f'[-MCSM] Sent resource {server.title()} to ({server_files_path})')

        return forge, server, libs
    except:
        log(server_files_path, f'[-MCSM- ERROR] Resources were lost. Program closed. <---------------- Directory at {os.path.join(server_files_path, "resources")}'
                               f'is either empty, missing files, or non-existant. If this error persists, email the author at alexandresilvacode@gmail.com or open'
                               f'an Issue on GitHub. (Try to reinstall the program!)')
        raise LostResources('Resources folder is missing files.')


def checkfor_files():

    # Checks if the required files exist. Returns the server files path.

    server_files_path = os.path.join(os.getcwd(), 'server_files')
    if not os.path.isdir(server_files_path):

        # Checks if the "server_files" folder exists in the same dir as the executable. If not, creates it.

        os.mkdir(server_files_path)

    if not os.path.isfile(os.path.join(server_files_path, 'forge-1.7.10-10.13.4.1614-1.7.10-universal.jar')):

        # Checks if the files exist inside the server_files. If not:
        # 1 - Sends the resources from the resource folder to it, to begin installation;
        # 2 - Runs the server; (Creates it)
        # 3 - Accepts the EULA

        log(server_files_path, f'[-MCSM] Sending resources to ({server_files_path}).')
        os.mkdir(os.path.join(server_files_path, 'libraries'))
        send_resources(server_files_path)
        log(server_files_path, f'[-MCSM] Successfully sent resources to ({server_files_path}).')

        log(server_files_path, f'[-MCSM- SERVER] Generating server files...')
        run(server_files_path)
        log(server_files_path, f'[-MCSM SERVER] Files generated.')

        log(server_files_path, f'[-MCSM- SERVER.EULA] Agreeing to the Eula...')
        eula = os.path.join(server_files_path, 'eula.txt')
        agree_eula(eula)
        log(server_files_path, f'[-MCSM- SERVER.EULA] Successfully agreed to the Eula.')

    log(server_files_path, f'[-MCSM- SERVER] Running server...')
    return server_files_path


print(f'''
Server IP: {socket.gethostbyname(socket.gethostname())}:25565
- REQUIRES LAN CONNECTION -
Recommended: RadminVPN (https://www.radmin-vpn.com/)
''')

run(checkfor_files())
