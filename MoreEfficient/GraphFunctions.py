import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

class Graph():
    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.win = pg.GraphicsLayoutWidget(title="Bug Sim Stats")
        self.plot = self.win.addPlot(title="Universe Energy / Bug Count / Size")
        self.plot.showGrid(x=True, y=True)
        self.plot.addLegend()
        self.plot.setLabel('left', 'Value', units='Energy / Population / Radius')
        self.plot.setLabel('bottom', 'Time', units='s')

        #Makes the values go up the y axis instead of x
        self.plot.invertY(False)

        #Giving curves attributes
        self.energy_curve = self.plot.plot(pen=pg.mkPen('y', width=2), name="Energy")
        self.bugs_curve   = self.plot.plot(pen=pg.mkPen('g', width=2), name="Bug Count")
        self.radius_curve = self.plot.plot(pen=pg.mkPen('b', width=2), name="Average Radius")
        self.immortal_curve = self.plot.plot(pen=pg.mkPen('r', width=2), name="Immortal")

        #Starts Window up
        self.win.show()

        #Initialize empty data
        self.data = None

        self.lock = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)

    #Setting up the sources for the graph to access
    def set_data_sources(self, lock, data):
        self.lock = lock
        self.data = data

    def update_plot(self):
        if self.lock is None or self.data is None:
            return
        with self.lock:
            # assingns data to simple varaibels to make it easier to type
            t = self.data["time"]
            e = self.data["energy"]
            b = self.data["bugCount"]
            r = self.data["radius_avg"]
            i = self.data["immortals"]

            if len(t) == 0:
                return

            # normalize and plot
            max_energy = max(e) if max(e) != 0 else 1
            max_bugs = max(b) if max(b) != 0 else 1
            max_radius = max(r) if max(r) != 0 else 1
            max_immortal = max(i) if max(i) != 0 else 1

            # Scales the other types of data with time that way it doesnt look too small when energy is too high
            self.energy_curve.setData(t, [v / max_energy for v in e])
            self.bugs_curve.setData(t, [v / max_bugs for v in b])
            self.radius_curve.setData(t, [v / max_radius for v in r])
            self.immortal_curve.setData(t, [v / max_immortal for v in i])

            if t[-1] > 20:
                self.plot.setXRange(t[-1] - 20, t[-1])
            else:
                self.plot.setXRange(0, 20)
            self.plot.enableAutoRange('y', True)

    def run(self):
        self.app.exec()