import winreg

#reg_path = r"SOFTWARE\Keylogger\Settings"
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



