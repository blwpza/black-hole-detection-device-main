import tkinter as tk
import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk
from gps_handler import GPSHandler
from hold_detector import HoldDetector
from client import APIClient
from threading import Thread
import time

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("480x320")
        self.title("Street-Sight-Navigator-Ai")

        label_font = ctk.CTkFont(family="Arial", size=12, weight="bold")

        # init object
        self.gps_handler = GPSHandler('/dev/ttyUSB1', 115200)
        self.lat = 0
        self.lng = 0

        self.hold_detector = HoldDetector('models/holedetect.pt')
        self.client = APIClient('http://192.168.1.45:3000', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NmI4ZTUwODUwN2JjMjg3MmUxNTQ4N2EiLCJpYXQiOjE3MjMzOTMyODh9.dXdMnz1az1W88GOZYFNwzKcoQMezb4EUui1yxw4EZHE')

        self.cap = cv2.VideoCapture(0)
        self.client_self = self.client.get_self()

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        self.name_label = ctk.CTkLabel(self, text="Name: "+ self.client_self.get("name"), text_color="#FFFFFF", font=label_font)
        self.name_label.grid(row=0, column=0, padx=(20, 10), pady=5, sticky="nw")

        self.button_gps_status = ctk.CTkButton(self, width=20, height=20, fg_color="red", text="", hover=False)
        self.button_gps_status.grid(row=0, column=4, padx=(0, 10), pady=5, sticky="nw")

        self.lmain = ctk.CTkLabel(self,text="")
        self.lmain.grid(row=1, column=0, columnspan=2, rowspan=3, padx=20, pady=20, sticky="nsew")

        # Config size button
        button_font = ctk.CTkFont(family="Arial", size=12, weight="bold")
        button_style = {"font": button_font}

        # Toggle Start/Stop Switch
        self.is_running = tk.BooleanVar()
        self.toggle_switch = ctk.CTkSwitch(self, text="Start/Stop", variable=self.is_running, command=self.toggle_detection, onvalue=True, offvalue=False)
        self.toggle_switch.place(x=350, y=80)

        # Button Send
        self.button_send = ctk.CTkButton(self, text="Send >", width=100, height=40, fg_color="#1bb55f", text_color="#FFFFFF", **button_style, command=self.submit_data)
        self.button_send.place(x=350, y=140)

        self.start_task()
        self.render_video()
    
    def start_task(self):
        thread = Thread(target=self.task_gps)
        thread.daemon = True 
        thread.start()

    def task_gps(self):
        while True:
            try:
                lat, lng = self.gps_handler.get_location()
                self.lat = lat
                self.lng = lng
                is_online = self.gps_handler.is_online()
                if is_online:
                    self.button_gps_status.configure(fg_color="green")
                else:
                    self.button_gps_status.configure(fg_color="red")
                time.sleep(1)
            except Exception as e:
                pass

    def toggle_detection(self):
        pass
    
    def submit_data(self):
        self.client.create_explore()
        

    def render_video(self):
        try:
            _, img = self.cap.read()
            if not _:
                return
            if self.is_running.get():
                roi, detections = self.hold_detector.detect_objects(img)
                if detections:
                    for detection in detections:
                        cv2.rectangle(roi, (detection['x1'], detection['y1']), (detection['x2'], detection['y2']), (0, 255, 0), 2)
                        label = f"{detection['size_hole']} ({detection['confidence']:.2f})"
                        cv2.putText(roi, label, (detection['x1'], detection['y1'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    _, buffer = cv2.imencode('.jpg', img)
                    self.client.add_data(buffer,self.lat,self.lng)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (330, 221))
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.lmain.imgtk = imgtk
            self.lmain.configure(image=imgtk)
        except Exception as e:
            pass
        self.lmain.after(10, self.render_video)

