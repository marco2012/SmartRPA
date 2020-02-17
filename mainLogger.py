# https://docs.microsoft.com/en-us/WINDOWS/win32/api/
from sys import exit
from time import sleep
import errno
import os
from csv import writer
from datetime import datetime
from threading import Thread
from utils import GUI
from utils import consumerServer
from utils.consumerServer import HEADER
from utils.utils import WINDOWS,MAC,LINUX
from modules import systemEvents
from modules import officeEvents
from modules import clipboardEvents

#  this method is called by GUI when the user presses "start logger" button
def startLogger(systemLoggerFilesFolder,
                systemLoggerPrograms,
                systemLoggerClipboard,
                systemLoggerHotkeys,
                systemLoggerUSB,
                systemLoggerEvents,
                officeFilename,
                officeExcel,
                officeWord,
                officePowerpoint,
                officeOutlook,
                browserChrome,
                browserFirefox,
                browserEdge,
                browserOpera,
                ):
    try:  # create the threads as daemons so they are closed when main ends

        # ************
        # main logging server
        # ************
        createLogFile()
        t0 = Thread(target=consumerServer.runServer)
        t0.daemon = True
        t0.start()

        # ************
        # system logger
        # ************

        if systemLoggerFilesFolder:
            t1 = Thread(target=systemEvents.watchFolder)
            t1.daemon = True
            t1.start()

            if WINDOWS:
                t2 = Thread(target=systemEvents.watchRecentsFolderWin)
                t2.daemon = True
                t2.start()

                # maybe it consumes too much memory
                t9 = Thread(target=systemEvents.detectSelectedFilesInExplorer)
                t9.daemon = True
                t9.start()

                # t4=Thread(target=printerLogger)
                # t4.daemon = True
                # t4.start()

        if systemLoggerPrograms:
            if WINDOWS:
                t3 = Thread(target=systemEvents.logProcessesWin)
                t3.daemon = True
                t3.start()
            if MAC:
                t12 = Thread(target=systemEvents.logProcessesMac)
                t12.daemon = True
                t12.start()

        if systemLoggerClipboard:
            t4 = Thread(target=clipboardEvents.logClipboard)
            t4.daemon = True
            t4.start()

        if systemLoggerHotkeys and WINDOWS:
            t10 = Thread(target=systemEvents.logHotkeys)
            t10.daemon = True
            t10.start()

        if systemLoggerUSB and WINDOWS:
            t11 = Thread(target=systemEvents.logUSBDrives)
            t11.daemon = True
            t11.start()

        if systemLoggerEvents:
            pass

        # ************
        # office logger
        # ************

        if officeExcel and WINDOWS:
            t5 = Thread(target=officeEvents.excelEvents)
            t5.daemon = True
            t5.start()

        if officeWord and WINDOWS:
            t6 = Thread(target=officeEvents.wordEvents)
            t6.daemon = True
            t6.start()

        if officePowerpoint and WINDOWS:
            t7 = Thread(target=officeEvents.powerpointEvents)
            t7.daemon = True
            t7.start()

        if officeOutlook and WINDOWS:
            t8 = Thread(target=officeEvents.outlookEvents)
            t8.daemon = True
            t8.start()

        # ************
        # browser logger
        # ************

        if browserChrome:
            consumerServer.LOG_CHROME = True

        if browserFirefox:
            consumerServer.LOG_FIREFOX = True

        if browserEdge:
            consumerServer.LOG_EDGE = True

        if browserOpera:
            consumerServer.LOG_OPERA = True

        print("[mainLogger] Selected threads activated")

        while 1:  # keep main active
            # sleep(1)
            pass

    except (KeyboardInterrupt, SystemExit):
        print("Closing threads and exiting...")
        exit(0)


# used by main, creates new log file with the current timestamp in /logs directory at the root of the project.
def createLogFile():
    current_directory = os.getcwd()
    # logs are saved in logs/ direcgory
    logs_directory = os.path.join(current_directory, 'logs/')
    filenameWithTimestamp = logs_directory + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.csv'  # use current timestamp as filename
    consumerServer.filename = filenameWithTimestamp  # filename to use in current session until the 'stop' button is pressed. must be set here because the ilename uses the current timestamp and it must remain the same during the whole session
    if not os.path.exists(logs_directory):
        try:
            os.makedirs(logs_directory)
            print(f"Created directory {logs_directory}")
        except OSError as exc:  # Guard against race condition
            print(f"Could not create directory {logs_directory}")
            if exc.errno != errno.EEXIST:
                raise

    # create HEADER
    with open(consumerServer.filename, 'a', newline='') as out_file:
        f = writer(out_file)
        f.writerow(HEADER)


if __name__ == "__main__":
    #  launch gui
    GUI.buildGUI()
