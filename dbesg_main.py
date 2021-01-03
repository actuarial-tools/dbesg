import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pathlib
import os
import numpy as np
from dbesg import SmithWilson, NelsonSiegel
from datetime import datetime
import logging
import pandas as pd

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
        self.btn_crawling.clicked.connect(self.crawling)
        self.btn_loadfile.clicked.connect(self.load_file)

        self.spot = None
        self.forward = None

    def load_file(self):
        # 파일 불러오기
        fname = QFileDialog.getOpenFileName(self, '파일 열기', '.')[0]
        rf_interest_rate = pd.read_excel(fname).set_index('일자')
        
        # for date, row in rf_interest_rate.iterrows():
        #     for value in row:
        #         print(date, value)

        # Table로 올리기
        rows, cols = rf_interest_rate.shape
        self.data.setRowCount(rows)
        self.data.setColumnCount(cols)
        self.data.setHorizontalHeaderLabels(rf_interest_rate.columns.map(lambda x: f'{x}년'))
        self.data.setVerticalHeaderLabels(rf_interest_rate.index.map(lambda x: x.strftime('%Y.%m.%d')))
        for r in range(rows):
            for c in range(cols):
                self.data.setItem(r, c, QTableWidgetItem(f"{round(rf_interest_rate.iloc[r, c], 3)}"))
        self.data.resizeColumnsToContents()
        self.data.cellDoubleClicked.connect(self.setData)

    def setData(self, row):
        self.yr1.setText(self.data.item(row, 0).text())
        self.yr3.setText(self.data.item(row, 1).text())
        self.yr5.setText(self.data.item(row, 2).text())
        self.yr10.setText(self.data.item(row, 3).text())
        self.yr20.setText(self.data.item(row, 4).text())
        self.yr30.setText(self.data.item(row, 5).text())

    def crawling(self):
        os.system("python kofiabond.py")

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
            log_time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
            logger.error("input value type error")
            print(f"[{log_time}] input value type error")

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

        # logging
        log_time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
        logger.info(f"run success")
        print(f"[{log_time}] run success")

    def save(self):
        if type(self.spot) == type(None):
            # logging
            log_time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
            logger.warning("there is no value to save")    
            print(f"[{log_time}] there is no value to save")

            return
        else:
            # export
            now = datetime.now().strftime('%Y%m%d%H%M%S')
            np.savetxt(f"{PATH}\\result\\forward_{now}.csv", self.forward, delimiter=",")
            np.savetxt(f"{PATH}\\result\\spot_{now}.csv", self.spot, delimiter=",")

            # logging
            log_time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
            logger.info(f"save as \"{PATH}\\result\\forward_{now}.csv\"")
            print(f"[{log_time}] save as \"{PATH}\\result\\forward_{now}.csv\"")
            logger.info(f"save as \"{PATH}\\result\\spot_{now}.csv\"")
            print(f"[{log_time}] save as \"{PATH}\\result\\spot_{now}.csv\"")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DBEsgWindow()
    window.show()
    app.exec_()
