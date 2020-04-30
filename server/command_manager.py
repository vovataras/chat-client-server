import config
import constants
import struct
import threading
import json
import users_data


def handle_command(message):
    # get user command from message
    command = message[0]
    debug_message(f'Command: {command}')

    # get the function of a specific command
    cmd_func = select_command(command)

    args = None
    # if there is args of the command
    if (len(message) > 1):
        args = message[1:].decode(config.ENCODING)
        debug_message(f'Content: {args}')

    try:
        response = cmd_func(args)
    except:
        debug_message('Wrong command')
        response = create_response(constants.INCORRECT_COMMAND)

    return response


def select_command(command):
    func_ping  = ping
    func_echo  = echo
    func_login = login
    func_list  = list_cmd
    func_msg   = msg
    func_file  = file_cmd

    switcher = {
        constants.CMD_PING: func_ping,
        constants.CMD_ECHO: func_echo,
        constants.CMD_LOGIN: func_login,
        constants.CMD_LIST: func_list,
        constants.CMD_MSG : func_msg,
        constants.CMD_FILE: func_file,
    }

    # Get the function from switcher dictionary
    func = switcher.get(command, "nothing")
    # Return command function
    return func



def ping(args=None):
    debug_message('ping')
    response_code = constants.CMD_PING_RESPONSE
    response = struct.pack('b', response_code)
    return response


def echo(args=None):
    debug_message('echo')
    if (args):
        response = bytearray(f'ECHO: {args}', config.ENCODING)
    else:
        response = bytearray(f'ECHO:', config.ENCODING)
    
    return response


def login(args=None):
    debug_message('login')
    debug_message(users_data.AUTHORIZED_USERS)
    
    if not (args):
        return create_response(constants.WRONG_PARAMS)
        
    userdata = json.loads(args)
    if not (('login' in userdata) and ('password' in userdata)):
        return create_response(constants.WRONG_PARAMS)

    registered = False
    auth_success = False

    # check if user is registered
    for user in users_data.REGISTERED_USERS:
        if (userdata['login'] == user['login']):
            registered = True
            if (userdata['password'] == user['password']):
                auth_success = True
            break

    # add new user if not registered
    if not registered:
        users_data.REGISTERED_USERS.append(userdata)
        users_data.AUTHORIZED_USERS.append(userdata)
        return create_response(constants.CMD_LOGIN_OK_NEW)
    
    # if wrong password
    if not auth_success:
        return create_response(constants.LOGIN_WRONG_PASSWORD)

    authorized = False
    # check if user is authorized
    for user in users_data.AUTHORIZED_USERS:
        if (userdata['login'] == user['login']):
            authorized = True
            break
    
    if not authorized:
        # add new user if not registered
        users_data.AUTHORIZED_USERS.append(userdata)
    
    return create_response(constants.CMD_LOGIN_OK)



def list_cmd(args=None):
    print('list')


def msg(args=None):
    print('msg')


def file_cmd(args=None):
    print('file')



def create_response(code):
    response = struct.pack('b', code)
    return response



def debug_message(message):
    print('-'*35)
    print(f'|debugging| {threading.current_thread().native_id}: {message}')