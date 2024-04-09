import socket
import tkinter as tk
from tkinter import simpledialog, scrolledtext, font

class ChatClient(tk.Frame):
    def __init__(self, host='localhost', master=None):
        super().__init__(master)
        self.master = master
        self.master.title("CHAT ROOM")
        self.button_font = font.Font(family="Helvetica", size=10)  
        self.text_font = font.Font(family="Consolas", size=14) 
        self.create_widgets()
        self.pack(fill=tk.BOTH, expand=True)
        self.chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (host, 1027)

    def create_widgets(self):
        # Left frame for buttons
        left_frame = tk.Frame(self)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.create_btn = tk.Button(left_frame, text="Create Room", command=self.create_room, font=self.button_font)
        self.create_btn.pack(fill=tk.X)

        self.list_btn = tk.Button(left_frame, text="List Rooms", command=self.list_rooms, font=self.button_font)
        self.list_btn.pack(fill=tk.X, pady=5)

        self.join_btn = tk.Button(left_frame, text="Join Room", command=self.join_room, font=self.button_font)
        self.join_btn.pack(fill=tk.X)

        # Right frame for rooms history
        right_frame = tk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.rooms_list = scrolledtext.ScrolledText(right_frame, height=30, width=80)
        self.rooms_list.pack(fill=tk.BOTH, expand=True)
        self.rooms_list.tag_configure('message_font', font=self.text_font)

    def connect_to_server(self):
        self.chat_socket.connect(self.server_address)

    def create_room(self):
        room_name = simpledialog.askstring("Room Name", "Enter room name:", parent=self)
        if room_name:
            self.send_command(f"CREATE {room_name}")
            response = self.chat_socket.recv(1024).decode()
            self.rooms_list.insert(tk.END, f"{response}\n", 'message_font')

    def list_rooms(self):
        self.send_command("LIST")
        response = self.chat_socket.recv(1024).decode()
        self.rooms_list.insert(tk.END, f"{response}\n", 'message_font')

    def join_room(self):
        room_name = simpledialog.askstring("Room Name", "Enter room name to join:", parent=self)
        if room_name:
            self.send_command(f"JOIN {room_name}")
            response = self.chat_socket.recv(1024).decode()
            self.rooms_list.insert(tk.END, f"{response}\n", 'message_font')

    def send_command(self, command):
        self.chat_socket.send(command.encode())

root = tk.Tk()
client = ChatClient(master=root)
client.connect_to_server()
root.mainloop()
