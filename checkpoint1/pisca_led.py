#!/bin/python3

from gpiozero import LED
from time import sleep
import atexit

led = LED(18)

def saida():
    led.off()

atexit.register(saida)

while True:
    led.on()
    sleep(0.5)
    led.off()
    sleep(0.5)
