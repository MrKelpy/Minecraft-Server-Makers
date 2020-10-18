from shutil import copy
from datetime import datetime
import os
import subprocess
import socket


version = '1.8.9'


class LostResources(BaseException):
    pass


class NoPortPropertyFound(BaseException):
    pass


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


def change_server_port(server, port):

    log(server, '[-MCSM- SERVER] Updating server port')
    # Changes the port of a server in the properties of it.

    properties = os.path.join(server, 'server.properties')

    with open(properties, 'r') as file:
        # Reads the server.properties file.
        data = file.readlines()

    for line in data:

        # Finds the server-port line in the properties. If None, raises a NoPortPropertyFound Error.

        if 'server-port=' in line:

            # Pops the index of the server-port line.
            index_of_portline = data.index(line)
            data.pop(index_of_portline)
            break
    else:
        log(server, f'[-MCSM- ERROR] Could not find Property "Server Port" at ({os.path.join(properties, "server.properties")}) ')
        raise NoPortPropertyFound(
            f'Could not find Property "Server Port" at ({os.path.join(properties, "server.properties")})')

    # Inserts the new port into the same line of the server.properties file.
    data.insert(index_of_portline, f'server-port={port}\n')
    log(server, f'[-MCSM- SERVER] Changed server port to "{port}"')

    with open(properties, 'w') as changed:

        # Writes each new line into the server.properties file.

        for line in data:
            changed.write(line)


def getserver_ip(java_server):

    # Gets an unique server IP.

    port = 25565  # Sets the starting port to 25565
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    done = False

    # Loops through a function to detect if the current port is being used.

    while not done:
        try:

            log(java_server, f'[-MCSM- SERVER] Checking port "{port}"')
            self_ip = socket.gethostbyname(socket.gethostname())  # Gets the local IPv4 address.
            s.bind((socket.gethostbyname(socket.gethostname()), port))  # Tries to bind the IPv4 address to the current port.

            log(java_server, '[-MCSM- SERVER] Port is free. Claiming port...')
            change_server_port(java_server, port)  # Changes the server port.
            return f'{self_ip}:{port}\n'  # Returns the server IP in the format - IPv4:port

        except NoPortPropertyFound as err:
            raise err

        except:

            # If port is being used, jumps to the next port.
            log(java_server, f'[-MCSM- SERVER] Port already in use. Jumping to next port - {port+1}')
            port += 1


def run(server_files_path, integral=False):

    # Runs the server on preset args.
    # If integral is set to true, the server will be run with the objective of starting it.

    if integral is True:

        log(server_files_path, '[-MCSM- SERVER] Running server')
        print(f'''
----------------------------------------------------
© Copyright - Alexandre Silva 2020
Server IP: {getserver_ip(server_files_path).strip()}
Version: Vanilla {version}
- REQUIRES LAN CONNECTION -
Recommended: RadminVPN (https://www.radmin-vpn.com/)
----------------------------------------------------
''')

    subprocess.run(
        ['java', '-Xmx1024M', '-Xms1024M', '-jar', f'minecraft_server.{version}.jar', 'nogui'],
        cwd=server_files_path
    )


def send_resources(server_files_path):

    # Tries to get the resources from the "resources" folder. If except; Raises a LostResources error.
    # Tries to copy the resources to the server_files folder. If except; Raises a LostResources error.
    # Logs every action

    try:

        properties_file = os.path.join(os.getcwd(), 'resources', 'server.properties')
        if not os.path.isfile(properties_file):
            log(server_files_path, f'[-MCSM] Failed to load resource {properties_file.title()}.')
            raise LostResources('Resources folder is missing files.')
        log(server_files_path, f'[-MCSM] Loaded resource {properties_file.title()}.')

        server = os.path.join(os.getcwd(), 'resources', f'minecraft_server.{version}.jar')
        if not os.path.isfile(server):
            log(server_files_path, f'[-MCSM] Failed to load resource {server.title()}.')
            raise LostResources('Resources folder is missing files.')
        log(server_files_path, f'[-MCSM] Loaded resource {server.title()}.')

        copy(properties_file, server_files_path)
        log(server_files_path, f'[-MCSM] Sent resource {properties_file.title()} to ({server_files_path})')

        copy(server, server_files_path)
        log(server_files_path, f'[-MCSM] Sent resource {server.title()} to ({server_files_path})')

        return server
    except:
        log(server_files_path, f'[-MCSM- ERROR] Resources were lost. Program closed. <---------------- Directory at {os.path.join(server_files_path, "resources")}'
                               f'is either empty, missing files, or non-existent. If this error persists, email the author at alexandresilvacode@gmail.com or open'
                               f'an Issue on GitHub. (Try to reinstall the program!)')
        raise LostResources('Resources folder is missing files.')


def checkfor_files():

    # Checks if the required files exist. Returns the server files path.

    server_files_path = os.path.join(os.getcwd(), 'server_files')

    if not os.path.isdir(server_files_path):

        # Checks if the "server_files" folder exists in the same dir as the executable. If not, creates it.

        os.mkdir(server_files_path)

    log(server_files_path, '[-MCSM] Preparing server...')

    if not os.path.isfile(os.path.join(server_files_path, f'minecraft_server.{version}.jar')):

        # Checks if the files exist inside the server_files. If not:
        # 1 - Sends the resources from the resource folder to it, to begin installation;
        # 2 - Runs the server; (Creates it)
        # 3 - Accepts the EULA

        log(server_files_path, f'[-MCSM] Checking for resources to be sent to ({server_files_path}).')
        os.makedirs(os.path.join(server_files_path, 'libraries'), exist_ok=True)
        send_resources(server_files_path)
        log(server_files_path, f'[-MCSM] Successfully sent resources to ({server_files_path}).')

        log(server_files_path, f'[-MCSM- SERVER] Generating server files...')
        run(server_files_path)
        log(server_files_path, f'[-MCSM SERVER] Files generated.')

        log(server_files_path, f'[-MCSM- SERVER.EULA] Agreeing to the Eula...')
        eula = os.path.join(server_files_path, 'eula.txt')
        agree_eula(eula)
        log(server_files_path, f'[-MCSM- SERVER.EULA] Successfully agreed to the Eula.')

    log(server_files_path, f'[-MCSM] Server prepared.')
    log(server_files_path, f'[-MCSM- SERVER] Initialising Server')

    return server_files_path


sv = checkfor_files()
run(sv, integral=True)
