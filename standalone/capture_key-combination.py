from pynput import keyboard

COMBINATIONS = [
    #{keyboard.Key.shift_l, keyboard.Key.ctrl_l, keyboard.Key.cmd}
    {keyboard.Key.shift_l, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.shift_r}
]
current = set()
def on_press(key):
    if any([key in COMBO for COMBO in COMBINATIONS]):
        current.add(key)
        if any(all(k in current for k in COMBO) for COMBO in COMBINATIONS):
            print('hi')


def on_release(key):
    try:
        current.remove(key)
    except:
        pass
    if key == keyboard.Key.esc:
        return False


listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

