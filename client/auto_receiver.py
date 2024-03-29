import constants
import struct
import time
import config
import json
import socket
import tkinter as tk
from client import Client
import base64


def create_receiver(request, frame, listbox):
    global messages_frame
    messages_frame = frame
    global lbox
    lbox = listbox

    try:
        client = Client()
        client.connect(config.HOST, config.PORT)
    except ConnectionRefusedError as e:
        tk.messagebox.showerror('Connection Error', 'Wrong params or server is shutdown!')
        exit()

    # login to server
    client.handle(request)
    
    while True:
        time.sleep(1)
        request = create_request(constants.CMD_RECEIVE_MSG)
        response = client.handle(request)
        unpack_response(constants.CMD_RECEIVE_MSG, response)

        request = create_request(constants.CMD_LIST)
        response = client.handle(request)
        unpack_response(constants.CMD_LIST, response)

        request = create_request(constants.CMD_RECEIVE_FILE)
        response = client.handle(request)
        unpack_response(constants.CMD_RECEIVE_FILE, response)



def create_request(cmd_code: int) -> bytes:
    request = get_request_code(cmd_code)
    return request


def unpack_response(cmd_code: int, response: bytes) -> None:
    if (len(response) == 1):
        return
    
    cmd_func = select_command(cmd_code)
    try:
        cmd_func(response)
    except:  
        pass


def select_command(cmd_code: int):
    switcher = {
        constants.CMD_LIST: list_cmd,
        constants.CMD_RECEIVE_MSG: recv_msg,
        constants.CMD_RECEIVE_FILE: recv_file,
    }

    # Get the function from switcher dictionary
    func = switcher.get(cmd_code, "nothing")
    # Return command function
    return func



def get_request_code(code: int) -> bytes:
    request = struct.pack('b', code)
    return request


def unpack_response_code(response: bytes) -> int:
    response_code = struct.unpack('b', response)[0]
    return response_code


lbox = None
registered_users = []
def list_cmd(response):
    global registered_users
    response_content = response.decode(config.ENCODING)
    users = json.loads(response_content)
    user_list = users['user_list']

    is_changed = False

    if (len(registered_users) == 0):
        registered_users = list(user_list)
        is_changed = True

    if is_changed:
        for user in registered_users:
            lbox.insert(tk.END, user)
        return    

    for user in user_list:
        if not (user in registered_users):
            registered_users.append(user)
            lbox.insert(tk.END, user)



messages_frame = None
def print_in_messages(message_text):
    messageVar = tk.Message(messages_frame.scrollable_frame, text=message_text, width=350) 
    messageVar.pack(anchor=tk.W, pady=2, padx=2)
    pass


def recv_msg(response):    
    response_content = response.decode(config.ENCODING)
    msg = json.loads(response_content)

    msg_val = f'{msg["sender"]}:\n{msg["message"]}'
    print_in_messages(msg_val)


def recv_file(response):    
    response_content = response.decode(config.ENCODING)
    file_msg = json.loads(response_content)
    sender = file_msg['sender']
    filename = file_msg['filename']

    msg_val = f'{sender}:\nSent a "{filename}" file.'
    print_in_messages(msg_val)

    file_content = file_msg['file_content']

    with open(filename, "w") as f:
        f.write(file_content)
