import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import pathlib
import os
import numpy as np
from dbesg import SmithWilson, NelsonSiegel
from datetime import datetime
import logging
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 환경설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
PATH = pathlib.Path(__file__).parent.absolute()
if not any([s == 'img' for s in os.listdir('.')]): os.mkdir('img')
if not any([s == 'result' for s in os.listdir('.')]): os.mkdir('result')
if not any([s == 'data' for s in os.listdir('.')]): os.mkdir('data')

# set logger
logging.root.setLevel(logging.ERROR)
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

        self.model.addItem("SW")
        self.model.addItem("NS")

        self.btn_run.clicked.connect(self.run)
        self.btn_save.clicked.connect(self.save)
        self.btn_crawling.clicked.connect(self.crawling)
        self.btn_loadfile.clicked.connect(self.load_file)
        self.model.currentTextChanged.connect(self.ltfr_enabled)

        self.spot = None
        self.forward = None

        fig, ax = plt.subplots(2, 1, figsize=(4, 4))
        plt.savefig('img/tmp.png')
        img_spot = QPixmap()
        img_spot.load('img/tmp.png')
        self.img_spot.setPixmap(img_spot)

    def ltfr_enabled(self):
        if self.model.currentText() == "NS":
            self.ltfr.setEnabled(False)
        elif self.model.currentText() == "SW":
            self.ltfr.setEnabled(True)
        else:
            raise Exception("model selection error")

    def load_file(self):
        # 파일 불러오기
        fname = QFileDialog.getOpenFileName(self, '파일 열기', 'data')[0]
        rf_interest_rate = pd.read_excel(fname).set_index('일자')

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
        self.yr1.setValue(float(self.data.item(row, 0).text()))
        self.yr3.setValue(float(self.data.item(row, 1).text()))
        self.yr5.setValue(float(self.data.item(row, 2).text()))
        self.yr10.setValue(float(self.data.item(row, 3).text()))
        self.yr20.setValue(float(self.data.item(row, 4).text()))
        self.yr30.setValue(float(self.data.item(row, 5).text()))

    def crawling(self):
        os.system("python kofiabond.py")

    def run(self):
        # get data
        try:
            yr1 = self.yr1.value()/100
            yr3 = self.yr3.value()/100
            yr5 = self.yr5.value()/100
            yr10 = self.yr10.value()/100
            yr20 = self.yr20.value()/100
            yr30 = self.yr30.value()/100
            ltfr = self.ltfr.value()/100
        except ValueError:
            # logging
            log_time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
            logger.error("input value type error")
            print(f"[{log_time}] input value type error")

            return

        # calculate spot, forward rate
        maturity = np.array([1, 3, 5, 10, 20, 30])
        rate = np.array([yr1, yr3, yr5, yr10, yr20, yr30])
        
        if self.model.currentText() == "SW":
            # Smith-Wilson Method
            alpha = 0.1
            sw = SmithWilson(alpha, ltfr)
            sw.set_params(maturity, rate)
            t = np.linspace(0, 100, 1201)
            self.spot = sw.spot_rate(t)
            self.forward = sw.forward_rate(t, 1)
        elif self.model.currentText() == "NS":
            # Nelson-Siegel Model
            ns = NelsonSiegel()
            ns.set_params(maturity, rate)
            t = np.linspace(0, 100, 1201)
            self.spot = ns.spot_rate(t)
            self.forward = ns.forward_rate(t, 1/12)
        else:
            raise Exception("model selection error")

        # visualization
        fig, ax = plt.subplots(2, 1, figsize=(4, 4), sharex=True)
        ax[0].scatter(maturity*12, rate*100, marker='x', s=50, color='black', label='data')
        ax[0].plot(self.spot*100, label='SW', color='royalblue')
        ax[1].plot(self.forward*100, label='SW', color='tomato')
        if self.model.currentText() == "SW":
            ax[1].axhline(y=ltfr*100, linestyle='--', color='black', label=f'LTFR({ltfr*100:,.2f}%)')
        ax[0].set_title('Spot Rate')
        ax[1].set_title('Forward Rate')
        ax[0].grid(True);ax[1].grid(True)
        ax[0].legend();ax[1].legend()
        ax[0].set_ylabel('금리(%)');ax[1].set_ylabel('금리(%)')
        ax[1].set_xlabel('만기(월)')
        ax[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x:,.1f}'))
        ax[1].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x:,.1f}'))

        plt.tight_layout()
        plt.savefig('img/tmp.png')
        img_spot = QPixmap()
        img_spot.load('img/tmp.png')
        self.img_spot.setPixmap(img_spot)

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
            plt.savefig(f'{PATH}\\result\\spot&forward_{now}.png')

            # logging
            log_time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
            logger.info(f"save as \"{PATH}\\result\\forward_{now}.csv\"")
            print(f"[{log_time}] save as \"{PATH}\\result\\forward_{now}.csv\"")
            logger.info(f"save as \"{PATH}\\result\\spot_{now}.csv\"")
            print(f"[{log_time}] save as \"{PATH}\\result\\spot_{now}.csv\"")
            logger.info(f"save as \"{PATH}\\result\\spot&forward_{now}.png\"")
            print(f"[{log_time}] save as \"{PATH}\\result\\spot&forward_{now}.png\"")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DBEsgWindow()
    window.show()
    app.exec_()
