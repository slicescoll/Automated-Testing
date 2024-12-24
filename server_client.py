# import socket
#
# # 创建socket对象
# socket_client = socket.socket()
# # 连接到服务器
# socket_client.connect(("localhost", 8888))
#
# while True:
#     send_msg = input("请输入要发送给服务端的消息：")
#     if send_msg == "exit":
#         break
#     # 发送消息
#     socket_client.send(send_msg.encode("UTF-8"))
#     # 接受消息
#     recv_data = socket_client.recv(1024).decode("UTF-8")  # 1024是缓冲区大小，一般就填1024， recv是阻塞式
#     print(f"服务端回复的消息是：{recv_data}")
#
# # 关闭连接
# socket_client.close()
import socket
import time

from PyQt6.QtCore import QThread, pyqtSignal


class Client:

    def __init__(self, ui, ip, clientName, port):
        self.ui = ui
        self.ip = ip
        self.hostName = clientName
        self.port = port

        self.socket = None
        self.socketThread = None
        self.connect_server()

    def connect_server(self):
        max_retries = 5
        retry_count = 0

        while retry_count < max_retries:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.settimeout(60)  # 设置超时时间，避免无限等待
                self.socket.connect((self.ip, self.port))

                self.socketThread = ClientSocketReceiveThread(self.socket)
                self.socketThread.receivedServerData.connect(self.update_ui_chat_content)
                self.socketThread.start()

                print("连接成功")
                break  # 连接成功后退出循环

            except (socket.timeout, socket.error) as e:
                print(f"连接失败: {e}")
                self.ui.textEdit_2.append(f"连接失败: {e}")
                if self.socket:
                    self.socket.close()
                retry_count += 1
                time.sleep(5)  # 等待5秒后重试

        if retry_count == max_retries:
            print("超过最大重试次数，连接失败")
            self.ui.textEdit_2.append("连接失败，请检查网络设置")




    def update_ui_chat_content(self, serverMessage):
        self.ui.textEdit_2.append("服务端:" + serverMessage)

    def stop(self):
        if self.socketThread:
            self.socketThread.stop()
            self.socketThread.wait()  # 等待线程结束
        if self.socket:
            self.socket.close()

    def send_data(self, sentence):
        if self.socket:
            try:
                self.ui.textEdit_2.append(self.hostName + ":" + sentence)
                self.socket.send(sentence.encode())
            except BrokenPipeError:
                self.ui.textEdit_2.append("发送数据失败，连接已关闭")

    def connect_success(self, ip, port):
        try:
            self.socket.connect((ip, port))
            return True
        except Exception as reason:
            print(reason)
            return False




class ClientSocketReceiveThread(QThread):
    receivedServerData: pyqtSignal = pyqtSignal(str)  # 向主线程发送接受到客户端的数据

    def __init__(self, clientSocket):
        super(ClientSocketReceiveThread, self).__init__()
        self.clientSocket = clientSocket
        self.is_running = True

    def stop(self):
        self.is_running = False
        self.clientSocket.close()

    def run(self):
        while self.is_running:
            try:
                msg = self.clientSocket.recv(1024).decode("utf-8")  # 接受服务端消息
                if not msg:
                    break
                self.receivedServerData.emit(msg)
            except ConnectionResetError:
                self.receivedServerData.emit("连接被远程主机重置")
                break
            except Exception as e:
                self.receivedServerData.emit(f"接收数据错误: {e}")
                break
        self.stop()
        self.receivedServerData.emit("已经与服务端断开。")

