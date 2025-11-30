#!/usr/bin/env python3

"""pys-qapp-eventloop"""

import signal
import argparse
import sys
import time
from datetime import datetime
from PySide6 import QtCore, QtGui, QtWidgets


# Rewrite main1.py as a class just to exercise/reinforce our understand 

class MyApplicationEventSpy(QtCore.QObject):
  def eventFilter(self, watched, event):
    etype = event.type()
    if etype == QtCore.QEvent.Timer:
      evt_name = etype.name
      tgt_name = watched.__class__.__name__
      print(f"[{datetime.now()}] Event={evt_name}, Target={tgt_name}")
    return super().eventFilter(watched, event)


class MyApplicationTimers(QtCore.QObject):
  def __init__(self, parent=None):
    super().__init__(parent)
    self.timer1 = QtCore.QTimer(self)
    self.timer2 = QtCore.QTimer(self)
    self.timer1.timeout.connect(self.timer_1000ms)
    self.timer2.timeout.connect(self.timer_0250ms)
    self.timer1.start(1000)
    self.timer2.start(250)

  @QtCore.Slot()
  def timer_1000ms(self):
    print(f"[{datetime.now()}] (1000ms) TIMER SLOT: timer_1000ms()")

  @QtCore.Slot()
  def timer_0250ms(self):
    print(f"[{datetime.now()}] (0250ms) TIMER SLOT: timer_0250ms()")


def main():
  app = QtCore.QCoreApplication(sys.argv)
  spy = MyApplicationEventSpy()
  app.installEventFilter(spy)

  timers = MyApplicationTimers(app) # good practice so ownership is clearly communicated

  def handle_sigint(signum, frame):
    print("SIGINT received by Python signal handler: ", signum)
    app.quit()

  signal.signal(signal.SIGINT, handle_sigint)

  sys.exit(app.exec())


if __name__ == "__main__":
  main()
