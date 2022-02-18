import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from pyupbit import WebSocketManager

class OverViewWorker(QThread):
    dataSent = pyqtSignal(float, float, str)
    def __init__(self, ticker="KRW-BTC"):
        super().__init__()
        self.ticker = ticker
        self.alive = True

    def run(self):
        wm = WebSocketManager("ticker", [f"{self.ticker}"])
        while self.alive:
            data = wm.get()
            self.dataSent.emit(float(data['trade_price']),
                               float(data['change_rate']),
                               str(data['change']))
        wm.terminate()

    def close(self):
        self.alive = False


class OverviewWidget(QWidget):
    def __init__(self, parent=None, ticker="KRW-BTC"):
        super().__init__(parent)
        uic.loadUi("resource/overview.ui", self)

        self.ticker = ticker
        self.ovw = OverViewWorker(ticker)
        self.ovw.dataSent.connect(self.fillData)
        self.ovw.start()

    def closeEvent(self, event):
        self.ovw.close()

    def fillData(self, currPrice, changeRate, change):
        self.label_1.setText(f"{currPrice:,}")
        if change == "FALL":
            changeRate =  f"-{changeRate * 100:,.2}%"
        else:
            changeRate = f"{changeRate * 100:,.2}%"
        self.label_2.setText(f"{changeRate}")

        # ----------------- 추 가 ------------------
        self.__updateStyle()
        # ------------------------------------------

    def __updateStyle(self):
        if '-' in self.label_2.text():
            self.label_1.setStyleSheet("color:blue;")
            self.label_2.setStyleSheet("background-color:blue;color:white")
        else:
            self.label_1.setStyleSheet("color:red;")
            self.label_2.setStyleSheet("background-color:red;color:white")



if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ob = OverviewWidget()
    ob.show()
    exit(app.exec_())