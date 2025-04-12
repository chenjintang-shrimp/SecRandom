from PyQt5.Qt import *
from PyQt5.QtCore import *
 
class SingleApplication(QApplication):
    def __init__(self, argv):
        QApplication.__init__(self, argv)
        self.main_window = None
        self.local_server = None
        self.is_running = False
        self.server_name = 'SecRandom'
        self.init_local_connection()
 
    def init_local_connection(self):
        socket = QLocalSocket()
        socket.connectToServer(self.server_name)
        if socket.waitForConnected(500):
            self.is_running = True
        else:
            self.is_running = False
            self.local_server = QLocalServer()
            self.local_server.newConnection.connect(self.new_local_connection)
            # 监听，如果监听失败，可能是之前程序崩溃时残留进程服务导致的，移除残留进程
            if not self.local_server.listen(self.server_name):
                if self.local_server.serverError() == QAbstractSocket.AddressInUseError:
                    QLocalServer.removeServer(self.server_name)
                    self.local_server.listen(self.server_name)
 
    def new_local_connection(self):
        if self.main_window is not None:
            self.main_window.raise_()
            self.main_window.activateWindow()
            self.main_window.setWindowState((self.main_window.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
            self.main_window.show()