#!/usr/bin/env python3
"""
Application launcher
"""
from page_app.app import app

if __name__ == "__main__":
    port = 8095
    url = "http://127.0.0.1:{0}".format(port)
    app.run(port=port, debug=False)
