import sys
import time

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget
from socket import socket, AF_INET, SOCK_STREAM


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
            try:
                recv_data = self.sock.recv(1024)
                recv_data = recv_data.decode('utf-8')
                self.recv_signal.emit(recv_data)
            except ConnectionResetError as cre:
                print('연결이 종료되었습니다.@RecvThread')
                break


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


class ServerThread(QThread):

    def __init__(self, sock, recv_thread, send_thread):
        super().__init__()
        self.server_sock = sock
        self.recv_thread = recv_thread
        self.send_thread = send_thread

    @pyqtSlot()
    def run(self) -> None:
        while True:
            print('Wait for a connection...')
            conn_sock, addr = self.server_sock.accept()
            print(f'Connected from {addr}')

            self.recv_thread.set_sock(conn_sock)
            self.recv_thread.start()
            self.send_thread.set_sock(conn_sock)
            self.send_thread.start()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.btn_send = None
        self.te_messages = None
        self.lbl_title = None
        self.le_input = None
        self.init_ui()
        self.init_server()

        self.show()

    def init_ui(self):
        self.setWindowTitle('PyQt5 server')
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

    def send_msg(self):
        msg = self.le_input.text()
        msg = str(msg).strip()
        if msg == '':
            return

        self.send_thread.push_message(msg)
        self.le_input.setText('')

    def recv_msg(self, msg):
        self.te_messages.append(msg)

    def init_server(self):
        self.port = 20080
        self.server_sock = socket(AF_INET, SOCK_STREAM)
        self.server_sock.bind(('', self.port))
        self.server_sock.listen()

        self.send_thread = SendThread()
        self.recv_thread = RecvThread()
        self.recv_thread.recv_signal.connect(self.recv_msg)
        self.svr_thread = ServerThread(self.server_sock, self.recv_thread, self.send_thread)
        self.svr_thread.start()


app = QApplication(sys.argv)

mw = MainWindow()

app.exec_()
