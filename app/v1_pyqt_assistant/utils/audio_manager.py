

import asyncio  # 异步 I/O 库，用于异步任务管理
import io  # 提供内存中文件的操作接口
import os  # 操作系统接口，用于路径、文件等操作
import queue  # 提供线程安全的队列
import tempfile  # 用于创建临时文件和目录

import time  # 提供时间相关函数，例如 sleep

import aiofiles  # 异步文件操作库
import edge_tts  # Edge TTS 语音合成库
import pyaudio  # 音频录制和播放库
import pygame  # 游戏和多媒体库，这里用于播放音频

from PyQt5.QtCore import QThread, pyqtSignal  # PyQt5 线程类和信号机制

from pydub import AudioSegment  # 音频处理库，用于转换格式和保存
from utils.logging_manager import get_logger  # 自定义日志管理模块
from utils.config_manager import ConfigManager  # 自定义配置管理模块

logger = get_logger(__name__)  # 获取当前模块的日志对象
config = ConfigManager.get_instance()  # 获取配置管理单例实例

pygame.mixer.init()  # 初始化 pygame 的音频混音器，用于播放音频


# 定义一个音频录制类，继承 PyQt5 的线程类
class AudioRecorder(QThread):

    record_success = pyqtSignal(str)  # 定义录音成功信号，传递音频文件路径
    record_error = pyqtSignal(str, str)  # 定义录音错误信号，传递线程名和错误信息

    # 构造函数，初始化音频录制参数
    def __init__(self):
        super().__init__()  # 调用父类 QThread 的初始化
        self.setObjectName('audio_recorder')  # 设置线程对象名称

        # PyAudio 音频参数设置
        self.FORMAT = pyaudio.paInt16  # 16 位深度音频
        self.CHANNELS = 1  # 单声道录音
        self.RATE = 16000  # 采样率 16kHz
        self.CHUNK = 1024  # 每个缓冲区读取 1024 个采样点

        self.is_recording = False  # 标记录音状态
        self.frames = []  # 存储录制的音频帧
        self.save_flag = True  # 标记是否保存录音文件

        os.makedirs('./temp', exist_ok=True)  # 创建临时目录用于存储录音文件

    # 重写 QThread 的 run 方法，线程启动时执行
    def run(self):
        logger.info("开始初始化音频流")  # 日志记录
        self.frames.clear()  # 清空之前可能存在的音频帧
        self.audio = pyaudio.PyAudio()  # 初始化 PyAudio 对象

        try:
            # 打开音频输入流
            self.stream = self.audio.open(
                format=self.FORMAT,  # 采样格式
                channels=self.CHANNELS,  # 声道数
                rate=self.RATE,  # 采样率
                input=True,  # 打开输入流
                frames_per_buffer=self.CHUNK  # 每次读取缓冲区大小
            )
            logger.info("音频输入流已建立")
        except Exception as e:  # 捕获初始化异常
            self.record_error.emit(
                self.objectName(),  # 发射错误信号，包含线程名称
                f"无法打开音频，请检查硬件设备！！!{e}"  # 错误信息
            )
            logger.error(f"麦克风初始化失败: {e}")
            return  # 初始化失败直接返回

        self.is_recording = True  # 标记录音状态为 True

        try:
            # 循环读取音频流
            while self.is_recording:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)  # 读取一帧音频
                self.frames.append(data)  # 添加到帧列表
                time.sleep(0.01)  # 防止 CPU 占用过高，稍微休眠
        except Exception as e:  # 捕获录音异常
            self.record_error.emit(
                self.objectName(),
                f"读取音频数据失败: {e}"
            )
            logger.error(f"录音数据读取异常: {e}")
        finally:  # 无论是否异常，都执行清理操作
            if self.save_flag:  # 如果需要保存音频
                self.save_audio_to_mp3()  # 调用保存函数

            # 停止并关闭音频流
            if hasattr(self, "stream") and self.stream:
                self.stream.stop_stream()
                self.stream.close()

            # 终止 PyAudio
            if hasattr(self, "audio") and self.audio:
                self.audio.terminate()

            self.frames.clear()  # 清空缓存帧
            logger.info("录音线程已结束")  # 日志记录

    # 保存音频为 MP3 文件
    def save_audio_to_mp3(self):
        try:
            audio_data = b''.join(self.frames)  # 合并所有帧为字节流

            if len(audio_data) % 2 != 0:  # 确保字节数为偶数
                audio_data = audio_data[:-1]

            output_file = "./temp/recorded_audio.mp3"  # 输出文件路径

            # 使用 pydub 将原始音频数据转换为 AudioSegment 对象
            audio = AudioSegment(
                data=audio_data,  # 原始字节数据
                sample_width=2,  # 每个采样点 2 字节（16 位）
                frame_rate=self.RATE,  # 采样率
                channels=self.CHANNELS  # 声道数
            )
            audio.export(output_file, format="mp3", bitrate="128k")  # 导出为 mp3 文件

            self.record_success.emit(output_file)  # 发射录音成功信号
            logger.info(f"录音保存成功: {output_file}")
        except Exception as e:  # 捕获保存异常
            self.record_error.emit(
                self.objectName(),
                f"保存音频失败: {e}"
            )
            logger.error(f"保存音频失败: {e}")

    # 停止录音
    def stop(self, save_flag=True):
        self.is_recording = False  # 设置标记终止循环
        self.save_flag = save_flag  # 是否保存音频
        logger.info("录音线程已终止")  # 日志记录


class SoundToText:
    # 构造函数，初始化语音识别对象
    def __init__(self, client):
        self.client = client  # 外部传入的语音识别客户端对象（可能是 SiliconFlow 或其他 API）
        self.path = None  # 存放待识别的音频文件路径
        self.service = None  # 使用的语音识别服务类型
        self.model = None  # 当前使用的识别模型名称
        self.local_model = None  # 本地模型对象（如果有的话）

        # 回调函数字典，支持多个回调函数注册
        self.handlers = {
            "stt_success": [],  # 语音识别成功回调列表
            "stt_error": []     # 语音识别失败回调列表
        }

    # 注册语音识别成功的回调函数
    def on_stt_success(self, handler):
        self.handlers["stt_success"].append(handler)

    # 注册语音识别失败的回调函数
    def on_stt_error(self, handler):
        self.handlers["stt_error"].append(handler)

    # 发射信号，调用对应的回调函数
    def emit(self, signal_name, *args):
        for handler in self.handlers.get(signal_name, []):  # 遍历该信号的所有回调
            try:
                if asyncio.iscoroutinefunction(handler):  # 如果是协程函数
                    asyncio.create_task(handler(*args))  # 创建异步任务执行
                else:  # 普通函数
                    handler(*args)  # 直接调用
            except Exception as e:
                logger.error(f"执行 {signal_name} 回调失败: {e}")  # 回调异常日志

    # 设置待识别的音频文件路径
    def get_path(self, path):
        self.path = path
        logger.info(f'获取到录音文件路径：{path}')  # 日志记录

    # 异步执行语音识别
    async def run(self):
        try:
            # 获取配置文件中选择的语音识别服务
            self.service = config.get_config('CHOICE.SERVICE')
            logger.info(f'开始语音识别，服务类型：{self.service}')

            # 检查音频文件是否存在
            if not os.path.exists(self.path):
                self.emit('stt_error', 'stt_thread', f"音频文件不存在: {self.path}")
                return  # 文件不存在则直接返回

            # 根据服务类型选择对应的识别方法
            if self.service == 'LOCAL_SERVICE':
                result = await self._recognize_local()  # 本地模型识别
            elif self.service == 'SILICONFLOW':
                result = await self._recognize_siliconflow()  # 云端识别
            else:
                self.emit('stt_error', 'stt_thread', f"不支持的服务类型: {self.service}")
                return

            # 日志记录识别结果
            logger.info(f'语音识别成功: {result}')
            self.emit("stt_success", result)  # 发射成功信号
            time.sleep(0.001)  # 轻微休眠，避免阻塞事件循环

        except asyncio.CancelledError:  # 协程被取消异常
            raise

        except Exception as e:  # 捕获其他异常
            logger.error(f"语音识别过程异常: {e}")
            self.emit("stt_error", 'stt_thread', str(e))  # 发射错误信号
            time.sleep(0.001)  # 轻微休眠

    # 异步本地识别方法
    async def _recognize_local(self):
        self.model = config.get_config('LOCAL_SERVICE.SPEECH_REC')  # 获取本地模型名称
        return await self._recognize_with_client(self.path, self.model)  # 调用通用识别方法

    # 异步 SiliconFlow 云端识别方法
    async def _recognize_siliconflow(self):
        try:
            self.model = config.get_config(f'{self.service}.SPEECH_REC')  # 获取云端模型名称
            return await self._recognize_with_client(self.path, self.model)
        except Exception as e:
            raise e  # 异常向上抛出，由 run 方法捕获

    # 通用识别方法，通过 client 调用接口
    async def _recognize_with_client(self, path, model):
        try:
            # 异步读取音频文件内容
            async with aiofiles.open(path, "rb") as f:
                content = await f.read()

            audio_file = io.BytesIO(content)  # 将文件内容转换为 BytesIO 对象，便于上传

            # 调用客户端 API 进行语音转文本
            response = await self.client.audio.transcriptions.create(
                file=("audio.mp3", audio_file, "audio/mp3"),  # 上传音频
                model=model  # 使用指定模型
            )

            return response.text  # 返回识别文本

        except Exception as e:
            logger.error(f"语音识别过程异常: {e}")  # 异常日志
            raise e  # 抛出异常，供上层捕获


class TextToSound:
    # 构造函数，初始化 TTS 对象
    def __init__(self, client, audio_queue: queue.Queue, sentence_queue: queue.Queue):
        self.siliconflow_client = client  # 外部传入的 SiliconFlow TTS 客户端
        self.audio_queue = audio_queue  # 音频队列，用于存放合成后的音频
        self.sentence_queue = sentence_queue  # 文本队列，用于存放待合成的文本
        self.voice = None  # 当前选用的语音配置
        self.tts_provider = None  # 当前使用的 TTS 服务提供商（LOCAL_SERVICE 或 SILICONFLOW）
        self.tts_running = False  # TTS 主循环是否正在运行
        self.start_flag = False  # 是否已启动 TTS

        # 定义回调函数字典
        self.handlers = {
            "tts_start": [],  # TTS 启动时回调
            "tts_error": [],  # TTS 出错时回调
            "tts_done": []    # TTS 完成时回调
        }

    # 注册 TTS 启动回调
    def on_tts_start(self, handler):
        self.handlers["tts_start"].append(handler)

    # 注册 TTS 出错回调
    def on_tts_error(self, handler):
        self.handlers["tts_error"].append(handler)

    # 注册 TTS 完成回调
    def on_tts_done(self, handler):
        self.handlers["tts_done"].append(handler)

    # 发射信号，调用回调函数
    def emit(self, signal_name, *args):
        for handler in self.handlers.get(signal_name, []):  # 遍历回调列表
            try:
                if asyncio.iscoroutinefunction(handler):  # 如果是异步函数
                    asyncio.create_task(handler(*args))  # 异步调用
                else:  # 普通函数
                    handler(*args)  # 直接调用
            except Exception as e:
                logger.error(f"执行 {signal_name} 回调失败: {e}")  # 回调异常日志

    # 异步启动 TTS
    async def run(self):
        if not self.start_flag:  # 如果未启动过
            self.start_flag = True
            self.emit("tts_start")  # 发射 TTS 启动信号
            await asyncio.sleep(0.001)  # 轻微休眠，避免阻塞

        self.tts_running = True  # 设置运行标记
        await self.main_loop()  # 进入主循环处理队列

    # TTS 主循环，从队列获取文本进行合成
    async def main_loop(self):
        while self.tts_running:
            try:
                text = self.sentence_queue.get_nowait()  # 非阻塞获取文本
                if text and text != '__END_OF_SPEECH__':  # 有效文本
                    logger.info(f"开始合成语音: {text}")

                    audio_data = await self._play_tts(text)  # 异步合成 TTS

                    self.audio_queue.put({text: audio_data})  # 将音频数据放入队列

                elif text == '__END_OF_SPEECH__':  # 接收到结束标志
                    logger.info("接收到结束标志 '__END_OF_SPEECH__'")
                    self.audio_queue.put({text: ''})  # 放入空音频占位
                    self.emit("tts_done")  # 发射完成信号

                await asyncio.sleep(0.001)  # 避免阻塞事件循环

            except queue.Empty:  # 队列为空
                await asyncio.sleep(0.01)  # 稍作休眠等待新文本

            except Exception as e:  # 主循环异常
                logger.error(f"主循环中语音合成失败: {e}")
                self.emit("tts_error", self.__class__.__name__, str(e))  # 发射错误信号

    # 核心 TTS 调用方法，包含重试逻辑
    async def _play_tts(self, text):
        max_retries = 2  # 最大重试次数
        audio_data = None

        self.tts_provider = config.get_config('CHOICE.SERVICE')  # 获取 TTS 服务提供商

        for attempt in range(max_retries):
            try:
                self.voice = config.get_config(f'{self.tts_provider}.VOICE')  # 获取语音配置

                if self.tts_provider == 'LOCAL_SERVICE':
                    audio_data = await self.local_tts(text)  # 本地 Edge-TTS 合成
                elif self.tts_provider == 'SILICONFLOW':
                    audio_data = await self.siliconflow_tts(text)  # SiliconFlow 合成

                break  # 成功则跳出重试循环

            except Exception as e:
                logger.error(f"第 {attempt + 1} 次合成失败: {e}")
                await asyncio.sleep(1)  # 重试前等待

        if audio_data is None:  # 如果重试仍失败
            self.emit("tts_error", self.__class__.__name__, '语音合成失败')
            return

        return audio_data  # 返回合成音频字节

    # 本地 TTS（Edge-TTS）合成方法
    async def local_tts(self, text):
        communicate = edge_tts.Communicate(text, self.voice)  # 创建 Edge-TTS 通信对象
        audio_data = b""  # 用于存储音频字节

        # 异步流式获取音频
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        # 转换为 pydub AudioSegment 进行处理
        mp3_stream = io.BytesIO(audio_data)
        audio = AudioSegment.from_file(mp3_stream, format="mp3")
        audio = audio.set_frame_rate(16000).set_channels(1)  # 设置采样率和单声道

        mp3_stream = io.BytesIO()
        audio.export(mp3_stream, format="mp3", bitrate="16k")  # 导出为 MP3

        return mp3_stream.getvalue()  # 返回音频字节

    # 云端 TTS（SiliconFlow）合成方法
    async def siliconflow_tts(self, text):
        response = await self.siliconflow_client.audio.speech.create(
            model=config.get_config('SILICONFLOW.SPEECH_SYN'),  # 选择模型
            voice=self.voice,  # 语音类型
            input=text,  # 输入文本
            response_format="mp3",  # 输出格式
            speed=1.0  # 播放速度
        )

        return await response.aread()  # 异步读取音频字节流

    # 停止 TTS
    def stop(self):
        self.tts_running = False  # 停止主循环
        self.start_flag = False  # 重置启动标记
        logger.info("已停止语音合成")


# 播放文本音频的线程类
class PlayText(QThread):
    # 定义 PyQt 信号
    play_start = pyqtSignal()  # 播放开始信号
    play_finish = pyqtSignal()  # 播放完成信号
    play_show = pyqtSignal(str)  # 播放显示文本信号
    play_error = pyqtSignal(str, str)  # 播放出错信号，传递线程名和错误信息

    # 构造函数，初始化线程
    def __init__(self, audio_queue):
        super().__init__()  # 初始化父类 QThread
        self.audio_queue = audio_queue  # 音频队列，从 TextToSound 或其他模块获取音频数据
        self.play_running = True  # 播放循环标记
        self.start_flag = True  # 控制首次播放发射 start 信号
        self.setObjectName("play_thread")  # 设置线程名称
        self.current_channel = None  # 当前播放的 pygame 音频通道对象

        logger.info("已启动语音播报线程")

    # 重写 QThread 的 run 方法，线程启动后执行
    def run(self):
        self.play_running = True
        while self.play_running:  # 播放循环
            try:
                # 非阻塞获取队列音频数据
                data = self.audio_queue.get_nowait()
                if data:
                    # 提取字典中的文本和音频字节
                    text = next(iter(data.keys()))
                    audio_data = next(iter(data.values()))

                    # 检查结束标志
                    if text == '__END_OF_SPEECH__':
                        self.play_finish.emit()  # 发射播放完成信号
                        self.start_flag = True  # 重置 start_flag
                        logger.info("播放完成")
                        time.sleep(0.001)  # 微小休眠
                        continue

                    # 使用 pydub 读取 MP3 字节数据
                    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")

                    # 临时保存音频文件用于 pygame 播放
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3:
                        audio_segment.export(temp_mp3.name, format="mp3")
                        temp_mp3_path = temp_mp3.name

                    # 发射显示文本信号
                    self.play_show.emit(text)
                    time.sleep(0.001)

                    # 首次播放时发射 start 信号
                    if self.start_flag:
                        self.play_start.emit()
                        time.sleep(0.001)
                        self.start_flag = False

                    # 播放音频
                    logger.info(f"开始播放: {text}")
                    sound = pygame.mixer.Sound(temp_mp3_path)
                    self.current_channel = sound.play()

                    # 等待播放完成或停止标记
                    while self.current_channel.get_busy():
                        if not self.play_running:  # 停止播放
                            self.current_channel.stop()
                            break
                        time.sleep(0.01)
                    time.sleep(0.001)

            except queue.Empty:  # 队列为空
                time.sleep(0.01)  # 等待新音频

            except Exception as e:  # 播放异常
                logger.error(f"音频播放异常: {e}")
                self.play_error.emit(self.objectName(), f'语音播报失败: {e}')
                time.sleep(0.001)

    # 停止播放
    def stop(self):
        self.play_running = False  # 停止循环
        self.start_flag = True  # 重置 start_flag
        if self.current_channel:  # 停止当前播放通道
            self.current_channel.stop()
        logger.info("已停止语音播报线程")


# 播放唤醒音频的线程类（单次播放）
class PlayWakeUp(QThread):
    def __init__(self):
        super().__init__()  # 初始化 QThread
        self.file_path = None  # 唤醒音频文件路径
        self.channel = None  # pygame 播放通道对象

    # 设置唤醒音频文件路径
    def get_file_path(self, file_path):
        self.file_path = file_path

    # 重写 run 方法，线程启动后执行
    def run(self):
        try:
            logger.info("开始播放唤醒语音...")

            # 创建 pygame 播放对象
            sound = pygame.mixer.Sound(self.file_path)

            # 播放音频并获取播放通道
            self.channel = sound.play()

            # 等待播放完成
            while self.channel.get_busy():
                self.msleep(10)  # 每次睡眠 10 毫秒，避免阻塞

        except Exception as e:
            logger.error(f"唤醒语音播放失败: {e}")
