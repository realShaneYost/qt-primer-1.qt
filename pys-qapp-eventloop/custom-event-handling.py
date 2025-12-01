#!/usr/bin/env python3

"""pys-qapp-eventloop"""

import sys
from PySide6 import QtCore, QtWidgets


# This example shows how to define, post and handle a custom QEvent within Qt's event-driven 
# architecture. The key concepts I want to hit on here are ...
#
# 1. Custom QEvent Type
#     
# A new event type is registered (allocated) in Qt's user-defined event range. This type I've 
# encapsulated inside the custom event class to keep classification local to the class that owns
# it.
#
# 2. Post Events
# 
# The widget uses the postEvent method to enqueue the custom event into the global event queue.
# This is asynchronous and respects the normal event dispatch cycle.
#
# 3. Event Handling
#
# The widget overrides the event() method to intercept our custom event and handle it. It still
# delegates all other events to the base implementation of event()


class MyCustomEvent(QtCore.QEvent):
  """
  Custom application-level event carrying a simple string payload. I set a TYPE constant that ID's
  this event in the global QEvent::Type namespace
  """
  TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

  def __init__(self, payload):
    super().__init__(MyCustomEvent.TYPE)
    self.payload = payload


class MyWidget(QtWidgets.QWidget):
  def __init__(self, parent=None):
    super().__init__(parent)

    # Button that will trigger posting a custom event.
    self.button = QtWidgets.QPushButton("Post custom event")
    layout = QtWidgets.QVBoxLayout(self)
    layout.addWidget(self.button)

    # Connect a QPushButton signal to a slot that posts the custom event.
    self.button.clicked.connect(self.on_button_clicked)

  @QtCore.Slot()
  def on_button_clicked(self):
    # Create a custom event instance with a payload.
    the_event = MyCustomEvent("hello from custom event")

    # Post the event using the core event system API. This will enqueue the event to Qt's global
    # event queue.
    QtCore.QCoreApplication.postEvent(self, the_event)

  def event(self, event):
    """
    Intercepts events before they are routed to specialized handlers so that we can handle our 
    custom type. Defer all others to base implementation of event processing.
    """
    if event.type() == MyCustomEvent.TYPE:
      print(f"Received custom event with payload: {event.payload}")
      return True  # Indicate that the event was fully handled (docs say to do this).
    return super().event(event)


def main():
  # QApplication owns the global event loop and outlives all widgets.
  app = QtWidgets.QApplication(sys.argv)
  win = MyWidget()
  win.show()
  sys.exit(app.exec())


if __name__ == "__main__":
  main()

