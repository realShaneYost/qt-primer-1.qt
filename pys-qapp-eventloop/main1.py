#!/usr/bin/env python3

"""pys-qapp-eventloop"""

import signal
import argparse
import sys
import time
from datetime import datetime
from PySide6 import QtCore, QtGui, QtWidgets


# -------------------------------------------------------------------------------------------------
# Abstract mental model of the Qt event loop
#
# Before diving deeper into implementation details, it helps to establish a correct, high-level
# understanding of how Qt handles events.
#
# 1. For most purposes, the OS layer can be ignored. Qt hides the underlying native event
#    mechanism (select/epoll/kqueue, Windows message pump, etc.).
#
# 2. QEvent objects are generated inside Qt. OS input (mouse, keyboard, windowing) is wrapped by
#    Qt into QEvent types, but pure Qt events (timers, repaint requests, deferred deletes)
#    originate internally.
#
# 3. The Qt event loop detects available QEvents and dispatches them. It reacts to incoming events
#    and delivers each QEvent to the QObject it targets.
#
# 4. QObjects handle these events. For example, QTimer receives a QEvent::Timer and responds by
#    emitting the timeout() signal.
# -------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------
# EventSpy
#
# To observe Qt’s event flow, I can create an event filter and install it on a specific QObject.
# Since I have two timers I don't want to install twice so I'll just install on our QApplication.
# -------------------------------------------------------------------------------------------------
class EventSpy(QtCore.QObject):
  def eventFilter(self, watched, event):
    etype = event.type()
    if etype == QtCore.QEvent.Timer:
      evt_name = etype.name
      tgt_name = watched.__class__.__name__
      print(f"[{datetime.now()}] Event={evt_name}, Target={tgt_name}")
    return super().eventFilter(watched, event)


# -------------------------------------------------------------------------------------------------
# Slot (callback)
# Typical slot to show the end-to-end behavior.
# -------------------------------------------------------------------------------------------------
def print_time_1000ms():
  print(f"[{datetime.now()}] (1000ms) TIMER SLOT: print_time_1000ms()")


# -------------------------------------------------------------------------------------------------
# Slot (callback)
# Typical slot to show the end-to-end behavior.
# -------------------------------------------------------------------------------------------------
def print_time_0250ms():
  print(f"[{datetime.now()}] (0250ms) TIMER SLOT: print_time_0250ms()")


# -------------------------------------------------------------------------------------------------
# Slot (callback)
# The event loop runs in the main thread. If I block that thread (such as here) then no events are
# processed (i.e. no QEvent::Timer, no repaint, no input). When the block ends, things catch up.
# -------------------------------------------------------------------------------------------------
def bad_print_time():
  print(f"[{datetime.now()}] TIMER SLOT: entering print_time()")
  time.sleep(5)
  print(f"[{datetime.now()}] TIMER SLOT: leaving print_time()")


# -------------------------------------------------------------------------------------------------
# Main application entry point
# -------------------------------------------------------------------------------------------------
def main():
  app = QtCore.QCoreApplication(sys.argv)
  spy = EventSpy()
  app.installEventFilter(spy)

  # Connect timeout signal to slot and register repeating timers with the event loop.
  timer1 = QtCore.QTimer()
  timer1.timeout.connect(print_time_1000ms)
  timer1.start(1000)  # Register a 1000 ms repeating timer.

  timer2 = QtCore.QTimer()
  timer2.timeout.connect(print_time_0250ms)
  timer2.start(250)   # Register a 250 ms repeating timer.

  # Ctrl-C sends SIGINT. Python receives SIGINT, but Qt's C++ event loop will not automatically
  # stop just because the signal arrived. I install a SIGINT handler that explicitly asks the
  # Qt event loop to quit, so Ctrl-C cleanly exits this program.
  def handle_sigint(signum, frame):
    print("SIGINT received in Python signal handler:", signum)
    app.quit()

  signal.signal(signal.SIGINT, handle_sigint)

  # Start the Qt event loop and ensure the event loop's exit code is returned to the shell.
  sys.exit(app.exec())


if __name__ == "__main__":
  main()

