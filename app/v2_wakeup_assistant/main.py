# -*- coding: utf-8 -*-
# 导入操作系统模块，用于与操作系统交互（如路径操作、环境变量等）
import os

# 导入队列模块，用于线程间通信或数据交换
import queue

# 导入信号模块，用于处理 Unix/Linux 系统信号（如中断、终止等）
import signal

# 导入异步 I/O 模块 asyncio，用于编写异步程序（协程、事件循环等）
import asyncio

# 导入 sys 模块，用于访问解释器相关的变量和函数（如命令行参数、退出等）
import sys

# 导入 time 模块，用于时间相关操作（如 sleep、获取当前时间）
import time

# 导入 traceback 模块，用于打印异常堆栈信息，便于调试
import traceback
from difflib import SequenceMatcher

# 导入 qasync 模块，将 Qt 与 asyncio 结合，实现异步 GUI 应用
import qasync

# 从 PyQt5 导入 QtWidgets 模块，提供各种窗口控件类
from PyQt5 import QtWidgets

# 从 QtCore 模块导入 pyqtSignal 和 QObject，用于定义信号/槽机制，QTimer 用于定时任务
from PyQt5.QtCore import pyqtSignal, QObject, QTimer, Qt

# 从 QtGui 模块导入 QIcon 和 QPixmap，用于图标和图像显示
from PyQt5.QtGui import QIcon, QPixmap

# 从 QtWidgets 模块导入常用界面组件：QApplication（主应用）、QMainWindow（主窗口）、QListWidget（列表控件），
# QMessageBox（消息框）、QListWidgetItem（列表项）、QDialog（对话框）、QWidget（基础控件）、QLabel（标签）
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QMessageBox, QListWidgetItem, QDialog, QWidget, QLabel

# 异步 OpenAI 客户端，用于调用 OpenAI 的 API 接口
from openai import AsyncOpenAI

# 导入自定义模块 settings_dialog 中的 Ui_Dialog 类，用于设置对话框的 UI 布局
from UI.settings_dialog import Ui_Dialog

# 导入自定义模块 ui_mainwindow 中的 Ui_MainWindow 类，用于主窗口的 UI 布局
from UI.ui_mainwindow import Ui_MainWindow

# 从 utils.logging_manager 导入日志工具函数 setup_logging 和 get_logger，用于初始化日志系统并获取日志记录器
from utils.logging_manager import get_logger, setup_logging

# 初始化日志系统，配置日志格式、输出方式等
setup_logging()

# 从 utils.client_change 导入 ClientChange 类，可能用于切换客户端服务（如本地 vs 远程）
from utils.client_change import ClientChange

# 从 utils.audio_manager 导入音频管理相关类：
# AudioRecorderWithVAD（带语音活动检测的录音器）、SoundToText（语音转文字）、TextToSound（文字转语音），
# PlayText（播放文本语音）、PlayWakeUp（播放唤醒音效）
from utils.audio_manager import AudioRecorderWithVAD, SoundToText, TextToSound, PlayText, PlayWakeUp

# 从 utils.mqtt_manager 导入 MQTTClient 类，用于连接和使用 MQTT 协议进行消息通信
from utils.mqtt_manager import MQTTClient

# 从 utils.chat_manager 导入 ChatWithLLM 类，用于与大语言模型进行聊天交互
from utils.chat_manager import ChatWithLLM

# 从 utils.set_message_item 导入 SetMessageItem 类，用于在界面上设置消息条目（例如聊天记录）
from utils.set_message_item import SetMessageItem

# 从 utils.config_manager 导入 ConfigManager 类，用于读取和写入应用程序配置
from utils.config_manager import ConfigManager

# 从 utils.camera_manager 导入 CameraProcessor 类，用于摄像头图像处理功能
from utils.camera_manager import CameraProcessor

# 从 utils.wake_manager 导入 WakeWordDetector（唤醒词检测器）和 AssistantState（助手状态机）
from utils.wake_manager import WakeWordDetector, AssistantState

# 获取当前模块的日志记录器实例，用于记录日志信息
logger = get_logger(__name__)

# 实例化配置管理器对象，加载配置文件或默认配置
config = ConfigManager()

# 更新配置项 'CHOICE.SERVICE' 的值为 'LOCAL_SERVICE'，表示选择本地服务作为后端
config.update_config('CHOICE.SERVICE', 'LOCAL_SERVICE')


class SettingsDialog(QDialog):
    # 定义自定义信号：当配置保存成功时发出此信号
    config_save_success = pyqtSignal()

    # 定义另一个自定义信号：当配置保存失败时发出此信号
    # 参数为 (错误来源函数名, 错误信息)
    config_save_error = pyqtSignal(str, str)

    def __init__(self, parent=None):
        # 调用父类 QDialog 的构造函数
        super().__init__(parent)

        # 移除窗口右上角的帮助按钮（问号），避免不必要的交互干扰
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # 实例化 UI 对象（由 Qt Designer 生成的界面类）
        self.ui = Ui_Dialog()

        # 设置当前对话框的界面布局
        self.ui.setupUi(self)

        # 初始化界面结构与样式设置
        self._init_ui()

        # 连接控件的信号与槽函数
        self._connect_signals()

        # 从配置文件中加载数据并显示到界面上
        self._load_config()

    """初始化 UI 页面结构与默认显示页"""
    def _init_ui(self):
        # 定义页面映射关系：页面名称 -> (页面组件, 切换按钮)
        self.page_map = {
            "LOCAL_SERVICE": (self.ui.local_service_page, self.ui.local_service_btn),
            "SILICONFLOW": (self.ui.siliconflow_page, self.ui.siliconflow_service_btn),
        }

        # 默认显示本地服务页面
        self.change_page('LOCAL_SERVICE')

        self.url_qlabel = self.ui.url_qlabel
        self.url_qlabel.setText('<a href="https://account.siliconflow.cn/zh/login?redirect=https%3A%2F%2Fcloud.siliconflow.cn&invitation=07eiFvRu">点我创建API')
        self.url_qlabel.setOpenExternalLinks(True)

    """连接各个控件的点击/状态变化事件与对应的处理函数"""
    def _connect_signals(self):
        # 遍历 page_map 中的所有按钮，并连接它们的 clicked 信号到 change_page 函数
        for page_name, (_, btn) in self.page_map.items():
            btn.clicked.connect(lambda _, pn=page_name: self.change_page(pn))

        # 保存按钮点击后触发 save_config 方法
        self.ui.save_btn.clicked.connect(self.save_config)
        # 恢复默认按钮点击后触发 save_default_config 方法
        self.ui.default_btn.clicked.connect(self.save_default_config)

    """切换设置页面"""
    def change_page(self, page_name):
        widget, _ = self.page_map[page_name]
        # 使用 stackedWidget 控件切换页面
        self.ui.stackedWidget.setCurrentWidget(widget)
        logger.info(f'切换到页面：{page_name}')

    """恢复默认配置并保存到文件"""
    def save_default_config(self):
        # 弹出确认对话框
        reply = QMessageBox.question(self, '确认', '确定要恢复默认配置吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        # 获取默认配置并替换当前配置
        default_config = ConfigManager.default_config_dict()
        config._config = default_config.copy()

        # 尝试保存默认配置到文件
        if config.save_config(default_config):
            QMessageBox.information(self, "提示", "已恢复默认配置！")
        else:
            QMessageBox.warning(self, "错误", "无法保存默认配置到文件。")

        # 重新加载配置到 UI
        self._load_config()
        # 发送配置保存成功信号
        self.config_save_success.emit()
        logger.info("已恢复默认配置！")

    """将用户在界面中修改的配置保存回配置文件"""
    def save_config(self):
        try:
            # 文本字段映射表：配置项路径 -> 对应输入框控件
            text_fields = {
                "LOCAL_SERVICE.API_KEY": self.ui.local_api_key,
                "LOCAL_SERVICE.LLM": self.ui.local_llm,
                "LOCAL_SERVICE.VL": self.ui.local_vl,
                "SILICONFLOW.API_KEY": self.ui.siliconflow_api_key,
                "SILICONFLOW.LLM": self.ui.siliconflow_llm_name,
                "SILICONFLOW.SPEECH_REC": self.ui.siliconflow_speech_rec,
                "SILICONFLOW.SPEECH_SYN": self.ui.siliconflow_speech_syn,
                "SILICONFLOW.VL": self.ui.siliconflow_vl,
                "MQTT_SERVICE.BROKER": self.ui.mqtt_server,
                "MQTT_SERVICE.PUB_TOPIC": self.ui.mqtt_pub,
                "MQTT_SERVICE.SUB_TOPIC": self.ui.mqtt_sub,
            }

            # 遍历文本字段，更新配置
            for key, widget in text_fields.items():
                value = widget.text().strip()
                if value:
                    config.update_config(key, value)

            # 处理端口号字段，转换为整数
            port_text = self.ui.mqtt_port.text().strip()
            if port_text:
                config.update_config("MQTT_SERVICE.PORT", int(port_text) if port_text.isdigit() else port_text)

            # 更新复选框相关配置
            config.update_config("WAKE_WORD_OPTIONS.USE_WAKE_WORD", self.ui.check_wake.isChecked())

            # 提示用户保存成功
            QMessageBox.information(self, "提示", "配置保存成功！")
            logger.info("配置保存成功！")

            # 发出自定义信号：配置保存成功
            self.config_save_success.emit()
        except Exception as e:
            # 捕获异常并记录日志
            logger.error(f"配置保存失败: {e}")
            # 发出错误信号
            self.config_save_error.emit('save_config', f"配置保存失败: {e}")

    """将配置文件内容加载并显示到 UI 控件中"""
    def _load_config(self):
        # 从配置文件重新加载配置数据
        config.reload_from_file()

        # 文本字段映射表：配置项路径 -> 输入框控件
        text_fields = {
            "LOCAL_SERVICE.API_KEY": self.ui.local_api_key,
            "LOCAL_SERVICE.LLM": self.ui.local_llm,
            "LOCAL_SERVICE.VL": self.ui.local_vl,
            "LOCAL_SERVICE.SPEECH_REC": self.ui.local_speech_rec,
            "SILICONFLOW.API_KEY": self.ui.siliconflow_api_key,
            "SILICONFLOW.LLM": self.ui.siliconflow_llm_name,
            "SILICONFLOW.SPEECH_REC": self.ui.siliconflow_speech_rec,
            "SILICONFLOW.SPEECH_SYN": self.ui.siliconflow_speech_syn,
            "SILICONFLOW.VL": self.ui.siliconflow_vl,
            "MQTT_SERVICE.BROKER": self.ui.mqtt_server,
            "MQTT_SERVICE.PUB_TOPIC": self.ui.mqtt_pub,
            "MQTT_SERVICE.SUB_TOPIC": self.ui.mqtt_sub,
        }

        # 遍历并设置每个文本框的内容
        for key, widget in text_fields.items():
            widget.setText(str(config.get_config(key, "")))

        # 设置 MQTT 端口号
        port = config.get_config("MQTT_SERVICE.PORT", "")
        self.ui.mqtt_port.setText(str(port))

        # 加载复选框状态
        use_wake = config.get_config("WAKE_WORD_OPTIONS.USE_WAKE_WORD")

        # 设置复选框勾选状态
        self.ui.check_wake.setChecked(use_wake)
        logger.info("加载配置到UI成功！")


# 定义一个名为 LoadingOverlay 的类，继承自 QWidget
# 用于创建一个覆盖在父窗口上的加载遮罩层（带背景透明度和居中加载图标的界面）
class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        # 调用父类 QWidget 的初始化方法
        super().__init__(parent)

        # 获取父控件的宽度和高度，并保存为实例变量
        self.width = parent.width()
        self.height = parent.height()

        # 设置当前控件的固定大小为与父控件相同
        # 这样遮罩层会完全覆盖父控件区域
        self.setFixedSize(self.width, self.height)

        # 使用样式表设置背景颜色为半透明黑色（RGBA：R=0, G=0, B=0, A=50）
        # rgba 中的第四个参数是透明度（alpha），值范围 0~255
        self.setStyleSheet("background-color: rgba(0, 0, 0, 50);")

        # 设置窗口标志：
        # Qt.SubWindow 表示这是一个子窗口
        # Qt.FramelessWindowHint 表示无边框窗口
        self.setWindowFlags(Qt.SubWindow | Qt.FramelessWindowHint)

        # 设置属性：禁用鼠标穿透事件（即遮罩层会拦截鼠标操作）
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        # 设置属性：不使用系统默认背景（防止系统绘制背景干扰）
        self.setAttribute(Qt.WA_NoSystemBackground, False)

        # 启用样式表背景绘制，确保 setStyleSheet() 生效
        self.setAttribute(Qt.WA_StyledBackground, True)

        # 创建一个 QLabel 控件用于显示加载图片
        self.image_label = QLabel(self)

        # 加载资源文件中的图片，路径为 ":/icons/loading.png"
        # QPixmap 是 Qt 用于处理图像的类
        pixmap = QPixmap(":/icons/loading.png")  # 注意：这个路径应存在于 Qt 的资源系统中

        # 将 QPixmap 设置到 QLabel 上，使其显示该图片
        self.image_label.setPixmap(pixmap)

        # 设置图片标签的固定大小为图片原始尺寸
        self.image_label.setFixedSize(pixmap.size())

        # 计算图片在遮罩层中的居中位置，并移动 QLabel 到该位置
        # (窗口宽度 - 图片宽度) // 2 → 水平居中
        # (窗口高度 - 图片高度) // 2 → 垂直居中
        self.image_label.move(
            (self.width - pixmap.width()) // 2,
            (self.height - pixmap.height()) // 2
        )

        # 设置图片标签支持背景透明（例如 PNG 图像的透明通道）
        self.image_label.setAttribute(Qt.WA_TranslucentBackground)

        # 将图片标签提升到所有子控件的最上层，确保不会被其他控件遮挡
        self.image_label.raise_()

        # 显示遮罩层控件
        self.show()


# 定义主窗口类 MyMainWindow，继承自 QMainWindow
class MyMainWindow(QMainWindow):
    def __init__(self):
        # 调用父类 QMainWindow 的构造函数
        super().__init__()

        # 设置窗口标题为“多模态大模型智能助手”
        self.setWindowTitle("多模态大模型智能助手")

        # 创建 UI 对象并调用 setupUi 方法初始化界面布局（来自 Qt Designer 生成的 Ui_MainWindow）
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 设置应用程序图标，使用资源文件中的图标路径 ":/icons/icon.png"
        self.setWindowIcon(QIcon(":/icons/icon.png"))

        # 获取界面上的 QListWidget 控件 chatListWidget，并赋值给实例变量
        self.chatListWidget = self.ui.chatListWidget

        # 设置聊天列表控件的垂直滚动模式为像素级滚动（Smooth Scrolling）
        self.chatListWidget.setVerticalScrollMode(QListWidget.ScrollPerPixel)

        # 使用样式表设置 QListWidget 中项的悬停和选中背景为透明
        self.chatListWidget.setStyleSheet("""
                                QListWidget::item:hover {
                                    background-color: transparent;
                                }
                                QListWidget::item:selected {
                                    background-color: transparent;
                                }
                            """)

        # 从配置模块获取唤醒词相关参数
        self.use_wake_word = config.get_config("WAKE_WORD_OPTIONS.USE_WAKE_WORD")

        # 获取界面上的各个控件引用并保存为实例变量
        self.choose_service = self.ui.comboBox              # 下拉框：选择服务提供商
        self.openCameraButton = self.ui.openCameraButton    # 打开摄像头按钮
        self.closeCameraButton = self.ui.closeCameraButton  # 关闭摄像头按钮
        self.cameraDisplay = self.ui.cameraDisplay          # 显示摄像头画面的组件
        self.recordButton = self.ui.speak_button            # 录音按钮
        self.endButton = self.ui.end_button                 # 结束按钮
        self.settingsButton = self.ui.settingsButton        # 设置按钮

        # 初始化对话相关的属性
        self.bot_item = None     # 存储机器人回复的消息条目
        self.bot_message = None  # 存储机器人当前正在处理的消息内容

        # 初始化助手状态为“空闲”状态
        self.assistant_state = AssistantState.IDLE

        # 用于保存后台异步任务（协程），防止被垃圾回收器提前销毁
        self.background_tasks = set()

        # 初始化录音状态标志位
        self.is_recording = False

        # 标志是否正在进行中止操作
        self.is_aborting = False

        # 初始化 FPS 相关变量
        self.fpsLabel = None       # FPS 显示标签（可能是一个 QLabel）
        self.frame_count = 0       # 帧计数器
        self.start_time = time.time()  # 开始时间戳，用于计算 FPS

        # 创建 LoadingOverlay 遮罩层，并传入当前窗口作为父控件
        self.loading_overlay = LoadingOverlay(self)

        # 连接按钮点击事件到对应的槽函数（事件响应函数）

        # 点击打开摄像头按钮时执行 open_camera 方法
        self.openCameraButton.clicked.connect(self.open_camera)

        # 点击关闭摄像头按钮时执行 close_camera 方法
        self.closeCameraButton.clicked.connect(self.close_camera)

        # 点击录音按钮时执行 toggle_recording 方法
        self.recordButton.clicked.connect(self.toggle_recording)

        # 点击结束按钮时执行 end_button 方法
        self.endButton.clicked.connect(self.end_button)

        # 点击设置按钮时执行 open_settings_dialog 方法
        self.settingsButton.clicked.connect(self.open_settings_dialog)

        # 下拉框选项改变时触发 change_service 方法
        self.choose_service.currentTextChanged.connect(self.change_service)

    # 异步初始化方法 thread_init，用于在主线程中启动异步加载过程
    async def thread_init(self):
        # 显示加载遮罩层
        self.loading_overlay.show()

        try:
            # 创建 FPS 显示标签（可能是 QLabel）
            await self.create_fps_label()

            # 获取单例模式下的 MQTT 客户端实例
            self.mqtt_client = MQTTClient.get_instance()

            # 创建音频录制子线程对象
            self.record_worker = AudioRecorderWithVAD()

            # 连接录音成功信号到 handle_record_success_signal 方法
            self.record_worker.record_success.connect(self.handle_record_success_signal)

            # 连接录音错误信号到 handle_error_signal 方法
            self.record_worker.record_error.connect(self.handle_error_signal)

            # 连接语音结束信号到 handle_speech_ended_signal 方法
            self.record_worker.speech_ended.connect(self.handle_speech_ended_signal)

            # 连接超时退出信号到 handle_timeout_exit 方法
            self.record_worker.timeout_exit.connect(self.handle_timeout_exit)

            # 从配置中获取当前服务提供方名称（如 OpenAI、Azure 等）
            self.service = config.get_config('CHOICE.SERVICE')

            # 获取该服务的 API 密钥
            self.api_key = config.get_config(f'{self.service}.API_KEY')

            # 获取该服务的 API 地址
            self.base_url = config.get_config(f'{self.service}.URL')

            # 初始化 AsyncOpenAI 客户端（异步 OpenAI 接口）
            self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            logger.info(f"初始化 OpenAI 客户端成功，当前服务为 {self.service}")

            # 初始化语音转文本子线程
            self.stt_worker = SoundToText(self.client)

            # 连接语音识别成功信号到 handle_stt_success_signal 方法
            self.stt_worker.on_stt_success(self.handle_stt_success_signal)

            # 连接语音识别错误信号到 handle_error_signal 方法
            self.stt_worker.on_stt_error(self.handle_error_signal)

            # 记录日志：语音转文本初始化成功
            logger.info("语音转文本功能初始化成功")

            # 初始化句子队列（最大容量为20），用于传递用户输入的语句
            self.sentences_queue = queue.Queue(maxsize=20)

            # 初始化与大语言模型交互的线程
            self.chat_worker = ChatWithLLM(self.client, self.sentences_queue)

            # 连接开始对话信号到 handle_chat_start_signal 方法
            self.chat_worker.on_chat_start(self.handle_chat_start_signal)

            # 连接打开摄像头信号到 handle_chat_open_camera_signal 方法
            self.chat_worker.on_open_camera(self.handle_chat_open_camera_signal)

            # 连接函数调用信号到 handle_chat_function_call_signal 方法
            self.chat_worker.on_function_call(self.handle_chat_function_call_signal)

            # 连接对话错误信号到 handle_error_signal 方法
            self.chat_worker.on_chat_error(self.handle_error_signal)

            # 记录日志：大模型对话初始化成功
            logger.info("大模型对话功能初始化成功")

            # 初始化音频队列（最大容量为20），用于传递合成后的语音数据
            self.audio_queue = queue.Queue(20)

            # 初始化文本转语音子线程
            self.tts_worker = TextToSound(self.client, self.audio_queue, self.sentences_queue)

            # 连接 TTS 开始信号到 handle_tts_start_signal 方法
            self.tts_worker.on_tts_start(self.handle_tts_start_signal)

            # 连接 TTS 完成信号到 handle_tts_done_signal 方法
            self.tts_worker.on_tts_done(self.handle_tts_done_signal)

            # 连接 TTS 错误信号到 handle_error_signal 方法
            self.tts_worker.on_tts_error(self.handle_error_signal)

            # 记录日志：文本转语音初始化成功
            logger.info("文本转语音功能初始化成功")

            # 初始化播放器子线程，用于播放语音合成结果
            self.player_worker = PlayText(self.audio_queue)

            # 连接播放开始信号到 handle_play_start_signal 方法
            self.player_worker.play_start.connect(self.handle_play_start_signal)

            # 连接播放显示信号到 handle_play_show_signal 方法
            self.player_worker.play_show.connect(self.handle_play_show_signal)

            # 连接播放完成信号到 handle_play_finish_signal 方法
            self.player_worker.play_finish.connect(self.handle_play_finish_signal)

            # 连接播放错误信号到 handle_error_signal 方法
            self.player_worker.play_error.connect(self.handle_error_signal)

            # 记录日志：播报功能初始化成功
            logger.info("播报功能初始化成功")

            # 初始化唤醒词检测子线程
            logger.info("正在检测是否启动语音唤醒功能...")

            self.wake_worker = WakeWordDetector()

            # 连接唤醒词检测成功信号到 handle_wake_detected_signal 方法
            self.wake_worker.wake_detected.connect(self.handle_wake_detected_signal)

            # 如果启用了唤醒词并且使用本地 Vosk 模型
            if self.use_wake_word:
                # 如果唤醒检测线程未运行，则启动
                if not self.wake_worker.isRunning():
                    self.wake_worker.start()
                    logger.info("本地vosk唤醒词检测功能启动成功")
            # 如果未启用唤醒词
            else:
                logger.info("语音唤醒功能未启动！！！")

            # 初始化唤醒提示播放器
            self.play_waker = PlayWakeUp()

            # 初始化摄像头处理子线程
            self.camera_processor = CameraProcessor()

            # 连接摄像头帧捕获信号到 handle_camera_success_signal 方法
            self.camera_processor.camera_frame.connect(self.handle_camera_success_signal)

            # 连接摄像头错误信号到 handle_error_signal 方法
            self.camera_processor.camera_error.connect(self.handle_error_signal)

            # 记录日志：摄像头处理初始化成功
            logger.info("摄像头处理初始化成功")

            # 初始化完成后隐藏加载遮罩层
            self.loading_overlay.close()

        # 捕获初始化过程中发生的任何异常
        except Exception as e:
            # 记录错误日志
            logger.error(f"初始化失败: {e}")

            # 弹出错误对话框提示用户
            QMessageBox.critical(self, "错误", f"初始化失败: {e}")

            # 强制退出程序
            os._exit(0)

    # 异步槽函数：当播放完成信号触发时执行此方法
    @qasync.asyncSlot()
    async def handle_play_finish_signal(self):
        try:
            # 记录日志：播报已完成
            logger.info("播放完成")

            # 如果播放线程正在运行，则停止它
            if self.player_worker.isRunning():
                self.player_worker.stop()
                logger.info("停止播报...")

            # 判断当前助手状态是否为“说话中”
            if self.assistant_state == AssistantState.SPEAKING:
                # 如果是唤醒状态下播报完毕，进入“聆听”状态
                self.assistant_state = AssistantState.LISTENING

                # 短暂等待确保播放线程完全释放资源
                time.sleep(0.1)

                # 如果录音线程未运行，则启动录音线程，并传入当前状态
                if not self.record_worker.isRunning():
                    self.record_worker.get_assistant_state(self.assistant_state)
                    self.record_worker.start()
                    logger.info("开始录音...")

                # 如果不是中止操作，更新按钮文本为“聆听中...”
                if not self.is_aborting:
                    self.recordButton.setText('聆听中...')

            else:
                # 非唤醒流程（例如按钮点击后的对话），恢复按钮状态
                if not self.is_aborting:
                    self.recordButton.setText('开始录音')
                    self.recordButton.setEnabled(True)  # 启用按钮

            # 清空当前机器人消息项和内容引用
            self.bot_item = None
            self.bot_message = None

        except Exception as e:
            # 捕获异常并记录错误日志
            logger.error(f"处理播放完成信号时发生错误: {e}")
            # 显示错误提示框
            QMessageBox.critical(self, "错误", f"播放完成处理失败：{e}")

    # 异步槽函数：在播报过程中实时更新聊天界面（显示文本）
    @qasync.asyncSlot(str)
    async def handle_play_show_signal(self, text):
        try:
            # 如果还没有创建 bot 的消息项，则新建一个
            if self.bot_item is None:
                # 创建一个新的 QListWidgetItem 用于展示消息
                self.bot_item = QListWidgetItem(self.chatListWidget)

                # 保存当前收到的文本内容
                self.bot_message = text

                # 创建自定义的消息控件（可能是气泡样式），设置为非用户发送
                widget = SetMessageItem(self.bot_message, is_user=False)

                # 将控件添加到列表中
                self.chatListWidget.addItem(self.bot_item)

                # 设置该项的高度与控件一致
                self.bot_item.setSizeHint(widget.sizeHint())

                # 将自定义控件绑定到该 item 上
                self.chatListWidget.setItemWidget(self.bot_item, widget)

            else:
                # 如果已有 bot 消息项，则追加新文本
                self.bot_message += text

                # 更新 UI 控件内容
                widget = SetMessageItem(self.bot_message, is_user=False)

                # 更新 item 的高度和内容
                self.bot_item.setSizeHint(widget.sizeHint())
                self.chatListWidget.setItemWidget(self.bot_item, widget)

            # 自动滚动到底部，显示最新消息
            self.chatListWidget.scrollToBottom()

        except Exception as e:
            # 捕获异常并记录错误日志
            logger.error(f"更新聊天列表失败: {e}")

            # 显示错误提示框
            QMessageBox.critical(self, "错误", f"更新聊天列表失败: {e}")

    # 异步槽函数：当播放开始时执行此方法
    @qasync.asyncSlot()
    async def handle_play_start_signal(self):
        try:
            # 记录日志：开始播报
            logger.info("开始播报")

            # 如果不是中止操作，更新按钮文本为“语音播报中...”
            if not self.is_aborting:
                self.recordButton.setText('语音播报中...')

            # 如果当前处于“思考中”状态，改为“说话中”状态
            if self.assistant_state == AssistantState.THINKING:
                self.assistant_state = AssistantState.SPEAKING

            # 如果启用了本地 Vosk 唤醒词检测，并且线程未运行，则启动唤醒检测线程
            if self.use_wake_word:
                if not self.wake_worker.isRunning():
                    self.wake_worker.start()

        except Exception as e:
            # 捕获异常并记录错误日志
            logger.error(f"启动播报失败: {e}")

            # 显示错误提示框
            QMessageBox.critical(self, "错误", f"启动播报失败: {e}")

    # 异步槽函数：当语音合成完成时触发
    @qasync.asyncSlot()
    async def handle_tts_done_signal(self):
        try:
            # 记录日志：语音合成已完成
            logger.info("语音合成完成")

            # 如果存在 tts_task 并且任务未完成，则取消该任务
            if hasattr(self, 'tts_task') and self.tts_task:
                self.tts_worker.stop()  # 停止 TTS 子线程
                self.tts_task.cancel()  # 取消异步任务
                self.tts_task = None  # 清空任务引用
                logger.info("已取消 TTS 任务")

        except Exception as e:
            # 捕获异常并记录错误日志
            logger.error(f"语音合成处理失败: {e}")

            # 显示错误提示框
            QMessageBox.critical(self, "错误", f"语音合成处理失败: {e}")

    # 异步槽函数：当语音合成开始时触发
    @qasync.asyncSlot()
    async def handle_tts_start_signal(self):
        try:
            # 记录日志：开始进行语音合成
            logger.info("开始语音合成...")

            # 如果不是中止状态，更新按钮显示为“语音合成中...”
            if not self.is_aborting:
                self.recordButton.setText('语音合成中...')

            # 如果播报子线程未运行，则启动它
            if not self.player_worker.isRunning():
                self.player_worker.start()
                logger.info('启动播报功能...')

        except Exception as e:
            # 捕获异常并记录错误日志
            logger.error(f"语音合成启动失败: {e}")

            # 显示错误提示框
            QMessageBox.critical(self, "错误", f"语音合成启动失败：{e}")

    # 异步槽函数：当大模型调用插件或工具时触发
    @qasync.asyncSlot()
    async def handle_chat_function_call_signal(self):
        # 如果不是中止状态，更新按钮显示为“工具执行中”
        if not self.is_aborting:
            self.recordButton.setText("工具执行中")

    # 异步槽函数：当大模型请求打开摄像头时触发
    @qasync.asyncSlot()
    async def handle_chat_open_camera_signal(self):
        # 显示一个错误提示对话框：“请打开摄像头”
        self.show_error_dialog('请打开摄像头', '警告')

        # 如果不是中止状态，更新按钮为“开始录音”并启用按钮
        if not self.is_aborting:
            self.recordButton.setText("开始录音")
            self.recordButton.setEnabled(True)

        # 执行清理所有后台任务的方法（可能是关闭线程、停止播放等）
        await self.cleanup_all_tasks()

    # 异步槽函数：当大模型开始回复用户消息时触发
    @qasync.asyncSlot()
    async def handle_chat_start_signal(self):
        try:
            # 记录日志：大模型开始生成回复内容
            logger.info("大模型开始回复...")

            # 创建一个后台异步任务来运行 TTS 子线程
            self.tts_task = self.create_background_task(self.tts_worker.run())

            # 记录日志：准备进行语音合成
            logger.info('准备进行语音合成...')

        except Exception as e:
            # 捕获异常并记录错误日志
            logger.error(f"大模型回复阶段出错: {e}")

            # 显示错误提示框
            QMessageBox.critical(self, "错误", f"大模型回复失败：{e}")

    # 异步槽函数：当检测到用户发出“退出”指令时调用
    @qasync.asyncSlot()
    async def handle_exit_detected_signal(self):
        try:
            # 记录日志：开始执行退出流程
            logger.info('检测到退出指令，正在退出...')

            # 将助手状态设置为“空闲”，表示当前无任务
            self.assistant_state = AssistantState.IDLE

            # 日志提示：准备播放退出提示音
            logger.info('正在播报退出指令...')

            # 设置要播放的退出提示音频文件路径
            self.play_waker.get_file_path('./resources/response/exit_response.wav')

            # 启动音频播放线程（播放“好的，再见！”之类的提示语）
            self.play_waker.start()

            # 等待音频播放完成（异步等待）
            while self.play_waker.isRunning():
                await asyncio.sleep(0.1)

            # 如果不是中止操作，则恢复录音按钮的状态
            if not self.is_aborting:
                self.recordButton.setText('开始录音')
                self.recordButton.setEnabled(True)

            # 如果启用了本地 Vosk 唤醒词检测，并且唤醒线程未运行，则重新启动
            if self.use_wake_word:
                if not self.wake_worker.isRunning():
                    self.wake_worker.start()
                    logger.info('启动唤醒功能...')

        except Exception as e:
            # 捕获异常并记录错误日志
            logger.error(f"退出流程异常：{e}")

            # 显示错误提示框
            QMessageBox.critical(self, "错误", f"退出流程失败：{e}")

    # 计算两个字符串的相似度
    def similar(self, a, b):
        """
        使用 SequenceMatcher 计算字符串 a 和 b 的相似度。

        参数:
            a (str): 第一个字符串
            b (str): 第二个字符串

        返回:
            float: 相似度，范围 [0, 1]，1 表示完全相同，0 表示完全不同
        """
        # SequenceMatcher 用于比较两个序列（这里是字符串）
        # 第一个参数 None 表示不使用自定义字符比较函数
        matcher = SequenceMatcher(None, a, b)

        # ratio() 返回两个字符串的相似度
        # 公式为 2.0 * M / T
        # M = 匹配字符数，T = 两个字符串总长度
        return matcher.ratio()

    # 异步槽函数：当语音识别完成后触发，携带识别出的文本内容
    @qasync.asyncSlot(str)
    async def handle_stt_success_signal(self, text):
        try:
            EXIT_KEYWORDS = ["退下", "退下吧", "拜拜"]
            FAILED_KEYWORDS = ["请求失败"]

            # 判断是否识别到了“退下”关键词
            if any(self.similar(text, kw) > 0.7 for kw in EXIT_KEYWORDS):
                await self.handle_exit_detected_signal()

            # 如果识别结果为空，说明用户没说话
            elif text == '':
                logger.info('用户没有说话...')
                # 显示警告对话框
                self.show_error_dialog('用户没有说话...', '警告')
                # 清理所有后台任务（停止播放、录音等）
                await self.cleanup_all_tasks()
                # 恢复按钮状态
                if not self.is_aborting:
                    self.recordButton.setText('开始录音')
                    self.recordButton.setEnabled(True)

            elif any(self.similar(text, kw) > 0.7 for kw in FAILED_KEYWORDS):
                logger.error('服务请求失败')
                # 显示警告对话框
                self.show_error_dialog('服务请求失败，请检查网络连接或重新尝试...', '警告')
                await self.cleanup_all_tasks()
                if not self.is_aborting:
                    self.recordButton.setText('开始录音')
                    self.recordButton.setEnabled(True)

            # 正常识别到了有效文本
            else:
                logger.info('添加用户语音信息到聊天框...')

                # 添加用户消息到聊天列表（UI 上显示）
                self.add_user_message(text)  # 可能会抛异常

                # 将识别到的文本传给大模型对话线程
                self.chat_worker.get_text(text)

                # 创建一个后台任务运行 chat_worker 的 run 方法（开始获取大模型回复）
                self.chat_task = self.create_background_task(self.chat_worker.run())

                # 日志提示：大模型开始输出
                logger.info("开始获取大模型输出...")

                # 更新 UI 提示用户当前状态
                if not self.is_aborting:
                    self.recordButton.setText('大模型回复中...')

        except Exception as e:
            # 捕获异常并记录错误日志
            logger.error(f"处理用户语音逻辑出错：{e}")

            # 显示错误提示框
            self.show_error_dialog(f"语音识别失败：{e}", '错误')

            # 恢复按钮状态
            if not self.is_aborting:
                self.recordButton.setText('开始录音')
                self.recordButton.setEnabled(True)

    # 创建异步任务
    def create_background_task(self, coro):
        """
        创建并管理一个异步后台任务，防止被垃圾回收，并在任务完成后自动移除引用。

        参数:
            coro: 一个异步协程对象，例如 some_async_function()

        返回:
            task: 创建的 asyncio.Task 对象，可用于 await 或取消
        """
        try:
            # 使用 asyncio.create_task 将传入的协程对象包装为一个 Task 并立即调度执行
            # 这是非阻塞的，任务会在事件循环中运行
            task = asyncio.create_task(coro)

            # 将创建的任务添加到实例的 background_tasks 集合中
            # 这样做是为了持有任务引用，防止它被 Python 垃圾回收机制提前销毁
            self.background_tasks.add(task)

            # 定义一个回调函数，在任务完成后调用
            def on_done(t):
                # 从集合中移除已完成的任务，释放内存
                self.background_tasks.discard(t)
                # 如果任务被取消，则记录日志
                if t.cancelled():
                    logger.info("后台任务被取消")
                # 如果任务抛出异常，则记录错误信息
                elif t.exception():
                    logger.error(f"后台任务异常：{t.exception()}")

            # 为 task 添加完成回调函数，任务完成（成功、失败或取消）时触发 on_done
            task.add_done_callback(on_done)

            # 返回任务对象，外部可以 await 或 cancel 这个任务
            return task

        except Exception as e:
            # 如果创建任务的过程中出现异常，记录错误日志并返回 None
            logger.error(f"创建后台任务失败：{e}")
            return None

    # 录音完成处理槽函数，接收一个录音文件路径作为参数
    @qasync.asyncSlot(str)
    async def handle_record_success_signal(self, path):
        try:
            # 记录日志，表示录音已完成
            logger.info("录音完成...")

            # 将录音文件路径传递给语音识别模块（stt_worker）
            self.stt_worker.get_path(path)

            # 创建一个后台语音识别任务，并保存为 self.stt_task
            self.stt_task = self.create_background_task(self.stt_worker.run())

            # 如果任务创建失败，抛出运行时异常
            if self.stt_task is None:
                raise RuntimeError("语音识别任务创建失败")

            # 记录日志，表示语音识别即将开始
            logger.info('开始语音识别...')

            # 如果当前不是中断状态，则更新按钮显示为“语音识别中...”
            if not self.is_aborting:
                self.recordButton.setText('语音识别中...')

            # 如果当前助手状态是“监听中”，切换为“思考中”
            if self.assistant_state == AssistantState.LISTENING:
                self.assistant_state = AssistantState.THINKING

        except Exception as e:
            # 捕获异常，记录错误日志
            logger.error(f"语音识别任务执行异常: {e}")

            # 显示错误提示对话框
            self.show_error_dialog("语音识别启动失败，请检查语音模块或路径。", "错误")

            # 如果没有中断，恢复按钮为初始状态
            if not self.is_aborting:
                self.recordButton.setText("开始录音")
                self.recordButton.setEnabled(True)

    # 切换录音状态槽函数（无参数）
    @qasync.asyncSlot()
    async def toggle_recording(self):
        try:
            # 日志记录，用户请求切换录音状态
            logger.info('切换录音状态...')

            # 重置中断标志
            self.is_aborting = False

            # 如果当前不在录音状态，准备进入录音模式
            if not self.is_recording:
                # 如果没有中断，更新按钮文字为“结束录音”
                if not self.is_aborting:
                    self.recordButton.setText('结束录音')

                # 启动录音线程（如果尚未运行）
                if not self.record_worker.isRunning():
                    # 向录音线程传递当前助手状态
                    self.record_worker.get_assistant_state(self.assistant_state)

                    # 启动录音线程
                    self.record_worker.start()
                    logger.info('开始录音...')

            else:
                # 如果当前正在录音，准备停止录音
                if not self.is_aborting:
                    # 禁用按钮，避免用户重复点击
                    self.recordButton.setEnabled(False)

                # 如果录音线程仍在运行，调用 stop 停止录音
                if self.record_worker.isRunning():
                    self.record_worker.stop(True)
                    logger.info('录音结束')

            # 切换录音状态标志（True ↔ False）
            self.is_recording = not self.is_recording

        except Exception as e:
            # 异常处理：记录日志
            logger.error(f"切换录音状态失败: {e}")

            # 显示错误提示
            self.show_error_dialog("录音模块发生错误，请检查麦克风或录音线程。", "错误")

            # UI 回退：将按钮恢复为默认状态
            self.recordButton.setText("开始录音")
            self.recordButton.setEnabled(True)

    # 定义一个异步槽函数：当唤醒词监听超时时被触发
    @qasync.asyncSlot()
    async def handle_timeout_exit(self):
        try:
            # 记录日志，提示超时发生
            logger.info("唤醒状态超时...")

            # 将助手状态切换为“空闲”
            self.assistant_state = AssistantState.IDLE

            # 如果录音线程仍在运行，尝试停止它（参数 False 表示非强制停止）
            if self.record_worker.isRunning():
                self.record_worker.stop(False)

            # 等待直到录音线程完全停止（避免强行中断，防止资源冲突）
            while self.record_worker.isRunning():
                await asyncio.sleep(0.01)  # 每 10ms 检查一次

            # 日志记录，准备进行语音播报提示
            logger.info("开始播报超时回复...")

            # 设置语音播报模块的播放音频文件路径（超时提示音）
            self.play_waker.get_file_path('./resources/response/timeout_response.wav')

            # 启动语音播报线程
            self.play_waker.start()

            # 等待播报完成（播报线程停止）
            while self.play_waker.isRunning():
                await asyncio.sleep(0.01)

            # 如果当前启用了唤醒词功能，并且使用的是本地 Vosk 模型
            if self.use_wake_word:
                # 如果唤醒词检测线程没有在运行，则重新启动它
                if not self.wake_worker.isRunning():
                    self.wake_worker.start()
                    logger.info("启动唤醒词检测功能...")

            # 如果没有中断标志，则恢复录音按钮状态
            if not self.is_aborting:
                self.recordButton.setEnabled(True)  # 启用按钮
                self.recordButton.setText('开始录音')  # 恢复按钮文字

        except Exception as e:
            # 如果过程中出现异常，记录错误日志
            logger.error(f"唤醒状态超时处理失败: {e}")

            # 弹出错误对话框提示用户
            self.show_error_dialog("唤醒超时后处理失败，请检查播报或唤醒模块。", "错误")

            # 如果不是中断状态，仍然恢复按钮
            if not self.is_aborting:
                self.recordButton.setEnabled(True)
                self.recordButton.setText("开始录音")

    # 定义一个异步槽函数：当语音检测到用户说话结束时触发
    @qasync.asyncSlot()
    async def handle_speech_ended_signal(self):
        try:
            # 日志记录：用户语音结束
            logger.info("用户说话结束...")

            # 如果录音线程还在运行，尝试强制停止（参数 True 表示立刻停止）
            if self.record_worker.isRunning():
                self.record_worker.stop(True)

        except Exception as e:
            # 记录异常信息
            logger.error(f"停止录音线程时发生错误: {e}")

            # 弹出错误对话框提示用户
            self.show_error_dialog("录音停止失败，请检查录音模块。", "错误")

    # 定义异步槽函数：当唤醒词被检测到时调用
    @qasync.asyncSlot()
    async def handle_wake_detected_signal(self):
        logger.info("唤醒词已触发...")
        try:
            # 设置助手当前状态为“监听中”
            self.assistant_state = AssistantState.LISTENING

            # 如果启用了唤醒词功能，且使用的是本地 vosk 模型
            if self.use_wake_word:
                logger.info("本地模型唤醒词已触发...")

                # 如果唤醒线程仍在运行，先停止它，并等待最多 10 毫秒
                if self.wake_worker.isRunning():
                    self.wake_worker.stop()
                    self.wake_worker.wait(10)

            # 如果没有使用唤醒词功能，直接退出函数
            else:
                return

            # 如果之前已经有语音识别任务在运行，则取消它
            if hasattr(self, 'stt_task') and self.stt_task:
                self.stt_task.cancel()
                self.stt_task = None
                logger.info("已取消 语音识别 任务")

            # 如果之前已有大模型对话任务，先停止 worker，取消任务
            if hasattr(self, 'chat_task') and self.chat_task:
                self.chat_worker.stop()
                self.chat_task.cancel()
                self.chat_task = None
                logger.info("已取消 大模型对话 任务")

            # 如果语音合成任务在进行，取消它并停止 worker
            if hasattr(self, 'tts_task') and self.tts_task:
                self.tts_worker.stop()
                self.tts_task.cancel()
                self.tts_task = None
                logger.info("已取消 语音合成 任务")

            # 如果语音播报线程仍在运行，则停止它
            if self.player_worker.isRunning():
                self.player_worker.stop()
                logger.info("停止播报...")

            # 等待短暂时间确保线程已释放资源
            await asyncio.sleep(0.1)

            # 播报唤醒提示音
            logger.info('开始播报唤醒回复...')
            self.play_waker.get_file_path('./resources/response/wake_up_response.wav')
            self.play_waker.start()

            # 等待唤醒提示音播放完毕
            while self.play_waker.isRunning():
                await asyncio.sleep(0.1)

            # 清空所有输入/输出队列（如语音、文本、响应等）
            self.clear_all_queues()

            # 重置中止标志
            self.is_aborting = False

            # 如果不是中止状态，则更新按钮状态为“聆听中...”
            if not self.is_aborting:
                self.recordButton.setText('聆听中...')
                self.recordButton.setEnabled(False)

            # 如果录音线程未启动，启动它并传入助手状态
            if not self.record_worker.isRunning():
                self.record_worker.get_assistant_state(self.assistant_state)
                self.record_worker.start()
                logger.info('开始录音...')

            # 清除上一次的对话缓存（如消息内容等）
            self.bot_item = None
            self.bot_message = None

        except Exception as e:
            # 捕获异常并记录日志
            logger.error(f"唤醒处理发生错误: {e}")
            # 显示错误提示
            self.show_error_dialog("唤醒词处理异常，请检查系统状态。", "错误")

    # 定义异步槽函数：当用户点击“中止”按钮时调用
    @qasync.asyncSlot()
    async def end_button(self):
        try:
            logger.info('中止对话...')

            # 设置中止状态标志，防止 UI 被其他信号修改
            self.is_aborting = True

            # 异步清理所有任务（语音识别、对话、播报、唤醒等）
            await self.cleanup_all_tasks("用户点击中止按钮")

            # 重置录音状态标志
            self.is_recording = False

            # 设置助手状态为“空闲”
            self.assistant_state = AssistantState.IDLE

            # 恢复 UI 按钮显示为“开始录音”
            self.recordButton.setText('开始录音')
            self.recordButton.setEnabled(True)

            # 稍作等待，避免冲突
            time.sleep(0.01)

            # 如果启用了本地唤醒词检测功能且线程未运行，则启动唤醒检测
            if self.use_wake_word:
                if not self.wake_worker.isRunning():
                    self.wake_worker.start()

        except Exception as e:
            # 如果处理过程中出错，记录日志
            logger.error(f"中止对话处理异常: {e}")
            # 显示错误提示
            self.show_error_dialog("中止对话时发生错误，请重试。", "错误")

    ''' 处理摄像头传来的数据 '''
    @qasync.asyncSlot(QPixmap)
    async def handle_camera_success_signal(self, frame):
        try:
            # 清空摄像头显示组件上的旧图像
            self.cameraDisplay.clear()

            # 显示新的摄像头图像帧（frame 为 QPixmap 类型）
            self.cameraDisplay.setPixmap(frame)

            # 增加帧计数器（用于 FPS 计算）
            self.frame_count += 1

            # 获取当前时间（秒）
            current_time = time.time()

            # 计算距离上次统计 FPS 的时间间隔
            elapsed_time = current_time - self.start_time

            # 如果时间超过 1 秒，计算并更新 FPS
            if elapsed_time >= 1.0:
                fps = round(self.frame_count / elapsed_time)
                self.fpsLabel.setText(f"  FPS: {fps}  ")  # 更新界面上的 FPS 显示
                self.frame_count = 0  # 重置帧计数
                self.start_time = current_time  # 重置起始时间

        except Exception as e:
            # 捕获异常并记录日志
            logger.error(f"更新摄像头帧失败: {e}")
            # 弹出错误提示框
            self.show_error_dialog("显示摄像头画面时出错，请检查设备。", "错误")

    ''' 打开摄像头 '''
    @qasync.asyncSlot()
    async def open_camera(self):
        try:
            # 如果摄像头线程尚未启动，则开始摄像头处理线程
            if not self.camera_processor.isRunning():
                logger.info("准备打开摄像头...")
                self.camera_processor.start()  # 启动后台摄像头线程
                logger.info("摄像头已打开...")
                self.chat_worker.camera_open = True  # 标记摄像头已开启（供对话逻辑使用）

        except Exception as e:
            logger.error(f"打开摄像头失败: {e}")
            self.show_error_dialog("打开摄像头失败，请检查设备或权限。", "错误")

    ''' 关闭摄像头 '''
    @qasync.asyncSlot()
    async def close_camera(self):
        try:
            # 如果摄像头线程正在运行，发出停止指令
            if self.camera_processor.isRunning():
                logger.info("准备关闭摄像头...")
                self.camera_processor.stop()  # 请求停止摄像头处理线程
                self.camera_processor.wait(10)  # 等待线程最多 10ms 停止
                self.chat_worker.camera_open = False  # 更新摄像头状态

            # 清除图像 base64 数据（防止后续误用）
            self.chat_worker.image_base64 = None

            # 清除显示图像帧
            self.cameraDisplay.clear()
            time.sleep(0.1)  # 简短等待，确保 UI 刷新
            self.cameraDisplay.clear()

            # FPS 重置为 0
            self.fpsLabel.setText(f"  FPS: 0  ")

            logger.info("摄像头已关闭...")

        except Exception as e:
            logger.error(f"关闭摄像头失败: {e}")
            self.show_error_dialog("关闭摄像头失败，请检查程序状态。", "错误")

    ''' 错误信号处理 '''
    @qasync.asyncSlot(str, str)
    async def handle_error_signal(self, thread_name, error):
        # 日志记录错误来源线程及错误内容
        logger.error(f"{thread_name}发生错误: {error}")

        # 如果是摄像头线程报错
        if thread_name == 'camera_thread':
            # 清空摄像头显示区域
            self.cameraDisplay.clear()
            await asyncio.sleep(0.1)  # 使用异步等待，防止阻塞事件循环
            self.cameraDisplay.clear()
            self.fpsLabel.setText("  FPS: 0  ")

            # 如果摄像头线程仍在运行，尝试安全关闭
            if self.camera_processor.isRunning():
                self.camera_processor.stop()
                logger.info(f'关闭摄像头功能')

        else:
            # 其他线程发生错误时，清理所有相关任务（如语音识别、大模型等）
            await self.cleanup_all_tasks(f"{thread_name}错误")

        # 显示统一错误提示框
        self.show_error_dialog(error)

        # 如果系统当前不是中止状态，则恢复录音按钮状态
        if not self.is_aborting:
            self.recordButton.setText('开始录音')
            self.recordButton.setEnabled(True)

    ''' 修改服务端 '''
    @qasync.asyncSlot(str)
    async def change_service(self, text):
        # 创建服务名称到配置键的映射字典
        services_dict = {"本地服务": "LOCAL_SERVICE", "硅基流动": "SILICONFLOW"}

        # 根据UI传入的选项文本（text）获取配置中对应的服务标识
        self.service = services_dict[text]

        # 更新配置文件中所选服务项（写入 config.json 等）
        config.update_config('CHOICE.SERVICE', self.service)

        await asyncio.sleep(0.01)  # 等待更新生效或异步线程让出

        # 获取选中服务的新 API 密钥和基础 URL
        self.api_key = config.get_config(f'{self.service}.API_KEY')
        self.base_url = config.get_config(f'{self.service}.URL')

        # 创建服务切换线程 ClientChange（用于创建新客户端）
        self.change_worker = ClientChange(self.base_url, self.api_key)

        # 连接线程完成信号，任务完成后触发 handle_change_client_success_signal
        self.change_worker.finished.connect(self.handle_change_client_success_signal)

        # 启动服务切换线程
        self.change_worker.start()
        logger.info(f"更改使用的AI服务为：{self.service}")

    ''' 修改后重新绑定信号 '''
    @qasync.asyncSlot(object)
    async def handle_change_client_success_signal(self, client):
        # 使用新的客户端对象（OpenAI / SiliconFlow / 本地服务）
        self.client = client

        # 重新创建用于对话的大模型线程
        self.chat_worker = ChatWithLLM(self.client, self.sentences_queue)
        self.chat_worker.on_chat_start(self.handle_chat_start_signal)
        self.chat_worker.on_chat_error(self.handle_error_signal)

        # 重新创建语音识别模块（STT）
        self.stt_worker = SoundToText(self.client)
        self.stt_worker.on_stt_success(self.handle_stt_success_signal)
        self.stt_worker.on_stt_error(self.handle_error_signal)

        # 重新创建语音合成模块（TTS）
        self.tts_worker = TextToSound(self.client, self.audio_queue, self.sentences_queue)
        self.tts_worker.on_tts_start(self.handle_tts_start_signal)
        self.tts_worker.on_tts_done(self.handle_tts_done_signal)
        self.tts_worker.on_tts_error(self.handle_error_signal)

    ''' 打开设置对话框 '''
    def open_settings_dialog(self):
        logger.info("打开设置对话框")

        # 创建设置对话框实例（可能包含 MQTT、唤醒词配置等）
        dialog = SettingsDialog(self)

        # 连接保存成功信号到配置更新槽函数
        dialog.config_save_success.connect(self.update_mqtt_client)
        dialog.config_save_success.connect(self.update_wake_word_options)

        # 连接保存失败信号到通用错误处理槽
        dialog.config_save_error.connect(self.handle_error_signal)

        # 打开对话框（模态）
        dialog.exec_()

    ''' 更新唤醒设置 '''
    @qasync.asyncSlot()
    async def update_wake_word_options(self):
        # 获取当前配置中唤醒词选项
        new_use_wake_word = config.get_config("WAKE_WORD_OPTIONS.USE_WAKE_WORD")

        # 检查是否有配置变更
        changed = (
                new_use_wake_word != self.use_wake_word
        )

        # 如果没变化，则跳过更新
        if not changed:
            logger.info("唤醒词配置未发生变化，跳过更新")
            return

        # 更新内部状态
        self.use_wake_word = new_use_wake_word

        logger.info("唤醒词配置已更新，应用新设置")

        # 弹出提示框，建议重启程序以使配置生效
        QMessageBox.information(
            self,
            "需要重启",
            "唤醒词配置已更改，请重新启动程序以使更改生效。"
        )

        # 强制退出（可改为优雅关闭）
        os._exit(0)

    ''' 更新mqtt设置 '''
    @qasync.asyncSlot()
    async def update_mqtt_client(self):
        try:
            # 读取最新的 MQTT 配置信息
            new_broker = config.get_config('MQTT_SERVICE.BROKER')
            new_port = config.get_config('MQTT_SERVICE.PORT')
            new_pub_topic = config.get_config('MQTT_SERVICE.PUB_TOPIC')
            new_sub_topic = config.get_config('MQTT_SERVICE.SUB_TOPIC')

            # 获取当前 MQTT 客户端的连接参数
            current_broker = self.mqtt_client.target_ip
            current_port = self.mqtt_client.default_port
            current_pub_topic = self.mqtt_client.pub_topic
            current_sub_topic = self.mqtt_client.sub_topic

            # 如果没有任何配置变动，则直接跳过更新
            if (
                    new_broker == current_broker and
                    new_port == current_port and
                    new_pub_topic == current_pub_topic and
                    new_sub_topic == current_sub_topic
            ):
                return

            # 有变化，则异步执行 reconnect（在线程池中避免阻塞主线程）
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.mqtt_client.reconnect,
                new_broker, new_port, new_sub_topic, new_pub_topic
            )

            logger.info("MQTT 客户端配置已更新")

        except Exception as e:
            logger.error(f"MQTT客户端更新失败: {e}")

    """ 清空 sentence_queue 和 audio_queue 两个队列 """
    def clear_all_queues(self):

        for q in [self.sentences_queue, self.audio_queue]:  # 遍历两个队列
            while not q.empty():  # 只要队列不为空就继续取出
                try:
                    q.get_nowait()  # 非阻塞方式取出（无需 await）
                except Exception:
                    break  # 如果出错（队列操作异常）则跳出当前队列

    """ 错误弹窗 """
    @staticmethod
    def show_error_dialog(error_message: str, title: str = "错误"):
        # 内部函数 _show：创建消息框并弹出
        def _show(icon_path):
            msg_box = QMessageBox()
            msg_box.setWindowTitle(title)
            msg_box.setText(f"<b>{error_message}</b>")
            msg_box.setWindowIcon(QIcon(icon_path))  # 设置图标
            msg_box.exec_()

        # 根据标题类型选择图标
        if title == '错误':
            icon_path = ":/icons/error.png"
        elif title == '警告':
            icon_path = ":/icons/warning.png"

        # 使用 Qt 单次定时器异步调用，防止阻塞事件循环（非常重要）
        QTimer.singleShot(0, lambda: _show(icon_path))

    """ 添加消息 """
    def add_user_message(self, message):
        item = QListWidgetItem(self.chatListWidget)  # 创建列表项
        widget = SetMessageItem(message, is_user=True)  # 创建用户气泡组件
        item.setSizeHint(widget.sizeHint())  # 设置显示区域尺寸
        self.chatListWidget.addItem(item)  # 添加项到聊天列表
        self.chatListWidget.setItemWidget(item, widget)  # 设置聊天组件
        self.chatListWidget.scrollToBottom()  # 滚动到底部（最新消息）

    ''' 创建FPS帧率显示标签 '''
    async def create_fps_label(self):
        self.fpsLabel = QtWidgets.QLabel(self.cameraDisplay)  # 创建标签，挂在图像窗口上
        self.fpsLabel.setText("  FPS: 0  ")  # 初始文字

        # 设置样式：白字黑底、透明背景、圆角、较大字号
        self.fpsLabel.setStyleSheet("""
            color: white;
            background-color: rgba(0, 0, 0, 160);  /* 半透明背景 */
            padding: 4px 8px;
            border-radius: 5px;
            font-size: 30px;
        """)
        self.fpsLabel.setAlignment(Qt.AlignCenter)
        self.fpsLabel.adjustSize()  # 自动适配文本内容
        self.fpsLabel.move(10, 10)  # 设置位置：左上角
        self.fpsLabel.raise_()  # 提升到最前显示
        self.fpsLabel.show()  # 显示标签

    # 清理所有任务，适用于退出、中断、打断等清理操作
    async def cleanup_all_tasks(self, reason="用户操作"):
        logger.info(f"开始清理资源，原因：{reason}")

        # 停止录音线程
        if self.record_worker.isRunning():
            self.record_worker.stop(False)
            await asyncio.sleep(0)
            while self.record_worker.isRunning():
                await asyncio.sleep(0.01)
            logger.info("关闭录音线程")

        # 停止语音播放线程
        if self.player_worker.isRunning():
            self.player_worker.stop()
            await asyncio.sleep(0)
            while self.player_worker.isRunning():
                await asyncio.sleep(0.01)
            logger.info("关闭语音播报线程")

        # 除非是主动点击中止按钮，否则也关闭唤醒线程
        if reason != '用户点击中止按钮':
            if self.wake_worker.isRunning():
                self.wake_worker.stop()
                await asyncio.sleep(0)
                while self.wake_worker.isRunning():
                    await asyncio.sleep(0.01)
                logger.info("关闭唤醒线程")

        # 取消三种异步任务：语音识别、大模型、TTS
        for name, task, worker in [
            ("语音识别", getattr(self, 'stt_task', None), None),
            ("大模型对话", getattr(self, 'chat_task', None), getattr(self, 'chat_worker', None)),
            ("语音合成", getattr(self, 'tts_task', None), getattr(self, 'tts_worker', None)),
        ]:
            if task and not task.done():
                if worker:
                    worker.stop()  # 通知线程停止
                task.cancel()  # 异步任务取消
                setattr(self, name.replace("任务", "_task").lower(), None)
                logger.info(f"取消{name}")

        # 清空语音/文本队列
        self.clear_all_queues()

        # 清空状态记录（机器人回复项）
        self.bot_item = None
        self.bot_message = None

    """ 关闭触发事件 """
    def closeEvent(self, event):
        logger.info('触发关闭事件')

        # 关闭摄像头线程（如正在运行）
        if self.camera_processor.isRunning():
            self.camera_processor.stop()
            logger.info('关闭摄像头功能')

        # 获取当前 Qt 的事件循环
        loop = asyncio.get_event_loop()
        if not loop.is_running():
            logger.warning("事件循环未运行，跳过异步清理")
        else:
            # 在事件循环中异步执行清理任务
            try:
                asyncio.run_coroutine_threadsafe(
                    self.cleanup_all_tasks("关闭窗口"), loop)
            except Exception as e:
                logger.error(f"关闭时清理任务异常: {repr(e)}\n{traceback.format_exc()}")

        # 停止任何计时器（防止资源泄漏）
        if hasattr(self, 'timer'):
            self.timer.stop()

        # 强制退出整个程序（非优雅）
        os._exit(0)

    """ CTRL C 捕获处理"""
    def handle_sigint(self, sig, frame):
        print("SIGINT received, exiting...")  # 控制台打印
        self.close()  # 调用窗口关闭流程
        os._exit(0)  # 强制退出


if __name__ == '__main__':
    if sys.platform == "win32":
        # 判断当前操作系统是否为 Windows（sys.platform 返回 'win32' 表示 Windows 系统）
        import ctypes

        # 导入 Python 的 ctypes 模块，用于调用底层 C/C++ 接口，例如 Windows API

        # 使用 Windows 的 shcore.dll 动态链接库中的 SetProcessDpiAwareness 函数
        # 该函数用于设置整个进程的 DPI 感知级别（即程序如何响应高分辨率屏幕的 DPI 缩放）
        # 这里传入参数 1，表示将当前进程设置为：
        #   DPI_AWARENESS_CONTEXT_SYSTEM_DPI_AWARE
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

    # 设置 Qt 的高 DPI 缩放策略，防止高分屏界面模糊
    # 采用 PassThrough 策略，即不进行四舍五入，保留实际缩放比例
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # 创建 Qt 应用实例，管理应用程序的控制流和主要设置
    # sys.argv 用于接收命令行参数
    app = QApplication(sys.argv)

    # 使用 qasync 创建一个基于 Qt 的 asyncio 事件循环
    # 使 Qt 事件循环和 asyncio 协程能够协同工作
    loop = qasync.QEventLoop(app)

    # 设置当前线程的默认事件循环为刚才创建的 qasync 事件循环
    asyncio.set_event_loop(loop)

    # 创建主窗口实例，MyMainWindow 是你定义的主界面类
    window = MyMainWindow()

    # 捕获终端发送的 SIGINT 信号（Ctrl+C），调用主窗口的信号处理函数
    # 目的是让程序能优雅退出，而不是强制终止
    signal.signal(signal.SIGINT, window.handle_sigint)

    # 进入 qasync 事件循环上下文
    with loop:
        # 创建一个异步任务，初始化后台线程或资源（如摄像头、网络连接等）
        asyncio.ensure_future(window.thread_init())

        # 显示主窗口，UI 界面正式呈现给用户
        window.show()

        # 启动事件循环，进入消息循环，程序阻塞在这里，直到事件循环结束
        loop.run_forever()
