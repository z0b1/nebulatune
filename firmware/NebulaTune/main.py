import machine
import utime
from si5351 import SI5351
from ssd1306 import SSD1306_I2C

i2c = machine.I2C(0, sda=machine.Pin(4), scl=machine.Pin(5))

try:
    oled = SSD1306_I2C(128, 64, i2c)
    print("OLED detected successfully")
except Exception as e:
    print("Error initalizing", e)
    oled = None

try:
    crystal_freq = 25000000
    clock_gen = SI5351(i2c, crystal_freq)
    print("SI5351 detected successfully")
except Exception as e:
    print("Error initializing SI5351", e)
    clock_gen = None

frequency = 7000000 # Starting frequency 7.000MHz
steps = [1000, 10000, 100000] #step sizes for freq adjustment 1kHz 10kHz 100kHz 
step_index = 0
current_step = steps[step_index]

clk_pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP) # Pin 0 is used for frequency adjustment
dt_pin = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP) # Pin 1 is used for frequency adjustment
switch_pin = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP) # Pin 2 is used for step size adjustment

last_clk_state = clk_pin.value()
last_switch_time = 0

def update_system(freq):

    if clock_gen:
        try:
            clock_gen.set_freq(0, freq)
        except Exception as e:
            print("Error setting frequency", e)
    if oled:
        oled.fill(0)

        oled.text("NebulaTune", 4,2,1)
        oled.text("----------------", 0, 12, 1)
        freq_mhz = freq / 1000000
        oled.text(f"FREQ: {freq_mhz:.4f} MHz", 0, 28, 1)
        step_khz = current_step / 1000
        oled.text(f"STEP: {step_khz:g} kHz", 0, 48, 1)
        oled.show()
update_system(frequency)

while True:
    current_clk_state = clk_pin.value()
    if current_clk_state != last_clk_state:

        if dt_pin.value() != current_clk_state:
            frequency += current_step
        else:
            frequency -= current_step
        
        if frequency < 0:
            frequency = 0

        update_system(frequency)
        utime.sleep_ms(2)  # Debounce delay

    last_clk_state = current_clk_state

    if switch_pin.value() == 0:
        current_time = utime.ticks_ms()
        if current_time - last_switch_time > 200:  # Debounce delay
            step_index = (step_index + 1) % len(steps)
            current_step = steps[step_index]
            update_system(frequency)
            last_switch_time = current_time
    utime.sleep_ms(3)  # Main loop delay