# -*- coding: utf-8 -*-
"""
    monitor.py
    ~~~~~~~~~~~~~~
    :copyright:...
"""
from flask import Flask

# 创建项目对象
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
