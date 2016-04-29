import os

from gi.repository import GObject, Gedit, GtkSource
from pyprint.ConsolePrinter import ConsolePrinter
from coalib.output.printers.LogPrinter import LogPrinter
from coalib.processes.Processing import execute_section
from coalib.settings.ConfigurationGathering import gather_configuration
from coalib.results.HiddenResult import HiddenResult
from coalib.results.RESULT_SEVERITY import RESULT_SEVERITY

from .Utils import get_mark_category, RESULT_SEVERITY_ICONS, COALA_KEY


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

    def do_activate(self):
        """
        This function is called when the view is created - it will
        be called only once in a lifetime of a view.
        """
        self.register_marks()
        self.view.get_buffer().connect("saved", lambda x: self.analyze())

    def register_marks(self):
        """
        Creates mark-attributes for all result severities.
        """
        self.view.set_show_line_marks(True)
        for name, val in RESULT_SEVERITY.str_dict.items():
            attr = GtkSource.MarkAttributes()
            attr.set_icon_name(RESULT_SEVERITY_ICONS[val])
            attr.connect("query_tooltip_markup", self.show_mark_tooltip)
            self.view.set_mark_attributes(get_mark_category(name), attr, 0)
            self.log_printer.info("Mark attribute created for", name)

    def show_mark_tooltip(self, mark_attr, mark):
        result = getattr(mark, COALA_KEY + "Result")
        return str(result.origin) + ": " + str(result.message)

    def show_result(self, result):
        """
        Takes a result and shows it in gedit's UI.

        :param result: The result to display.
        """
        document = self.view.get_buffer()

        for sourcerange in result.affected_code:

            _iter = document.get_iter_at_line(sourcerange.start.line-1)
            mark = document.create_source_mark(
                None,
                get_mark_category(result.severity),
                _iter)
            setattr(mark, COALA_KEY + "Result", result)
            self.log_printer.info("Created mark at", sourcerange.start.line)

    def analyze(self):
        """
        This function fetches the location of the file in this view
        and runs coala on it.
        """
        document = self.view.get_buffer()
        location = document.get_location()
        if location == None:
            self.log_printer.warn("coala cannot run on unsaved files")
            return

        results = CoalaViewActivatable.run_coala(location.get_path())

        document.remove_source_marks(document.get_start_iter(),
                                     document.get_end_iter())
        for section_results in results.values():
            for result in section_results:
                self.show_result(result)

    @staticmethod
    def run_coala(path):
        """
        Run coala on the file at the given path. The config file is got using
        the `find-config` option of coala.

        :param path: The path of the file to analyze.
        :return:     The result dictionary from coala.
        """
        results = {}
        log_printer = LogPrinter(ConsolePrinter())
        cwd = os.getcwd()
        try:
            os.chdir(os.path.dirname(path))
            args = ["--find-config", "--limit-files", path, '-S',
                    'autoapply=false']
            sections, local_bears, global_bears, targets = (
                # Use `lambda *args: True` so that `gather_configuration` does
                # nothing when it needs to request settings from user.
                gather_configuration(lambda *args: True,
                                     log_printer,
                                     arg_list=args))

            for section_name in sections:
                section = sections[section_name]
                if not section.is_enabled(targets):
                    continue

                section_result = execute_section(
                    section=section,
                    global_bear_list=global_bears[section_name],
                    local_bear_list=local_bears[section_name],
                    print_results=lambda *args: True,
                    log_printer=log_printer)

                results_for_section = []
                for i in 1, 2:
                    for value in section_result[i].values():
                        for result in value:
                            if isinstance(result, HiddenResult):
                                continue
                            results_for_section.append(result)
                results[section_name] = results_for_section
        except BaseException as exception:
            log_printer.log_exception(str(exception), exception)
        finally:
            os.chdir(cwd)

        return results
