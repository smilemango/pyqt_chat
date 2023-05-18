import sys
import time
from socket import socket, AF_INET, SOCK_STREAM

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QLabel, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget, QApplication

class RecvThread(QThread):
    recv_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.sock = None

    def set_sock(self, sock):
        self.sock = sock

    @pyqtSlot()
    def run(self) -> None:
        while True:
            recv_data = self.sock.recv(1024)
            recv_data = recv_data.decode('utf-8')
            self.recv_signal.emit(recv_data)

class SendThread(QThread):

    def __init__(self):
        super().__init__()
        self.sock = None
        self.msg = None

    def set_sock(self, sock):
        self.sock = sock

    def push_message(self, msg):
        self.msg = msg

    @pyqtSlot()
    def run(self) -> None:
        while True:
            time.sleep(0.01)
            if self.msg is not None:
                self.sock.send(self.msg.encode('utf-8'))
                self.msg = None



class MainWindow(QMainWindow):
    port = 20080

    def __init__(self):
        super().__init__()

        self.setWindowTitle('PyQt5 client')

        self.lbl_title = QLabel('Messages:')
        self.te_messages = QTextEdit()
        self.te_messages.setAcceptRichText(False)
        self.te_messages.setReadOnly(True)

        self.le_input = QLineEdit()
        self.le_input.returnPressed.connect(self.send_msg)
        self.btn_send = QPushButton('Send')
        self.btn_send.pressed.connect(self.send_msg)

        layout = QVBoxLayout()
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.te_messages)
        layout.addWidget(self.le_input)
        layout.addWidget(self.btn_send)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.client_sock = socket(AF_INET, SOCK_STREAM)
        print('Connecting...')
        self.client_sock.connect(('127.0.0.1', self.port))
        print('Connected')

        self.send_thread = SendThread()
        self.send_thread.set_sock(self.client_sock)
        self.send_thread.start()
        self.recv_thread = RecvThread()
        self.recv_thread.set_sock(self.client_sock)
        self.recv_thread.recv_signal.connect(self.recv_msg)
        self.recv_thread.start()

        self.show()

    def send_msg(self):
        msg = self.le_input.text()
        msg = str(msg).strip()
        if msg == '':
            return

        self.send_thread.push_message(msg)
        self.le_input.setText('')
    def recv_msg(self, msg):
        self.te_messages.append(msg)




app = QApplication(sys.argv)
mw = MainWindow()

app.exec_()