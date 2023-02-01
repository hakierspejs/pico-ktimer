PORT=/dev/tty.usbmodem101
ifeq (,$(wildcard /dev/tty.usbmodem101))
	PORT=/dev/tty.usbmodem1101
endif

shell:
	mpremote connect $(PORT) repl

ls:
	mpremote connect $(PORT) ls

burn: program

program:
	mpremote connect $(PORT) mip install github:stlehmann/micropython-ssd1306/ssd1306.py
	mpremote connect $(PORT) mip install github:hakierspejs/micropython-segclock/
	mpremote connect $(PORT) fs cp -r ./*.py :

run: program
	mpremote connect $(PORT) run main.py
