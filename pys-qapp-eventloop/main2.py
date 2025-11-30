#!/usr/bin/env python3

"""pys-qapp-eventloop"""

import sys
from PySide6 import QtCore


# -------------------------------------------------------------------------------------------------
# I will demonstrate three core Qt behaviors:
#
# 1. Same-thread signals with the default connection type behave as direct connections. The slot is
#    invoked immediately when emit() is called, just like a normal function call.
#
# 2. QCoreApplication.quit() does NOT abort the current call stack. It only requests that the Qt
#    event loop stop AFTER the current event handler returns to the event dispatcher. I was having
#    a hard time, initially, understanding why do_stuff doesn't just return after emitting
#    finished.
#
# 3. QTimer.singleShot(0, ...) is the idiomatic way to schedule startup work inside the event loop,
#    ensuring that initialization occurs after the loop is running. This seemed to be an idiomatic
#    pattern used quite often from online systems.
#
# These behaviors are fundamental to understanding how Qt dispatches events, signals, and shutdown
# requests.
# -------------------------------------------------------------------------------------------------

class Foo(QtCore.QObject):
  # -----------------------------------------------------------------------------------------------
  # Signals declared without parameters for simplicity which seems like a nice to way to write my
  # examples. These are class attributes which happen to be signals for Foo type
  # -----------------------------------------------------------------------------------------------
  signal1 = QtCore.Signal()
  signal2 = QtCore.Signal()
  finished = QtCore.Signal()

  def __init__(self, parent=None):
    super().__init__(parent)

  # -----------------------------------------------------------------------------------------------
  # This function emits three signals in sequence. Because all objects live in the same thread,
  # each signal uses a direct connection, meaning the connected slot executes immediately before
  # emit() returns.
  # -----------------------------------------------------------------------------------------------
  def do_stuff(self):
    print("Emit signal one")
    self.signal1.emit()   # slot1 executes immediately (direct connection)

    # here's the crux of what i'm trying to understand. I now know that app.quit won't actually 
    # quit until after this event handler do_stuff returns.
    print("Emit finished")
    self.finished.emit()  # app.quit() is invoked, but it only requests exit after this handler ends

    print("Emit signal two")
    self.signal2.emit()   # slot2 executes immediately (direct connection)

  # -----------------------------------------------------------------------------------------------
  # Slots that react to signal1 and signal2.
  # -----------------------------------------------------------------------------------------------
  @QtCore.Slot()
  def slot1(self):
    print("Execute slot one")

  @QtCore.Slot()
  def slot2(self):
    print("Execute slot two")

  # -----------------------------------------------------------------------------------------------
  # This method is scheduled using QTimer.singleShot(0, ...). It executes once the event loop is
  # running, guaranteeing that all work happens inside the event delivery system.
  # -----------------------------------------------------------------------------------------------
  @QtCore.Slot()
  def start(self):
    self.do_stuff()
    print("Bye!")   # Printed before the event loop actually exits.


def main():
  # QCoreApplication provides the event loop, event dispatcher, and signal delivery system for
  # non-GUI Qt applications.
  app = QtCore.QCoreApplication(sys.argv)

  foo = Foo()

  # Because sender and receiver live in the same thread, Qt uses direct connections. Slots run
  # immediately and synchronously when signals are emitted.
  foo.signal1.connect(foo.slot1)
  foo.signal2.connect(foo.slot2)

  # When 'finished' is emitted, app.quit() requests that the event loop exit once the current event
  # handler returns. It does NOT interrupt active functions.
  foo.finished.connect(app.quit)

  # Schedule startup work to run after the event loop begins. This is the recommended Qt pattern
  # for deferring initialization until the event system is active.
  QtCore.QTimer.singleShot(0, foo.start)

  # Enter the Qt event loop. It runs until app.quit() is requested and control returns to the
  # dispatcher.
  return app.exec()


if __name__ == "__main__":
  sys.exit(main())
