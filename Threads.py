from PySide6 import QtWidgets, QtGui, QtCore
import psutil
import cpuinfo
import time
import win32com.client
import pythoncom



class DisksInfo(QtCore.QThread):
    Discinfo_list = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.delay = 10

    def run(self):
        while True:
            disk_dict = {}

            for i in psutil.disk_partitions():
                try:
                    disk_dict.setdefault(str(i.device), [round(psutil.disk_usage(i.device).total / 1024 ** 3, 2),
                                                      round(psutil.disk_usage(i.device).used / 1024 ** 3, 2), str(i.fstype)])
                except PermissionError:
                    disk_dict.setdefault(str(i.device), ["Нет данных", "Нет данных", "Нет данных"])
            self.Discinfo_list.emit(disk_dict)
            time.sleep(self.delay)

class CPUInfo(QtCore.QThread):
    CPUinfo_list = QtCore.Signal(list)
    def __init__(self, parent = None):
        super().__init__(parent)
        self.delay = None
    def run(self):
        if self.delay is None:
            self.delay = 1
        while True:
            CPU_list = [psutil.cpu_percent(), cpuinfo.get_cpu_info()['brand_raw']]
            self.CPUinfo_list.emit(CPU_list)
            time.sleep(self.delay)

class RamInfo(QtCore.QThread):
    RAMinfo_list = QtCore.Signal(list)
    def __init__(self, parent = None):
        super().__init__(parent)
        self.delay = None
    def run(self):
        if self.delay is None:
            self.delay = 1
        while True:
            total = f"{psutil.virtual_memory().total} байт"
            percent = psutil.virtual_memory().percent
            used = round(psutil.virtual_memory().used /1024/1024/1024, 1)
            total2 = round(psutil.virtual_memory().total/1024/1024/1024, 1)
            Ram_list = [total, percent, used, total2]
            self.RAMinfo_list.emit(Ram_list)
            time.sleep(self.delay)

class UpdateGraf(QtCore.QThread):
    Signal = QtCore.Signal(str)
    def __init__(self, parent = None):
        super().__init__(parent)
        self.delay = 1
    def run(self):
        while True:
            self.Signal.emit("Start")
            time.sleep(self.delay)


class ProcessesInfo(QtCore.QThread):
    process_info = QtCore.Signal(list)
    def __init__(self, parent= None):
        super().__init__(parent)
        self.delay = 1

    def run(self):
        while True:
            process_list = []
            for i in psutil.process_iter():
                a = i.name()
                b = i.status()
                c = round(i.cpu_percent(), 1)
                d = round(i.memory_percent(), 1)
                process_list.append([a, b, c, d])

            self.process_info.emit(process_list)
            time.sleep(self.delay)


class UpdateGraf(QtCore.QThread):
    Signal = QtCore.Signal(str)
    def __init__(self, parent = None):
        super().__init__(parent)
        self.delay = 1
    def run(self):
        while True:
            self.Signal.emit("Start")
            time.sleep(self.delay)


class SlujbaInfo(QtCore.QThread):
    slug_info = QtCore.Signal(list)
    def __init__(self, parent= None):
        super().__init__(parent)
        self.delay = 1

    def run(self):
        while True:
            slug_list = []
            for i in psutil.win_service_iter():
                a = i.name()
                b = i.status()
                c = i.display_name()
                d = i.start_type()
                if d == "manual":
                    d = "Ручной"
                else:
                    d = "Автоматический"
                slug_list.append([a, c, b, d])

            self.slug_info.emit(slug_list)
            time.sleep(self.delay)

class Tasks(QtCore.QThread):
    task_info = QtCore.Signal
    def __init__(self, parent = None):
        super().__init__(parent)

    def run(self):
        while True:
            tasks_list = []
            pythoncom.CoInitialize()
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            folders = [scheduler.GetFolder('\\')]
            while folders:
                folder = folders.pop(0)
                folders += list(folder.GetFolders(0))
                for task in folder.GetTasks(0):
                    a = task.Path
                    # b = Tasks.TASK_STATE[task.State]
                    c = str(task.NextRunTime)
                    tasks_list.append([a, c])
            print(tasks_list)
            self.task_info.emit(tasks_list)








