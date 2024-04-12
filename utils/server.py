import socket
import threading

class ChatServer:
    def __init__(self, host='0.0.0.0', port=1027):
        self.host = host
        self.port = port
        self.rooms = {}  # key: room name, value: list of client sockets
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client_socket, _ = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                if data.startswith(b'AUDIO '):  
                    room_name, audio_data = self.parse_audio_data(data)
                    self.broadcast_audio(room_name, audio_data, client_socket)
                else:
                    self.handle_text_data(client_socket, data)
            except ConnectionResetError:
                break
        client_socket.close()

    def handle_text_data(self, client_socket, data):
        command, _, room_name = data.decode().partition(' ')
        if command == 'CREATE':
            self.create_room(room_name)
            client_socket.send(f"Room '{room_name}' created.".encode())
        elif command == 'LIST':
            rooms_list = ', '.join(self.rooms.keys())
            client_socket.send(f"Available rooms: {rooms_list}".encode())
        elif command == 'JOIN':
            message = self.join_room(room_name, client_socket)
            client_socket.send(message.encode())
        elif command == 'LEAVE':
            current_room = room_name
            message = self.leave_room(current_room, client_socket)
            client_socket.send(message.encode())

    def create_room(self, room_name):
        if room_name not in self.rooms:
            self.rooms[room_name] = []

    def join_room(self, room_name, client_socket):
        if room_name in self.rooms:
            self.rooms[room_name].append(client_socket)
            return f"Joined room: {room_name}"
        else:
            return f"Room '{room_name}' does not exist."

    def leave_room(self, current_room, client_socket):
        self.rooms[current_room].remove(client_socket)
        return f"Left room: {current_room}"
        
    def parse_audio_data(self, data):
        _, room_name, audio_data = data.split(b' ', 2)
        return room_name.decode(), audio_data
    
    def broadcast_audio(self, room_name, audio_data, sender_socket):
        if room_name in self.rooms:
            for client_socket in self.rooms[room_name]:
                if client_socket != sender_socket:
                    client_socket.send(b'AUDIO ' + room_name.encode() + b' ' + audio_data)

if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.start_server()
