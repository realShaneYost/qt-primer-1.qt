#!/usr/bin/env python3

"""
Event Loop

It helps to establish a high level understanding of the Qt event loop. This examples outlines my
understanding of this and gets me familiar with the Pyside6 documentation.

- For learning purposes, the OS layer will be ignored. Qt hides the underlying native event 
  mechanisms (select/epoll/kqueue, Windows message pump, etc) and this goes beyond most basics.

- QEvent objects are generated inside Qt for most purposes. My understanding, is that OS input
  (e.g. mouse, keyboard, windowing) is wrapped by Qt into QEvent types while pure Qt generated 
  events (e.g. timers, repaint, deferred deletes) are generated within.

- The Qt event loop detects available QEvents and dispatches them. How though and where do they go?
  Qt event loop reacts to incoming events and delivers each QEvent to the QObject it targets.

- QObjects handle these events. For example, the following sets up a custom event type. The event
  gets published to the event queue. Here is where it will be received and processed by our QObject
"""

import sys
from PySide6 import QtCore


# -------------------------------------------------------------------------------------------------
# Create our custom event ...
#
# - A new event type is registered in Qt's user-defined event range. This type I will encapsulate
#   inside the custom event class to keep classification local to the class that owns it.
#
# - I'll use a small payload to identify some attribute level data. This will be a simple string
#   that will get printed later as part of it being received by the target (QObject) as an event.
# -------------------------------------------------------------------------------------------------
class MyEvent(QtCore.QEvent):
  Type = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
  def __init__(self, payload):
    super().__init__(MyEvent.Type)
    self.payload = payload


# -------------------------------------------------------------------------------------------------
# Create a custom QObject ...
#
# - This custom QObject will be the target that we publish our custom event to. We will override
#   the event handler to print the event payload.
#
# - In addition, we signal quit so that upon next frame of event loop the application shuts down.
#   Per the docs it is important that we return true upon that happening and allow all other events
#   to be processed using the base implementation.
#
# - Originally, I was creating a nested function in main to connect to the signal aboutToQuit but
#   it kind of fits nicely here as well. Not important but wanted to reference/utilize some method
#   in the docs and aboutToQuit seemed easy.
# -------------------------------------------------------------------------------------------------
class Receiver(QtCore.QObject):
  def __init__(self, mapp):
    super().__init__()
    mapp.aboutToQuit.connect(self.callback)

  def event(self, event):
    if event.type() == MyEvent.Type:
      print(f"[recv] Received MyEvent with payload: '{event.payload}'")
      QtCore.QCoreApplication.quit()   # Stop event loop after handling
      return True
    return super().event(event)

  def callback(self):
    print(f"[recv] Callback to Receiver when app is about to quit")

# -------------------------------------------------------------------------------------------------
# Implement and setup main application ...
#
# [MyEvent] ----post----> [Qt Event Queue] ---> [Event Loop] ---> [Receiver]
# 
# 1. Create an event
# 2. Post event to application event queue
# 3. Event loop retrieves and dispatches the event to appropriate QObject (target)
# -------------------------------------------------------------------------------------------------
def main():
  mapp = QtCore.QCoreApplication(sys.argv)
  recv = Receiver(mapp)

  # Prove the main app and receiver qobject are in same event loop thread
  print(f"[main] mapp.thread(): {mapp.thread().objectName()}")
  print(f"[main] recv.thread(): {recv.thread().objectName()}")

  # Create and post a single custom event to our target (custom qobject)
  event = MyEvent("This is my custom event")
  QtCore.QCoreApplication.postEvent(recv, event)

  # Start event loop
  return sys.exit(mapp.exec())


if __name__ == "__main__":
  main()
