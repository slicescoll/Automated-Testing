import logging

import requests
import pandas as pd
from socket_server import Server
#
# class TestServer:
#     def __init__(self):
#         self.server = None
#         self.log_file = 'test_report.log'
#
#         # 设置日志配置
#         logging.basicConfig(filename=self.log_file,
#                             level=logging.INFO,
#                             format='%(asctime)s - %(message)s')
#
#     def data_report(self):
#         """
#                 获取数据并记录到日志中，同时向客户端发送报告。
#                 """
#         try:
#             data = self.startReceiveData.data
#             # 生成日志消息
#             message = f"Received data: {data}"
#
#             # 记录日志
#             logging.info(message)
#             # 自动生成测试报告
#             self.generate_test_report(data)
#
#         except Exception as e:
#             error_message = f"Error occurred while processing data: {str(e)}"
#             logging.error(error_message)
#             self.server.send_message_to_client(error_message)
#
# from datetime import datetime
#
# def generate_html_report():
#     # 打开日志文件读取内容
#     with open('test_log.txt', 'r') as log_file:
#         log_lines = log_file.readlines()
#
#     # 获取当前时间
#     current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#
#     # HTML 报告头部
#     html_content = f"""
#     <html>
#     <head>
#         <title>Test Report</title>
#         <style>
#             body {{ font-family: Arial, sans-serif; }}
#             table {{ border-collapse: collapse; width: 100%; }}
#             th, td {{ padding: 8px; text-align: left; border: 1px solid #ddd; }}
#             th {{ background-color: #f2f2f2; }}
#             .info {{ background-color: #e7f4e4; }}
#             .warning {{ background-color: #fff3cd; }}
#             .error {{ background-color: #f8d7da; }}
#             .raw {{ background-color: #e2e2e2; }}
#             .qr-code {{ background-color: #cce5ff; }}
#         </style>
#     </head>
#     <body>
#         <h1>Test Report</h1>
#         <p>Generated on: {current_time}</p>
#         <table>
#             <thead>
#                 <tr>
#                     <th>Timestamp</th>
#                     <th>Log Level</th>
#                     <th>Message</th>
#                 </tr>
#             </thead>
#             <tbody>
#     """
#
#     # 将日志逐行转换为表格行
#     for line in log_lines:
#         line = line.strip()  # 去除行首尾的空白字符
#
#         # 如果行是纯数字，作为原始数据处理
#         if line.isdigit():
#             html_content += f"""
#                 <tr class="raw">
#                     <td>{line}</td>
#                     <td>RAW</td>
#                     <td>{line}</td>
#                 </tr>
#             """
#         # 检查行是否包含二维码生成相关信息
#         elif '二维码生成成功' in line or '显示二维码' in line:
#             html_content += f"""
#                 <tr class="qr-code">
#                     <td>{line.split(' ')[0]}</td>
#                     <td>QR Code</td>
#                     <td>{line}</td>
#                 </tr>
#             """
#         # 检查行是否为空或格式不对，跳过
#         elif len(line.split(' ', 2)) >= 3:
#             parts = line.split(' ', 2)  # 分割时间戳、级别和消息
#             timestamp, level, message = parts
#
#             # 根据日志级别选择背景颜色
#             if 'INFO' in level:
#                 css_class = 'info'
#             elif 'WARNING' in level:
#                 css_class = 'warning'
#             elif 'ERROR' in level:
#                 css_class = 'error'
#             else:
#                 css_class = ''  # 默认没有特定颜色
#
#             # 添加日志到 HTML 表格
#             html_content += f"""
#                 <tr class="{css_class}">
#                     <td>{timestamp}</td>
#                     <td>{level}</td>
#                     <td>{message}</td>
#                 </tr>
#             """
#
#     # HTML 表格尾部
#     html_content += """
#             </tbody>
#         </table>
#     </body>
#     </html>
#     """
#
#     # 保存为 HTML 文件
#     with open('test_report.html', 'w') as report_file:
#         report_file.write(html_content)
#
#     print("HTML report generated: test_report.html")
#
# # 生成测试报告
# generate_html_report()


from datetime import datetime

'''生成html测试报告'''
def generate_html_report():
    # 打开日志文件读取内容
    try:
        with open('test_log.txt', 'r') as log_file:
            log_lines = log_file.readlines()
    except FileNotFoundError:
        print("Error: Log file 'test_log.txt' not found!")
        return

    # 获取当前时间
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # HTML 报告头部
    '''不同类型对应不同的颜色'''
    html_content = f"""
    <html>
    <head>
        <title>Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ padding: 8px; text-align: left; border: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            .info {{ background-color: #e7f4e4; }}
            .warning {{ background-color: #fff3cd; }}
            .error {{ background-color: #f8d7da; }}
            .raw {{ background-color: #FFC0CB; }}  
            .qr-code {{ background-color: #cce5ff; }}
            .special-background {{ background-color: #ffeb3b; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Test Report</h1>
        <p>Generated on: {current_time}</p>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Log Level</th>
                    <th>Message</th>
                </tr>
            </thead>
            <tbody>
    """


    # 处理每一行日志并转换为 HTML 表格行
    for line in log_lines:
        line = line.strip()  # 去除行首尾的空白字符
        if not line:
            continue  # 跳过空行

        # 解析日志行
        # if line.isalnum():  #digit 数字   isalnum  判断数字或字符  无法识别带空格的字符如：31 321a2b3c4d31 32
        #     html_content += generate_log_row(line, 'RAW', 'raw', line)
        if all(c.isalnum() or c.isspace() for c in line):  #判断数字或字符并允许存在空格
            html_content += generate_log_row(line, 'RAW', 'raw', line)
        elif 'sample code' in line or '显示二维码' in line:
            timestamp = line.split(' ')[0]
            html_content += generate_log_row(timestamp, 'QR Code', 'qr-code', line)
        elif 'config code' in line or '刷卡' in line:
            timestamp = line.split(' ')[0]
            html_content += generate_log_row(timestamp, 'Special', 'special-background', line)
        elif 'DEBUG' in line:  # 如果您希望显示调试信息，则取消注释这一行
            # 如果不想添加 debug 信息到 html_content，可以选择跳过
            continue  # 跳过 debug 日志，直接处理下一行
        # elif len(line.split(' ', 2)) >= 3:
        #     timestamp, level, message = line.split(' ', 2)
        #     css_class = get_css_class(level)
        #     html_content += generate_log_row(timestamp, level, css_class, message)
        elif len(line.split(' ', 2)) >= 3:
            parts = line.split(' ', 2)
            timestamp, level, message = parts[0], parts[1], parts[2]
            css_class = get_css_class(level)
            html_content += generate_log_row(timestamp, level, css_class, message)

    # HTML 表格尾部
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    # 保存为 HTML 文件
    with open('test_report.html', 'w') as report_file:
        report_file.write(html_content)

    print("HTML report generated: test_report.html")


def generate_log_row(timestamp, level, css_class, message):
    """生成单行日志的 HTML 表格行"""
    return f"""
        <tr class="{css_class}">
            <td>{timestamp}</td>
            <td>{level}</td>
            <td>{message}</td>
        </tr>
    """


def get_css_class(level):
    """根据日志级别返回对应的 CSS 类"""
    level = level.upper()  # 统一转为大写，防止大小写不一致
    if 'INFO' in level:
        return 'info'
    elif 'WARNING' in level:
        return 'warning'
    elif 'ERROR' in level:
        return 'error'
    return ''  # 默认无背景色


# 生成测试报告
generate_html_report()
