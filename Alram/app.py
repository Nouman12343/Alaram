import tkinter as tk
from time import strftime
from datetime import datetime, timedelta
from threading import Thread
import os # Import os module to check for file existence

# Attempt to import playsound. If it fails, provide a dummy function
try:
    from playsound import playsound
except ImportError:
    print("Warning: 'playsound' module not found. Alarm sound will not play.")
    print("Please install it using: pip install playsound")
    def playsound(sound, block=True):
        print(f"Simulating playing sound: {sound}")


# Global variables
alarm_time = None
alarm_triggered = False
snooze_minutes = 5
alarm_thread = None # To keep track of the alarm playing thread for stopping

# --- UI Message Box for alerts (replaces alert() and confirm()) ---
def show_message_box(title, message):
    """Creates a simple message box for user feedback."""
    msg_box = tk.Toplevel(root)
    msg_box.title(title)
    msg_box.geometry("300x100")
    msg_box.transient(root) # Make it appear on top of the main window
    msg_box.grab_set() # Disable interaction with the main window

    tk.Label(msg_box, text=message, wraplength=280).pack(pady=10)
    tk.Button(msg_box, text="OK", command=msg_box.destroy).pack(pady=5)

    root.wait_window(msg_box) # Wait for the message box to close

# --- Functions ---
def update_time():
    """Updates the digital clock display every second and checks for alarm."""
    current_time = strftime("%H:%M:%S %p\n%D")
    label.config(text=current_time)
    check_alarm()
    label.after(1000, update_time)

def set_alarm():
    """Sets the alarm time based on user input."""
    global alarm_time, alarm_triggered
    alarm_time_str = alarm_entry.get()
    
    # Input validation: Check for placeholder text
    if alarm_time_str == "HH:MM:SS":
        show_message_box("Input Error", "Please enter a valid alarm time (HH:MM:SS).")
        return

    try:
        # Parse the input string to a datetime object
        # We only care about hour, minute, second from the input
        # The date part will be inferred from current date when comparing
        parsed_time = datetime.strptime(alarm_time_str, "%H:%M:%S").time()
        
        # Combine with today's date for comparison
        today = datetime.now().date()
        alarm_datetime_today = datetime.combine(today, parsed_time)

        # If the alarm time is in the past for today, set it for tomorrow
        if alarm_datetime_today <= datetime.now():
            alarm_time = alarm_datetime_today + timedelta(days=1)
            status_label.config(text=f"Alarm set for tomorrow at {alarm_time.strftime('%H:%M:%S')}")
        else:
            alarm_time = alarm_datetime_today
            status_label.config(text=f"Alarm set for today at {alarm_time.strftime('%H:%M:%S')}")

        alarm_triggered = False
        snooze_button.pack_forget() # Ensure snooze button is hidden when a new alarm is set
        stop_button.pack_forget() # Ensure stop button is hidden

        print(f"Alarm successfully set for: {alarm_time}")

    except ValueError:
        show_message_box("Input Error", "Invalid time format! Please use HH:MM:SS (e.g., 14:30:00).")
        status_label.config(text="Invalid format! Use HH:MM:SS")
    except Exception as e:
        show_message_box("Error", f"An unexpected error occurred: {e}")
        status_label.config(text=f"Error setting alarm: {e}")


def check_alarm():
    """Checks if the current time matches the set alarm time."""
    global alarm_time, alarm_triggered, alarm_thread
    if alarm_time:
        now = datetime.now()
        # Compare only hour and minute for robustness, and check if current time is past the alarm time
        # This handles cases where the exact second might be missed
        if not alarm_triggered and now.hour == alarm_time.hour and now.minute == alarm_time.minute:
            if now >= alarm_time: # Trigger if current time is at or past the alarm time
                alarm_triggered = True
                status_label.config(text="ALARM! ALARM! ALARM!")
                print("Alarm triggered!")
                
                # Start playing alarm in a new thread
                alarm_thread = Thread(target=play_alarm_sound)
                alarm_thread.start()
                
                snooze_button.pack()
                stop_button.pack()
                # Reset alarm_time to None so it doesn't keep triggering until snoozed or reset
                # Or, if you want it to ring again tomorrow, you'd re-calculate alarm_time + timedelta(days=1) here
                # For simplicity, we'll clear it for now.
                # If you want it to re-arm for the next day automatically, uncomment the line below
                # alarm_time = alarm_time + timedelta(days=1)
                # print(f"Alarm re-armed for tomorrow: {alarm_time}")
                
        # If alarm has passed and hasn't been snoozed/reset, clear status
        elif alarm_triggered and now.hour == alarm_time.hour and now.minute > alarm_time.minute:
            # This condition helps clear the ALARM message if it wasn't snoozed or stopped
            # and the minute has passed.
            if alarm_time is not None: # Only clear if an alarm was actually set
                 status_label.config(text="")
                 snooze_button.pack_forget()
                 stop_button.pack_forget()
                 alarm_time = None # Clear the alarm so it doesn't keep checking
                 alarm_triggered = False


def play_alarm_sound():
    """Plays the alarm sound."""
    alarm_file = "mixkit-alert-alarm-1005.wav" # Ensure this file is in the same directory as your script
    if not os.path.exists(alarm_file):
        show_message_box("Error", f"Alarm sound file '{alarm_file}' not found. Please ensure it's in the same directory.")
        print(f"Error: Alarm sound file '{alarm_file}' not found.")
        return

    try:
        print(f"Playing alarm sound: {alarm_file}...")
        playsound(alarm_file)
        print("Alarm sound finished.")
    except Exception as e:
        show_message_box("Audio Error", f"Could not play alarm sound: {e}\nEnsure 'playsound' is installed and the file is valid.")
        print(f"Error playing alarm sound: {e}")
        status_label.config(text=f"Audio Error: {e}")

def stop_alarm():
    """Stops the currently playing alarm sound."""
    global alarm_triggered, alarm_time, alarm_thread
    # playsound doesn't have a direct stop method once it starts playing in blocking mode.
    # The best way to "stop" it is to let the current sound finish or kill the thread.
    # Killing threads is generally bad practice.
    # For playsound, often the workaround is to play a very short silent sound,
    # but that's not reliable.
    # A more robust solution would involve a different audio library (e.g., pygame, simpleaudio).
    
    # For now, we'll just hide the buttons and reset the state.
    # The current playsound call will finish its current iteration.
    show_message_box("Alarm Stopped", "Alarm will finish playing its current sound. Set a new alarm or snooze.")
    snooze_button.pack_forget()
    stop_button.pack_forget()
    alarm_triggered = False
    alarm_time = None # Clear the alarm so it doesn't re-trigger
    status_label.config(text="Alarm stopped. Set a new alarm.")
    print("Alarm state reset.")


def snooze():
    """Snoozes the alarm for a specified number of minutes."""
    global alarm_time, alarm_triggered
    snooze_button.pack_forget()
    stop_button.pack_forget()
    
    # Set alarm for snooze_minutes from now
    alarm_time = datetime.now() + timedelta(minutes=snooze_minutes)
    alarm_triggered = False # Reset triggered state
    status_label.config(text=f"Snoozed for {snooze_minutes} minutes. Next alarm at {alarm_time.strftime('%H:%M:%S')}")
    print(f"Alarm snoozed. Next alarm at: {alarm_time}")

# --- Main UI Setup ---
root = tk.Tk()
root.title("Digital Clock with Alarm")
root.geometry("400x350") # Set a fixed size for better layout control
root.resizable(False, False) # Prevent resizing

# Clock display
label = tk.Label(root, font=('calibri', 40, 'bold'), background='#282c34', foreground='#61dafb', padx=20, pady=20)
label.pack(anchor='center', fill='both', expand=True, pady=(20, 10))

# Alarm input
alarm_entry = tk.Entry(root, font=('calibri', 18), justify='center', width=10, bd=2, relief='groove')
alarm_entry.pack(pady=5)
alarm_entry.insert(0, "HH:MM:SS")
# Clear placeholder on focus
alarm_entry.bind("<FocusIn>", lambda event: alarm_entry.delete(0, tk.END) if alarm_entry.get() == "HH:MM:SS" else None)
alarm_entry.bind("<FocusOut>", lambda event: alarm_entry.insert(0, "HH:MM:SS") if not alarm_entry.get() else None)


# Buttons frame for better layout
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

set_button = tk.Button(button_frame, text="Set Alarm", command=set_alarm, font=('calibri', 14), bg='#4CAF50', fg='white', relief='raised', bd=3)
set_button.pack(side=tk.LEFT, padx=5)

snooze_button = tk.Button(button_frame, text="Snooze", font=('calibri', 14), command=snooze, bg='#FFC107', fg='black', relief='raised', bd=3)
snooze_button.pack(side=tk.LEFT, padx=5)
snooze_button.pack_forget() # Hide snooze button initially

stop_button = tk.Button(button_frame, text="Stop Alarm", font=('calibri', 14), command=stop_alarm, bg='#F44336', fg='white', relief='raised', bd=3)
stop_button.pack(side=tk.LEFT, padx=5)
stop_button.pack_forget() # Hide stop button initially

# Status label
status_label = tk.Label(root, font=('calibri', 12), fg='blue', wraplength=350)
status_label.pack(pady=5)

# Start clock
update_time()
root.mainloop()
