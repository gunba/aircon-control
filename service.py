import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import logging
import time
from datetime import datetime
import threading
import main

class PythonService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PythonService"
    _svc_display_name_ = "Python Service"
    _svc_description_ = "Manages the air conditioner automatically"

    def __init__(self, args):
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.logger = self._setup_logging()

    def _setup_logging(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_folder = os.path.join(script_dir, "logs")
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        log_file = os.path.join(log_folder, f"aircon_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.logger.info('Service stopped')

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.logger.info('Service started')
        self.main()

    def run_main_script(self):
        main.run("192.168.50.20")

    def main(self):
        while True:
            try:
                thread = threading.Thread(target=self.run_main_script)
                thread.start()
                thread.join()
                self.logger.info("Waiting for 5 minutes...")
                time.sleep(300)  # Sleep for 5 minutes (300 seconds)
            except Exception as e:
                self.logger.error(f"An error occurred: {str(e)}")
                self.logger.info("Retrying in 1 minute...")
                time.sleep(60)  # Sleep for 1 minute before retrying

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(PythonService)
        PythonService.run()
    else:
        win32serviceutil.HandleCommandLine(PythonService)