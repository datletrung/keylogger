import os
#import keylogger
import shutil
import tkinter as tk
import tkinter.font as font
import tkinter.messagebox as messagebox

class BasicFunctionFunction(object):
    def popup_msg(self, mode, title, msg):
        if mode == 0:
            messagebox.showinfo(str(title), str(msg))
        elif mode == 1:
            messagebox.showwarning(str(title), str(msg))
        elif mode == 2:
            messagebox.showerror(str(title), str(msg))

class Config(object):
    working_dir = os.getcwd()
    log_path = str(os.path.join(working_dir, 'log',))
    screenshot_path = str(os.path.join(working_dir, 'screenshot',))
    camera_path = str(os.path.join(working_dir, 'camera',))


class Setting(object):
    def __init__(self, root):
        self.root = root
        #self.k = keylogger.Keylogger()
        #self.cam_list = self.k.get_camera_list()
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
    def switch_log_path(self):
        if self.switch_button_1.config('text')[-1] == 'ON' or self.switch_button_2.config('text')[-1] == 'ON':
            self.path_1.config(state='normal')
        else:
            self.path_1.config(state='disabled')
    def toggle_button_3(self): #screenshot
        if self.switch_button_3.config('text')[-1] == 'ON':
            self.switch_button_3.config(text='OFF')
            self.switch_button_3.config(bg='red')
            self.interval_3.config(state='disabled')
            self.path_3.config(state='disabled')
        else:
            self.switch_button_3.config(text='ON')
            self.switch_button_3.config(bg='green')
            self.interval_3.config(state='normal')
            self.path_3.config(state='normal')
    def toggle_button_4(self): #camera
        if self.switch_button_4.config('text')[-1] == 'ON':
            self.switch_button_4.config(text='OFF')
            self.switch_button_4.config(bg='red')
            self.interval_4.config(state='disabled')
            self.path_4.config(state='disabled')
        else:
            self.switch_button_4.config(text='ON')
            self.switch_button_4.config(bg='green')
            self.interval_4.config(state='normal')
            self.path_4.config(state='normal')
    def apply_button(self):
        #save to config file
        pass

    def start_button(self):
        error = False
        #check log setting
        if self.switch_button_1.config('text')[-1] == 'ON':
            keyboard = True
            log_path = self.path_1.get()
            if os.path.exists(log_path):
                pass
            elif os.access(os.path.dirname(log_path), os.W_OK):
                pass
            else:
                error = True
                BasicFunction().popup_msg(2, "Error", "Cannot create Log folder!\nPlease change your folder.")
        if self.switch_button_2.config('text')[-1] == 'ON':
            clipboard = True
            log_path = self.path_1.get()
            if os.path.exists(log_path):
                pass
            elif os.access(os.path.dirname(log_path), os.W_OK):
                pass
            else:
                error = True
                BasicFunction().popup_msg(2, "Error", "Cannot create Log folder!\nPlease change your folder.")
        #check screenshot setting                
        if self.switch_button_3.config('text')[-1] == 'ON':
            screenshot = True
            try:
                screenshot_interval = int(self.interval_3.get())*60
            except:
                error = True
                BasicFunction().popup_msg(2, "Error", "Invalid Screenshot interval!")
            screenshot_path = self.path_3.get()
            if os.path.exists(screenshot_path):
                pass
            elif os.access(os.path.dirname(screenshot_path), os.W_OK):
                pass
            else:
                error = True
                BasicFunction().popup_msg(2, "Error", "Cannot create Screenshot folder!\nPlease change your folder.")
        #check camera setting
        if self.switch_button_4.config('text')[-1] == 'ON':
            camera = True
            try:
                camera_interval = int(self.interval_4.get())*60
            except:
                error = True
                BasicFunction().popup_msg(2, "Error", "Invalid Camera interval!")
            camera_path = self.path_4.get()
            if os.path.exists(camera_path):
                pass
            elif os.access(os.path.dirname(camera_path), os.W_OK):
                pass
            else:
                error = True
                BasicFunction().popup_msg(2, "Error", "Cannot create Camera folder!\nPlease change your folder.")
            
        if not error:
            #print(screenshot_interval, camera_interval, camera_path, screenshot_path, log_path)
            #do sth here
            pass
        
        
    def render(self):       
        tk.Label(self.root, text="CAPTURE", font=font.Font(size=10, weight='bold')).grid(row=0, padx=5, pady=5)
        tk.Label(self.root, text="INTERVAL (mins)", font=font.Font(size=10, weight='bold')).grid(row=0, column=2, padx=5, pady=5)
        tk.Label(self.root, text="PATH", font=font.Font(size=10, weight='bold')).grid(row=0, column=3, padx=5, pady=5)
        tk.Label(self.root, text="Keyboard").grid(row=1, padx=5, pady=5)
        tk.Label(self.root, text="Clipboard").grid(row=2, padx=5, pady=5)
        tk.Label(self.root, text="Screenshot").grid(row=3, padx=5, pady=5)
        tk.Label(self.root, text="Camera").grid(row=4, padx=5, pady=5)

        #1-keyboard | 2-clipboard | 3-screenshot | 4-camera | 5-apply | 6-start
        #button
        self.switch_button_1 = tk.Button(self.root, text="OFF", font=font.Font(size=8, weight='bold'), width=10, bg="red", command=self.toggle_button_1)
        self.switch_button_2 = tk.Button(self.root, text="OFF", font=font.Font(size=8, weight='bold'), width=10, bg="red", command=self.toggle_button_2)
        self.switch_button_3 = tk.Button(self.root, text="OFF", font=font.Font(size=8, weight='bold'), width=10, bg="red", command=self.toggle_button_3)
        self.switch_button_4 = tk.Button(self.root, text="OFF", font=font.Font(size=8, weight='bold'), width=10, bg="red", command=self.toggle_button_4)
        self.switch_button_5 = tk.Button(self.root, text="APPLY", font=font.Font(size=8, weight='bold'), width=10, command=self.apply_button)
        self.switch_button_6 = tk.Button(self.root, text="START", font=font.Font(size=8, weight='bold'), width=10, command=self.start_button)
        self.switch_button_1.grid(row=1, column=1, padx=5, pady=5)
        self.switch_button_2.grid(row=2, column=1, padx=5, pady=5)
        self.switch_button_3.grid(row=3, column=1, padx=5, pady=5)
        self.switch_button_4.grid(row=4, column=1, padx=5, pady=5)
        self.switch_button_5.grid(row=5, column=1, columnspan=2, padx=5, pady=5)
        self.switch_button_6.grid(row=5, column=2, columnspan=2, padx=5, pady=5)

        #path input
        self.path_1 = tk.Entry(self.root)
        self.path_3 = tk.Entry(self.root)
        self.path_4 = tk.Entry(self.root)
        self.path_1.insert(0, Config().log_path)
        self.path_3.insert(0, Config().screenshot_path)
        self.path_4.insert(0, Config().camera_path)
        self.path_1.config(state='disabled')
        self.path_3.config(state='disabled')
        self.path_4.config(state='disabled')
        self.path_1.grid(row=1, column=2, rowspan=2, padx=5, pady=5)
        self.path_3.grid(row=3, column=2, padx=5, pady=5)
        self.path_4.grid(row=4, column=2, padx=5, pady=5)

        #interval input
        self.interval_3 = tk.Entry(self.root)
        self.interval_4 = tk.Entry(self.root)
        self.interval_3.insert(0, 5)
        self.interval_4.insert(0, 5)
        self.interval_3.config(state='disabled')
        self.interval_4.config(state='disabled')
        self.interval_3.grid(row=3, column=3, padx=5, pady=5)
        self.interval_4.grid(row=4, column=3, padx=5, pady=5)

root = tk.Tk()
root.title("Keylogger")
root.geometry("435x207")
root.resizable(False, False)

setting_tab = Setting(root)

root.mainloop()

