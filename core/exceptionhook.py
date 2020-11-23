import os
import sys
import time
import traceback

from PyQt5 import QtWidgets, QtCore


def exception_log_and_kill_hook(exctype, value, tb, joan_module, exception_event):
    # trigger the event to transition the module to ERROR state
    exception_event.set()

    print('exception occurred in run process of the %s module' % str(joan_module))
    traceback.print_exception(exctype, value, tb)

    #  save log
    try:
        log_dir = os.path.join(os.getcwd(), 'crash_logs')
        if not os.path.isdir(os.path.dirname(log_dir)):
            os.makedirs(log_dir)

        file_path = log_dir + os.path.sep + str(joan_module).replace(' ', '_') + '_' + time.strftime('%d-%m-%Y_%Hh%Mm%Ss') + '.txt'
        with open(file_path, 'a') as file:
            traceback.print_exception(exctype, value, tb, file=file)

        dialog_message = "An error occurred in the %s module. A log has been saved at %s." % (str(joan_module), file_path)
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
