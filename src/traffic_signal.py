from tkinter import ttk
import customtkinter as ctk
from PIL import Image

from src import constants


class TrafficSignal(ctk.CTkFrame):
    def __init__(self, master, lane, row, col, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.lane = lane
        self.signal_text = 0
        self.red = constants.DEFAULT_RED
        self.yellow = constants.DEFAULT_YELLOW
        self.green = constants.DEFAULT_GREEN
        self.vehicle_density = 0
        self.grid(row=row, column=col, padx=10, pady=10)
        self.columnconfigure(0, weight=1)

        self.signal_img = ctk.CTkImage(
            Image.open("images/signals/red.png"), size=(60, 150)
        )

        self.heading = ctk.CTkLabel(
            self, width=245, font=(None, 16), text=f"Lane {lane + 1}", bg_color="gray28"
        )
        self.heading.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        self.signal_img_label = ctk.CTkLabel(self, image=self.signal_img, text="")
        self.signal_img_label.grid(
            row=1, column=0, sticky="w", padx=(10, 0), pady=(0, 10)
        )

        self.vehicle_density_label = ctk.CTkLabel(
            self, text=f"Vehicle density: 0", font=(None, 14)
        )
        self.vehicle_density_label.place(x=85, y=45)

        ctk.CTkLabel(self, text=f"On Time: ", font=(None, 14)).place(x=85, y=80)
        self.signal_text_label = ctk.CTkLabel(self, text="10", font=(None, 14))
        self.signal_text_label.place(x=155, y=80)

    def update_signal_img(self, img):
        self.signal_img_label.configure(image=img)

    def update_signal_text(self, text):
        self.signal_text_label.configure(text=f"{text}")

    def update_vehicle_density(self, density):
        self.vehicle_density_label.configure(text=f"Vehicle density: {density}")

    def decrease_green_time(self):
        self.green -= 1
        self.update_signal_text(self.green)

    def decrease_yellow_time(self):
        self.yellow -= 1
        self.update_signal_text(self.yellow)
