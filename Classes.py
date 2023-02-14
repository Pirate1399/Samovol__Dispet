from PySide6 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Canvas(QtWidgets.QWidget):
    """
    Класс для отображения графика
    работы процессора
    """
    def __init__(self, parent = None):
        super(Canvas, self).__init__(parent)
        self.delay = 1000
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.axis = self.figure.add_subplot(111) #fixme Если поставить значение 211 будет видна ось абцисс

        self.lay = QtWidgets.QVBoxLayout(self)
        self.lay.addWidget(self.canvas)