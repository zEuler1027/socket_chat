from utils.gui import ChatClient
import tkinter as tk

if __name__ == '__main__':
    root = tk.Tk()
    client = ChatClient(hots='localhost', master=root)
    client.connect_to_server()
    root.mainloop()
