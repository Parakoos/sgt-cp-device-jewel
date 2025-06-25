from core.utils.settings import get_float, get_int

# 0-1. How bright do you want the LED?
MONO_COLOR_TRANSITION_DURATION = get_float('MONO_COLOR_TRANSITION_DURATION', 0.5)

# How many seconds should it take for the large ring to go one way around
# during a turn and for the next indicator light to turn on in the middle?
JEWEL_SECONDS_PER_ROTATION = get_int('JEWEL_SECONDS_PER_ROTATION', 60)

import adafruit_logging as logging
log = logging.getLogger()
from neopixel import NeoPixel

import adafruit_fancyled.adafruit_fancyled as fancy
from adafruit_led_animation.animation import Animation
from adafruit_led_animation.group import AnimationGroup
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.sparklepulse import SparklePulse
from adafruit_led_animation.helper import PixelSubset, PixelMap

from core.game_state import GameState
from core.sgt_animation import SgtAnimation, SgtSolid
from core.view.view import View
from core.color import PlayerColor, RED, BLUE, BLACK, GREEN, ColorMix
from core.transition.easing import LinearInOut

WHITE = PlayerColor('ff00ff', True)

class ViewJewel(View):
	def __init__(self, pixels: NeoPixel):
		super().__init__()
		self.pixels = pixels
		self.animation = SgtSolid(self.pixels, BLACK)
		self.outer_ring = PixelSubset(pixels, 0, 12)
		self.central_dot = PixelSubset(pixels, 12, 13)
		self.middle_ring = PixelSubset(pixels, 13, 19)
		self.central_disk = PixelSubset(pixels, 12, 19)
		# Normal spiral, out going in
		# self.sandtimer = PixelMap(pixels, [1,2,3,4,5,6,7,8,9,10,11, 0, 18, 13,14,15,16,17, 12], individual_pixels=True)
		# Wedges. Kinda cool.
		self.wedges = PixelMap(pixels, [0,18,1, 2,13,3, 4,14,5, 6,15,7, 8,16,9, 10,11,17, 12 ], individual_pixels=True)

	def animate(self) -> bool:
		shared_stuff_busy = super().animate()
		this_animation_busy = self.animation.animate()
		return this_animation_busy or shared_stuff_busy

	def on_state_update(self, state: GameState|None, old_state: GameState|None):
		if state is None:
			return
		if isinstance(self.animation, Animation):
			self.animation.color = state.color_p.highlight.create_display_color().current_color
		elif isinstance(self.animation, SgtAnimation):
			self.animation.transition_color(state.color_p.highlight, LinearInOut(0, 1, MONO_COLOR_TRANSITION_DURATION))

	def set_connection_progress_text(self, text):
		if not isinstance(self.animation, BluetoothConnectionAnimation):
			self.animation = BluetoothConnectionAnimation(self)
		log.info(f"Connection Progress: {text}")
	def switch_to_playing(self, state: GameState, old_state: GameState):
		if not isinstance(self.animation, TimedAnimation):
			self.animation = TimedAnimation(self)
		log.info(f"-> Playing")
	def switch_to_simultaneous_turn(self, state: GameState, old_state: GameState):
		if not isinstance(self.animation, SimTurnAnimation):
			self.animation = SimTurnAnimation(self)
		log.info(f"-> Simultaneous Turn")
	def switch_to_admin_time(self, state: GameState, old_state: GameState):
		if not isinstance(self.animation, TimedAnimation):
			self.animation = TimedAnimation(self)
		log.info(f"-> Admin Time")
	def switch_to_paused(self, state: GameState, old_state: GameState):
		if not isinstance(self.animation, TimedAnimation):
			self.animation = TimedAnimation(self)
		log.info(f"-> Paused")
	def switch_to_sandtimer_running(self, state: GameState, old_state: GameState):
		if not isinstance(self.animation, SandtimerAnimation):
			self.animation = SandtimerAnimation(self)
		log.info(f"-> Sand Timer (Running)")
	def switch_to_sandtimer_not_running(self, state: GameState, old_state: GameState):
		if not isinstance(self.animation, SandtimerAnimation):
			self.animation = SandtimerAnimation(self)
		log.info(f"-> Sand Timer (Stopped)")
	def switch_to_start(self, state: GameState, old_state: GameState):
		self.set_button_led_to_periodic_pulse(state.color_p, 1, 2)
		log.info(f"-> Setup")
	def switch_to_end(self, state: GameState, old_state: GameState):
		# self.animation = Rainbow(self.pixels, speed=0.1)
		log.info(f"-> Game Over")
	def switch_to_no_game(self):
		super().switch_to_no_game()
		self.set_button_led_to_sparkle_pulse(WHITE)
		log.info(f"-> No Game In Progress")
	def switch_to_not_connected(self):
		super().switch_to_not_connected()
		self.set_button_led_to_periodic_pulse(BLUE, 2, 2)
		log.info(f"-> Not Connected")
	def switch_to_error(self):
		super().switch_to_error()
		self.set_button_led_to_blink(RED, 0.2)
		log.info(f"-> Error")

	# Helper methods
	def set_button_led_to_solid(self, color: PlayerColor):
		self.animation = SgtAnimation(color.highlight, (SgtSolid(self.pixels, color=0), None, False))
	def set_button_led_to_blink(self, color: PlayerColor, speed: float):
		self.animation = SgtAnimation(color.highlight, (Blink(self.pixels, speed=speed, color=0), None, False))
	def set_button_led_to_pulse(self, color: PlayerColor, pulse_time: float):
		self.animation = SgtAnimation(color.highlight, (Pulse(self.pixels, speed=0.01, color=0), None, False))
	def set_button_led_to_periodic_pulse(self, color: PlayerColor, pulse_time, pause_time):
		pause = SgtSolid(self.pixels, BLACK)
		pulse = Pulse(self.pixels, speed=0.001, color=0, period=pulse_time)
		self.animation = SgtAnimation(color.highlight, (pulse, 1, False), (pause, pause_time, True))
	def set_button_led_to_sparkle_pulse(self, color: PlayerColor, period=2, breath=0):
		self.pixels.fill(0x0)
		self.pixels.show()
		self.animation = SparklePulse(self.pixels, 0.01, color.dim.create_display_color().current_color, period=period, breath=breath)

class BluetoothConnectionAnimation():
	def __init__(self, jewel_view: ViewJewel):
		outer = Comet(jewel_view.outer_ring, 0.1, BLUE.dim.create_display_color().current_color, tail_length=5, ring=True, reverse=False)
		middle = Comet(jewel_view.middle_ring, 0.1, BLUE.dim.create_display_color().current_color, tail_length=5, ring=True, reverse=True)
		jewel_view.central_dot.fill(0x0)
		jewel_view.central_dot.show()
		self.animation =  AnimationGroup(outer, middle)

	def animate(self):
		self.animation.animate()

class TimedAnimation():
	def __init__(self, jewel_view: ViewJewel):
		self.jewel_view = jewel_view
		self.numeric_displays = [
			None,
			PixelMap(jewel_view.pixels, [12], individual_pixels=True),
			PixelMap(jewel_view.pixels, [13, 16], individual_pixels=True),
			PixelMap(jewel_view.pixels, [13, 15, 17], individual_pixels=True),
			PixelMap(jewel_view.pixels, [14, 16, 18, 12], individual_pixels=True),
			PixelMap(jewel_view.pixels, [13, 14, 16, 17, 12], individual_pixels=True),
			PixelMap(jewel_view.pixels, [(13, 19)], individual_pixels=False),
			PixelMap(jewel_view.pixels, [(12, 19)], individual_pixels=False),
		]
		self.current_player_color: PlayerColor = None
		self.current_dim_color: int = None
		self.current_highlight_color: int = None
		self.current_mix: ColorMix = None

	def animate(self):
		if self.jewel_view.state == None or self.jewel_view.state.color_p == None:
			return
		if self.current_player_color != self.jewel_view.state.color_p:
			self.current_player_color = self.jewel_view.state.color_p
			self.current_dim_color = self.current_player_color.dim.create_display_color().current_color
			self.current_highlight_color = self.current_player_color.highlight.create_display_color().current_color
			self.current_mix = ColorMix(self.current_player_color.dim, self.current_player_color.highlight)

		current_timings = self.jewel_view.state.get_current_timings()
		turn_time = current_timings.turn_time
		mins, seconds = divmod(turn_time, JEWEL_SECONDS_PER_ROTATION)

		# Set the inner display
		self.jewel_view.pixels.fill(0x0)
		if mins > 0:
			self.numeric_displays[min(int(mins), 7)].fill(self.current_highlight_color)

		# Set the outer ring to dim
		pixel_count = len(self.jewel_view.outer_ring)
		pixels_completed, last_pixel_completion = divmod(pixel_count * (seconds / JEWEL_SECONDS_PER_ROTATION), 1)
		pixels_completed_int = int(pixels_completed)
		for i in range(pixel_count):
			if i < pixels_completed_int:
				self.jewel_view.outer_ring[i] = self.current_highlight_color
			elif i == pixels_completed_int:
				fancy_color, rounded_brightness = self.current_mix.mix(last_pixel_completion)
				new_color = fancy.gamma_adjust(fancy_color, brightness=rounded_brightness).pack()
				self.jewel_view.outer_ring[i] = new_color
			else:
				self.jewel_view.outer_ring[i] = self.current_dim_color

		self.jewel_view.pixels.show()


class SandtimerAnimation():
	def __init__(self, jewel_view: ViewJewel):
		self.jewel_view = jewel_view
		self.red_color: int = RED.dim.create_display_color().current_color
		self.green_color: int = GREEN.highlight.create_display_color().current_color
		self.blue_color: int = BLUE.dim.create_display_color().current_color
		self.green_to_blue_mix: ColorMix = ColorMix(GREEN.highlight, BLUE.dim)

	def animate(self):
		if self.jewel_view.state == None:
			return

		current_timings = self.jewel_view.state.get_current_timings()
		total_time = current_timings.player_time
		used_time = current_timings.turn_time
		if used_time > total_time:
			self.jewel_view.pixels.fill(self.red_color)
		elif used_time == 0:
			self.jewel_view.pixels.fill(self.green_color)
		else:
			pixel_count = len(self.jewel_view.wedges)
			seconds_per_pixel = total_time / pixel_count
			pixels_completed, seconds_into_border_pixel = divmod(used_time, seconds_per_pixel)
			pixels_completed_int = int(pixels_completed)
			for i in range(pixel_count):
				if i < pixels_completed_int:
					self.jewel_view.wedges[i] = self.blue_color
				elif i == pixels_completed_int:
					fancy_color, rounded_brightness = self.green_to_blue_mix.mix(seconds_into_border_pixel/seconds_per_pixel)
					new_color = fancy.gamma_adjust(fancy_color, brightness=rounded_brightness).pack()
					self.jewel_view.wedges[i] = new_color
				else:
					self.jewel_view.wedges[i] = self.green_color
		self.jewel_view.pixels.show()

class SimTurnAnimation():
	def __init__(self, jewel_view: ViewJewel):
		self.jewel_view = jewel_view

	def animate(self):
		if self.jewel_view.state == None:
			return

		colors = [player.color for player in self.jewel_view.state.players if player.action != None]
		player_count = len(colors)
		self.jewel_view.pixels.fill(0x0)
		if player_count == 1:
			self.jewel_view.middle_ring.fill(colors[0].dim.create_display_color().current_color)
		elif player_count == 2:
			for i in range(12):
				self.jewel_view.outer_ring[i] = colors[int(i / 6)].dim.create_display_color().current_color
		elif player_count == 3:
			for i in range(12):
				self.jewel_view.outer_ring[i] = colors[int(i / 6)].dim.create_display_color().current_color
			self.jewel_view.middle_ring.fill(colors[2].dim.create_display_color().current_color)
		elif player_count == 4:
			for i in range(12):
				self.jewel_view.outer_ring[i] = colors[int(i / 4)].dim.create_display_color().current_color
			mid_color = colors[3].dim.create_display_color().current_color
			self.jewel_view.pixels[12] = mid_color
			self.jewel_view.pixels[14] = mid_color
			self.jewel_view.pixels[16] = mid_color
			self.jewel_view.pixels[18] = mid_color
		elif player_count <= 6:
			for i in range(player_count):
				if i == 12:
					self.jewel_view.pixels[18] = colors[i].dim.create_display_color().current_color
					self.jewel_view.pixels[i*2+1] = colors[i].dim.create_display_color().current_color
				else:
					self.jewel_view.wedges[i*3] = colors[i].dim.create_display_color().current_color
					self.jewel_view.wedges[i*3+1] = colors[i].dim.create_display_color().current_color
					self.jewel_view.wedges[i*3+2] = colors[i].dim.create_display_color().current_color
		elif player_count <= 9:
			for i in range(player_count):
				if i == 6:
					self.jewel_view.pixels[18] = colors[i].dim.create_display_color().current_color
					self.jewel_view.pixels[i*2+1] = colors[i].dim.create_display_color().current_color
				else:
					self.jewel_view.pixels[i*2] = colors[i].dim.create_display_color().current_color
					self.jewel_view.pixels[i*2+1] = colors[i].dim.create_display_color().current_color
		else:
			for i in range(min(player_count, len(self.jewel_view.pixels))):
				self.jewel_view.pixels[i] = colors[i].dim.create_display_color().current_color

		self.jewel_view.pixels.show()