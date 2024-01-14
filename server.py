import os
import sys
import json
import glob
import time
import socket
import base64
import pyautogui
from des import *
from PyQt5 import QtCore, QtGui, QtWidgets

class MyThread(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(list)
    def __init__(self, ip, port, parent=None):
        QtCore.QThread.__init__(self.parent)


        #глобальные переменные
        self.active_socket = None
        self.ip = ip
        self.port = port
        self.command = 'screen'

        #TCP сервера 
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, self.port))
        self.server.listen(0)

    #привем и обработка изображения
    def run(self):
        #прием входящего соединения
        self.data_connaction, _ = self.server.accept()
        self.active_socket = self.data_connaction
    #цикл проверки обратной связи с клиентом и полчение скрина экрана
        while True:
            if self.command.split(' ', 1)[0] != 'screen':
                self.send_json(self.command.split(' '))
                responce = self.receive_json()
                self.mysignal.emit([responce])
                self.command.listen(0)
            if self.command.split(' ', 1)[0] == 'screen':
                self.send_json(self.command.split(' '))
                responce = self.receive_json()
                self.mysignal.emit([responce])
    #отправка json данных клиенту
    def send_json(self, data):
       #обрабатываем бинарные данные 
        try: json_data = json.dumps(data.decode('utf-8'))
        except: json_data = json.dumps(data)

        
        #в случае если клиент разорвал соединение на сервер отправляет команду
        try:
           self.active_socket.send(json_data.encode('utf-8'))
        except ConnectionResetError:
            #отключаем от текущей сессии
            self.active_socket = None

    #получаем json данные от клиента
    def receive_json(self):
        json_data = ' '
        while True:
            try:
                if self.active_socket != None:
                    json_data += self.active_socket.recv(1024).decode('utf-8')
                    return json.loads(json_data)
                else:
                    return None
            except ValueError:
                pass

class VNServer(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #создаем эмулятор обработчика
        self.ip = '127.0.0.1'
        self.port = 4444
        self.thread_hendler = MyThread(self.ip, self.port)
        self.thread_hendler.start()

        #обработчик потока для  обнавления GUI
        self.thread_hendler.mysignal.connect(self.screen_hendler)

    #обработка и вывод изображения 
    def screen_hendler(self, screen_value):
        data = ['mouse_left_click', 'mouse_right_click','mouse_duble_left_click']        

        #в случае если это не скрин пропускаем шаг
        if screen_value[0] not in data:
            decrypt_image = base64.b64decode(screen_value[0])
            with open('2.png', 'wb') as file:
                file.write(decrypt_image)


            #вводим изображение в панель
            image = QtGui.QPixmap('2.png')
            self.ui.label.setPixmap(image)

    #После закрытия сервера удаляем изображение 
    def closeEvent(self, event):
        for file in glob.glob('*.png'):
            try: os.remove(file)
            except: pass

    #Обработка Event событий 
    def event(self, event):
        #обработка ЛКМ и ПКМ
        if event.type() == QtCore.QEvent.MouseButtonPress:
            current_button = event.button()#определяет нажатую кнопку 

            if current_button == 1:
                mouse_cord = f'mouse_left_click {event.x()} {event.y()}'
            elif current_button == 2:
                mouse_cord = f'mouse_right_click {event.x()} {event.y()}'
            self.thread_hendler.command = mouse_cord

            #обработка даблкликов 
        elif event.type() == QtCore.QEvent.MouseButtonPress:
                mouse_cord = f'mouse_duble_left_click {event.x()} {event.y()}'
                self.thread_hendler.command = mouse_cord
        return QtWidgets.QWidget.event(self, event)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myapp = VNServer()
    myapp.show()
    sys.exit(app.exec_())
