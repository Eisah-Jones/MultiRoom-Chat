'''
Created on Jan 24, 2018

@author: Eisah
'''
import tkinter, threading
from socket import *

class ChatWindow():
    
    def __init__(self):
        self._master = tkinter.Tk()
        self._master.title("Eisah Jones HW1: Chatroom")
        
        self._entry_frame = tkinter.Frame(self._master)
        self._entry_frame.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tkinter.W + tkinter.E, columnspan = 6)
        self._entry_frame.columnconfigure(0, weight = 1)
        
        self._ip_label = tkinter.Label(master = self._entry_frame, text = "IP:")
        self._ip_label.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tkinter.W)
        
        self._ip_var = tkinter.StringVar()
        self._e1 = tkinter.Entry(master = self._entry_frame, textvariable = self._ip_var)
        self._e1.grid(row = 0, column = 1, padx = 5 , pady = 5, sticky = tkinter.W)
        
        
        self._ip_label = tkinter.Label(master = self._entry_frame, text = "Port:")
        self._ip_label.grid(row = 0, column = 2, padx = 5 , pady = 5)
        
        self._port_var = tkinter.StringVar()
        self._e2 = tkinter.Entry(master = self._entry_frame, textvariable = self._port_var, width = 15)
        self._e2.grid(row = 0, column = 3, padx = 6 , pady = 5)
        
        self._connect_button = tkinter.Button(master = self._entry_frame, command = self.connect, text = "Connect")
        self._connect_button.grid(row = 0, column = 4, padx = 5 , pady = 5, sticky = tkinter.W)
        
        self._button_frame = tkinter.Frame(self._master)
        self._button_frame.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = tkinter.W + tkinter.E, columnspan = 6)
        self._button_frame.columnconfigure(0, weight = 1)
        
        self._room1_button = tkinter.Button(master = self._button_frame, command = self.move_room1, text = "Room 1")
        self._room1_button.grid(row = 0, column = 1, padx = 5, pady = 5)
        
        self._room2_button = tkinter.Button(master = self._button_frame, command = self.move_room2, text = "Room 2")
        self._room2_button.grid(row = 0, column = 2, padx = 5 , pady = 5)
        
        self._room3_button = tkinter.Button(master = self._button_frame, command = self.move_room3, text = "Room 3")
        self._room3_button.grid(row = 0, column = 3, padx = 5 , pady = 5)
        
        self._room4_button = tkinter.Button(master = self._button_frame, command = self.move_room4, text = "Room 4")
        self._room4_button.grid(row = 0, column = 4, padx = 5 , pady = 5)
        
        self._name_var = tkinter.StringVar()
        self._e3 = tkinter.Entry(master = self._button_frame, textvariable = self._name_var, width = 15)
        self._e3.grid(row = 0, column = 5, padx = 5 , pady = 5, sticky = tkinter.W)
        self._e3.bind('<Return>', lambda x: self.change_name())
        
        self._confirm_button = tkinter.Button(master = self._button_frame, command = self.change_name, text = "Change Name")
        self._confirm_button.grid(row = 0, column = 6, padx = 5 , pady = 5)
        
        
        chat_frame = tkinter.Frame(self._master)
        chat_frame.grid(row = 2, column = 0, pady = 5, sticky = tkinter.W + tkinter.E, columnspan = 6)
        chat_frame.columnconfigure(0, weight = 1)
        
        self._listbox = tkinter.Listbox(chat_frame, width = 62, height = 25)
        self._listbox.grid(row = 0, column = 0, padx = 5 , pady = 5)


        self._send_frame = tkinter.Frame(self._master)
        self._send_frame.grid(row = 3, column = 0, padx = 5, pady = 5, sticky = tkinter.W + tkinter.E, columnspan = 6)
        self._send_frame.columnconfigure(0, weight = 1)
        
        
        self._send_button = tkinter.Button(master = self._send_frame, command = self._message, text = "Send")
        self._send_button.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tkinter.W)
        
        self._send_var = tkinter.StringVar()
        self._e4 = tkinter.Entry(master = self._send_frame, textvariable = self._send_var, width = 55)
        self._e4.grid(row = 0, column = 1, padx = 5 , pady = 5, sticky = tkinter.W)
        self._e4.bind('<Return>', lambda x: self._message())
        
        self._error_frame = tkinter.Frame(self._master, relief = tkinter.RIDGE, borderwidth = 8)
        self._error_frame.grid(row = 5, column = 0, sticky = tkinter.W + tkinter.E, columnspan = 6)
        self._error_frame.columnconfigure(0, weight = 1)
        
        self._info_label = tkinter.Label(master = self._error_frame, text = "No errors")
        self._info_label.grid(row = 0, column = 0, padx = 5 , pady = 5, sticky = tkinter.W)
        
        def close():
            try:
                self._serverSocket.close()
                self._serverSocket = None
                self._name = None
                self._connected = False
            except:
                pass
        
        self._serverSocket = None
        self._name = None
        self._connected = False
        
        self._master.protocol("WM_DELETE_WINDOW", close())
        self._master.mainloop()
     
    def check_server_response(self):
        while self._connected:
            if not self._serverSocket == None:
                try:
                    response = self._serverSocket.recv(1024).decode("UTF-8")
                    self._parse_packet(response)
                    #print(response)
                except:
                    pass
    
    def _parse_packet(self, p: str):
        # Packet Types
        # Message     -> MessageHeader;MessageContent
        # Room Change -> RoomHeader;RoomNum
        # Disconnect  -> DisconnectHeader;
        parsed = p.split(';')
        command = parsed[0]
        if command == '_message':
            self._update_messages(';'.join(parsed[1:]).rstrip())
        elif command == 'room':
            self.set_room(int(parsed[1]))
        elif command == 'disconnect':
            self._serverSocket.close()
            self.activate_others(0)
            self._serverSocket = None
            self._name = None
            self._connected = False
            self._connect_button['text'] = "Connect"
            self.set_error("Disconnected from server")
        elif command == '1':
            self._name = parsed[1]
        elif command == 'error':
            self.set_error(';'.join(parsed[1:]).rstrip())
        elif command == 'update':
            self._update_messages(';'.join(parsed[1:]).rstrip())
        elif command == '':
            self.activate_others(0)
            self._serverSocket.close()
            self._serverSocket = None
            self._name = None
            self._connected = False
            self._connect_button['text'] = "Connect"
            self.set_error("Disconnected from server")
     
    def change_name(self):
        new_name = self._name_var.get()
        self._name = new_name
        if len(new_name) <= 10: 
                self._send_packet(str('name;' + new_name))
        else:
            self.set_error("Name must be fewer than 10 letters")
     
    def _update_messages(self, m):
        if len(m) == 0 or not self._connected:
            return
        self._listbox.insert('end', m)
     
    def _message(self):
        m = self._send_var.get().rstrip()
        if len(m) == 0:
            return
        self._send_var.set('')
        self._listbox.insert('end', self._name + ': ' + m)
        self._send_packet(str('_message;' + m))
     
    def _send_packet(self, p):
        if self._connected:
            self._serverSocket.send(p.encode())
            self.set_error("Request Sent")
        else:
            self.set_error("Could not send packet, not connected to server.")
    
    def activate_others(self, roomNum):
        i = 1
        for f in [self._room1_button.config, self._room2_button.config, self._room3_button.config, self._room4_button.config]:
            if not i == roomNum:
                f(state = tkinter.NORMAL)
            i += 1
      
    def move_room1(self):
        self._listbox.delete(0, tkinter.END)
        self.activate_others(1)
        self._room1_button.config(state = tkinter.DISABLED)
        self._send_packet("room;1")
    
    def move_room2(self):
        self._listbox.delete(0, tkinter.END)
        self.activate_others(2)
        self._room2_button.config(state = tkinter.DISABLED)
        self._send_packet("room;2")
    
    def move_room3(self):
        self._listbox.delete(0, tkinter.END)
        self.activate_others(3)
        self._room3_button.config(state = tkinter.DISABLED)
        self._send_packet("room;3")
    
    def move_room4(self):
        self._listbox.delete(0, tkinter.END)
        self.activate_others(4)
        self._room4_button.config(state = tkinter.DISABLED)
        self._send_packet("room;4")
    
    def reset_error(self):
        self._info_label.config(text = "No errors")
    
    def set_error(self, e):
        self._info_label.config(text = e)
    
    def connect(self):
        if self._connect_button['text'] == "Connect":
            serverIP = self._ip_var.get()
            serverPort = self._port_var.get() #ports 0-1024 are reserved
            self._serverSocket = socket(AF_INET, SOCK_STREAM) #SOCK_STREAM stands for TCP protocol
            try:
                self._serverSocket.connect((serverIP, int(serverPort)))
                self._connected = True
                self.set_error("Connected!")
                self._connect_button['text'] = "Disconnect"
                self._room1_button.config(state = tkinter.DISABLED)
                listeningThread = threading.Thread(target = self.check_server_response)
                listeningThread.start()
            except:
                self.set_error("Could Not Connect")
        elif self._connect_button['text'] == "Disconnect":
            try:
                self._send_packet('disconnect;{}'.format(self._name))
                self._serverSocket.close()
                self._connected = False
                self._connect_button['text'] = "Connect"
                self.activate_others(0)
                self._listbox.delete(0, tkinter.END)
            except:
                self.set_error("Failed to disconnect")



if __name__ == "__main__":
    window = ChatWindow()
