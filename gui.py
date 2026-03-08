
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import sys
import queue
from main import ObjectDetectionApp
import os

# Configuration
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ThreadSafeConsole:
    def __init__(self, queue):
        self.queue = queue
    
    def write(self, msg):
        self.queue.put(msg)
    
    def flush(self):
        pass

class DetectionGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Object Detection")
        self.geometry("850x600")
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Build UI
        self._create_sidebar()
        self._create_main_area()
        
        # Setup Logging Redirection
        self.log_queue = queue.Queue()
        self.status_queue = queue.Queue() # For thread-safe UI updates
        self.console_redirect = ThreadSafeConsole(self.log_queue)
        sys.stdout = self.console_redirect
        sys.stderr = self.console_redirect
        
        # Initial State
        self.check_log_queue()
        self.check_status_queue()

    def _create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Action Buttons in Sidebar
        self.start_btn = ctk.CTkButton(self.sidebar_frame, text="START DETECTION", command=self.start_thread, font=ctk.CTkFont(weight="bold"))
        self.start_btn.grid(row=2, column=0, padx=20, pady=150,)
        
        self.quit_btn = ctk.CTkButton(self.sidebar_frame, text="QUIT", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.on_close)
        self.quit_btn.grid(row=3, column=0, padx=20, pady=10)
        

    def _create_main_area(self):
        # Scrollable Frame for main content
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # --- Input Mode ---
        self.mode_label = ctk.CTkLabel(self.main_frame, text="Input Mode", font=ctk.CTkFont(size=14, weight="bold"))
        self.mode_label.pack(pady=(10, 5), anchor="w", padx=10)
        
        self.mode_view = ctk.CTkSegmentedButton(self.main_frame, values=["Video File", "Image File", "Webcam"], command=self.update_inputs)
        self.mode_view.set("Video File")
        self.mode_view.pack(pady=5, padx=10, fill="x")
        
        # --- Source Input ---
        self.source_label = ctk.CTkLabel(self.main_frame, text="Source Path / Index", font=ctk.CTkFont(size=14, weight="bold"))
        self.source_label.pack(pady=(20, 5), anchor="w", padx=10)
        
        self.source_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.source_frame.pack(fill="x", padx=10)
        
        self.source_entry = ctk.CTkEntry(self.source_frame, placeholder_text="Path to video or image...")
        self.source_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_btn = ctk.CTkButton(self.source_frame, text="Browse", width=100, command=self.browse_file)
        self.browse_btn.pack(side="right")
        
        # --- Profile Selection ---
        self.profile_label = ctk.CTkLabel(self.main_frame, text="Detection Profile", font=ctk.CTkFont(size=14, weight="bold"))
        self.profile_label.pack(pady=(20, 5), anchor="w", padx=10)
        
        self.profile_view = ctk.CTkSegmentedButton(self.main_frame, values=["General Objects", "Playing Cards", "PPE Detection"])
        self.profile_view.set("General Objects")
        self.profile_view.pack(pady=5, padx=10, fill="x")
        
        # --- Options ---
        self.options_label = ctk.CTkLabel(self.main_frame, text="Execution Options", font=ctk.CTkFont(size=14, weight="bold"))
        self.options_label.pack(pady=(20, 5), anchor="w", padx=10)
        
        self.options_frame = ctk.CTkFrame(self.main_frame)
        self.options_frame.pack(fill="x", padx=10, pady=5)
        
        self.save_output_chk = ctk.CTkCheckBox(self.options_frame, text="Save Output Image/Video")
        self.save_output_chk.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.export_data_chk = ctk.CTkCheckBox(self.options_frame, text="Export Data (CSV/JSON)")
        self.export_data_chk.grid(row=0, column=1, padx=20, pady=15, sticky="w")
        
        self.show_display_chk = ctk.CTkCheckBox(self.options_frame, text="Show Live Display")
        self.show_display_chk.select()
        self.show_display_chk.grid(row=0, column=2, padx=20, pady=15, sticky="w")
        
        # --- Console Log ---
        self.log_label = ctk.CTkLabel(self.main_frame, text="System Log", font=ctk.CTkFont(size=14, weight="bold"))
        self.log_label.pack(pady=(20, 5), anchor="w", padx=10)
        
        self.log_text = ctk.CTkTextbox(self.main_frame, height=200, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_text.pack(fill="x", padx=10, pady=5)
        self.log_text.configure(state="disabled")

    def update_inputs(self, mode):
        # Map nice names back to internal values
        if isinstance(mode, str):
             # When called by SegmentedButton, mode is the value string
             pass
        else:
             # When called manually, might need to get it
             mode = self.mode_view.get()
             
        mode_map = {"Video File": "video", "Image File": "image", "Webcam": "webcam"}
        internal_mode = mode_map.get(mode, "video")
        
        if internal_mode == "webcam":
            self.source_entry.delete(0, "end")
            self.source_entry.insert(0, "0")
            self.browse_btn.configure(state="disabled")
        else:
            current = self.source_entry.get()
            if current == "0":
                self.source_entry.delete(0, "end")
            self.browse_btn.configure(state="normal")
            
        return internal_mode

    def browse_file(self):
        mode = self.mode_view.get()
        if mode == "Video File":
            filetypes = [("Video files", "*.mp4;*.avi;*.mov;*.mkv"), ("All files", "*.*")]
        elif mode == "Image File":
            filetypes = [("Image files", "*.jpg;*.jpeg;*.png;*.bmp"), ("All files", "*.*")]
        else:
            return
            
        filename = filedialog.askopenfilename(title=f"Select {mode}", filetypes=filetypes)
        if filename:
            self.source_entry.delete(0, "end")
            self.source_entry.insert(0, filename)

    def check_log_queue(self):
        while not self.log_queue.empty():
            try:
                msg = self.log_queue.get_nowait()
                self.log_text.configure(state="normal")
                self.log_text.insert("end", msg)
                self.log_text.see("end")
                self.log_text.configure(state="disabled")
            except queue.Empty:
                break
        self.after(100, self.check_log_queue)

    def check_status_queue(self):
        while not self.status_queue.empty():
            try:
                msg = self.status_queue.get_nowait()
                if msg == "finished":
                    self.start_btn.configure(state="normal")
            except queue.Empty:
                break
        self.after(200, self.check_status_queue)

    def start_thread(self):
        # Validation
        source = self.source_entry.get()
        if not source:
            messagebox.showerror("Error", "Please provide an input source.")
            return
        
        mode_val = self.mode_view.get()
        mode_map = {"Video File": "video", "Image File": "image", "Webcam": "webcam"}
        internal_mode = mode_map.get(mode_val, "video")

        if internal_mode != "webcam" and not os.path.exists(source):
             messagebox.showerror("Error", f"File not found: {source}")
             return

        # UI Updates
        self.start_btn.configure(state="disabled")
        
        profile_val = getattr(self, "profile_view", None)
        profile = profile_val.get() if profile_val else "General Objects"

        # Start Thread
        t = threading.Thread(target=self.run_app, args=(internal_mode, source, profile))
        t.daemon = True
        t.start()

    def run_app(self, mode, source, profile="General Objects"):
        try:
            print(f"--- Starting Detection [Mode: {mode}, Profile: {profile}] ---")
            
            if profile == "Playing Cards":
                config_path = "config/cards.yaml"
            elif profile == "PPE Detection":
                config_path = "config/ppe.yaml"
            else:
                config_path = "config/config.yaml"
                
            # Create App Instance
            app = ObjectDetectionApp(config_path=config_path)
            
            # Check if source is int (webcam)
            if mode == 'webcam':
                try:
                    source = int(source)
                except ValueError:
                    pass

            app.run(
                source=source,
                mode=mode,
                save_output=self.save_output_chk.get(),
                export_data=self.export_data_chk.get(),
                show_display=self.show_display_chk.get()
            )
            print("--- Processing Complete ---")
            
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            self.status_queue.put("finished")

    def on_close(self):
        # Restore stdout/stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    try:
        app = DetectionGUI()
        app.mainloop()
    except Exception as e:
        print(f"Failed to start GUI: {e}")
