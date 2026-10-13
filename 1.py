import sys

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView


app = QApplication(sys.argv)

browser = QWebEngineView()

browser.setUrl(
    QUrl("https://rsts.org.cn/")
)

browser.resize(1200, 800)
browser.setWindowTitle("RSTS")
browser.show()

sys.exit(app.exec())