import os
import sys
from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer, QProcess
from PyQt6.QtGui import QIcon
from acb.gui_acb import Ui_MainWindow
import setproctitle
from acb.utils import *



setproctitle.setproctitle('srv_main_gui')
if not os.path.isdir('logs'):
    os.mkdir('logs')
filename_log = utils_get_today_log_path()




class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def load_log_to_listview(self, p):
        self.lv_log.clear()
        if os.path.exists(p):
            bn = os.path.basename(p)
            print(f'GUI: loading log file {bn}')
            with open(p, 'r') as f:
                ll = f.readlines()
                if ll:
                    s = f'load log {bn}'
                    self.lv_log.addItem(s)
                for i in ll:
                    self.lv_log.addItem(i.strip())
        else:
            print(f'GUI: NOT detected log file {p}')



    def slot_btn_close(self):
        # user press 'X' button inside the window to close the program
        self.close()


    def slot_btn_minimize(self):
        # makes press '_' button to minimize and see desktop / terminal
        self.showMinimized()


    def _cb_api_state(self, state):
        ls_states = {
            QProcess.ProcessState.NotRunning: 'No',
            QProcess.ProcessState.Starting: 'Starting',
            QProcess.ProcessState.Running: 'Yes',
        }

        # this is examined by the GUI timer
        self.state_api = ls_states[state]
        if state == QProcess.ProcessState.Starting:
            print("API: starting")



    def _cb_aws_state(self, state):
        ls_states = {
            QProcess.ProcessState.NotRunning: 'No',
            QProcess.ProcessState.Starting: 'Starting',
            QProcess.ProcessState.Running: 'Yes',
        }

        # this is examined by the GUI timer
        self.state_aws = ls_states[state]

        if state == QProcess.ProcessState.Starting:
            print("AWS: starting")



    # -------------------------------------------------------------------
    # main GUI timer functionality
    # shows incoming rsync-progress, local API state, local rsync state
    # -------------------------------------------------------------------

    def cb_timer_gui_100_ms(self):

        # update time
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.lbl_time.setText(now)


        # GUI show API state
        color = 'green' if self.state_api == 'Yes' else 'red'
        self.lbl_api_color.setStyleSheet(f"background-color: {color};")


        # GUI shows RSYNC state
        c = 'systemctl is-active rsync'
        rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        color = 'green' if rv.returncode == 0 else 'red'
        self.lbl_rsyncd_color.setStyleSheet(f"background-color: {color};")


        # GUI shows rsync status written in redis by local API
        s = red.get('acb:rsync_state_text')
        if s:
            s = s.decode()
        self.lbl_main.setText(s)


        # GUI shows AWS status written in redis by process
        s = red.get('acb:aws')
        if s:
            s = s.decode()
        if s == 'OK':
            self.lbl_aws.setStyleSheet(f"background-color: green;")
        elif s == 'working':
            self.lbl_aws.setStyleSheet(f"background-color: yellow;")
        else:
            self.lbl_aws.setStyleSheet(f"background-color: red;")


        # GUI shows logs status written in redis by process
        if red.exists(RD_ACB_RSYNC_FLAG_LOG):
            print('GUI: refreshing log list view')
            red.delete(RD_ACB_RSYNC_FLAG_LOG)
            p = utils_get_today_log_path()
            self.load_log_to_listview(p)



    # -------------
    # GUI layout
    # -------------

    def __init__(self):

        # create buttons, window size and timer
        super().__init__()
        self.setupUi(self)
        self.btn_close.clicked.connect(self.slot_btn_close)
        self.btn_minimize.clicked.connect(self.slot_btn_minimize)
        self.setWindowTitle('⬆️ Rsync Transfer ACB')
        self.setWindowIcon(QIcon('./acb/icon_lobster.png'))
        if utils_is_rpi():
            self.showFullScreen()
        else:
            _wx = 100
            _wy = 100
            _ww = 500
            _wh = 400
            self.setGeometry(_wx, _wy, _ww, _wh)
        self.timer_gui = QTimer()
        self.timer_gui.timeout.connect(self.cb_timer_gui_100_ms)
        self.timer_gui.start(100)
        self.lbl_version.setText('v. 0.7')
        ip_wlan0 = utils_get_ip_address('wlan0')
        ip_wlan1 = utils_get_ip_address('wlan1')
        s_ip = ''
        if ip_wlan0 != 'N/A':
            s_ip += f'wlo0 {ip_wlan0} '
        if ip_wlan1 != 'N/A':
            s_ip += f'wlo1 {ip_wlan1}'
        self.lbl_ip.setText(s_ip)
        print(s_ip)


        # prevent the label from growing much
        wg = self.geometry()
        _w = int(wg.width() / 2)
        self.lbl_main.setMaximumWidth(_w)
        self.lbl_main.setMinimumWidth(_w)



        # variable to monitor the state of the API
        self.state_api = 'Not running'
        self.state_aws = 'Not running'


        # ------------------------------------
        # start API thread from this GUI
        # ------------------------------------
        self.proc_api = QProcess()
        self.proc_api.setProcessChannelMode(QProcess.ProcessChannelMode.ForwardedChannels)
        self.proc_api.stateChanged.connect(self._cb_api_state)
        self.proc_api.start("uvicorn", ['srv_main_api:app', '--host', '0.0.0.0'])
        self.proc_aws = QProcess()
        self.proc_aws.setProcessChannelMode(QProcess.ProcessChannelMode.ForwardedChannels)
        self.proc_aws.stateChanged.connect(self._cb_aws_state)
        self.proc_aws.start("python3", ["aws.py"])


        # loading the log file to GUI upon boot
        self.load_log_to_listview(filename_log)






if __name__ == '__main__':
    print('os_wd', os.getcwd())
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
