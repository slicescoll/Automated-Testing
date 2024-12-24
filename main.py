import base64
import hashlib
import hmac
import json
import os
import runpy
import threading
import time
from io import BytesIO
from time import sleep
import logging
import qrcode
from PIL import Image
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QFileDialog, QTextEdit
from debugpy.common.timestamp import current
from mistune.plugins.formatting import insert

from socket_server import Server
from server_client import Client
from ui.ui_main import Ui_MainWindow
# from ui.ui_mmd import Ui_MainWindow
import barcode
from barcode.writer import ImageWriter
# import debug_2

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """
        主窗口初始化
    """

    def __init__(self):
        super(MainWindow, self).__init__()

        self.config_path1 = "D:/python/auto_test/device/dw200/testcase2/qr_http_config.json"     #扫码配置路径
        self.config_path2 = "D:/python/auto_test/device/dw200/testcase2/nfc_http_config.json"     #刷卡配置路径
        self.setupUi(self)
        self.show()

        self.pushButton.clicked.connect(self.server_start)  #启动服务器
        self.pushButton_2.clicked.connect(self.server_stop)
        self.pushButton_3.clicked.connect(self.server_send_data)     #将监听到的数据在文本框中显示

        self.display_text_edit_qr()   #文本框输入字符自动生成二维码

        self.textEdit_3.textChanged.connect(self.display_text_edit_qr)  # 文本框切换事件与二维码生成绑定
        self.pushButton_5.clicked.connect(self.display_text_edit_qr) #生成二维码
        self.pushButton_4.clicked.connect(self.update_qr_code) #自动生成扫码二维码
        # self.pushButton_4.clicked.connect(self.scan_QR)  # scan定制
        self.pushButton_10.clicked.connect(self.scan_card)  # 刷卡启动机械臂
        self.pushButton_11.clicked.connect(self.update_card)  # 切换刷卡二维码
        self.pushButton_6.clicked.connect(self.prev_qr_code)  # 上一张
        self.pushButton_7.clicked.connect(self.next_qr_code)  # 下一张
        self.pushButton_8.clicked.connect(self.stop)  # 暂停

        self.pushButton_12.clicked.connect(self.act_auto_test) #一键开启自动化全程的测试
        # self.pushButton_9.clicked.connect(self.load_config)  # 选择对应用例的文件路径

        self.server = None
        self.client = None

        self.current_index = 0  # 维护当前二维码索引
        self.data = []  # 初始化数据为一个空列表
        self.timer = QTimer(self)

        # 配置日志记录
        logging.basicConfig(
            level=logging.DEBUG,  # 设置日志级别
            format='%(asctime)s - %(levelname)s - %(message)s',  # 设置日志格式
            handlers=[
                logging.FileHandler('test_log.txt'),  # 保存日志到文件
                logging.StreamHandler()  # 控制台输出日志
            ]
        )


    def client_connect_server(self):
        ''' 客户端连接服务器 '''
        server_ip = self.lineEdit.text()
        server_port = int(self.lineEdit_2.text())
        client_name = '客户端'
        self.client = Client(self, server_ip, client_name, server_port)


    def client_disconnect_server(self):
        self.client.stop()

    def client_send_data(self):
        ''' 客户端发送信息，将信息写入GUI文本框中 '''
        message = self.textEdit.text()
        self.client.send_data(message)

    def server_start(self):
        server_ip = self.lineEdit.text()
        server_port = int(self.lineEdit_2.text())
        server_name = '服务器'
        self.server = Server(self, server_ip, server_name, server_port)

    def server_stop(self):
        self.server.stop()

    def server_send_data(self):
        message = self.textEdit.text()
        self.server.send_message_to_client(message)

    def act_auto_test(self, value):

        '''启动自动切换扫码配置码，配置HTTP等参数。。。。待优化'''
        self.update_qr_code()
        '''启动服务器，连接设备'''
        self.server_start()
        '''检查设备与服务器是否连接，校验是否接收到数据内容（即扫码、刷卡输出的值）'''
        # self.check_connection()

        '''配置码修改为刷卡配置'''
        self.update_card()
        '''调用机械臂'''
        self.scan_card()

        '''将输出的数据进行比对，列举，生成测试报告'''

        # self.generate_report()

    # def check_connection(self):
    #     print("检查设备与服务器连接...")
    #     response = self.device_check_status()
    #     if response != "OK":
    #         print("设备连接失败")
    #         return False
    #     return True

    def display_text_edit_qr(self):
        """
        根据 lineEdit_3 的文本生成并显示对应的二维码

        :return:
        """
        current_text = self.textEdit_3.toPlainText()
        qr_img = qrcode.make(current_text)  # 根据文本生成二维码

        # 将 PIL 图像转换为内存中的图像文件
        buffered = BytesIO()
        qr_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # 创建 HTML 内容
        html = f'<img src="data:image/png;base64,{img_str}" />'
        # 在 QTextEdit 中显示 HTML
        self.textEdit_2.setHtml(html)

    def next_qr_code(self):
        '''下一张图片，-----待优化'''
        self.current_index += 1
        if self.current_index >= len(self.data):
            self.current_index = 0  # 循环到开头
        # self.display_qr()
        # self.timer.start(5000)  # 每次翻页后重启计时器

    def prev_qr_code(self):
        '''上一张图片，-----待优化'''
        self.current_index -= 1
        if self.current_index < 0:
            self.current_index = len(self.data) - 1  # 循环到最后一张
        # self.display_qr()
        # self.timer.start(5000)  # 每次翻页后重启计时器


    def stop(self):
        self.timer.stop()  # 停止定时器




    # def load_config(self):
    #     ''' 用户选择不同的配置文件，不固定路径'''
    #     file_path, _ = QFileDialog.getOpenFileName(self, "Open Config File", "", "JSON Files (*.json)")
    #     if file_path:
    #         self.config_path = file_path
    #         self.load_data()
    #         self.update_qr_code()

    def load_data(self):
        """
        从 JSON 配置文件中读取数据 ,固定了路径
        """
        if not self.config_path:
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                 self.config_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            print(f"Error loading config file: {e}")
            self.config_data = {}


    def scan_card(self):

        '''
        点击刷卡按钮，调用scan_card test.py，机械臂进行循环刷卡
        '''
        result = runpy.run_path("scan_card test.py")
        WebAutomation = result['WebAutomation']
        obj = WebAutomation()
        obj.run()

    #     """点击刷卡按钮，调动机械臂进行循环刷卡"""
    #     # 使用线程执行刷卡动作，避免阻塞UI线程
    #     threading.Thread(target=self.run_scan_card).start()
    #
    # def run_scan_card(self):
    #     """执行刷卡动作，模拟机械臂操作"""
    #     try:
    #         result = runpy.run_path("debug_2.py")
    #         WebAutomation = result['WebAutomation']
    #         obj = WebAutomation()
    #         obj.run()  # 假设run是刷卡动作的函数
    #
    #         print("刷卡动作已完成")
    #     except Exception as e:
    #         print(f"刷卡过程中发生错误: {e}")

    # def scan_QR(self):
    #     result = runpy.run_path("QR_code_Auto.py")
    #     QRCodeDisplayer = result['QRCodeDisplayer']
    #     obj = QRCodeDisplayer()
    #     obj.run()




    '''生成配置码逻辑'''
    def generate_qr_code(self,config_test):
        '''配置码生成的逻辑，固定前缀+配置数据，通过hmac算法生成'''
        self.prefix = "___VBAR_CONFIG_V1.1.0___"
        self.key = b"1234567887654321"
        data_to_sign = (self.prefix + config_test).encode()
        hmac_signature = hmac.new(self.key, data_to_sign, hashlib.md5).digest()
        suffix = base64.b64encode(hmac_signature).decode()
        config_code = f"{self.prefix}{config_test}--{suffix}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(config_code)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white')
        return qr_img



    '''扫码部分'''
    #选取扫码对应的json配置文件,调用display_qr逻辑


    def update_qr_code(self):

        """
            根据扫码逻辑定时切换并生成二维码，显示在 QTextEdit 中
        """
        print("Updating QR code...")

        try:
            with open(self.config_path1, 'r', encoding='utf-8') as file:
                self.data = json.load(file)

            if not self.data:
                self.textEdit_2.setHtml('<p>No data to encode.</p>')
                return


            self.timer.timeout.connect(self.display_qr)
            self.current_index = 0  # 重置当前索引
            self.display_qr()  # 显示第一张二维码
            self.timer.start(3000)  # 每3秒更新一次二维码

        except Exception as e:
            print(f"An error occurred: {e}")

    def display_qr(self):
        """交替显示QR配置码和样码"""
        if self.current_index % 2 == 0:
            # 偶数索引，显示配置二维码
            self.display_qr_code()
        else:
            # 奇数索引，显示样码（图片）
            self.display_sample_code()

    def display_qr_code(self):

        """
        显示QR配置码，调节图片大小，图片转base64，最后以HTML格式显示在textEdit_2框里面
        """

        item = self.data[self.current_index]
        data_to_encode = item.get('config_data1', '')
        name = item.get('name', 'Unnamed')  # 默认名称

        if not data_to_encode:
            print(f"Skipping empty data for QR code generation")
            return

        try:
            # 生成二维码图像
            qr_img = self.generate_qr_code(data_to_encode)
            qr_img.thumbnail((300, 300))  # 调整二维码图片大小
            img_str = self.image_to_base64(qr_img)
            # 图片转base64
            html = self.construct_html(name, img_str, '')  # html格式显示

            self.textEdit_2.setHtml(html)  # 在设定框里显示
            self.textEdit_2.repaint()  # 更新
            print(f"二维码生成成功，显示二维码: {name}")
            logging.info(f"show QR config code:  {name}")
            self.current_index += 1

        except Exception as e:
            print(f"生成二维码出错: {e}")
            logging.exception(f"Unexpected config code error: {e}")

    def display_sample_code(self):
        """
        显示样码，只显示插入的图片
        """
        image_path = 'D://python/python learning/AUTO TEST/N_serial/TEST_TK//1.png'  # 设定插入图片的路径
        try:
            # 确保图片路径有效
            if not os.path.exists(image_path):
                print(f"错误：图片文件不存在，路径：{image_path}")
                logging.error(f"its wrong,not any picture,line:{image_path}")
                return

            # 读取图片并转换为 Base64 格式
            img = Image.open(image_path)  # 假设你使用 PIL (Pillow) 来处理图片
            img.thumbnail((300, 300))  # 可根据需要调整图片大小
            img_base64 = self.image_to_base64(img)  # 转图片为base64

            # 构建并显示 HTML
            html = self.construct_html('', '', img_base64)

            self.textEdit_2.setHtml(html)
            self.textEdit_2.repaint()
            print(f"显示样码成功")
            logging.info(f"show sample code success")
            self.current_index += 1
        except Exception as e:
            print(f"显示样码时出错: {e}")
            logging.exception(f"Unexpected sample error: {e}")




    '''刷卡部分'''


    #选取刷卡对应的json文件，调用显示刷卡的display_card逻辑
    def update_card(self):
        """
            根据刷卡逻辑，切换配置码和插入图片在 QTextEdit 中显示
        """
        print("Updating card code...")
        try:
            with open(self.config_path2, 'r', encoding='utf-8') as file:
                self.data = json.load(file)

            if not self.data:
                self.textEdit_2.setHtml('<p>No data to encode.</p>')
                return

            self.timer.timeout.connect(self.display_card)
            self.current_index = 0  # 重置当前索引
            self.display_card()  # 显示第一张二维码
            self.timer.start(5000)  # 每5秒更新一次二维码

        except Exception as e:
            print(f"An error occurred: {e}")

    def display_card(self):
        """交替显示配置码和执行刷卡动作"""
        if self.current_index % 2 == 0:
            # 偶数索引，显示配置二维码
            self.display_card_code()
        else:
            # 奇数索引，调用机械臂
            # self.scan_card()  #这里同时调用机械臂会导致卡死，所以选择另外运行对应的py文件
            # 插入空白图片对应机械臂动作延迟
            self.insert_blank()

    def display_card_code(self):
        """
            显示nfc配置码，调节图片大小，图片转base64，最后以HTML格式显示在textEdit_2框里面
        """
        if self.data and 0 <= self.current_index < len(self.data):
            item = self.data[self.current_index]
            data_to_encode = item.get('config_data1', '')
            name = item.get('name', 'Unnamed')  # 默认名称
            if not data_to_encode:
                return

            qr_img = self.generate_qr_code(data_to_encode)
            qr_img.thumbnail((300, 300))  # 调整二维码图片大小
            img_str = self.image_to_base64(qr_img)

            # insert_img = self.get_additional_image_base64()  # 获取附加图片
            '''这里无需插入图片，应该是机械臂进行刷卡动作'''

            html = self.construct_html(name, img_str, '')

            self.textEdit_2.setHtml(html)
            self.textEdit_2.repaint()

            print(f"正在显示二维码：{name}")
            logging.info(f"show card config code:  {name}")
            self.current_index += 1  # 移动到下一个索引

            if self.current_index >= len(self.data):
                self.current_index = 0  # 循环回到开始
        else:
            self.timer.stop()  # 超出范围停止计时器

    def insert_blank(self):
        """显示样码，只显示插入的图片"""
        image_path = 'D://python/python learning/AUTO TEST/N_serial/TEST_TK//blank.png'  # 设定插入图片的路径
        try:
            # 确保图片路径有效
            if not os.path.exists(image_path):
                print(f"错误：图片文件不存在，路径：{image_path}")
                logging.error(f"nothing ,line:{image_path}")
                return

            # 读取图片并转换为 Base64 格式
            img = Image.open(image_path)  # 假设你使用 PIL (Pillow) 来处理图片
            img.thumbnail((300, 300))  # 可根据需要调整图片大小
            img_base64 = self.image_to_base64(img)  # 转图片为base64

            # 构建并显示 HTML
            html = self.construct_html('', '', img_base64)

            self.textEdit_2.setHtml(html)
            self.textEdit_2.repaint()
            print(f"显示样码成功")
            logging.info(f"show blank success")
            self.current_index += 1
        except Exception as e:
            print(f"显示样码时出错: {e}")
            logging.exception(f"Exception: {e}")

    '''html显示配置'''

    def construct_html(self, name, qr_img_str, insert_img):
        '''BASE64二维码转HTML格式显示'''
        if qr_img_str:  # 偶数索引，显示二维码
            return f'''
                          <div style="text-align: center; width: 280px; margin: auto;">
                              <img src="data:image/png;base64,{qr_img_str}" style="width: 100px; height: 100px; margin: 0;" />
                              <h4 style="font-size: 6px; vertical-align: text-top;">{name}</h4>
                          </div>
                          '''
        elif insert_img:  # 奇数索引并且有附加图片
            return f'''
                          <div style="text-align: center; width: 280px; margin: auto;">
                              <img src="data:image/png;base64,{insert_img}" style="width: 100px; height: 100px; margin: 0;" />
                          </div>
                          '''
        else:  # 仅显示名称
            return f'''
                          <div style="text-align: center; width: 280px; margin: auto;">
                              <h4 style="font-size: 6px; vertical-align: text-top;">{name}</h4>
                          </div>
                          '''

    def image_to_base64(self, img):
        '''配置码图片转BASE64'''
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def get_additional_image_base64(self):
        '''插入的图片转BASE64'''
        insert_image_path = "D://python/python learning/AUTO TEST/N_serial/TEST_TK//1.png"

        try:
            with Image.open(insert_image_path) as img:
                img.thumbnail((260, 260))
                return self.image_to_base64(img)
        except Exception as e:
            print(f"加载图片时出错: {e}")
            return None








    # def update_qr_code(self):
    #     """
    #         根据加载的配置数据生成二维码并显示在 QTextEdit 中
    #         """
    #     print("Updating QR code...")
    #
    #     try:
    #         with open(self.config_path1, 'r', encoding='utf-8') as file:
    #             self.data = json.load(file)
    #
    #         if not self.data:
    #             self.textEdit_2.setHtml('<p>No data to encode.</p>')
    #             return
    #
    #
    #         self.timer.timeout.connect(self.display_qr)
    #         self.current_index = 0  # 重置当前索引
    #         self.display_qr()  # 显示第一张二维码
    #         self.timer.start(5000)  # 每5秒更新一次二维码
    #
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    #
    # def display_qr(self):
    #     """交替显示二维码和样码"""
    #     if self.current_index % 2 == 0:
    #         # 偶数索引，显示二维码
    #         self.display_qr_code()
    #     else:
    #         # 奇数索引，显示样码（图片）
    #         self.display_sample_code()
    #
    #
    # def display_qr_code(self):
    #     """显示二维码"""
    #     # current_index = 1
    #     item = self.data[self.current_index]
    #     data_to_encode = item.get('config_data1', '')
    #     name = item.get('name', 'Unnamed')  # 默认名称
    #
    #     if not data_to_encode:
    #         print(f"Skipping empty data for QR code generation")
    #         return
    #
    #     try:
    #         # 生成二维码图像
    #         qr_img = self.generate_qr_code(data_to_encode)
    #         qr_img.thumbnail((260, 260))  # 调整二维码图片大小
    #         img_str = self.image_to_base64(qr_img)
    #         item = self.data[self.current_index]
    #         data_to_encode = item.get('config_data1', '')
    #         name = item.get('name', 'Unnamed')  # 默认名称
    #
    #         html = self.construct_html(name,img_str,'')
    #
    #         self.textEdit_2.setHtml(html)
    #         self.textEdit_2.repaint()
    #         # # 构建并显示 HTML
    #         # html = self.construct_to_html(
    #         #     name=f"{name}",
    #         #     img_str=img_str,
    #         # )
    #         # self.set_html_to_text_edit(html)
    #         print(f"二维码生成成功，显示二维码: {name}")
    #         self.current_index += 1
    #
    #     except Exception as e:
    #         print(f"生成二维码出错: {e}")
    #
    # def display_sample_code(self):
    #     """显示样码，只显示插入的图片"""
    #     # current_index = 1
    #     image_path = 'D://python/python learning/AUTO TEST/N_serial/TEST_TK//1.png'
    #     try:
    #         # 确保图片路径有效
    #         if not os.path.exists(image_path):
    #             print(f"错误：图片文件不存在，路径：{image_path}")
    #             return
    #
    #         # 读取图片并转换为 Base64 格式
    #         img = Image.open(image_path)  # 假设你使用 PIL (Pillow) 来处理图片
    #         img.thumbnail((260, 260))  # 可根据需要调整图片大小
    #         img_base64 = self.image_to_base64(img)
    #
    #         # 构建并显示 HTML
    #         html = self.construct_html('','',img_base64)
    #
    #         self.textEdit_2.setHtml(html)
    #         self.textEdit_2.repaint()
    #         # html = self.construct_html()
    #         # self.set_html_to_text_edit(html)
    #         print(f"显示样码成功")
    #         # current_index += 1
    #
    #         self.current_index += 1
    #
    #     except Exception as e:
    #         print(f"显示样码时出错: {e}")
    #
    # def set_html_to_text_edit(self, html):
    #     """设置 HTML 到 QTextEdit 控件"""
    #     try:
    #         self.textEdit_2.setHtml(html)
    #         self.textEdit_2.repaint()
    #     except Exception as e:
    #         print(f"Error setting HTML to QTextEdit: {e}")
    #


    # def display_qr(self):
    #     if self.data and 0 <= self.current_index < len(self.data):
    #         item = self.data[self.current_index]
    #         data_to_encode = item.get('config_data1', '')
    #         name = item.get('name', 'Unnamed')  # 默认名称
    #         if not data_to_encode:
    #             return
    #
    #         qr_img = self.generate_qr_code(data_to_encode)
    #         qr_img.thumbnail((260, 260))  # 调整二维码图片大小
    #         img_str = self.image_to_base64(qr_img)
    #
    #         insert_img = self.get_additional_image_base64()  # 获取附加图片
    #
    #         html = self.construct_html(name, insert_img)
    #
    #         self.textEdit_2.setHtml(html)
    #         self.textEdit_2.repaint()
    #
    #         print(f"正在显示第 {self.current_index + 1}/{len(self.data)} 个二维码")
    #         self.current_index += 1  # 移动到下一个索引
    #
    #         if self.current_index >= len(self.data):
    #             self.current_index = 0  # 循环回到开始
    #     else:
    #         self.timer.stop()  # 超出范围停止计时器
    #
    #



    # def update_card(self):
    #     """
    #         根据加载的配置数据生成二维码并显示在 QTextEdit 中
    #         """
    #     # self.current_index = 0
    #     print("Updating QR code...")
    #     # print(f"Current index: {self.current_index}")
    #
    #     try:
    #         with open(self.config_path2, 'r', encoding='utf-8') as file:
    #             self.data = json.load(file)
    #
    #         if not self.data:
    #             self.textEdit_2.setHtml('<p>No data to encode.</p>')
    #             return
    #
    #
    #         self.timer.timeout.connect(self.display_card)
    #         self.current_index = 0  # 重置当前索引
    #         self.display_card()  # 显示第一张二维码
    #         self.timer.start(5000)  # 每5秒更新一次二维码
    #
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    #
    # def display_card(self):
    #     if self.data and 0 <= self.current_index < len(self.data):
    #         item = self.data[self.current_index]
    #         data_to_encode = item.get('config_data1', '')
    #         name = item.get('name', 'Unnamed')  # 默认名称
    #         if not data_to_encode:
    #             return
    #
    #         qr_img = self.generate_qr_code(data_to_encode)
    #         qr_img.thumbnail((300, 300))  # 调整二维码图片大小
    #         img_str = self.image_to_base64(qr_img)  # 图片转base64
    #
    #         insert_img = self.get_additional_image_base64()  # 获取附加图片
    #
    #         html = self.construct_html(name, img_str, insert_img)
    #
    #         self.textEdit_2.setHtml(html)
    #         self.textEdit_2.repaint()
    #
    #         print(f"正在显示第 {self.current_index + 1}/{len(self.data)} 个二维码")
    #         self.current_index += 1  # 移动到下一个索引
    #
    #         if self.current_index >= len(self.data):
    #             self.current_index = 0  # 循环回到开始
    #     else:
    #         self.timer.stop()  # 超出范围停止计时器
    #
    # def construct_html(self, name, qr_img_str, insert_img):
    #     if qr_img_str:  # 偶数索引，显示二维码
    #         return f'''
    #                       <div style="text-align: center; width: 280px; margin: auto;">
    #                           <img src="data:image/png;base64,{qr_img_str}" style="width: 100px; height: 100px; margin: 0;" />
    #                           <h4 style="font-size: 6px; vertical-align: text-top;">{name}</h4>
    #                       </div>
    #                       '''
    #     elif insert_img:  # 奇数索引并且有附加图片
    #         return f'''
    #                       <div style="text-align: center; width: 280px; margin: auto;">
    #                           <img src="data:image/png;base64,{insert_img}" style="width: 100px; height: 100px; margin: 0;" />
    #                       </div>
    #                       '''
    #     else:  # 仅显示名称
    #         return f'''
    #                       <div style="text-align: center; width: 280px; margin: auto;">
    #                           <h4 style="font-size: 6px; vertical-align: text-top;">{name}</h4>
    #                       </div>
    #                       '''
    #
    # def image_to_base64(self, img):
    #     buffered = BytesIO()
    #     img.save(buffered, format="PNG")
    #     return base64.b64encode(buffered.getvalue()).decode("utf-8")
    #
    # def get_additional_image_base64(self):
    #     insert_image_path = "D://python/python learning/AUTO TEST/N_serial/TEST_TK//1.png"
    #
    #     try:
    #         with Image.open(insert_image_path) as img:
    #             img.thumbnail((260, 260))
    #             return self.image_to_base64(img)
    #     except Exception as e:
    #         print(f"加载图片时出错: {e}")
    #         return None

    # def generate_coded(self,data, code_type, filename):
    #     """根据条形码类型生成条形码并保存为图像文件"""
    #     if code_type == 'code128':
    #         coded = barcode.get('code128', data, writer=ImageWriter())
    #     elif code_type == 'code39':
    #         coded = barcode.get('code39', data, writer=ImageWriter())
    #     else:
    #         print(f"Unsupported barcode type: {code_type}")
    #         return
    #
    #     # 保存为图像文件
    #     coded.save(filename)

    # 1
#----------------------------------加上间隔要扫描的qr/pdf17/code39...码，上一张，下一张，暂停仍然有点问题------------------------------------------------------------
















        # print(f"Data length: {len(self.data)}")

        # try:
        #     with open(self.config_path, 'r', encoding='utf-8') as file:
        #         self.data = json.load(file)
        #
        #     if not self.data:
        #         self.textEdit_2.setHtml('<p>No data to encode.</p>')
        #         return
        #
        #     num_items = len(self.data)
        #     if num_items == 0:
        #         return
        #     while self.current_index < len(self.data):
        #         item = self.data[self.current_index]
        #         data_to_encode = item.get('config_data1', '')
        #         if not data_to_encode:
        #             return
        #
        #         qr_img = self.generate_qr_code(data_to_encode)
        #         width = self.textEdit_2.viewport().width()
        #         height = self.textEdit_2.viewport().height()
        #
        #         qr_img.thumbnail((width, height))
        #         buffered = BytesIO()
        #         qr_img.save(buffered, format="PNG")
        #         img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        #
        #         html = f'<img src="data:image/png;base64,{img_str}" style="width:{width}px; height:{height}px;" />'
        #         self.textEdit_2.setHtml(html)
        #         self.textEdit_2.repaint()
        #
        #         # 增加延时，确保每张二维码有足够的显示时间

        #         # time.sleep(2)  # 暂停2秒
        #
        #         # 更新索引到下一张
        #         self.current_index += 1
        #
        # except Exception as e:
        #     print(f"An error occurred: {e}")



        # if not hasattr(self, 'config_data') or not self.config_data:
        #     self.textEdit_2.setHtml('<p>No data to encode.</p>')
        #     return

        # 从配置数据中提取要编码的数据

        # """
        # 根据 JSON 文件中的 data 字段生成并显示对应的二维码
        # """
        # self.current_index = 0
        # # 读取 JSON 文件
        # with open(self.config_path, 'r', encoding='utf-8') as file:
        #     self.data = json.load(file)
        #
        # if not self.data:
        #     self.textEdit_2.setHtml('<p>No data to encode.</p>')
        #     return
        #
        #
        # item = self.data[self.current_index]
        # config_test = item.get('config_data1', '')
        # name = item.get('name', 'Unnamed')
        #
        # qr_html = self.generate_qr_code(config_test)
        # html_content = f"<p>QR Code for {name}:</p>{qr_html}<br/>"
        # self.textEdit_2.setHtml(html_content)     # 在 QTextEdit 中显示 HTML
        #
        # self.current_index = (self.current_index + 1) % len(self.data)
        # # self.timer.start(5000)  # 5000 ms = 5 seconds



