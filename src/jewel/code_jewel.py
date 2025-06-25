import adafruit_logging as logging
log = logging.getLogger()
log.setLevel(10)

import board
from jewel.pausable_pixels import PausablePixels
from core.buttons import Buttons
from microcontroller import Pin
from core.loop import main_loop, ErrorHandlerResumeOnButtonPress
from jewel.view_jewel import ViewJewel
from core.connection.sgt_connection_bluetooth import SgtConnectionBluetooth

# === Constants and Setup ===
BTN_PIN = board.D4
LED_PIN = board.D6
LED_COUNT = 19
LED_BRIGHTNESS = 1

# Suggested Script and Action Mapping
# These are sent on connection to the SGT to pre-populate the Action/Write scripts for quick save.
BLE_DEVICE_NAME = "Jewel"
BLUETOOTH_FIELD_DIVIDER = ';'
BLUETOOTH_FIELD_ORDER = ['sgtTimerMode','sgtState','sgtColorHsv','sgtTurnTime','sgtPlayerTime','sgtTotalPlayTime','sgtTimeReminders', 'sgtPlayerColors', 'sgtPlayerActions']

# ---------- VIEW SETUP -------------#
pixels = PausablePixels(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)
view = ViewJewel(pixels)
view.set_state(None)

# ---------- BLUETOOTH SETUP -------------#

sgt_connection = SgtConnectionBluetooth(view,
		device_name=BLE_DEVICE_NAME,
		field_order=BLUETOOTH_FIELD_ORDER,
		field_divider=BLUETOOTH_FIELD_DIVIDER,
	)

# ---------- BUTTONS SETUP -------------#
buttons = Buttons({BTN_PIN: False})
def btn_callback(pin: Pin, presses: int, long_press: bool):
	log.info(f"Button pressed: {presses} times, long press: {long_press}")
	def on_success():
		pass

	if long_press:
		if presses == 1:
			sgt_connection.enqueue_send_toggle_admin(on_success=on_success)
		elif presses == 2:
			sgt_connection.enqueue_send_undo(on_success=on_success)
	else:
		if presses == 1:
			sgt_connection.enqueue_send_primary(on_success=on_success)
		elif presses == 2:
			sgt_connection.enqueue_send_secondary(on_success=on_success)

def pressed_keys_callback(pins: set[Pin]):
	if len(pins) == 0:
		pixels.pause = False
		pixels.fill(0x0)
		pixels.show()
	else:
		pixels.pause = False
		pixels.fill(0xFFFFFF)
		pixels.show()
		pixels.pause = True

# ---------- MAIN LOOP -------------#
error_handler = ErrorHandlerResumeOnButtonPress(view, buttons)
def on_connect():
	buttons.clear_callbacks()
	buttons.set_callback(pin=BTN_PIN, presses=1, callback = btn_callback)
	buttons.set_callback(pin=BTN_PIN, presses=2, callback = btn_callback)
	buttons.set_callback(pin=BTN_PIN, presses=1, long_press=True, callback = btn_callback)
	buttons.set_callback(pin=BTN_PIN, presses=2, long_press=True, callback = btn_callback)
	buttons.set_pressed_keys_update_callback(pressed_keys_callback)

main_loop(sgt_connection, view, on_connect, error_handler.on_error, (buttons.loop,))