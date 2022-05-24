import os
import json

SETTINGS_FILE = 'settings.conf'
VERSIONCONTROL_FILE = 'versioncontrol.conf'
SYS_DIR = 'sys'
### Default
DEVICENAME = 'esp32-test'
TOPIC = 'esp32/stream'
SERVER = "otter.rmq.cloudamqp.com"
USER = "zyrncjnm:zyrncjnm"
PASS = "xvH1xL9oSUlvDPkmrX9EaDCzhd4h4YY6"

def isDir(dirname):
    if dirname in os.listdir():
        return True
    else:
        return False

def isFile(dirname, filename):
    if filename in os.listdir(dirname):
        return True
    else:
        return False

class version_control:
    def __init__(self, dirname=SYS_DIR):
        self._dirname = dirname
        if not isDir(self._dirname):
            os.mkdir(self._dirname)
        if not isFile(self._dirname, VERSIONCONTROL_FILE):
            print('Version control file does not exist')
            t_version_json = {}
            files = os.listdir()
            for t_file in files:
                if '.' in t_file:
                    t_version_json.update({ t_file:0 })
                else:
                    files_inside = os.listdir(t_file)
                    for t_file2 in files_inside:
                        if '.' in t_file2:
                            t_version_json.update({ t_file+'/'+t_file2:0 })
            print('File created:')
            print(json.dumps(t_version_json))
            f_version = open(self._dirname + '/' + VERSIONCONTROL_FILE, 'w')
            f_version.write(json.dumps(t_version_json))
            f_version.close()

    def getVersionStruct(self):
        if not isFile(self._dirname, VERSIONCONTROL_FILE):
            return {}
        else:
            f_version = open(self._dirname + '/' + VERSIONCONTROL_FILE)
            data = f_version.read()
            f_version.close()
            if data == '':
                print('Empty settings file')
                return {}
            else:
                try:
                    return json.loads(data)
                except Exception as e:
                    print('Error getting version control file\n' + str(e))

    def getVersion(self,filename):
        t_version_json = self.getVersionStruct()
        if filename in t_version_json:
            version = t_version_json[filename]
            return version

class local:
    def saveSetting(self, var, value):
        prev_settings = self.getSettingsStruct()
        if type(var) != str:
            raise Exception('Setting must be a string')
        if prev_settings == {} and value != None:
            prev_settings = { var : value }
        else:
            if var in prev_settings:
                if value != None:
                    prev_settings[var] = value
                else:
                    prev_settings.pop(var)
            elif value != None and value != '-' and value != '':
                prev_settings.update({ var : value })
        f_settings = open(self._dirname + '/' + self._filename, 'w')
        f_settings.write(json.dumps(prev_settings))
        f_settings.close()

    def getSettingsStruct(self):
        if not isFile(self._dirname, self._filename):
            return {}
        else:
            f_settings = open(self._dirname + '/' + self._filename)
            data = f_settings.read()
            f_settings.close()
            if data == '':
                print('Empty settings file')
                return {}
            else:
                try:
                    return json.loads(data)
                except Exception as e:
                    print('Error getting settings\n' + str(e))

    def getSettings(self, buf):
        t_list = []
        if type(buf) != list:
            var = []
            var.append(buf)
        else:
            var = buf
        settings = self.getSettingsStruct()
        if settings == {}:
            print('Empty settings struct')
            for i in range(len(buf)):
                t_list.append(None)
            print('Returning: ' + str(t_list))
            #return None
        else:
            for varname in var:
                if type(varname) != str:
                    t_list.append(None)
                    #raise Exception('Setting must be a string')
                if varname in settings:
                    t_list.append(settings[varname])
                else:
                    t_list.append(None)
            print('Returning: ' + str(t_list))
        return t_list

    def __init__(self, dirname=SYS_DIR, filename=SETTINGS_FILE):
        self._dirname = dirname
        self._filename = filename
        if not isDir(self._dirname):
            os.mkdir(self._dirname)
        if not isFile(self._dirname, self._filename):
            print('Settings file does not exist')
            default_struct = { 'default_key':'default_val' }
            f_settings = open(self._dirname + '/' + self._filename, 'w')
            f_settings.write(json.dumps(default_struct))
            f_settings.close()
                    # if 'uplink_period' in settings:
                    #     self.uplink_period = settings['uplink_period']
                    # if 'ssid' in settings:
                    #     ssid = settings['ssid']
                    # if 'password' in settings:
                    #     password = settings['password']
                    # if 'mqtt_server' in settings:
                    #     mqtt_server = settings['mqtt_server']
                    # if 'mqtt_user' in settings:
                    #     mqtt_user = settings['mqtt_user']
                    # if 'mqtt_pass' in settings:
                    #     mqtt_pass = settings['mqtt_pass']
                    # if 'mqtt_port' in settings:
                    #     mqtt_port = settings['mqtt_port']
                    # if 'downlink_topic' in settings:
                    #     downlink_topic = settings['downlink_topic']
                    # if 'uplink_topic' in settings:
                    #     uplink_topic = settings['uplink_topic']