import sys
import time
import pyupbit
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTableWidgetItem, QProgressBar
# ----------------- 수 정 ------------------
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation
# ------------------------------------------

class OrderbookWorker(QThread):
    dataSent = pyqtSignal(list)

    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.alive = True

    def run(self):
        while self.alive:
            orderbook = pyupbit.get_orderbook(self.ticker)
            data = orderbook['orderbook_units']
            time.sleep(0.05)
            self.dataSent.emit(data)

    def close(self):
        self.alive = False


class OrderbookWidget(QWidget):
    def __init__(self, parent =None, ticker = "KRW-BTC"):
        super().__init__(parent)
        uic.loadUi("resource/orderbook.ui", self)
        self.ticker = ticker

        # ----------------- 추 가 ------------------
        self.asksAnim = [ ]
        self.bidsAnim = [ ]
        # ------------------------------------------

        for i in range(self.tableBids.rowCount()):
            # 매도호가
            item_0 = QTableWidgetItem(str(""))
            item_0.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableAsks.setItem(i, 0, item_0)

            item_1 = QTableWidgetItem(str(""))
            item_1.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableAsks.setItem(i, 1, item_1)

            item_2 = QProgressBar(self.tableAsks)
            item_2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_2.setStyleSheet("""
                QProgressBar {background-color : rgba(0, 0, 0, 0%);border : 1}
                QProgressBar::Chunk {background-color : rgba(255, 0, 0, 50%);border : 1}
            """)
            self.tableAsks.setCellWidget(i, 2, item_2)
            # ----------------- 추 가 ------------------
            anim = QPropertyAnimation(item_2, b"value")
            anim.setDuration(200)
            self.asksAnim.append(anim)
            # ------------------------------------------

            # 매수호가
            item_0 = QTableWidgetItem(str(""))
            item_0.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableBids.setItem(i, 0, item_0)

            item_1 = QTableWidgetItem(str(""))
            item_1.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableBids.setItem(i, 1, item_1)

            item_2 = QProgressBar(self.tableBids)
            item_2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_2.setStyleSheet("""
                QProgressBar {background-color : rgba(0, 0, 0, 0%);border : 1}
                QProgressBar::Chunk {background-color : rgba(0, 255, 0, 40%);border : 1}
            """)
            self.tableBids.setCellWidget(i, 2, item_2)

        self.ow = OrderbookWorker(self.ticker)
        self.ow.dataSent.connect(self.updateData)
        self.ow.start()

    def updateData(self, data):
        data = data[:10] # resize data
        tradingBidValues = [ ]
        tradingAskValues = []
        for v in data:
            tradingBidValues.append(int(v['bid_price'] * v['bid_size']))
            tradingAskValues.append(int(v['ask_price'] * v['ask_size']))
        maxtradingValue = max(tradingBidValues + tradingAskValues)

        for i, v in enumerate(data):
            item_0 = self.tableAsks.item(9-i, 0)
            item_0.setText(f"{v['ask_price']:,}")
            item_1 = self.tableAsks.item(9-i, 1)
            item_1.setText(f"{v['ask_size']:,}")
            item_2 = self.tableAsks.cellWidget(9-i, 2)
            item_2.setRange(0, maxtradingValue)
            item_2.setFormat(f"{tradingAskValues[9-i]:,}")
            item_2.setValue(tradingAskValues[i])

        for i, v in enumerate(data):
            item_0 = self.tableBids.item(i, 0)
            item_0.setText(f"{v['bid_price']:,}")
            item_1 = self.tableBids.item(i, 1)
            item_1.setText(f"{v['bid_size']:,}")
            item_2 = self.tableBids.cellWidget(i, 2)
            item_2.setRange(0, maxtradingValue)
            item_2.setFormat(f"{tradingBidValues[i]:,}")
            item_2.setValue(tradingBidValues[i])

    def closeEvent(self, event):
        self.ow.close()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ow = OrderbookWidget()
    ow.show()
    exit(app.exec_())