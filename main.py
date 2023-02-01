# MIT License
#
# Copyright (c) 2023 Alex Ostrowski
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import gc
import _thread
import utime
from machine import Pin, PWM, I2C

import ssd1306
from segclock import Clock


PIN_POWER = Pin(2, Pin.OUT)
PIN_POWER.high()

PIN_BUZZER = const(11)
PIN_SDA = const(14)
PIN_SCL = const(15)
I2C_ID = const(1)

DISPLAY_WIDTH = const(128)
DISPLAY_HEIGHT = const(32)

BUZZER_LOCK = _thread.allocate_lock()
BUZZER_SETTINGS = (0, 0)  # freq, counter


def tone_thread(job):
    # thread to control buzzer
    global BUZZER_SETTINGS
    settings = BUZZER_SETTINGS
    PWM_BUZZER = PWM(Pin(PIN_BUZZER))
    PWM_BUZZER.freq(1500)

    while True:
        utime.sleep_ms(100)

        with BUZZER_LOCK:
            settings = BUZZER_SETTINGS

        freq, counter = settings
        if freq:
            print(freq, counter)
            PWM_BUZZER.freq(freq)

            for i in range(counter):
                PWM_BUZZER.duty_u16(32000)
                utime.sleep_ms(100)
                PWM_BUZZER.duty_u16(0)
                utime.sleep_ms(100)

            utime.sleep_ms(1000)
            with BUZZER_LOCK:
                BUZZER_SETTINGS = (0, 0)
                settings = (0, 0)
    return


def main():
    global BUZZER_SETTINGS
    start_time = utime.time()

    i2c = I2C(I2C_ID, sda=Pin(PIN_SDA), scl=Pin(PIN_SCL))

    display = ssd1306.SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c)

    _thread.start_new_thread(tone_thread, (1,))

    clock = Clock(
        display,
        DISPLAY_WIDTH,
        DISPLAY_HEIGHT,
        offset_x=6,
        offset_y=1,
        scale_x=3,
        scale_y=3,
    )
    seconds = 0

    while seconds < 60 * 10:

        seconds = utime.time() - start_time
        clock.draw(seconds // 60, seconds % 60)
        display.show()

        if seconds % 30 == 0:
            with BUZZER_LOCK:
                BUZZER_SETTINGS = (2000, seconds // 60 + 1)

        if seconds in (3 * 60, 4 * 60):
            with BUZZER_LOCK:
                BUZZER_SETTINGS = (500, 20)

        utime.sleep_ms(250)
        gc.collect()

    with BUZZER_LOCK:
        BUZZER_SETTINGS = (500, 20)

    utime.sleep_ms(10 * 1000)
    PIN_POWER.low()


if __name__ == "__main__":
    main()
