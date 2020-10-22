import os
import sys
import time
import traceback

from PyQt5 import QtWidgets, QtCore


def exception_log_and_kill_hook(exctype, value, tb, joan_module):
    """
    Logs exception and kills the process
    :param exctype: Exception type from from exc_info() in process
    :param value: from exc_info() in process
    :param tb: traceback from exc_info() in process
    :param joan_module: module that had an exception, needed for log
    :return:
    """
    print('exception occurred in run process of the %s module' % str(joan_module))
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
        app = QtWidgets.QApplication(sys.argv)
        message_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, 'An error occurred', dialog_message)
        message_box.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        message_box.show()
        app.exec_()
    except:  # again, if this fails at this point; just print and be done with it
        print(dialog_message)

    sys.exit(3)
