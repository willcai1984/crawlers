# -*- coding: utf-8 -*-
"""
    spider.util.py
    ~~~~~~~~~~~~~~
    :copyright:...
"""
import logging
import sys
import threading
import time
import traceback
from functools import wraps

logger = logging.getLogger(__name__)


class TimeoutException(Exception):
    """function run timeout"""


class VerifyErrorException(Exception):
    """Verify code error"""


class ThreadFunc(threading.Thread):
    def __init__(self, func, args=(), kwargs={}):
        threading.Thread.__init__(self)
        self.result = None
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self._run()
        except Exception as e:
            self.exitcode = 1
            self.exception = e
            self.exc_traceback = ''.join(traceback.format_exception(*sys.exc_info()))

    def _run(self):
        self.result = self.func(*self.args, **self.kwargs)

    def _stop(self):
        if self.isAlive():
            self._Thread__stop()


def timeout(seconds):
    def timeout_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            it = ThreadFunc(func, args, kwargs)
            it.start()
            it.join(seconds)
            if it.isAlive():
                it._stop()
                raise TimeoutException('The function %s run too long, timeout %d seconds.' % (func.__name__, seconds))
            else:
                return it.result

        return wrapper

    return timeout_decorator


def retry(attempt):
    def retry_decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):
            att = 0
            while att < attempt:
                logger.info("Try %s times start" % (att + 1))
                try:
                    return func(*args, **kw)
                except Exception as e:
                    # print e.message
                    logger.error("Try %s times meet error: %s" % ((att + 1), e), exc_info=True)
                    att += 1
            logger.info("Retry %s times,still failed" % attempt)
            return func(*args, **kw)
            # return func(*args, **kw)

        return wrapper

    return retry_decorator


if __name__ == '__main__':
    @retry(2)
    @timeout(3)
    def ttimeout(seconds):
        print("sleep %ss start" % seconds)
        time.sleep(seconds)
        print("sleep %ss end" % seconds)


    ttimeout(1)
    ttimeout(5)
