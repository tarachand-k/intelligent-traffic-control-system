import math
from PIL import Image
import customtkinter as ctk
from src import constants

from src.traffic_signal import TrafficSignal


class TrafficController(ctk.CTkToplevel):
    def __init__(self, image_processor, object_detector, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = []
        self.currentGreen = 0
        self.currentYellow = 0
        self.currentVehicleDensity = 0
        self.nextGreen = (self.currentGreen + 1) % 4
        self.simulationTime = 120
        self.timeElapsed = 0
        self.minimum = constants.DEFAULT_MINIMUM
        self.maximum = constants.DEFAULT_MAXIMUM
        self.image_processor = image_processor
        self.object_detector = object_detector
        self.green_signal_img = None
        self.yellow_signal_img = None
        self.red_signal_img = None

        self.initialize_window()

    # Initialization of signals with default values
    def initialize_window(self):
        self.red_signal_img = ctk.CTkImage(Image.open("images/signals/red.png"), size=(60, 150))
        self.yellow_signal_img = ctk.CTkImage(Image.open("images/signals/yellow.png"), size=(60, 150))
        self.green_signal_img = ctk.CTkImage(Image.open("images/signals/green.png"), size=(60, 150))

        self.title("Traffic Manager")
        self.geometry("560x515")

        # self.resizable(False, False)
        main_frame = ctk.CTkFrame(self, width=480, height=330)
        main_frame.pack(pady=(10, 5), padx=10)

        # initializeSignals(main_frame)
        for i in range(constants.NO_OF_SIGNALS):
            row = i // 2
            col = i % 2
            signal = TrafficSignal(main_frame, i, row, col)
            self.signals.append(signal)

        # Buttons at the button
        buttons_frame = ctk.CTkFrame(self, width=480, height=80)
        buttons_frame.pack(fill="x", pady=5, padx=5, side="bottom")

        start_button = ctk.CTkButton(buttons_frame, text="Start", font=(None, 18), border_spacing=8,
                                     cursor="hand2", command=lambda: self.after(200, self.start_simulation))
        start_button.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        back_button = ctk.CTkButton(buttons_frame, text="Back", font=(None, 18), border_spacing=10,
                                    cursor="hand2", command=lambda: self.destroy())
        back_button.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def start_simulation(self):
        vehicle_density = self.calculate_density(self.currentGreen + 1)

        current_signal = self.signals[self.currentGreen]
        current_signal.green = math.ceil(vehicle_density * 0.8)
        current_signal.red = 0
        current_signal.update_vehicle_density(vehicle_density)
        current_signal.update_signal_text(current_signal.green)
        current_signal.update_signal_img(self.green_signal_img)

        self.signals[self.nextGreen].red = current_signal.red + current_signal.yellow + current_signal.green
        self.update_values_periodically()

    def update_values_periodically(self):
        self.update_values()
        # calculate time and density for next signal
        if self.signals[self.nextGreen].red == 5:
            self.calculate_next_signal_info()
        if self.signals[self.currentGreen].green > 0:
            self.after(1000, self.update_values_periodically)  # Schedule next update after 1 second
        else:
            self.currentYellow = 1
            # current active signal
            current_signal = self.signals[self.currentGreen]
            current_signal.update_signal_img(self.yellow_signal_img)
            current_signal.update_signal_text(current_signal.yellow)
            self.after(1000, self.update_values_periodically_yellow)

    def update_values_periodically_yellow(self):
        self.update_values()
        if self.signals[self.currentGreen].yellow > 0:
            self.after(1000, self.update_values_periodically_yellow)  # Schedule next update after 1 second
        else:
            self.currentYellow = 0
            self.signals[self.currentGreen].update_signal_img(self.red_signal_img)
            self.signals[self.currentGreen].yellow = constants.DEFAULT_YELLOW
            self.signals[self.currentGreen].red = constants.DEFAULT_RED

            self.currentGreen = self.nextGreen
            self.nextGreen = (self.currentGreen + 1) % 4
            self.signals[self.nextGreen].red = self.signals[self.currentGreen].yellow + self.signals[
                self.currentGreen].green

            self.signals[self.currentGreen].update_signal_img(self.green_signal_img)
            self.after(1000, self.update_values_periodically)

    def update_values(self):
        for i in range(constants.NO_OF_SIGNALS):
            if i == self.currentGreen:
                if self.currentYellow == 0:
                    self.signals[i].decrease_green_time()
                else:
                    self.signals[i].decrease_yellow_time()
            else:
                self.signals[i].red -= 1

    def calculate_next_signal_info(self):
        vehicle_density = math.ceil(self.calculate_density(self.nextGreen+1))
        self.signals[self.nextGreen].update_vehicle_density(vehicle_density)
        greenTime = math.ceil(vehicle_density * 0.8)
        if greenTime < self.minimum:
            greenTime = self.minimum
        elif greenTime > self.maximum:
            greenTime = self.maximum
        self.signals[self.nextGreen].green = greenTime
        self.signals[self.nextGreen].update_signal_text(greenTime)

    def calculate_density(self, lane):
        lane_img = self.image_processor.load_image(f"lane_{lane}.png")
        boxes, confs, classes = self.object_detector.detect_and_filter_objects(lane_img)
        detected_next_lane_img, detected_classes = self.object_detector.draw_boxes(lane_img, boxes, confs, classes)

        print(f"*************** LANE {lane} ***************")
        print("Vehicle density: ", len(detected_classes))
        print("Detected classes: ", detected_classes)
        self.image_processor.save_processed_img(lane, detected_next_lane_img)
        return len(detected_classes)
