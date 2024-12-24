import time
from itertools import repeat

from jedi.parser_utils import function_is_staticmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import logging

'''
扫码器动作编号10-20
机械臂操作
开发模式测试用例
'''
class WebAutomation:
    def __init__(self):
        #初始化WebDriver
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 启用无头模式
        chrome_options.add_argument('--start-maximized')

        service = Service('D:\\RoArm\\chromedriver-win64\\chromedriver.exe')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.index = 0
        self.first_url = 'http://192.168.4.1/'
        self.second_url = 'http://192.168.4.1/config'
    #     # 初始化标志变量
    #     self.browser_opened = False  # 标记浏览器是否已经打开
    #     self.driver = None  # WebDriver 初始为 None
    #     self.first_url = 'http://192.168.4.1/'
    #     self.second_url = 'http://192.168.4.1/config'
    #
    # def open_browser(self):
    #     if not self.browser_opened:
    #         # 初始化 WebDriver
    #         chrome_options = Options()
    #         # chrome_options.add_argument('--headless')  # 启用无头模式
    #         chrome_options.add_argument('--start-maximized')
    #
    #         service = Service('D:\\RoArm\\chromedriver-win64\\chromedriver.exe')
    #         self.driver = webdriver.Chrome(service=service, options=chrome_options)
    #
    #         # 设置浏览器已打开标志
    #         self.browser_opened = True
    #         print("浏览器已打开")
    #     else:
    #         print("浏览器已经打开，无需重新启动")

    def initialize(self):
        '''
        打开配置页面，进行初始化
        '''
        # if not self.driver:
        #     print("错误：浏览器未打开，请先打开浏览器！")
        #     return
        self.driver.get(self.second_url)
        print("已打开初始化页面")

        # 等待并点击初始化按钮
        init_button = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/main/div[1]/section/div/div/div[2]/div/button'))
        )
        init_button.click()
        print("正在进行初始化动作")
        time.sleep(1)  # 设置时间间隔

    def set_input_and_click(self, input_value):
        '''
        设置输入框的值并点击提交按钮
        :param input_value:
        :return:
        '''
        # if not self.driver:
        #     print("错误：浏览器未打开，请先打开浏览器！")
        #     return
        try:
            self.driver.get(self.first_url)
            self.driver.refresh()
            time.sleep(1)

            input_element = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="recor-mum2"]'))
            )
            self.driver.execute_script(f"arguments[0].value = '{input_value}';", input_element)

            search_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/main/div[1]/section[2]/div/div/div[2]/div[2]/div/button'))
            )
            search_button.click()
            time.sleep(1)
        except Exception as e:
            print(f"操作失败: {e}")



    def move_to_standard(self):
        self.set_input_and_click('11')
        print("成功修改动作为11，接下来移到卡位")

    def grasp_card(self):
        self.set_input_and_click('12')
        print("成功修改动作为12，接下来抓取卡片")

    def move_to_device(self):
        self.set_input_and_click('13')
        # print("成功修改动作为13，移到刷卡器上方，17，高度更低")

    def scanning_card(self):
        self.set_input_and_click('18')    #18、19上下刷卡
        # print("成功修改动作为14，上下刷卡，16，幅度更大")

    def scanned_card(self):
        self.set_input_and_click('19')    #18、19上下刷卡
        # print("成功修改动作为14，左右刷卡")

    def get_current_time(self):
        # 获取当前时间
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # def return_card(self,functions=None,repeat_count=1)  :
    #
    #     '''重复刷卡'''
    #     if functions is None:
    #         functions = [self.move_to_device,self.scanning_card]
    #     for _ in range(repeat_count):
    #         for func in functions:
    #             try:
    #                 func()
    #                 self.index += 1
    #                 logging.info(f"第'{self.index}' 次刷卡，当前时间: {self.get_current_time()}")
    #             except Exception as e:
    #                 print(f"Error executing {func.__name__}: {e}")

    def return_card(self,functions=None,repeat_count=1)  :

        '''重复刷卡'''
        if functions is None:
            functions = [self.scanning_card,self.scanned_card]
        for _ in range(repeat_count):
            for func in functions:
                try:
                    func()
                    logging.info(f"第'{self.index}' 次刷卡，当前时间: {self.get_current_time()}")
                except Exception as e:
                    print(f"Error executing {func.__name__}: {e}")

            self.index += 1




    def put_card(self):
        self.set_input_and_click('16')
        print("成功修改动作为16，回到起点")


    def run(self):
        # self.open_browser()     #打开网页
        self.initialize()      # 初始化
        self.move_to_standard()    # 移到指定卡地点
        self.grasp_card()          # 抓取卡片
        # self.move_to_device()      #移到刷卡器位置
        # self.scanning_card()       # 进行刷卡操作
        self.return_card(repeat_count=50000)         # 循环刷卡
        self.grasp_card()           # 回到原位置
        self.put_card()            # 放下卡片
        self.driver.quit()    # 关闭浏览器

# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    automation = WebAutomation()
    automation.run()
