import os
from PIL import Image
import customtkinter as ctk
from tkinter import filedialog
from tkinter import messagebox
from threading import Thread

from src import constants
from src import ImageProcessing, ObjectDetection, TrafficController
from test import test_video_detection
from simulation import start_simulation


class TestVideoWindow(ctk.CTkToplevel):
    def __init__(self, input_folder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_folder = input_folder
        self.geometry("400x300")
        self.resizable(False, False)
        self.title("Test Video")
        self.test_live_window = None
        self.test_recorded_window = None

        container_frame = ctk.CTkFrame(self)
        container_frame.pack(expand=True)

        app_frame = ctk.CTkFrame(container_frame, fg_color="transparent")
        app_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        set_input_btn = Button(
            app_frame,
            text="Test Live Video",
            command=self.test_live_video,
        )
        set_input_btn.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        set_output_btn = Button(
            app_frame,
            text="Test Recorded Video",
            command=self.test_recorded_video,
        )
        set_output_btn.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")
    
    def test_live_video(self):
        if self.test_live_window is None or not self.test_live_window.winfo_exists():
            self.test_live_window = test_video_detection(self.input_folder, isLive=True)
        else:
            self.test_live_window.focus()

    def test_recorded_video(self):
        if self.test_recorded_window is None or not self.test_recorded_window.winfo_exists():
            self.test_recorded_window = test_video_detection(self.input_folder)
        else:
            self.test_recorded_window.focus()


class TestImgWindow(ctk.CTkToplevel):
    def __init__(self, image_processor, object_detector, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("800x500")
        self.resizable(False, False)

        test_img = image_processor.load_image("test.png")
        boxes, confs, classes = object_detector.detect_objects(test_img)
        test_img, detected_classes = object_detector.draw_boxes(
            test_img, boxes, confs, classes
        )
        test_img = Image.fromarray(test_img)
        test_photo = ctk.CTkImage(test_img, size=(800, 500))

        label = ctk.CTkLabel(self, image=test_photo, text="", bg_color="gray28")
        label.image = test_photo  # Keep a reference to prevent garbage collection
        label.pack(pady=10)
        # self.focus_force()
        print("Total detected objects: ", len(detected_classes))
        print("Detected classes: ", detected_classes)


class LaneFrame(ctk.CTkFrame):
    def __init__(self, master, lane, image, row, col, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.grid(row=row, column=col, padx=10, pady=10)

        label = ctk.CTkLabel(
            self, text=f"Lane: {lane}", font=(None, 16), bg_color="gray28"
        )
        label.pack(expand=True, pady=(0, 2), fill="x")

        processed_img = ctk.CTkImage(image, size=(450, 300))
        label = ctk.CTkLabel(self, image=processed_img, text="")
        label.image = processed_img
        label.pack()


class DetectedResultsWindow(ctk.CTkToplevel):
    def __init__(self, output_folder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_folder = output_folder
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(pady=10, padx=10)

        for i in range(constants.NO_OF_SIGNALS):
            row = i // 2
            col = i % 2
            output_image_path = Image.open(
                os.path.join(self.output_folder, f"lane_{i+1}.png")
            )
            print(output_image_path)
            LaneFrame(main_frame, i + 1, output_image_path, row, col)
            # output_image.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)


class Button(ctk.CTkButton):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.configure(font=(None, 20), border_spacing=10, cursor="hand2")


class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x400")
        self.resizable(False, False)
        self.title("Main Window")
        self.input_folder = None
        self.output_folder = None
        self.test_img_window = None
        self.test_video_window = None
        self.traffic_manager_window = None
        self.output_window = None
        self.simulation_window = None
        self.weights_path = WEIGHTS_PATH
        self.selective_classes = SELECTIVE_CLASSES
        self.image_processor = None
        self.object_detector = None

        container_frame = ctk.CTkFrame(self)
        container_frame.pack(expand=True)

        app_frame = ctk.CTkFrame(container_frame, fg_color="transparent")
        app_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        set_input_btn = Button(
            app_frame,
            text="Set input folder",
            command=lambda: self.set_folder_location("input"),
        )
        set_input_btn.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        set_output_btn = Button(
            app_frame,
            text="Set output folder",
            command=lambda: self.set_folder_location("output"),
        )
        set_output_btn.grid(row=0, column=1, pady=10, padx=10, sticky="nsew")

        test_img = Button(
            app_frame, text="Test image", command=self.open_test_img_window
        )
        test_img.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")

        test_btn = Button(
            app_frame, text="Test video", command=self.open_test_video_window
        )
        test_btn.grid(row=1, column=1, pady=10, padx=10, sticky="nsew")

        traffic_manager_btn = Button(
            app_frame,
            text="Run Traffic Manager",
            command=self.open_traffic_manager_window,
        )
        traffic_manager_btn.grid(
            row=2, column=0, columnspan=2, pady=10, padx=10, sticky="we"
        )

        display_output_btn = Button(
            app_frame, text="Show output", command=self.open_output_window
        )
        display_output_btn.grid(row=3, column=0, pady=10, padx=10, sticky="nsew")

        simulator_btn = Button(
            app_frame, text="Simulate flow", command=self.open_simulation_window
        )
        simulator_btn.grid(row=3, column=1, pady=10, padx=10, sticky="nsew")

        self.mainloop()

    def set_folder_location(self, folder_type):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            messagebox.showwarning(
                "Empty", f"Please enter an {folder_type} folder location!"
            )
            return
        if not os.path.isdir(folder_path):
            messagebox.showwarning("Warning", "Please enter a valid folder location!")
            return

        if folder_type == "input":
            self.input_folder = folder_path
        else:
            self.output_folder = folder_path

        if not self.input_folder or not self.output_folder:
            return

        self.image_processor = ImageProcessing(self.input_folder, self.output_folder)
        self.object_detector = ObjectDetection(
            self.weights_path, self.selective_classes
        )

    def is_folder_set(self):
        if not self.input_folder or not self.output_folder:
            messagebox.showerror("Empty", "Provide input and output folder!")
            return False
        return True

    def open_test_img_window(self):
        if not self.is_folder_set():
            return
        if self.test_img_window is None or not self.test_img_window.winfo_exists():
            # create window if its None or destroyed
            self.test_img_window = TestImgWindow(
                self.image_processor, self.object_detector
            )
        else:
            self.test_img_window.focus()  # if window exists focus it

        self.test_img_window.focus()

    def open_test_video_window(self):
        if not self.is_folder_set():
            return
        if self.test_video_window is None or not self.test_video_window.winfo_exists():
            # self.test_video_window = test_video_detection(self.input_folder)
            self.test_video_window = TestVideoWindow(self.input_folder)
        else:
            self.test_video_window.focus()

    def open_traffic_manager_window(self):
        if not self.is_folder_set():
            return
        if (
            self.traffic_manager_window is None
            or not self.traffic_manager_window.winfo_exists()
        ):
            # create window if its None or destroyed
            self.traffic_manager_window = TrafficController(
                self.image_processor, self.object_detector
            )
        else:
            self.traffic_manager_window.focus()  # if window exists focus it

    def open_output_window(self):
        if not self.is_folder_set():
            return
        if self.output_window is None or not self.output_window.winfo_exists():
            self.output_window = DetectedResultsWindow(self.output_folder)
        else:
            self.output_window.focus()
        self.output_window.focus()

    def open_simulation_window(self):
        if self.simulation_window is None:
            # Create a new simulation window
            self.simulation_window = Thread(
                name="Start Simulation", target=start_simulation, args=()
            )
            self.simulation_window.start()


WEIGHTS_PATH = "src/yolo-weights/yolov8n.pt"
SELECTIVE_CLASSES = [2, 3, 5, 7]

if __name__ == "__main__":
    App()
