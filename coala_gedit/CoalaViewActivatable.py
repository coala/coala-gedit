from gi.repository import GObject, Gedit
from coalib.output.printers.ConsolePrinter import ConsolePrinter
from coalib.output.printers.LogPrinter import LogPrinter


class CoalaViewActivatable(GObject.Object, Gedit.ViewActivatable):
    """
    A class inherited from Gedit.ViewActivatable - it gets created for every
    gedit view. This class has a property `view` which is the Gedit.View that
    the class is related to. From the Gedit.View, the Gedit.Document associated
    to it can be got using `view.get_buffer()`.
    """
    __gtype_name__ = "CoalaViewActivatable"

    view = GObject.Property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)
        self.log_printer = LogPrinter(ConsolePrinter())
