try:
    from sense_hat import SenseHat
    sense = SenseHat()
    sense.clear()
except OSError:
    sense = None
    print("[lights] Warning: No Sense HAT detected")

_display_mode = "temperature"

def init_joystick():
    if sense is not None:
        sense.stick.direction_any = _joystick_event

def _joystick_event(event):
    global _display_mode
    if event.action == "pressed":
        if event.direction == "left":
            _display_mode = "temperature"
        elif event.direction == "right":
            _display_mode = "humidity"

    try:
        from src import shared_state
        if shared_state.latest_data:
            update_display(shared_state.latest_data)
    except Exception as e:
        print(f"[joystick] Immediate update failed: {e}")

_digits = {
        '0': [
        [1,1,1],
        [1,0,1],
        [1,0,1],
        [1,0,1],
        [1,1,1],
    ],
    '1': [
        [0,1,0],
        [1,1,0],
        [0,1,0],
        [0,1,0],
        [1,1,1],
    ],
    '2': [
        [1,1,1],
        [0,0,1],
        [1,1,1],
        [1,0,0],
        [1,1,1],
    ],
    '3': [
        [1,1,1],
        [0,0,1],
        [1,1,1],
        [0,0,1],
        [1,1,1],
    ],
    '4': [
        [1,0,1],
        [1,0,1],
        [1,1,1],
        [0,0,1],
        [0,0,1],
    ],
    '5': [
        [1,1,1],
        [1,0,0],
        [1,1,1],
        [0,0,1],
        [1,1,1],
    ],
    '6': [
        [1,1,1],
        [1,0,0],
        [1,1,1],
        [1,0,1],
        [1,1,1],
    ],
    '7': [
        [1,1,1],
        [0,0,1],
        [0,1,0],
        [1,0,0],
        [1,0,0],
    ],
    '8': [
        [1,1,1],
        [1,0,1],
        [1,1,1],
        [1,0,1],
        [1,1,1],
    ],
    '9': [
        [1,1,1],
        [1,0,1],
        [1,1,1],
        [0,0,1],
        [1,1,1],
    ]
}

def draw_digits(x, y, digit, colour):
    pattern = _digits.get(digit)
    if not pattern:
        return
    for row in range(5):
        for col in range(3):
            if pattern[row][col]:
                sense.set_pixel(x+col, y+row, colour)
            else:
                sense.set_pixel(x+col, y+row, [0,0,0])


def update_display(data):
    if sense is None:
        if _display_mode in data and data[_display_mode] is not None:
            print(f"[Display: {_display_mode} {data[_display_mode]:.1f}]")
        else:
            print("[Display] ERR")
        return

    sense.clear()

    if _display_mode == "temperature":
        value = data.get("temperature")
        colour = [0, 0, 255]
    else:
        value = data.get("humidity")
        colour = [0, 255, 0]

    if value is None:
        sense.show_letter('E', text_colour = [255, 0, 0])
        return

    num = int(round(value))
    text = f"{num:02d}"[-2:]

    draw_digits(0, 1, text[0], colour)
    draw_digits(4, 1, text[1], colour)

    if _display_mode == "temperature":
        sense.set_pixel(7, 0, [0, 0, 255])
    else:
        sense.set_pixel(7, 0, [0, 255, 0])

def clear():
    if sense is not None:
        sense.clear()
