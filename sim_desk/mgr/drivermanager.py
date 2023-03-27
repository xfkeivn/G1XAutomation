from utilities import Singleton
import os
import sys
import re
import traceback
from devicedriver.genericdriver import GenericDriver
from devicedriver.busdllwrapper import DispatcherManager
import ctypes
VALID_MODULE_NAME = re.compile(r'[_a-z]\w*\.py$', re.IGNORECASE)


def _make_failed_import(name):
    message = 'Failed to import module: %s\n%s' % (name, traceback.format_exc())
    return _make_failed('ModuleImportFailure', name, ImportError(message))


def _make_failed(classname, methodname, exception):
    attrs = {"error": exception}
    ModuleImportFailureClass = type(classname, (object,), attrs)
    return ModuleImportFailureClass()


class DriverManager(metaclass=Singleton):
    def __init__(self):
        self.drivers=[]
        self.sync_started_counter = None
        

    def __find_driver(self,start_dir):
        paths = os.listdir(start_dir)
        for path in paths:
            full_path = os.path.join(start_dir, path)
            if os.path.isfile(full_path):
                if not VALID_MODULE_NAME.match(path):
                    continue
                name = self._get_name_from_path(full_path)
                try:
                    module = self._get_module_from_name(name)
                except Exception as err:
                    print (err)
                    yield _make_failed_import(name)
                else:
                    mod_file = os.path.abspath(getattr(module, '__file__', full_path))
                    realpath = os.path.splitext(os.path.realpath(mod_file))[0]
                    fullpath_noext = os.path.splitext(os.path.realpath(full_path))[0]
                    if realpath.lower() != fullpath_noext.lower():
                        module_dir = os.path.dirname(realpath)
                        mod_name = os.path.splitext(os.path.basename(full_path))[0]
                        expected_dir = os.path.dirname(full_path)
                        msg = ("%r module incorrectly imported from %r. Expected %r. "
                               "Is this module globally installed?")
                        raise ImportError(msg % (mod_name, module_dir, expected_dir))
                    yield self.loadDriversFromModule(module)
            elif os.path.isdir(full_path):
                #the folder must be a package 
                if not os.path.isfile(os.path.join(full_path, '__init__.py')):
                    continue
                for driver in self.__find_driver(full_path):
                    yield driver

    def discover(self,start_dir):
        self.start_dir = start_dir
        if start_dir not in sys.path:
            sys.path.insert(0, start_dir)
        driver_cluster = list(self.__find_driver(start_dir))
        self.drivers=[]
        for cluster in driver_cluster:
            if isinstance(cluster, list):
                for drv in cluster:
                    self.drivers.append(drv)
            else:
                self.drivers.append(cluster)
        return self.drivers
                    
                
                
    def getDriverClassByName(self,drivername):
        for driver in self.drivers:
            if drivername in str(driver):
                return driver
            
    def getDriverByName(self,drivername):
        for driverclass in self.drivers:
            if driverclass().getDriverName() == drivername:
                return driverclass
        return None

    def getResourceByName(self,resourcename):
        for driverclass in self.drivers:
            res = driverclass().getResourceByName(resourcename)
            if res is not None:
                return res
        return None


    def _get_module_from_name(self, name):
        __import__(name)
        return sys.modules[name]

    def _get_name_from_path(self, path):
        path = os.path.splitext(os.path.normpath(path))[0]
        _relpath = os.path.relpath(path, self.start_dir)
        assert not os.path.isabs(_relpath), "Path must be within the project"
        assert not _relpath.startswith('..'), "Path must be within the project"

        name = _relpath.replace(os.path.sep, '.')
        return name

    def loadDriversFromModule(self, module):
        drivers = []
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, GenericDriver) and obj is not GenericDriver :
                drivers.append(obj)
        return drivers

    def syncStart(self):
        self.sync_started_counter = ctypes.c_longlong(0)
        # ctypes.windll.kernel32.QueryPerformanceFrequency(ctypes.byref(freq))
        ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(self.sync_started_counter))
        DispatcherManager().syncStart(self.sync_started_counter)
        return self.sync_started_counter

    def elpaseSinceSyncStart(self):
        current = ctypes.c_longlong(0)
        freq = ctypes.c_longlong(0)
        ctypes.windll.kernel32.QueryPerformanceFrequency(ctypes.byref(freq))
        ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(current))
        return (int)((current.value - self.sync_started_counter.value + 500)*1000//(freq.value))


if __name__ == "__main__":
    dm = DriverManager()
    print((dm.discover(r"C:\Users\Administrator\DVTFront\drivers")))
