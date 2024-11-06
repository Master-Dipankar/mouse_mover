import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import random
import threading
import time
from datetime import datetime, timedelta
import keyboard  # You'll need to install this: pip install keyboard

class MouseMoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Mover")
        self.root.geometry("400x600")  # Made window taller for hotkey settings
        
        # Enable window controls
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.state('normal')
        
        # Create minimize/close buttons
        minimize_button = ttk.Button(root, text="−", width=3, command=self.minimize_window)
        minimize_button.place(x=340, y=5)
        
        close_button = ttk.Button(root, text="×", width=3, command=self.on_closing)
        close_button.place(x=370, y=5)
        
        # Initialize variables
        self.is_running = False
        self.current_thread = None
        self.start_time = None
        self.recording_hotkey = False
        self.start_hotkey = "ctrl+shift+1"
        self.stop_hotkey = "ctrl+shift+2"
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status indicator
        self.status_var = tk.StringVar(value="Status: Stopped")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Timer display
        self.timer_var = tk.StringVar(value="Running time: 00:00:00")
        self.timer_label = ttk.Label(main_frame, textvariable=self.timer_var)
        self.timer_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Movement Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Movement interval
        ttk.Label(settings_frame, text="Movement Interval (seconds):").grid(row=0, column=0, pady=5)
        self.interval_min = ttk.Entry(settings_frame, width=10)
        self.interval_min.insert(0, "15")
        self.interval_min.grid(row=0, column=1, padx=5)
        ttk.Label(settings_frame, text="to").grid(row=0, column=2)
        self.interval_max = ttk.Entry(settings_frame, width=10)
        self.interval_max.insert(0, "30")
        self.interval_max.grid(row=0, column=3, padx=5)
        
        # Movement range
        ttk.Label(settings_frame, text="Movement Range (pixels):").grid(row=1, column=0, pady=5)
        self.range_entry = ttk.Entry(settings_frame, width=10)
        self.range_entry.insert(0, "10")
        self.range_entry.grid(row=1, column=1, padx=5)
        
        # Movement speed
        ttk.Label(settings_frame, text="Movement Speed (seconds):").grid(row=2, column=0, pady=5)
        self.speed_entry = ttk.Entry(settings_frame, width=10)
        self.speed_entry.insert(0, "0.5")
        self.speed_entry.grid(row=2, column=1, padx=5)
        
        # Hotkey settings frame
        hotkey_frame = ttk.LabelFrame(main_frame, text="Hotkey Settings", padding="10")
        hotkey_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Start hotkey
        ttk.Label(hotkey_frame, text="Start Hotkey:").grid(row=0, column=0, pady=5)
        self.start_hotkey_var = tk.StringVar(value=self.start_hotkey)
        self.start_hotkey_label = ttk.Label(hotkey_frame, textvariable=self.start_hotkey_var)
        self.start_hotkey_label.grid(row=0, column=1, padx=5)
        self.start_hotkey_button = ttk.Button(hotkey_frame, text="Set Hotkey", 
                                            command=lambda: self.record_hotkey('start'))
        self.start_hotkey_button.grid(row=0, column=2, padx=5)
        
        # Stop hotkey
        ttk.Label(hotkey_frame, text="Stop Hotkey:").grid(row=1, column=0, pady=5)
        self.stop_hotkey_var = tk.StringVar(value=self.stop_hotkey)
        self.stop_hotkey_label = ttk.Label(hotkey_frame, textvariable=self.stop_hotkey_var)
        self.stop_hotkey_label.grid(row=1, column=1, padx=5)
        self.stop_hotkey_button = ttk.Button(hotkey_frame, text="Set Hotkey", 
                                           command=lambda: self.record_hotkey('stop'))
        self.stop_hotkey_button.grid(row=1, column=2, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_movement)
        self.start_button.grid(row=0, column=0, padx=10)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_movement, 
                                    state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=10)
        
        # Info text
        info_text = "Instructions:\n" + \
                   "1. Set your preferred movement settings\n" + \
                   "2. Configure hotkeys (optional)\n" + \
                   "3. Click Start or use hotkey to begin\n" + \
                   "4. Click Stop or use hotkey to end\n" + \
                   "5. Move mouse to upper-left corner to force stop\n" + \
                   "6. Minimize window to keep running in background"
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT, wraplength=380)
        info_label.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        
        # Configure grid weights
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)
        
        # Set up hotkey listeners
        self.setup_hotkeys()

    def setup_hotkeys(self):
        keyboard.unhook_all()  # Clear any existing hotkeys
        keyboard.add_hotkey(self.start_hotkey, self.start_movement)
        keyboard.add_hotkey(self.stop_hotkey, self.stop_movement)

    def record_hotkey(self, hotkey_type):
        if self.recording_hotkey:
            return
        
        self.recording_hotkey = True
        button = self.start_hotkey_button if hotkey_type == 'start' else self.stop_hotkey_button
        label_var = self.start_hotkey_var if hotkey_type == 'start' else self.stop_hotkey_var
        
        # Change button text to indicate recording
        button.configure(text="Press Keys...")
        
        def on_hotkey(e):
            if not self.recording_hotkey:
                return
            
            # Convert the event to hotkey string
            hotkey = []
            if e.modifiers:
                hotkey.extend(e.modifiers)
            if e.name not in ['shift', 'ctrl', 'alt']:
                hotkey.append(e.name)
            
            hotkey_str = '+'.join(hotkey)
            
            # Update the hotkey
            if hotkey_type == 'start':
                self.start_hotkey = hotkey_str
            else:
                self.stop_hotkey = hotkey_str
            
            label_var.set(hotkey_str)
            button.configure(text="Set Hotkey")
            self.recording_hotkey = False
            
            # Update hotkey listeners
            self.setup_hotkeys()
            
            # Remove this temporary hook
            keyboard.unhook(hook)
        
        # Add temporary hook for recording
        hook = keyboard.on_press(on_hotkey)

    def minimize_window(self):
        self.root.state('iconic')
        
    def on_closing(self):
        if self.is_running:
            self.stop_movement()
        keyboard.unhook_all()  # Clean up keyboard hooks
        self.root.destroy()

    def update_timer(self):
        if self.is_running and self.start_time:
            elapsed_time = datetime.now() - self.start_time
            self.timer_var.set(f"Running time: {str(elapsed_time).split('.')[0]}")
            self.root.after(1000, self.update_timer)

    def move_mouse_loop(self):
        self.start_time = datetime.now()
        screen_width, screen_height = pyautogui.size()
        
        while self.is_running:
            try:
                current_x, current_y = pyautogui.position()
                move_range = int(self.range_entry.get())
                move_x = random.randint(-move_range, move_range)
                move_y = random.randint(-move_range, move_range)
                new_x = max(0, min(current_x + move_x, screen_width))
                new_y = max(0, min(current_y + move_y, screen_height))
                pyautogui.moveTo(new_x, new_y, duration=float(self.speed_entry.get()))
                interval_min = int(self.interval_min.get())
                interval_max = int(self.interval_max.get())
                wait_time = random.randint(interval_min, interval_max)
                time.sleep(wait_time)
            except Exception as e:
                print(f"Error: {e}")
                self.stop_movement()
                break

    def start_movement(self):
        if not self.is_running:
            self.is_running = True
            self.status_var.set("Status: Running")
            self.start_button.configure(state=tk.DISABLED)
            self.stop_button.configure(state=tk.NORMAL)
            
            self.current_thread = threading.Thread(target=self.move_mouse_loop)
            self.current_thread.daemon = True
            self.current_thread.start()
            
            self.update_timer()

    def stop_movement(self):
        if self.is_running:
            self.is_running = False
            self.status_var.set("Status: Stopped")
            self.start_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.DISABLED)
            if self.current_thread:
                self.current_thread.join(timeout=1.0)

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseMoverApp(root)
    root.mainloop()