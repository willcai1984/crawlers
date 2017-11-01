# -*- coding: utf-8 -*-
"""
    main.py
    ~~~~~~~~~~~~~~
    :copyright:...
"""
import json
import os
import sys
import logging.config
from spider.tender_monitor import TenderMonitor

user_dicts = [{"name": "will", "id": "o76g9waXJGhxjdTP5bt-zG1vXT54"},
              {"name": "yoyii", "id": "o76g9wcVxV2_dYqBvw0EDwYWa5dQ"}]
# syspath为运行这个py去查找的所有py路径，第一个为本程序运行路径 __main__.py
# ['/home/qjdchina.com/node-server/crawlers-node/server/api/py3',
# '/usr/local/lib/python36.zip',
# '/usr/local/lib/python3.6',
# '/usr/local/lib/python3.6/lib-dynload',
#  '/usr/local/lib/python3.6/site-packages']
os.chdir(sys.path[0])
current_path = os.getcwd()

if __name__ == '__main__':
    with open(sys.argv[1]) as f_o:
        f_r = f_o.read()
    config = json.loads(f_r)
    # 处理logfile
    logging.config.fileConfig(config.get("log"), disable_existing_loggers=True)
    t = TenderMonitor(config)
    is_new = t.process_tender_zj()
    if is_new:
        result = t.notices_mail()
    sys.exit(0)
