import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pathlib
import os
import numpy as np
from dbesg import SmithWilson, NelsonSiegel
from datetime import datetime
import logging

PATH = pathlib.Path(__file__).parent.absolute()

# set logger
logging.root.setLevel(logging.INFO)
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


form_class = uic.loadUiType(
    os.path.join(PATH,
    'ui', 'dbesg.ui'))[0]

class DBEsgWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btn_run.clicked.connect(self.run)
        self.btn_save.clicked.connect(self.save)

        self.spot = None
        self.forward = None

    def run(self):
        # get data
        try:
            yr1 = float(self.yr1.text())/100
            yr3 = float(self.yr3.text())/100
            yr5 = float(self.yr5.text())/100
            yr10 = float(self.yr10.text())/100
            yr20 = float(self.yr20.text())/100
            yr30 = float(self.yr30.text())/100
            ltfr = float(self.ltfr.text())/100
        except ValueError:
            # logging
            logger.error("input value type error")
            self.log.append("input value type error")

            return

        # calculate spot, forward rate
        maturity = np.array([1, 3, 5, 10, 20, 30])
        rate = np.array([yr1, yr3, yr5, yr10, yr20, yr30])
        alpha = 0.1
        sw = SmithWilson(alpha, ltfr)
        sw.set_params(maturity, rate)
        t = np.linspace(0, 100, 1201)
        self.spot = sw.spot_rate(t)
        self.forward = sw.forward_rate(t, 1)

    def save(self):
        if type(self.spot) == type(None):
            # logging
            logger.warning("there is no value to save")
            self.log.append("there is no value to save")

            return
        else:
            # export
            now = datetime.now().strftime('%Y%m%d%H%M%S')
            np.savetxt(f"{PATH}\\result\\forward_{now}.csv", self.forward, delimiter=",")
            np.savetxt(f"{PATH}\\result\\spot_{now}.csv", self.spot, delimiter=",")

            # logging
            logger.info(f"save as \"{PATH}\\result\\forward_{now}.csv\"")
            self.log.append(f"save as \"{PATH}\\result\\forward_{now}.csv\"")
            logger.info(f"save as \"{PATH}\\result\\spot_{now}.csv\"")
            self.log.append(f"save as \"{PATH}\\result\\spot_{now}.csv\"")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DBEsgWindow()
    window.show()
    app.exec_()
