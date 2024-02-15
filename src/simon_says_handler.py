#! /usr/bin/env python
import os
import socket
import sys

import middleware as mw

s = None  # Socket
pan = mw.Pan()
tilt = mw.Tilt()
onboard = mw.Onboard()
speakers = mw.Speakers()
leds = mw.Leds()
server = mw.Server()

image_path = "images/simon_images/"
sound_path = "simon_sounds/"
icon_path = "simon_icons/"


def enable_torque():
    """
    Enables the torque for the pan and tilt motors.
    """
    pan.enable = True
    tilt.enable = True


def parse_message(message):
    """
    Parses the given message and performs the corresponding actions based on the
    command and value.

    Args:
        message (str): The message to be parsed in the format "command::value".
    """
    splitMessage = message.split("::")

    if len(splitMessage) != 2:
        print("Invalid message")

    command = splitMessage[0]
    value = splitMessage[1]

    if command == "pan":
        print("[PAN] setting...")
        pan.angle = int(value)
        print("[PAN] value: ", value)

    elif command == "tilt":
        print("[TILT] setting...")
        tilt.angle = int(value)
        print("[TILT] value: ", value)

    elif command == "image":
        print("[IMAGE] setting...")
        if "simon_images" in value:
            image_src = value
        else:
            image_src = os.path.join(image_path, f"{value}.png")
            print(image_src)
        onboard.image = image_src
        print("[IMAGE] src: ", image_src)

    elif command == "speakers":
        if value == "increaseVolume":
            print("[SPEAKERS] increasing volume...")
            speakers.volume += 10
        elif value == "decreaseVolume":
            print("[SPEAKERS] decreasing volume...")
            speakers.volume -= 10
        print("[SPEAKERS] volume: ", speakers.volume)

    elif command == "sound":
        print("[SOUND] setting...")
        sound_src = os.path.join(sound_path, f"{value}")
        sound_url = server.url_for_sound(sound_src)
        speakers.url = sound_url
        print("[SOUND] src: ", sound_src)

    elif command == "icon":
        print("[ICON] setting...")
        icon_src = os.path.join(icon_path, f"{value}")
        icon_url = server.url_for_icon(icon_src)
        leds.load_from_url(icon_url)
        print("[ICON] src: ", icon_url)

    elif command == "game":
        if value == "on":
            print("[GAME] starting...")
        elif value == "off":
            print("[GAME] ending...")
            s.close()
            exit()


def main():
    """
    Entry point of the Simon Says handler program.
    Parses command line arguments, establishes a connection, and handles
    incoming messages.
    """

    global s
    
    # Parse arguments
    if len(sys.argv) == 3 or len(sys.argv) == 4:
        elmo_ip, elmo_port = sys.argv[1:3]
        debug = False
    else:
        print("Usage: python3 simon_says_handler.py <elmoIp> <port> (--debug)")
        return

    # Check debug flag
    if len(sys.argv) == 4:
        if sys.argv[3] == "--debug":
            debug = True
        else:
            print("Usage: python3 simon_says_handler.py <elmoIp> <port> (--debug)")
            return

    print("Starting connection...")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((elmo_ip, int(elmo_port)))

    print("Server Started")

    if not debug:
        enable_torque()

    while True:
        data, addr = s.recvfrom(1024)
        data = data.decode("utf-8")
        print("Message from: " + str(addr))
        print("From connected user: " + data)

        if not debug:
            parse_message(data)


if __name__ == "__main__":
    main()
