
from PySide6 import QtWidgets, QtGui, QtCore
import psutil
import cpuinfo

from dispet_form import Ui_MainWindow
from Classes import Canvas
from Threads import CPUInfo, RamInfo, DisksInfo, UpdateGraf, ProcessesInfo, SlujbaInfo, Tasks

class Window(QtWidgets.QMainWindow):
    def __init__(self, parent= None):
        super().__init__(parent)
        self.startThreads()
        self.Window = Ui_MainWindow()
        self.Window.setupUi(self)
        self.CPUGraph()
        self.initSignals()



        self.group = QtGui.QActionGroup(self)
        self.group.addAction(self.Window.actionSlow)
        self.group.addAction(self.Window.actionMedium)
        self.group.addAction(self.Window.actionFast)

        self.Window.labelCPU.installEventFilter(self)
        self.message= QtWidgets.QMessageBox(self, "", "")


    def startThreads(self):
        self.discinfo = DisksInfo()
        self.cpuinfo = CPUInfo()
        self.raminfo = RamInfo()
        self.update = UpdateGraf()
        self.processes = ProcessesInfo()
        self.sluj = SlujbaInfo()
        self.tasks = Tasks()

        self.discinfo.start()
        self.cpuinfo.start()
        self.raminfo.start()
        self.update.start()
        self.processes.start()
        self.sluj.start()
        self.tasks.start()

    def initSignals(self):
        self.Window.actionSlow.changed.connect(self.speed)
        self.Window.actionMedium.changed.connect(self.speed)
        self.Window.actionFast.changed.connect(self.speed)
        self.cpuinfo.CPUinfo_list.connect(self.cpu_view)
        self.raminfo.RAMinfo_list.connect(self.ram_view)
        self.discinfo.Discinfo_list.connect(self.disks_view)
        self.update.Signal.connect(self.update_plot)
        self.processes.process_info.connect(self.processes_view)
        self.sluj.slug_info.connect(self.slujbi_view)
        self.tasks.task_info.connect(self.tasks_view)


    def CPUGraph(self):
        """
        Функция для отображения графика работы CPU.
        Немножко не угадал с размером виджета, не видны значения оси абцисс (секунды)
        По-видимому, проблему можно решить только полной переверсткой всей формы
        :return:
        """
        self.matplot = Canvas()
        self.matplot.setStyleSheet(u"background-color: rgb(165, 255, 6);")
        self.lat = QtWidgets.QVBoxLayout(self.Window.widgetGraph)
        self.lat.addWidget(self.matplot)
        n_data = 60
        self.xdata = list(range(n_data))
        self.xdata = self.xdata[::-1]
        self.ydata = [100 for i in range(n_data)]
        self.update_plot()


    def update_plot(self):
        """
        Обновление значений на графике CPU
        :return:
        """
        self.matplot.axis.clear()
        self.ydata = self.ydata[1:] + [psutil.cpu_percent()]
        self.matplot.axis.plot(self.xdata, self.ydata, 'r')
        self.matplot.canvas.draw()

    def cpu_view(self, CPUinfo_list):
        """
        Функция отображения данных о процессоре
        :param CPUinfo_list: list
        :return:
        """
        cpu_list = CPUinfo_list
        self.Window.labelCPU.setText(cpu_list[1])
        self.Window.progressBarCPU.setValue(cpu_list[0])
        self.Window.lcdNumberCPU.display(cpu_list[0])

    def ram_view(self, raminfo_list):
        """
        Функция отображения данных об оперативной памяти
        :param raminfo_list:
        :return:
        """
        ram_list = raminfo_list
        self.Window.labelRAM.setText(ram_list[0])
        self.Window.progressBarRAM.setValue(ram_list[1])
        self.Window.lcdNumberRAM.display(ram_list[1])
        self.Window.progressBarRAM2.setValue(ram_list[1])
        self.Window.progressBarRAM2.setFormat(f"{ram_list[2]}ГБ/{ram_list[3]}ГБ")

    def disks_view(self, disks_info):
        """
        Функция отображения данных о логических дисках
        :param disks_info:
        :return:
        """
        disks_dict = disks_info
        self.treeModel = QtGui.QStandardItemModel()
        self.treeModel.setHorizontalHeaderLabels(["Диск", "Информация"])
        self.Window.treeViewDisc.setModel(self.treeModel)
        self.Window.treeViewDisc.header().resizeSection(0, 200)
        self.Window.treeViewDisc.expandAll()
        for disk in disks_dict:
            itemDisk = QtGui.QStandardItem(disk)
            self.treeModel.appendRow(itemDisk)
            format_disk = QtGui.QStandardItem('Формат:')
            itemDisk.appendRow(format_disk)
            itemDisk.setChild(0,1, QtGui.QStandardItem(disks_dict[disk][2]))
            itemTotal = QtGui.QStandardItem('Общий объем памяти:')
            itemDisk.appendRow(itemTotal)
            itemDisk.setChild(1, 1, QtGui.QStandardItem(str(disks_dict[disk][0])))
            itemUsed = QtGui.QStandardItem('Занятый объем памяти:')
            itemDisk.appendRow(itemUsed)
            itemDisk.setChild(2, 1, QtGui.QStandardItem(str(disks_dict[disk][1])))

    def speed(self):
        """
        Изменение скорости обновления данных (СPU and RAM only)
        :return:
        """
        if self.Window.actionFast.isChecked():
            self.cpuinfo.delay = 1
            self.raminfo.delay = 1
            self.update.delay = 1
        elif self.Window.actionMedium.isChecked():
            self.cpuinfo.delay = 3
            self.raminfo.delay = 3
            self.update.delay = 3
        elif self.Window.actionSlow.isChecked():
            self.cpuinfo.delay = 7
            self.raminfo.delay = 7
            self.update.delay = 7


    def processes_view(self, process_list):
        """
        Отображения текущих процессов
        :param process_list:
        :return:
        """
        self.modelp = QtGui.QStandardItemModel()
        for i in process_list:
            self.modelp.appendRow([QtGui.QStandardItem(str(value)) for value in i])
        self.modelp.setHorizontalHeaderLabels(["Имя", "Статус", "Загрузка ЦПУ(%)", "Нагрузка RAM(%)"])

        self.Window.tableViewProc.setModel(self.modelp)

    def slujbi_view(self, slug_list):
        """
        Отображение служб
        :param slug_list:
        :return:
        """
        slug_list = slug_list
        self.modelS = QtGui.QStandardItemModel()
        for i in slug_list:
            self.modelS.appendRow([QtGui.QStandardItem(str(value)) for value in i])
        self.modelS.setHorizontalHeaderLabels(["Имя","Описание","Состояние","Тип запуска"])

        self.Window.tableViewProcSlujbi.setModel(self.modelS)


    def tasks_view(self, task_list): #fixme Не работает на 64x
        """
        Отображение задач
        :param task_list:
        :return:
        """
        task_list = task_list
        self.modelT = QtGui.QStandardItemModel()
        for i in task_list:
            self.modelT.appendRow([QtGui.QStandardItem(str(value)) for value in i])
        self.modelT.setHorizontalHeaderLabels(["Расположение","Статус","Следующий запуск"])

        self.Window.tableViewProcTasks.setModel(self.modelT)
        self.Window.tableViewProcTasks.setWordWrap(True)


    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if watched == self.Window.labelCPU and event.type() == QtCore.QEvent.Type.MouseButtonPress:
            cpu_dict = cpuinfo.get_cpu_info()
            self.message.setText(f"Brand_raw: {cpu_dict['brand_raw']}\nArch_string_raw: {cpu_dict['arch_string_raw']}\n"
                                 f"Arch: {cpu_dict['arch']}\nActual_friendly: {cpu_dict['hz_actual_friendly']}")
            self.message.setWindowTitle("Информация о процессоре")
            self.message.show()



if __name__ == "__main__":
    app = QtWidgets.QApplication()

    window = Window()
    window.show()

    app.exec()