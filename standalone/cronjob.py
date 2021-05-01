import os
import time
import winreg
import threading

class RegEditor(object):
    def set_reg(self, reg_path, name, value):
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(registry_key)
            return True
        except WindowsError:
            return False

    def get_reg(self, mode, reg_path, name=None):
        if mode == 0:
            try:
                registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
                value, regtype = winreg.QueryValueEx(registry_key, name)
                winreg.CloseKey(registry_key)
                return value
            except WindowsError:
                return None
        else: #read the whole key
            try:
                values = []
                registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
                for i in range(winreg.QueryInfoKey(registry_key)[1]):
                    values.append(winreg.EnumValue(registry_key, i))
                winreg.CloseKey(registry_key)
                return values
            except WindowsError:
                return None

    def del_reg(self, mode, reg_path, name=None):
        if mode == 0: # delete only value
            try:
                registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE)
                winreg.DeleteValue(registry_key, name)
                winreg.CloseKey(registry_key)
                return True
            except WindowsError:
                return False
        else: #delete the whole key (use with caution)
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
                return True
            except:
                return False
            
class Tasks(object): #always return True
    def test(self):
        print('test')
        return True
    def hello(self):
        print('hello')
        return True  

class CronJob(object):
    def __init__(self):
        self.reg_path = r"SOFTWARE\Keylogger\Task"
        self.tasks = { #declare all Tasks here
            'test': Tasks().test,
            'hello': Tasks().hello,
        }
        #threading.Thread(target=self.loop).start()
    
        
    def set_task(self, task, hour, minute=0):
        try:
            for item in r.get_reg(1, self.reg_path):
                exist_task = item[0]
                if task == exist_task:
                    print('Task already exists!')
                    return
        except:
            pass
        interval = str(hour*60 + minute)
        r.set_reg(self.reg_path, str(task), interval+'|N/A|N/A')
        print('Task created successfully!')
            
    def get_task(self):
        try:
            task_list = r.get_reg(1, self.reg_path)
        except:
            print('Task list is empty!')
            return
        for item in task_list:
            task = item[0]
            interval, last_run, status = item[1].split('|')
            interval = int(interval)
            if last_run == 'N/A':
                status = 'N/A'
            else:
                last_run = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(last_run)))
            print('Task: ', task, ' | Interval: ', interval, ' | Last run: ', last_run, ' | Status: ', status)
            
    def delete_task(self, task):
        if r.del_reg(0, reg_path, task):
            print('Task deleted successfully!')
        else:
            print('Task not found!')
            return
        
    def loop(self):
        def execute(task, interval):
            try:
                if self.tasks[task]():
                    r.set_reg(self.reg_path, str(task), str(interval)+'|'+str(time.time())+'|success')
                    return True
                else:
                    r.set_reg(self.reg_path, str(task), str(interval)+'|'+str(time.time())+'|failed')
                    return False
            except Exception as e:
                print(e)
                r.set_reg(self.reg_path, str(task), str(interval)+'|'+str(time.time())+'|failed')
                return False
            
        while True: #endless loop, put the whole def in threading
            try:
                task_list = r.get_reg(1, self.reg_path)
            except:
                print('Task list is empty!')
                return
            if task_list == None:
                print('Task list is empty!')
                return
            for item in task_list:
                task = item[0]
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
                print('Task: ', task, ' | Interval: ', interval, ' | Last run: ', last_run, ' | Status: ', status)
            time.sleep(60) #delay before check the next interval


reg_path = r"SOFTWARE\Keylogger\Task"
r = RegEditor()
c = CronJob()

#c.set_task('test', 0, 1)
#c.set_task('hello', 0, 2)
c.get_task()
#c.delete_task('test')
#c.delete_task('hello')
