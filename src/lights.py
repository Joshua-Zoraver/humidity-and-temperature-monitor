try:
    from sense_hat import SenseHat
    sense = SenseHat()
    sense.clear()
except ImportError:
    sense = None
    print("[lights] Warning: No Sense HAT detected")

_display_mode = "temperature"

def init_joystick():
    if sense is not None:
        sense.stick.direction_any = _joystick_event

def _joystick_event(event):
    global _display_mode
    for event in sense.stick.get_events():
        if event.action == "pressed":
            if event.direction == "left":
                _display_mode = "temperature"
            elif event.direction == "right":
                _display_mode = "humidity"

def update_display(data):
    if sense is None:
        if _display_mode in data and data[_display_mode] is not None:
            print(f"[Display: {_display_mode} {data[_display_mode]:.1f}")
        else:
            print("[Display] ERR")
        return

    sense.clear()
    if _display_mode == "temperature" and data.get("temperature") is not None:
        text = f"{data['temperature']:.1f}C"
    elif _display_mode == "humidity" and data.get("humidity") is not None:
        text = f"{data['temperature']:.1f}C"
    else:
        text = "ERR"

    sense.show_message(text, scroll_speed = 0.05, text_colour=[100,200,255])
