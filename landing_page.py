"""
Application launcher
"""
#!/usr/bin/env python3

from PyQt5.QtGui import QIcon
from page_app.app import app
from webui import WebUI

ui = WebUI(app, debug=True)

if __name__ == "__main__":
    ui.app.setApplicationName("Landing Cute Page")
    # ui.view.showMaximized()
    ui.app.setWindowIcon(QIcon('page_app/static/img/cat.png'))
    ui.run()
