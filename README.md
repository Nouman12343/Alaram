# Alarm
````markdown
Python Alarm System – Setup Instructions

This is a simple alarm system project in Python. It plays a sound when the alarm time is reached using the `playsound` module.

Installation Steps

1. First, upgrade `setuptools` and `wheel`:

```bash
pip install --upgrade setuptools wheel
````

2. Then install `playsound`:

```bash
pip install playsound
```

3. If you're using Python 3.10 or newer**, it's better to use this version:

```bash
pip install playsound==1.2.2
```

Alarm Sound

Make sure the sound file named `mixkit-alert-alarm-1005.wav` is in the same folder as your Python script.

Running the Alarm

Run your Python script (e.g., `alarm.py`) and enter the time in `HH:MM` format when prompted.

That’s it! The alarm will play the sound when the time matches.

