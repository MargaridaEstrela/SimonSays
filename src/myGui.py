import PySimpleGUI as sg
from server import ElmoServer
import random
import numpy as np
import cv2
import math

# setting up IP addresses for communication with Elmo
elmoIp = "192.168.0.101"  # replace with the IP address of Elmo
elmoPort = 4000  # replace with the port number used by Elmo
clientIp = "192.168.0.114"  # replace with the IP address of the client

# list of emotions for facial expression analysis
emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

# variables to control the game
play = 1  # play number in the game (incremented with each play)
player = 1  # current player
points = {"1": 0, "2": 0}  # points of each player (initially set to 0)

# when the respective buttons are clicked, one of the faces in the list will be played at random
bad_face = ["cry", "confused", "anger"]  # the list of faces containing the necessary sounds for the bad button
good_face = ["normal", "rolling_eyes", "thinking"]  # the list of faces containing the necessary faces for the good button
awesome_face = ["love", "images/simon_images/stars.gif", "blush"]  # the list of faces containing the necessary faces for the awesome button

# default angles
default_pan = 0
default_tilt = 0

# when the respective buttons are clicked, one of the sounds in the list will be played at random
goodSoundList = []  # the list of sounds containing the necessary sounds for the good button
badSoundList = []   # the list of sounds containing the necessary sounds for the bad button
awesomeSoundList = []   # the list of sounds containing the necessary sounds for the awesome button

# connection with Elmo 
myElmo = ElmoServer(elmoIp, elmoPort, clientIp, True)

sg.theme('DarkBlue')   # add a touch of color

# All the stuff inside your window.

#lst = sg.Combo(imageList, font=('Arial Bold', 14),  expand_x=True, enable_events=True,  readonly=False, key='-COMBO-')
layout = [   
    [sg.Text('ELMO', size=(5, 1)), sg.Text('', size=(80, 1)), sg.Text("GAME", size=(5, 1))],
    [sg.Button("Look Player1", size=(15, 1)), sg.Button("Look Player2", size=(15, 1)), sg.Text('', size=(47, 1)), sg.Button("Intro", size=(10, 1))],
    [sg.Text("Pan", size=(3, 1)), sg.InputText(key="pan_value", size=(18, 1)), sg.Button("Set", key="SetPan", size=(8, 1)), sg.Text('', size=(5, 1)), sg.Button("Set Default", key="SetDefaultPan", size=(10, 1)), sg.Text('', size=(26, 1)), sg.Button("Play", size=(10, 1))],
    [sg.Text("Tilt", size=(3, 1)), sg.InputText(key="tilt_value", size=(18, 1)), sg.Button("Set", key="SetTilt", size=(8, 1)),  sg.Text('', size=(5, 1)), sg.Button("Set Default", key="SetDefaultTilt", size=(10, 1)), sg.Text('', size=(26, 1)), sg.Button("🔴", size=(10, 1))],
    [sg.Button("Toggle Behaviour", size=(15, 1)), sg.Button("Toggle Motors", size=(15, 1)), sg.Text('', size=(47, 1)), sg.Button("Next", size=(10, 1))],
    [sg.Text('', size=(1, 2))],
    [sg.Text("Accuracy: "), sg.Text("0  ", key="player_accuracy"), sg.Text('', size=(46, 1)), sg.Text("Player1: "), sg.Text("0", key="player1_points", size=(10, 1))],
    [sg.Button("Bad", size=(10, 1)), sg.Button("Good", size=(10, 1)), sg.Button("Awesome", size=(10, 1)), sg.Text('', size=(20, 1)), sg.Text("Player2: "), sg.Text("0", key="player2_points", size=(10, 1))],
    [sg.Text('', size=(1, 2))], 
    [sg.Text('', size=(2, 1)), sg.Button("Winner", size=(24, 1)), sg.Text('', size=(5, 1)), sg.Button("Restart", size=(24, 1)), sg.Text('', size=(5, 1)), sg.Button("Close All", size=(24, 1))],
    [sg.Text('', size=(1, 1))], 
    [sg.Image(filename="", key="image")]  
]

# Create the Window
window = sg.Window('Elmo: Wizard of OZ', layout)
# Event Loop to process "events" and get the "values" of the inputs


while True:
    event, values = window.read(timeout=60)

    print(event, values)

    # lets update the image
    img = myElmo.grabImage()
    imgbytes = cv2.imencode(".png", img)[1].tobytes()
    window['image'].update(data=imgbytes)

    if event == "Toggle Behaviour":
        print("Toggling Behaviour")
        myElmo.toggleBehaviour()
        # change the color of the button
        if myElmo.activeBehaviour:
            window['Toggle Behaviour'].update(button_color=('white', 'green'))
        else:
            window['Toggle Behaviour'].update(button_color=('white', 'red'))
    
    if event == "Toggle Motors":
        print("Toggling Motors")
        myElmo.toggleMotors()
        # change the color of the button
        if myElmo.activeMotors:
            window['Toggle Motors'].update(button_color=('white', 'green'))
        else:
            window['Toggle Motors'].update(button_color=('white', 'red'))
    
    if event == "Look Player1":
        print("Looking at player 1")
        myElmo.moveLeft(default_pan, default_tilt)
    
    elif event == "Look Player2":
        myElmo.moveRight(default_pan, default_tilt)
        print("Looking at player 2")
   
    if event == "SetPan":
        value = values["pan_value"]
        if value: 
            myElmo.movePan(value)
            default_pan = value
    
    if event == "SetDefaultPan":
        myElmo.movePan(default_pan)

    if event == "SetTilt":
        value = values["tilt_value"]
        if value:
            myElmo.moveTilt(value)
            default_tilt = value

    if event == "SetDefaultTilt":
        myElmo.movePan(default_tilt)

    if event == "Intro":
        myElmo.introduceGame()
        myElmo.playGame()

    elif event == "Play":
        emotion = emotions[play-1]
        myElmo.sayEmotion(emotion)
    
    elif event == "🔴":
        frame = myElmo.takePicture()
        emotion = emotions[play-1]
        value = myElmo.analysePicture(frame, emotion)
        value = round(value)
        # update the text box with the result
        window['player_accuracy'].update(value)
        # update points and display
        points[str((play + 1) % 2 + 1)] += value
        window['player'+ str((play + 1) % 2 + 1)+"_points"].update(points[str((play + 1) % 2 + 1)])

    elif event == "Next":
        play += 1
        if play > len(emotions):
            myElmo.movePan(0)
            myElmo.endGame()
        else:
            emotion = emotions[play-1]
            myElmo.sayEmotion(emotion)
    
    if event == "Bad":
        face = random.choice(bad_face)
        sound = random.choice(badSoundList) if len(badSoundList) > 0 else ""
        myElmo.playSound(sound)
        # need to play a sound from the bad sound list

        myElmo.setImage(face)

    elif event == "Good":
        face = random.choice(good_face)
        # need to play a sound from the good sound list
        sound = random.choice(goodSoundList) if len(goodSoundList) > 0 else ""
        myElmo.playSound(sound)
        myElmo.setImage(face)

    elif event == "Awesome":
        face = random.choice(awesome_face)
        #need to play a sound from the awesome sound list
        sound = random.choice(awesomeSoundList) if len(awesomeSoundList) > 0 else ""
        myElmo.playSound(sound)
        myElmo.setImage(face)

    if event == "Winner":
        winner = max(points, key=points.get)
        myElmo.congratsWinner()

    if event == "Restart":
        play = 1
        points["1"] = 0
        points["2"] = 0

    if event == sg.WIN_CLOSED or event == "Close All": # if user closes window or clicks cancel
        print("Windows is going to close")
        myElmo.closeAll()
        break

window.close()