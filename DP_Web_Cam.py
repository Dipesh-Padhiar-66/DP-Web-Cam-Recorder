# ===========================================#
# This WebCam recording app was developed    #
# by Dipesh Padhiar with the help of ChatGPT #
# April 2026                                 #
# Built using Python script version 3.14.3   #
# FFmpeg version N-123829 (8.1 Hoare)        #
# OpenCV-Python version 4.13.0.92            #
# Released as is for educational purposes    #
# ===========================================#

import cv2
import subprocess
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import time
from datetime import datetime
import sys
import os
import ctypes


# ===== CHECK FOR DOUBLE INSTANCE =====
def is_already_running():
    mutex_name = "WebcamRecorderAppMutex"

    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW(None, False, mutex_name)

    last_error = kernel32.GetLastError()

    ERROR_ALREADY_EXISTS = 183

    return last_error == ERROR_ALREADY_EXISTS


# ===== FFMPEG PATH =====
def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "ffmpeg.exe")
    else:
        return "ffmpeg"


class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DP Webcam Recorder")
        self.root.geometry("720x780")
        self.root.resizable(False, False)

        # ===== WINDOWS NATIVE STYLE =====
        self.style = ttk.Style()

        available_themes = self.style.theme_names()

        if "vista" in available_themes:
            self.style.theme_use("vista")
        elif "xpnative" in available_themes:
            self.style.theme_use("xpnative")
        else:
            self.style.theme_use("clam")

        # ===== VARIABLES =====
        self.blink_state = False
        self.is_recording = False
        self.record_start_time = None
        self.segment_duration = 30 * 60
        self.output_dir = None

        self.quality_var = tk.StringVar(value="Medium")
        self.mirror_var = tk.BooleanVar(value=True)

        # ===== CAMERA DETECTION =====
        self.available_cameras = self.get_available_cameras()

        if not self.available_cameras:
            messagebox.showerror(
                "Error",
                "No cameras detected."
            )
            root.destroy()
            return

        self.camera_var = tk.StringVar(
            value=self.available_cameras[0]["name"]
        )

        self.current_camera_index = self.available_cameras[0]["index"]

        # ===== CAMERA =====
        self.cap = cv2.VideoCapture(
            self.current_camera_index,
            cv2.CAP_DSHOW
        )

        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot access webcam")
            root.destroy()
            return

        # ===== MENU =====
        menubar = tk.Menu(self.root)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Info", command=self.show_about)

        menubar.add_cascade(label="About", menu=help_menu)

        self.root.config(menu=menubar)

        # ===== MAIN CONTAINER =====
        main_frame = ttk.Frame(root, padding=12)
        main_frame.pack(fill="both", expand=True)

        # ===== VIDEO FRAME =====
        video_frame = ttk.LabelFrame(
            main_frame,
            text="Live Preview",
            padding=10
        )
        video_frame.pack(fill="both", expand=False)

        self.video_label = tk.Label(
            video_frame,
            bg="black",
            width=640,
            height=480
        )
        self.video_label.pack()

        # ===== CONTROL FRAME =====
        controls_frame = ttk.LabelFrame(
            main_frame,
            text="Controls",
            padding=10
        )
        controls_frame.pack(fill="x", pady=10)

        # ===== BUTTONS =====
        self.start_btn = ttk.Button(
            controls_frame,
            text="Start Recording",
            command=self.start_recording
        )
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)

        self.stop_btn = ttk.Button(
            controls_frame,
            text="Stop Recording",
            command=self.stop_recording,
            state="disabled"
        )
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5)

        # ===== QUALITY =====
        ttk.Label(
            controls_frame,
            text="Quality:"
        ).grid(row=0, column=2, padx=(20, 5))

        self.quality_dropdown = ttk.Combobox(
            controls_frame,
            textvariable=self.quality_var,
            values=["Low", "Medium", "High"],
            state="readonly",
            width=12
        )

        self.quality_dropdown.grid(row=0, column=3, padx=5)
        self.quality_dropdown.current(1)

        # ===== CAMERA DROPDOWN =====
        ttk.Label(
            controls_frame,
            text="Camera:"
        ).grid(row=1, column=0, padx=5, pady=(10, 5))

        camera_names = [
            cam["name"]
            for cam in self.available_cameras
        ]

        self.camera_dropdown = ttk.Combobox(
            controls_frame,
            textvariable=self.camera_var,
            values=camera_names,
            state="readonly",
            width=45
        )

        self.camera_dropdown.grid(
            row=1,
            column=1,
            columnspan=3,
            sticky="w",
            pady=(10, 5)
        )

        self.camera_dropdown.current(0)

        self.camera_dropdown.bind(
            "<<ComboboxSelected>>",
            self.change_camera
        )

        # ===== CAMERA MIRROR =====
        self.mirror_checkbox = ttk.Checkbutton(
            controls_frame,
            text="Mirror Video",
            variable=self.mirror_var
        )

        self.mirror_checkbox.grid(
            row=1,
            column=10,
            padx=10,
            columnspan=10,
            sticky="w",
            pady=(10, 5)
        )

        # ===== STATUS FRAME =====
        status_frame = ttk.LabelFrame(
            main_frame,
            text="Status",
            padding=10
        )
        status_frame.pack(fill="x")

        camera_fps = self.cap.get(cv2.CAP_PROP_FPS)

        self.status = ttk.Label(
            status_frame,
            text=f"Ready | Camera FPS: {camera_fps:.1f}"
        )
        self.status.pack(anchor="w", pady=2)

        # ===== SAVE PATH ROW =====
        save_path_frame = ttk.Frame(status_frame)
        save_path_frame.pack(fill="x", pady=2)

        self.save_path_label = ttk.Label(
            save_path_frame,
            text="Save Path: (not set)"
        )
        self.save_path_label.pack(side="left", anchor="w")

        self.open_folder_btn = ttk.Button(
            save_path_frame,
            text="Open Folder",
            command=self.open_save_folder
        )
        self.open_folder_btn.pack(side="right")

        # ===== RECORDING INDICATOR =====
        self.recording_indicator = ttk.Progressbar(
            status_frame,
            mode="indeterminate",
            length=200
        )

        # ===== START PREVIEW =====
        self.update_preview()

    # ===== GET CAMERA NAMES =====
    def get_available_cameras(self):
        cameras = []

        for i in range(10):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)

            if cap.isOpened():
                name = f"Camera {i}"

                try:
                    import pygrabber.dshow_graph

                    graph = pygrabber.dshow_graph.FilterGraph()
                    devices = graph.get_input_devices()

                    if i < len(devices):
                        name = devices[i]

                except Exception as e:
                    print(f"Camera name detection failed: {e}")

                cameras.append({
                    "index": i,
                    "name": name
                })

                cap.release()

        return cameras

    # ===== CHANGE CAMERA =====
    def change_camera(self, event=None):
        selected_name = self.camera_var.get()

        selected_camera = None

        for cam in self.available_cameras:
            if cam["name"] == selected_name:
                selected_camera = cam
                break

        if selected_camera is None:
            return

        was_recording = self.is_recording

        if was_recording:
            self.stop_recording()

        if self.cap:
            self.cap.release()

        self.current_camera_index = selected_camera["index"]

        self.cap = cv2.VideoCapture(
            self.current_camera_index,
            cv2.CAP_DSHOW
        )

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.status.config(
            text=f"Ready | Camera FPS: {fps:.1f}"
        )

        if not self.cap.isOpened():
            messagebox.showerror(
                "Camera Error",
                "Failed to open selected camera."
            )

    # ===== QUALITY TO CRF =====
    def get_crf(self):
        quality = self.quality_var.get()

        if quality == "High":
            return "18"
        elif quality == "Medium":
            return "23"
        else:
            return "28"

    # ===== VIDEO PREVIEW =====
    def update_preview(self):
        ret, frame = self.cap.read()

        if ret:
            if self.mirror_var.get():
                frame = cv2.flip(frame, 1)

            # ===== TIMESTAMP =====
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            font = cv2.FONT_HERSHEY_SIMPLEX
            scale = 0.7
            thickness = 2

            (text_width, text_height), _ = cv2.getTextSize(
                timestamp,
                font,
                scale,
                thickness
            )

            x = 10
            y = text_height + 10

            cv2.rectangle(
                frame,
                (x - 5, y - text_height - 5),
                (x + text_width + 5, y + 5),
                (0, 0, 0),
                -1
            )

            cv2.putText(
                frame,
                timestamp,
                (x, y),
                font,
                scale,
                (255, 255, 255),
                thickness,
                cv2.LINE_AA
            )

            # ===== RECORDING =====
            if (
                self.is_recording and
                hasattr(self, "ffmpeg_process") and
                self.ffmpeg_process
            ):
                elapsed = time.time() - self.record_start_time

                if elapsed >= self.segment_duration:
                    self.start_new_file()

                if self.ffmpeg_process.poll() is not None:
                    self.stop_recording()

                    messagebox.showerror(
                        "Recording Error",
                        "FFmpeg terminated unexpectedly."
                    )

                    return

                try:
                    self.ffmpeg_process.stdin.write(frame.tobytes())
                except Exception as e:
                    print("FFmpeg write error:", e)

            # ===== BLINKING REC =====
            if self.is_recording:
                current_time = time.time()

                if int(current_time * 2) % 2 == 0:

                    rec_text = "REC"

                    font = cv2.FONT_HERSHEY_SIMPLEX
                    scale = 1
                    thickness = 3

                    (text_width, text_height), _ = cv2.getTextSize(
                        rec_text,
                        font,
                        scale,
                        thickness
                    )

                    padding = 15

                    x = frame.shape[1] - text_width - padding
                    y = text_height + padding

                    cv2.circle(
                        frame,
                        (x - 25, y - 10),
                        8,
                        (0, 0, 255),
                        -1
                    )

                    cv2.putText(
                        frame,
                        rec_text,
                        (x, y),
                        font,
                        scale,
                        (0, 0, 255),
                        thickness,
                        cv2.LINE_AA
                    )

            # ===== DISPLAY =====
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(rgb)
            img = img.resize((640, 480))

            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.root.after(10, self.update_preview)

    # ===== START RECORDING =====
    def start_recording(self):
        base_dir = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "WebcamRecorder"
        )

        date_folder = datetime.now().strftime("%Y-%m-%d")

        self.output_dir = os.path.join(base_dir, date_folder)

        os.makedirs(self.output_dir, exist_ok=True)

        display_path = self.output_dir

        if len(display_path) > 55:
            display_path = "..." + display_path[-52:]

        self.save_path_label.config(
            text=f"Save Path: {display_path}"
        )

        if not self.cap.isOpened():
            messagebox.showerror("Error", "Camera not available")
            return

        self.is_recording = True

        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        self.start_new_file()

        self.status.config(
            text=f"Recording ({self.quality_var.get()} Quality)"
        )

        self.recording_indicator.pack(
            anchor="w",
            pady=(8, 0)
        )

        self.recording_indicator.start(10)

    # ===== START NEW FILE =====
    def start_new_file(self):
        if hasattr(self, "ffmpeg_process") and self.ffmpeg_process:
            self.ffmpeg_process.stdin.close()
            self.ffmpeg_process.wait()

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        quality = self.quality_var.get()

        if quality == "High":
            quality_label = "Hi-Q"
        elif quality == "Medium":
            quality_label = "Med-Q"
        else:
            quality_label = "Lo-Q"

        filename = os.path.join(
            self.output_dir,
            f"recording_{timestamp}_{quality_label}.mp4"
        )

        width = int(self.cap.get(3))
        height = int(self.cap.get(4))

        command = [
            get_ffmpeg_path(),
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-pix_fmt", "bgr24",
            "-s", f"{width}x{height}",
            "-r", "30",
            "-i", "-",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", self.get_crf(),
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            filename
        ]

        try:
            self.ffmpeg_process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"FFmpeg failed:\n\n{e}"
            )

            self.is_recording = False
            return

        self.record_start_time = time.time()

        print(f"Started new file: {filename}")

    # ===== STOP RECORDING =====
    def stop_recording(self):
        self.is_recording = False

        if hasattr(self, "ffmpeg_process") and self.ffmpeg_process:
            try:
                self.ffmpeg_process.stdin.close()
                self.ffmpeg_process.wait()

            except Exception as e:
                print("FFmpeg close error:", e)

            self.ffmpeg_process = None

        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

        self.status.config(text="Recording Saved")

        self.recording_indicator.stop()
        self.recording_indicator.pack_forget()

    # ===== CLOSE =====
    def on_close(self):
        self.is_recording = False

        if hasattr(self, "ffmpeg_process") and self.ffmpeg_process:
            try:
                self.ffmpeg_process.stdin.close()
                self.ffmpeg_process.wait()
            except Exception as e:
                print("Close error:", e)

        self.cap.release()
        self.root.destroy()

    # ===== OPEN SAVE FOLDER =====
    def open_save_folder(self):
        if self.output_dir and os.path.exists(self.output_dir):
            os.startfile(self.output_dir)
        else:
            messagebox.showwarning(
                "Folder Not Available",
                "No recording folder exists yet."
            )

    # ===== ABOUT =====
    def show_about(self):
        messagebox.showinfo(
            "About Webcam Recorder",
            "Webcam Recorder version 1.1\n\n"
            "Features:\n"
            "- Multi-camera support\n"
            "- Live webcam preview\n"
            "- H.264 recording\n"
            "- Automatic 30 minute file splitting\n"
            "- Timestamp overlay\n"
            "- Quality selection\n\n"
            "Developed by D. Padhiar\n"
            "with the help of CoPilot\n\n"
            "Built with Python, OpenCV, and FFmpeg\n"
            "Using GuiPy IDE"
        )


# ===== MAIN =====
if is_already_running():
    temp_root = tk.Tk()
    temp_root.withdraw()

    messagebox.showerror(
        "Already Running",
        "The application is already running."
    )

    temp_root.destroy()

else:
    root = tk.Tk()

    app = WebcamApp(root)

    root.protocol("WM_DELETE_WINDOW", app.on_close)

    root.mainloop()
