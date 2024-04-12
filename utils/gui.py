import socket
import tkinter as tk
from tkinter import simpledialog, scrolledtext, font
import pyaudio
import threading

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
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.audio_stream_open = False
        self.current_room = None
        self.mic = threading.Event()

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

        self.leave_btn = tk.Button(left_frame, text="Leave Room", command=self.leave_room_, font=self.button_font)
        self.leave_btn.pack(fill=tk.X, pady=5)

        self.microphone_btn = tk.Button(left_frame, text="Microphone", command=self.control_microphone, font=self.button_font)
        self.microphone_btn.pack(fill=tk.X)

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
            self.current_room = room_name
            self.mic = threading.Event()
            if not self.audio_stream_open:
                self.control_audio_stream()
                self.send_thread = threading.Thread(target=self.send_data_to_server, daemon=True)
                self.send_thread.start()
                self.receive_thread = threading.Thread(target=self.receive_audio_stream, daemon=True)
                self.receive_thread.start()

    def leave_room_(self):
        if self.current_room:
            threading.Thread(target=self.handle_leave_room).start()
        else:
            self.rooms_list.insert(tk.END, "You are not in a room.\n", 'message_font')

    def handle_leave_room(self):
        try:
            self.control_audio_stream()
            self.send_command(f"LEAVE {self.current_room}")
            response = self.chat_socket.recv(1024).decode()
            self.rooms_list.insert(tk.END, f"{response}\n", 'message_font')
            self.current_room = None
        except Exception as e:
            print(f"Error leaving room: {e}")
                
    def send_command(self, command):
        self.chat_socket.send(command.encode())

    def input_audio_stream(self):
        self.in_stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    def output_audio_stream(self):
        self.out_stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=1024)

    def send_data_to_server(self):
        while not (self.stop_event.is_set() or self.mic.is_set()):
            try:
                if self.current_room:
                    in_data = self.in_stream.read(1024)
                    audio_message = b'AUDIO ' + self.current_room.encode() + b' ' + in_data
                    self.chat_socket.sendall(audio_message)
            except:
                break

    def receive_audio_stream(self):
        self.chat_socket.settimeout(5) 
        while not self.stop_event.is_set():
            try:
                data = self.chat_socket.recv(4096)
                if data.startswith(b'AUDIO '):
                    _, room_name, audio_data = data.split(b' ', 2)
                    self.play_audio(audio_data)
                else:
                    pass
            except socket.timeout:
                print("Socket timeout, no data received or nobody is talking.")
                continue
            except Exception as e:
                print(f"Error receiving audio: {e}")
                break
    
    def play_audio(self, data):
        if self.audio_stream_open:
            self.out_stream.write(data)

    def control_audio_stream(self):
        if self.audio_stream_open:
            self.audio_stream_open = False
            self.in_stream.stop_stream()
            self.in_stream.close()
            self.out_stream.stop_stream()
            self.out_stream.close()
            self.stop_event.set()
        else:
            self.audio_stream_open = True
            self.stop_event = threading.Event()
            self.input_audio_stream()
            self.output_audio_stream()

    def control_microphone(self):
        if self.mic.is_set():
            self.mic = threading.Event()
            self.send_thread = threading.Thread(target=self.send_data_to_server, daemon=True)
            self.send_thread.start()
            self.microphone_btn.config(text="Microphone")
        else:
            self.mic.set()
            self.microphone_btn.config(text="Mute")
