# import socket
#
# socket_server = socket.socket()
# socket_server.bind(("localhost", 8888))
# # 监听端口
# socket_server.listen(1)
# # 等待客户端连接，accept方法返回二元元组(连接对象, 客户端地址信息)
# print(f"服务端已开始监听，正在等待客户端连接...")
# conn, address = socket_server.accept()
# print(f"接收到了客户端的连接，客户端的信息：{address}")
#
# # 接受客户端信息，使用客户端和服务端的本次连接对象，而非socket_server
# while True:
#     # 接收消息
#     data: str = conn.recv(1024).decode("UTF-8")
#     print(f"客户端发来的消息是：{data}")
#     # 回复消息
#     msg = input("请输入你要回复客户端的消息：")
#     if msg == 'exit':
#         break
#     conn.send(msg.encode("UTF-8"))  # encode将字符串编码为字节数组对象
#
# # 关闭连接
# conn.close()
# socket_server.close()
import logging
import socket
import json
import os
from datetime import datetime
from PyQt6.QtCore import pyqtSignal, QThread


class Server:

    def __init__(self, ui, server_ip, server_hostname, server_port):

        self.ui = ui  # 主界面
        self.ip = server_ip  # 服务器ip地址
        self.port = server_port  # 服务器端口号
        self.serverName = server_hostname  # 显示名称
        self.is_running = False  # 是否已经启动

        self.socket = None  # socket
        self.socketThread = None  # 新的 socket receive 线程

        self.start()

        # 配置日志记录
        logging.basicConfig(
            level=logging.DEBUG,  # 设置日志级别
            format='%(asctime)s - %(levelname)s - %(message)s',  # 设置日志格式
            handlers=[
                logging.FileHandler('test_log.txt'),  # 保存日志到文件
                logging.StreamHandler()  # 控制台输出日志
            ]
        )

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.ip, self.port))  # 绑定IP与端口
            self.socket.listen(1)  # 设定最大连接数
            self.startSocketReceiveThread()

    def stop(self):
        try:
            if self.is_running:
                self.is_running = False
                if self.socketThread.is_running:
                    self.socketThread.stop()
        except Exception as e:
            print(e)

    def startSocketReceiveThread(self):
        self.socketThread = ServerSocketReceiveThread(self.socket)
        self.socketThread.clientConnection.connect(self.socket_client_connect_trigger)
        self.socketThread.receivedClientData.connect(self.show_client_message)
        self.socketThread.serverStatus.connect(self.server_status_trigger)
        self.socketThread.start()

    def server_status_trigger(self, status):
        self.ui.statusbar.showMessage(status)

    def socket_client_connect_trigger(self, state):
        if state == 'connect':
            self.ui.statusbar.showMessage("客户端已经连接。")
        else:
            self.ui.statusbar.showMessage("客户端已经断开。")

    def show_client_message(self, message):
        self.ui.textEdit_4.append('客户端:' + message)

    def send_message_to_client(self, message):
        if self.is_running:
            self.ui.textEdit_4.append(self.serverName + ':' + message)
            self.socketThread.send_data_to_client(message)


# 处理客户端的连接和数据
class ServerSocketReceiveThread(QThread):
    clientConnection: pyqtSignal = pyqtSignal(str)  # 向主线程发送连接状态标志
    receivedClientData: pyqtSignal = pyqtSignal(str)  # 向主线程发送接受到客户端的数据
    serverStatus: pyqtSignal = pyqtSignal(str)  # 向主线程发送服务器状态

    def __init__(self, serverSocket):
        super(ServerSocketReceiveThread, self).__init__()
        self.serverSocket = serverSocket
        self.clientSocket = None
        self.addr = None
        self.is_running = True

    def run(self):
        self.serverStatus.emit("服务已经启动，等待客户端的连接......")
        self.serverSocket.settimeout(60)  # 60秒超时
        try:
            # self.clientSocket, self.addr = self.serverSocket.accept()  # 接受客户端的一次连接，连接成功后会关闭服务
            # self.emitConnectEvent('connect')  # 发送通知到主界面
            self.startReceiveData()
        except socket.timeout:
            self.serverStatus.emit("连接超时。")
            return

    def save_data_to_json(self, data):
        """将接收到的数据保存到以当前日期为名称的 JSON 文件"""
        # 获取当前日期，格式为 YYYY-MM-DD
        current_date = datetime.now().strftime("%Y-%m-%d")
        file_path = f"D:/python/Saved Data/received_data_{current_date}.json"

        # 检查文件是否已经存在，如果是新的一天，清空文件并重新保存
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        # 将新接收到的数据追加到已有的数据列表中
        existing_data.append(data)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)


    def startReceiveData(self):
        while self.is_running:
            try:
                self.clientSocket, self.addr = self.serverSocket.accept()     #不断接收客户端连接
                self.emitConnectEvent('connect')  # 发送通知到主界面
                logging.info(f"Client connected: {self.addr}")

                data = self.clientSocket.recv(1024).decode('utf-8')
                # print(f"接收到数据：{data}")
                logging.info(f"Received data: {data}")

                if not data:
                    self.emitConnectEvent('disconnect')  # 发送通知到主界面
                    break

                # 将接收到的数据保存到 JSON 文件
                self.save_data_to_json(data)

                # HTTP 响应构造
                response_body = "code=0000"  # 你想要的响应内容
                response = self.construct_http_response(response_body)
                # 记录发送响应到客户端
                logging.info(f"Sent response: {response_body}")
                # 发送 HTTP 响应数据到客户端
                self.send_data_to_client(response)
                # 将数据和响应内容发送到 UI
                self.sendClientDataToUi(data+"\r\n"+response_body+"\r\n")


            except ConnectionResetError:
                self.sendClientDataToUi("已经离开对话。")
                logging.error("Connection reset by client.")
                self.is_running = False
                self.emitConnectEvent('disconnect')  # 发送通知到主界面
            except Exception as e:
                print(f"Error: {e}")
                logging.exception(f"Unexpected error: {e}")
                break
        self.cleanUp()




    def construct_http_response(self, message):
        '''
            构造HTTP响应
        '''
        response_start_line = "HTTP/1.1 200 OK\r\n"
        response_headers = (
            "Server: MyServer\r\n"
            "Connection: keep-alive\r\n"
            f"Content-Length: {len(message)}\r\n"
        )
        response = f"{response_start_line}{response_headers}\r\n{message}"
        return response

    def send_data_to_client(self, message):
        try:
            self.clientSocket.sendall(message.encode("utf-8"))
        except Exception as reason:
            print("发送失败，原因 = ", reason)

    def stop(self):
        self.is_running = False
        if self.clientSocket:
            self.clientSocket.close()
        self.serverSocket.close()

    def emitConnectEvent(self, state):
        self.clientConnection.emit(state)

    def sendClientDataToUi(self, message):
        self.receivedClientData.emit(message)

    def cleanUp(self):
        if self.clientSocket:
            self.clientSocket.close()
        self.serverStatus.emit("服务已经关闭。")


