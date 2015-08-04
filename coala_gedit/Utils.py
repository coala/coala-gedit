"""
Holds various common functions and variables which will be useful in general
by the other classes.
"""

from coalib.results.RESULT_SEVERITY import RESULT_SEVERITY


# COALA_KEY is to specify which names for variables in gedit's plugin system
# which have been created by coala. (so that they are not confused with inbuilt
# names or names from other plugins)
COALA_KEY = "coala-gedit"


def get_mark_category(severity):
    """
    Get the mark category of the given result severity.

    :param severity:  The RESULT_SEVERITY's symbolic name or constant value.
    :return:          The mark category (string).
    :raises KeyError: When the severity provided is not in the RESULT_SEVERITY
                      enum.
    """
    if severity in RESULT_SEVERITY.str_dict.keys():
        return COALA_KEY + "." + severity
    elif severity in RESULT_SEVERITY.str_dict.values():
        return COALA_KEY + "." + RESULT_SEVERITY.reverse[severity]
    else:
        raise KeyError("Invalid result severity '{}'.".format(severity))


RESULT_SEVERITY_ICONS = {
    RESULT_SEVERITY.INFO: "dialog-information-symbolic",
    RESULT_SEVERITY.NORMAL: "dialog-warning-symbolic",
    RESULT_SEVERITY.MAJOR: "dialog-error-symbolic"}
