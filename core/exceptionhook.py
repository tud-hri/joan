import os
import sys
import time
import traceback

from PyQt5 import QtWidgets


def exception_log_and_kill_hook(exctype, value, tb, joan_module):
    print('exception occurred in ' + str(joan_module))
    traceback.print_exception(exctype, value, tb)

    dialog_message = "An error occurred in the % s module. A log has been saved." % str(joan_module)

    #  save log
    try:
        log_dir = os.getcwd() + '/crash_logs/'
        if not os.path.isdir(os.path.dirname(log_dir)):
            os.makedirs(log_dir)

        with open(log_dir + str(joan_module).replace(' ', '_') + '_' + time.strftime('%d-%m-%Y_%Hh%Mm%Ss') + '.txt', 'a') as file:
            traceback.print_exception(exctype, value, tb, file=file)
    except:  # if log saving fails here it's too far gone to attempt a rescue. Just give the user the opportunity to copy the error.
        dialog_message = "An error occurred in %s. \n \n WARNING: A log file could not be saved, but the stack trace can be copied from the terminal." % str(
            joan_module)

    try:
        QtWidgets.QMessageBox.critical(None, 'An error occurred', dialog_message)  # todo: this does not work, fix it
    except:  # again, if this fails at this point; just print and be done with it
        print(dialog_message)

    sys.exit(3)
