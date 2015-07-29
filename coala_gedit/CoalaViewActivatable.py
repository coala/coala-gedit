import os
from gi.repository import GObject, Gedit
from coalib.output.printers.ConsolePrinter import ConsolePrinter
from coalib.output.printers.LogPrinter import LogPrinter
from coalib.processes.Processing import execute_section
from coalib.settings.ConfigurationGathering import gather_configuration
from coalib.results.HiddenResult import HiddenResult


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
            args = ["--find-config", "--files=" + path]
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
                    log_printer=log_printer,
                    file_diff_dict={})

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
