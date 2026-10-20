import os
import sys
import redis
from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from acb_ss_gui.gui_acb import Ui_MainWindow
import setproctitle
from acb_ss_gui.ss_redis import *
from acb_ss_gui.utils import *



setproctitle.setproctitle('acb_ss_gui')
if not os.path.isdir('logs'):
    os.mkdir('logs')
filename_log = utils_get_today_log_path()
r = redis.Redis('localhost', port=6379, decode_responses=True)
SOFTWARE_VERSION = 'v0.7'




class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def load_log_to_listview(self, p):
        self.lv_log.clear()
        if os.path.exists(p):
            bn = os.path.basename(p)
            print(f'GUI: loading log file {bn}')
            with open(p, 'r') as f:
                ll = f.readlines()
                if ll:
                    self.lv_log.addItem(f'loaded log file')
                    self.lv_log.addItem(f'{bn}')
                for i in ll:
                    self.lv_log.addItem(i.strip())
        else:
            print(f'GUI: NOT loading log file {p} to view')



    def slot_btn_close(self):
        # user press 'X' button inside the window to close the program
        self.close()


    def slot_btn_minimize(self):
        # makes press '_' button to minimize and see desktop / terminal
        self.showMinimized()




    # -------------------------------------------------------------------
    # main GUI timer functionality
    # -------------------------------------------------------------------

    def cb_timer_gui_100_ms(self):

        # display time
        now = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
        self.lbl_time.setText(now)

        state = r.get(RD_ACB_SS_GUI_STATE) or 'ready'
        if state not in ('ready', 'upload'):
            self.lbl_main.setText(f'error state {state}')
            return
        s = state
        if state == 'upload':
            p = r.get(RD_ACB_SS_GUI_UPLOAD_PROGRESS) or '0'
            f = r.get(RD_ACB_SS_GUI_UPLOAD_FILENAME) or 'unknown'
            bn_f = os.path.basename(str(f))
            d = r.get(RD_ACB_SS_GUI_UPLOAD_DDH) or 'ddh_x'
            s = f'upload\n{bn_f}\n{p} %\nto {d}'
        self.lbl_main.setText(s)







    # -------------
    # GUI layout
    # -------------

    def __init__(self):

        # create buttons, window size and timer
        super().__init__()
        self.setupUi(self)
        self.btn_close.clicked.connect(self.slot_btn_close)
        self.btn_minimize.clicked.connect(self.slot_btn_minimize)
        self.setWindowTitle('⬆️ ACB SS GUI')
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
        self.lbl_version.setText(SOFTWARE_VERSION)
        ip0 = utils_get_my_interface_ip_address()
        ip1 = utils_get_my_interface_starlink_ip_address()
        s_ip = f'{ip0} / {ip1}'
        self.lbl_ip.setText(s_ip)
        print('local interfaces IP =', s_ip)


        # loading the log file to GUI upon boot
        self.load_log_to_listview(filename_log)

        # initialize main label
        self.lbl_main.setText('')






if __name__ == '__main__':
    print('os_wd', os.getcwd())
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
