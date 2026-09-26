
# 标准库导入
import asyncio               # 异步编程模块，用于协程调度
import importlib             # 动态导入模块的标准库
import io                    # 处理流（如内存中的文件）的标准库
import os                    # 操作系统接口，如文件路径、环境变量等
import queue                 # 队列模块，支持多线程通信
import tempfile              # 创建临时文件和目录的模块

# 音频处理和录音子线程相关
import time                  # 时间模块，用于计时、睡眠等

# 第三方库导入
import aiofiles              # 异步文件读写库
import edge_tts              # 微软 Edge 的 TTS 语音合成 API 库
import pyaudio               # 实时音频输入输出库（麦克风/扬声器）
import numpy as np           # 数值计算库，常用于音频数据处理
import pygame                # 游戏开发库，此处用于播放音频
import webrtcvad             # Google WebRTC 的语音活动检测器（VAD）


# PyQt5 信号线程导入
from PyQt5.QtCore import QThread, pyqtSignal  # PyQt 线程与信号机制


# 工具模块导入（项目内部模块）
from pydub import AudioSegment                # 用于音频文件的处理和格式转换
from utils.logging_manager import get_logger  # 项目自定义日志管理工具
from utils.config_manager import ConfigManager  # 项目配置管理类（单例）

# 初始化日志和配置
logger = get_logger(__name__)  # 获取当前模块专属的日志记录器
config = ConfigManager.get_instance()  # 获取配置管理器的单例实例

# 初始化 pygame 的音频模块，用于播放 TTS 语音等
pygame.mixer.init()


class AudioRecorderWithVAD(QThread):
    # 信号定义：用于通知主线程录音过程的各种状态
    record_success = pyqtSignal(str)         # 录音成功，传出音频文件路径
    record_error = pyqtSignal(str, str)      # 录音过程发生错误
    speech_ended = pyqtSignal()              # 语音检测到结束
    timeout_exit = pyqtSignal()              # 超时未检测到语音，退出

    def __init__(self):
        super().__init__()
        self.setObjectName('audio_recorder_with_vad')  # 设置线程名称，方便日志调试

        # 录音参数配置
        self.FORMAT = pyaudio.paInt16       # 采样格式：16bit
        self.CHANNELS = 1                   # 单声道
        self.RATE = 16000                   # 采样率：16kHz
        self.CHUNK = 1024                   # 每次读取的帧大小
        self.frame_duration_ms = 20         # 每帧的时间长度（毫秒）
        self.frame_size = int(self.RATE * self.frame_duration_ms / 1000)  # 每帧的采样点数

        # 初始化 VAD（语音活动检测器）
        self.vad = webrtcvad.Vad(3)         # 创建 VAD 实例，灵敏度设为 3（最敏感），取值为0-3
        self.energy_threshold = 260         # 能量阈值，小于该值认为是静音

        # 语音检测窗口配置
        self.speech_window = 10             # 连续多少帧判为语音开始
        self.silence_window = self.speech_window * 3  # 连续静音帧数判为语音结束
        self.pre_speech_buffer = 10         # 前置缓冲帧数量
        self.post_silence_buffer = 10       # 后置静音缓冲帧数量
        self.timeout_seconds = 5            # 超时时间：无语音输入就退出

        # 状态变量初始化
        self.is_recording = False           # 是否正在录音
        self.interrupt_running = False      # 是否启用中断检测模式
        self.frames = []                    # 所有音频帧
        self.pre_speech_frames = []         # 语音前的缓冲帧
        self.post_silence_frames = []       # 语音后的缓冲帧
        self.speech_count = 0               # 连续语音帧计数
        self.silence_count = 0              # 连续静音帧计数
        self.speaking = False               # 当前是否在说话
        self.speech_start_index = -1        # 语音开始帧索引
        self.speech_end_index = -1          # 语音结束帧索引
        self.last_voice_time = time.time()  # 上一次检测到语音的时间戳
        self.save_flag = True               # 是否保存录音结果

        # 创建临时文件夹用于保存音频
        os.makedirs('./temp', exist_ok=True)

    def get_assistant_state(self, state):
        """ 接收外部状态（如“LISTENING”），用于决定是否启用中断检测 """
        self.interrupt_running = (state == 'LISTENING')

    def run(self):
        """ 线程运行体：初始化音频流并实时处理语音数据 """
        logger.info("开始初始化音频流")

        # 清空帧列表并初始化 PyAudio
        self.frames.clear()
        self.audio = pyaudio.PyAudio()

        try:
            # 打开音频输入流
            self.stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            logger.info("音频输入流已建立")
        except Exception as e:
            # 捕获错误后发出信号并打印日志，然后直接return结束线程
            self.record_error.emit(self.objectName(), f"无法打开音频，请检查硬件设备！！!{e}")
            logger.error(f"麦克风初始化失败: {e}")
            return

        # 设置录音标志位，准备启动录音
        self.is_recording = True

        # 判断是否启用中断检测
        if self.interrupt_running:
            # 如果启用了中断检测，就先重置一下各状态变量
            self._reset_state()
            # 重新记录一下上一次检测到音频的时间
            self.last_voice_time = time.time()
            logger.info("语音中断检测已启动")

        try:
            while self.is_recording:
                # 开始获取音频数据
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                # 将数据添加到帧列表中
                self.frames.append(data)

                # 如果启用了中断检测，则处理超时和 VAD 检测
                if self.interrupt_running:
                    # 记录当前时间
                    current_time = time.time()
                    # 如果当前时间和上一次检测到音频时间的时差大于超时时间
                    if current_time - self.last_voice_time > self.timeout_seconds:
                        logger.info(f"超过 {self.timeout_seconds} 秒无语音输入，触发退出")
                        # 发出超时信号
                        self.timeout_exit.emit()
                        # 必须等一下，不然外面调用stop时来不及修改save_flag的数据，导致逻辑错误
                        time.sleep(0.01)
                        # 跳出循环，执行finally，退出线程
                        break
                    # 如果开启中断检测后，正常输入音频，进入音频处理
                    self._process_audio_data(data)
                # 休眠 0.01 秒避免过度占用 CPU
                time.sleep(0.01)

        except Exception as e:
            # 如果录音过程异常，发送错误信号并打印日志，然后进入finally，结束线程
            self.record_error.emit(self.objectName(), f"读取音频数据失败: {e}")
            logger.error(f"录音数据读取异常: {e}")

        finally:
            # 如果 save_flag 为 True，则保存录音数据为 mp3 文件
            if self.save_flag:
                self.save_audio_to_mp3()

            # 如果音频流已打开，则停止并关闭该流
            if self.stream:
                self.stream.stop_stream()  # 停止音频流
                self.stream.close()        # 关闭音频流

            # 如果 PyAudio 实例存在，则终止它，释放资源
            if self.audio:
                self.audio.terminate()

            # 清空所有已记录的音频帧数据，防止内存泄漏
            self.frames.clear()

            # 将 interrupt_running 状态重置为 False，表示当前不在中断检测模式下
            self.interrupt_running = False

    def _process_audio_data(self, data):
        """
        处理音频数据，将其拆分为帧并进行语音活动检测（VAD）。

        参数:
            data (bytes): 从音频流中读取的原始音频数据块。
        """
        # 将输入的音频数据按设定的帧大小进行切分
        frames = self._split_to_frames(data)

        # 遍历每一帧音频数据
        for frame in frames:
            # 使用 VAD 检测当前帧是否包含语音
            is_speech = self._is_speech(frame)

            if is_speech:
                # 如果检测到语音，则更新最后一次语音时间戳
                self.last_voice_time = time.time()

                if not self.speaking:
                    # 如果之前未处于说话状态，则记录语音开始的位置
                    # len(self.frames) - 1 表示当前帧在总帧列表中的索引位置
                    self.speech_start_index = len(self.frames) - 1

                # 处理语音帧逻辑（如增加语音计数、切换状态等）
                self._handle_speech(frame)
            else:
                # 处理静音帧逻辑（如增加静音计数、判断是否结束语音等）
                self._handle_silence(frame)


    def _split_to_frames(self, audio_data):
        """
        将原始音频数据切分为符合 VAD 要求的帧（每帧 20ms）。

        参数:
            audio_data (bytes): 原始音频字节流，来自 PyAudio 的一次读取结果。

        返回:
            List[bytes]: 切分后的音频帧列表，每个元素是一个完整帧的字节数据。
        """
        frame_bytes_needed = self.frame_size * 2  # 每个采样点占 2 字节（int16）
        frames = []
        for i in range(0, len(audio_data), frame_bytes_needed):
            chunk = audio_data[i:i + frame_bytes_needed]
            if len(chunk) == frame_bytes_needed:
                # 只添加长度正确的帧（避免不完整的帧）
                frames.append(chunk)
        return frames


    def _is_speech(self, frame):
        """
        使用 WebRTC-VAD 和能量阈值判断当前帧是否为语音。

        参数:
            frame (bytes): 一个完整音频帧的字节数据。

        返回:
            bool: True 表示是语音帧，False 表示是静音帧。
        """
        if len(frame) != self.frame_size * 2:
            # 如果帧长度不合法，直接视为无效帧（非语音）
            return False
        try:
            # 使用 WebRTC VAD 判断是否为语音帧
            is_speech = self.vad.is_speech(frame, self.RATE)

            # 计算该帧的能量（绝对值的均值），用于辅助判断
            energy = np.mean(np.abs(np.frombuffer(frame, dtype=np.int16)))

            # 同时满足 VAD 判定为语音 且 能量超过设定阈值 才认为是有效语音帧
            return is_speech and energy > self.energy_threshold
        except Exception as e:
            # 出现异常则默认返回 False
            return False


    def _handle_speech(self, frame):
        """
        处理语音帧逻辑，更新状态变量并判断是否进入“说话”状态。

        参数:
            frame (bytes): 当前语音帧数据。
        """
        self.speech_count += 1      # 增加连续语音帧计数
        self.silence_count = 0      # 重置静音帧计数
        self.post_silence_frames.clear()  # 清除后置静音缓冲区

        if not self.speaking and self.speech_count >= self.speech_window:
            # 如果尚未开始说话，并且连续语音帧数达到阈值，则判定为正式说话开始
            self.speaking = True                      # 进入说话状态
            self.speaking_start_time = time.time()    # 记录说话开始时间
            self.pre_speech_frames.clear()            # 清除前置缓冲帧（已保存）


    def _handle_silence(self, frame):
        """
        处理检测到的静音帧逻辑。

        参数:
            frame (bytes): 当前处理的音频帧数据（字节流）。
        """
        # 清空语音计数器，因为当前帧不是语音帧
        self.speech_count = 0

        if self.speaking:
            # 如果当前处于“说话”状态，则增加静音帧计数
            self.silence_count += 1

            # 计算当前说话已持续的时间（单位：毫秒）
            speaking_duration = (time.time() - self.speaking_start_time) * 1000

            # 将该静音帧加入后置缓冲区（用于裁剪语音结尾）
            self.post_silence_frames.append(frame)

            # 如果后置缓冲区超过最大容量，则移除最早的一帧
            if len(self.post_silence_frames) > self.post_silence_buffer:
                self.post_silence_frames.pop(0)

            # 判断是否满足语音结束条件：
            # 连续静音帧数 >= 阈值 并且 说话时间 >= 500ms（避免误判）
            if self.silence_count >= self.silence_window and speaking_duration >= 500:
                self.speaking = False  # 结束说话状态
                self.speech_end_index = len(self.frames)  # 记录语音结束位置
                self.speech_ended.emit()  # 发出“语音结束”信号
                self._reset_state()  # 重置检测器内部状态
        else:
            # 如果尚未开始说话，则将该静音帧加入前置缓冲区
            # （用于在语音开始时保留前面的音频帧）
            if len(self.pre_speech_frames) >= self.pre_speech_buffer:
                # 如果前置缓冲区已满，则移除最早的一帧
                self.pre_speech_frames.pop(0)
            self.pre_speech_frames.append(frame)  # 添加当前帧到缓冲区


    def _reset_state(self):
        """
        重置 VAD 检测器的内部状态变量。
        在语音段落结束或超时后调用此方法。
        """
        self.speech_count = 0             # 语音帧计数归零
        self.silence_count = 0           # 静音帧计数归零
        self.speaking = False            # 退出说话状态
        self.pre_speech_frames.clear()   # 清空前置缓冲帧
        self.post_silence_frames.clear() # 清除后置缓冲帧
        self.last_voice_time = time.time()  # 更新最后一次检测到语音的时间
        logger.debug("检测器状态已重置")


    def save_audio_to_mp3(self):
        """
        将录制的音频数据保存为标准 mp3 文件。
        支持只保存有效语音段（通过 VAD 检测结果）或完整录音。
        """
        try:
            # 如果启用了中断检测并且有明确的语音起止索引
            if self.interrupt_running and self.speech_start_index != -1 and self.speech_end_index != -1:
                # 截取有效语音段（包含前后缓冲帧）
                start_idx = max(0, self.speech_start_index - self.pre_speech_buffer)
                end_idx = min(len(self.frames), self.speech_end_index + self.post_silence_buffer)
                audio_segment = self.frames[start_idx:end_idx]
                audio_data = b''.join(audio_segment)
                logger.info(f"保存VAD检测语音段: 位置{start_idx}-{end_idx}, 长度{len(audio_data)}字节")
            else:
                # 否则保存全部录音内容
                audio_data = b''.join(self.frames)

            # mp3 文件要求帧长度为偶数字节，若奇数字节则截断最后一个字节
            if len(audio_data) % 2 != 0:
                audio_data = audio_data[:-1]

            output_file = "./temp/recorded_audio.mp3"

            # 使用pydub将PCM数据转换为AudioSegment对象
            audio = AudioSegment(
                data=audio_data,  # 音频数据
                sample_width=2,  # 采样宽度：16bit = 2字节
                frame_rate=self.RATE,  # 采样率：16kHz
                channels=self.CHANNELS  # 声道数：单声道
            )

            # 导出为MP3文件，设置比特率为128k
            audio.export(output_file, format="mp3", bitrate="128k")

            # 成功回调通知主线程
            self.record_success.emit(output_file)

        except Exception as e:
            # 捕获异常并发出错误信号
            self.record_error.emit(self.objectName(), f"保存音频失败: {e}")

    def stop(self, save_flag):
        """
        外部调用：终止录音线程，并决定是否保存录音结果。

        参数:
            save_flag (bool): 是否保存录音文件。
        """
        self.is_recording = False       # 停止录音循环
        self.save_flag = save_flag      # 设置是否保存标志
        logger.info("录音线程已终止")


# 语音转文本子线程
class SoundToText:
    def __init__(self, client):
        """
        初始化语音转文本处理器。

        参数:
            client (Any): 用于调用远程服务的客户端对象（如 OpenAI 或 SiliconFlow 的客户端）。
        """
        self.client = client           # 外部传入的 API 客户端
        self.path = None               # 音频文件路径（由 get_path 设置）
        self.service = None            # 当前使用的服务类型（LOCAL_SERVICE / SILICONFLOW）
        self.model = None              # 使用的语音识别模型名称
        self.local_model = None        # 本地加载的语音识别模型实例

        # 回调注册系统：支持 stt_success 和 stt_error 事件
        self.handlers = {
            "stt_success": [],         # 成功回调列表
            "stt_error": []            # 错误回调列表
        }

    def on_stt_success(self, handler):
        """注册 stt_success 回调"""
        self.handlers["stt_success"].append(handler)

    def on_stt_error(self, handler):
        """注册 stt_error 回调"""
        self.handlers["stt_error"].append(handler)


    def emit(self, signal_name, *args):
        """
        统一触发回调信号。

        参数:
            signal_name (str): 要触发的信号名（"stt_success" 或 "stt_error"）
            *args: 传递给回调函数的参数
        """
        for handler in self.handlers.get(signal_name, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(*args))  # 异步调用协程
                else:
                    handler(*args)  # 同步调用普通函数
            except Exception as e:
                logger.error(f"执行 {signal_name} 回调失败: {e}")


    def get_path(self, path):
        """设置录音文件路径"""
        self.path = path
        logger.info(f'获取到录音文件路径：{path}')


    async def run(self):
        """
        执行语音识别主流程：
        - 判断当前使用的服务类型（本地 or 远程）
        - 加载模型或连接 API
        - 调用识别方法
        - 发出结果或错误信号
        """
        try:
            # 获取配置中的服务类型（LOCAL_SERVICE / SILICONFLOW）
            self.service = config.get_config('CHOICE.SERVICE')
            logger.info(f'开始语音识别，服务类型：{self.service}')

            # 检查音频文件是否存在
            if not os.path.exists(self.path):
                self.emit('stt_error', 'stt_thread', f"音频文件不存在: {self.path}")
                return
            # 根据服务类型选择识别方式
            if self.service == 'LOCAL_SERVICE':
                result = await self._recognize_local()
            elif self.service == 'SILICONFLOW':
                result = await self._recognize_siliconflow()
            else:
                self.emit('stt_error', 'stt_thread', f"不支持的服务类型: {self.service}")
                return

            # 日志记录并发出成功信号
            logger.info(f'语音识别成功: {result}')
            self.emit("stt_success", result)
            time.sleep(0.001)

        except asyncio.CancelledError:
            raise  # 必须重新抛出取消异常

        except Exception as e:
            # 记录错误并发出错误信号
            logger.error(f"语音识别过程异常: {e}")
            self.emit("stt_error", 'stt_thread', str(e))
            time.sleep(0.001)

    async def _recognize_local(self):
        """
        使用本地 ASR 模型进行语音识别。
        如果未加载模型，则先动态导入并初始化模型。
        """
        # 是否启用本地模型
        self.user_local_model = config.get_config('LOCAL_SERVICE.USE_LOCAL_MODEL')

        if not self.user_local_model:
            # 不使用本地模型，则使用远程模型接口
            self.model = config.get_config('LOCAL_SERVICE.SPEECH_REC')
            return await self._recognize_with_client(self.path, self.model)

        if self.local_model is None:
            try:
                logger.info('正在加载本地模型...')

                # 延迟导入，避免阻塞 UI
                funasr_module = importlib.import_module("funasr")
                postprocess_module = importlib.import_module("funasr.utils.postprocess_utils")

                # 加载本地模型
                self.funasr = funasr_module.AutoModel(
                    model=config.get_config('LOCAL_SERVICE.LOCAL_VOICE_MODEL_PATH'),
                    trust_remote_code=True
                )

                # 初始化后处理模块
                self.postprocess = postprocess_module.rich_transcription_postprocess
                self.local_model = self.funasr
                logger.info("本地模型加载成功...")

            except Exception as e:
                logger.error(f"加载本地模型失败: {e}")
                raise e

        logger.info("开始进行语音识别...")

        # 实际执行本地语音识别
        result = self.local_model.generate(
            input=self.path,
            cache={},
            language="auto",
            use_itn=True,
            batch_size_s=64,
        )

        # 后处理识别结果
        result = self.postprocess(result[0]['text'])
        logger.info(f"本地语音模型识别结果: {result}")
        return result


    async def _recognize_siliconflow(self):
        """
        使用 SiliconFlow 服务进行语音识别。
        """
        try:
            self.model = config.get_config(f'{self.service}.SPEECH_REC')
            return await self._recognize_with_client(self.path, self.model)
        except Exception as e:
            raise e


    async def _recognize_with_client(self, path, model):
        """
        使用指定的客户端对音频文件进行远程语音识别。

        参数:
            path (str): 音频文件路径
            model (str): 使用的语音识别模型名称

        返回:
            str: 识别出的文本内容
        """
        try:
            async with aiofiles.open(path, "rb") as f:
                content = await f.read()

            # 创建 BytesIO 流式文件对象
            audio_file = io.BytesIO(content)

            # 调用远程 API 进行语音识别
            response = await self.client.audio.transcriptions.create(
                file=("audio.mp3", audio_file, "audio/mp3"),
                model=model
            )

            return response.text

        except Exception as e:
            logger.error(f"语音识别过程异常: {e}")
            raise e


# 文本转语音子线程
class TextToSound:
    def __init__(self, client, audio_queue: queue.Queue, sentence_queue: queue.Queue):
        """
        初始化 TTS 子线程处理器。

        参数:
            client (Any): 用于调用远程服务的客户端对象（如 SiliconFlow 的客户端）
            audio_queue (queue.Queue): 音频数据输出队列，供播放线程使用
            sentence_queue (queue.Queue): 文本输入队列，接收待合成的文本句子
        """
        self.siliconflow_client = client     # 远程 TTS 客户端
        self.audio_queue = audio_queue       # 合成后的音频输出队列
        self.sentence_queue = sentence_queue # 待合成文本输入队列
        self.voice = None                    # 当前使用的语音角色名称
        self.tts_provider = None           # 使用的服务类型（LOCAL_SERVICE / SILICONFLOW）
        self.tts_running = False           # 是否正在运行 TTS 主循环
        self.start_flag = False            # 是否已开始合成

        # 回调注册系统：支持 tts_start、tts_error、tts_done 事件
        self.handlers = {
            "tts_start": [],               # 开始回调列表
            "tts_error": [],               # 错误回调列表
            "tts_done": []                 # 结束回调列表
        }


    def on_tts_start(self, handler):
        """注册 tts_start 回调"""
        self.handlers["tts_start"].append(handler)

    def on_tts_error(self, handler):
        """注册 tts_error 回调"""
        self.handlers["tts_error"].append(handler)

    def on_tts_done(self, handler):
        """注册 tts_done 回调"""
        self.handlers["tts_done"].append(handler)

    def emit(self, signal_name, *args):
        """
        统一触发回调信号。

        参数:
            signal_name (str): 要触发的信号名（"tts_start", "tts_error", "tts_done"）
            *args: 传递给回调函数的参数
        """
        for handler in self.handlers.get(signal_name, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(*args))  # 异步调用协程
                else:
                    handler(*args)  # 同步调用普通函数
            except Exception as e:
                logger.error(f"执行 {signal_name} 回调失败: {e}")

    async def run(self):
        """
        启动异步 TTS 主循环。
        如果尚未启动，则先发出 tts_start 信号。
        """
        if not self.start_flag:
            self.start_flag = True
            self.emit("tts_start")  # 发出开始信号
            await asyncio.sleep(0.001)

        self.tts_running = True
        await self.main_loop()


    async def main_loop(self):
        """
        持续监听 sentence_queue，取出文本并调用 _play_tts 进行语音合成。
        合成完成后将音频放入 audio_queue，供播放线程使用。
        支持结束标志 '__END_OF_SPEECH__'。
        """
        while self.tts_running:
            try:
                text = self.sentence_queue.get_nowait()
                if text and text != '__END_OF_SPEECH__':
                    logger.info(f"开始合成语音: {text}")

                    # 执行语音合成
                    audio_data = await self._play_tts(text)

                    # 将合成结果放入音频队列
                    self.audio_queue.put({text: audio_data})

                elif text == '__END_OF_SPEECH__':
                    logger.info("接收到结束标志 '__END_OF_SPEECH__'")
                    self.audio_queue.put({text: ''})
                    self.emit("tts_done")  # 发出合成完成信号

                await asyncio.sleep(0.001)

            except queue.Empty:
                await asyncio.sleep(0.01)  # 队列为空则短暂休眠

            except Exception as e:
                logger.error(f"主循环中语音合成失败: {e}")
                self.emit("tts_error", self.__class__.__name__, str(e))

    async def _play_tts(self, text):
        """
        语音合成主逻辑，根据配置选择本地或远程服务进行文本转语音（TTS）合成。

        参数:
            text (str): 待合成的文本内容

        返回:
            bytes or None: 合成后的音频字节流（WAV/MP3等格式），失败时返回 None
        """
        max_retries = 2                # 最大重试次数，防止网络或服务异常导致失败
        audio_data = None             # 用于保存最终的音频数据

        # 获取当前配置中选用的语音合成服务类型，如 "LOCAL_SERVICE" 或 "SILICONFLOW"
        self.tts_provider = config.get_config('CHOICE.SERVICE')

        # 重试机制：最多尝试 max_retries 次
        for attempt in range(max_retries):
            try:
                # 获取当前服务下配置的发音人（VOICE 名称，如 "zh-CN-XiaoxiaoNeural"）
                self.voice = config.get_config(f'{self.tts_provider}.VOICE')

                # 根据服务类型调用不同的 TTS 实现
                if self.tts_provider == 'LOCAL_SERVICE':
                    # 使用本地 TTS 合成方法
                    audio_data = await self.local_tts(text)
                elif self.tts_provider == 'SILICONFLOW':
                    # 使用远程 SiliconFlow 服务进行合成
                    audio_data = await self.siliconflow_tts(text)

                # 如果执行成功，跳出重试循环
                break

            except Exception as e:
                # 捕获并记录当前轮次的异常信息
                logger.error(f"第 {attempt + 1} 次合成失败: {e}")
                await asyncio.sleep(1)  # 简单等待后重试，防止连续请求失败

        # 所有尝试失败，发送错误信号
        if audio_data is None:
            self.emit("tts_error", self.__class__.__name__, '语音合成失败')
            return

        # 成功返回合成音频数据（通常是字节流）
        return audio_data

    async def local_tts(self, text):
        """
        使用微软 Edge-TTS 本地 API 进行语音合成。

        参数:
            text (str): 待合成的文本内容

        返回:
            bytes: 合成后的 mp3 格式音频字节流
        """
        communicate = edge_tts.Communicate(text, self.voice)
        audio_data = b""

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        mp3_stream = io.BytesIO(audio_data)
        audio = AudioSegment.from_file(mp3_stream, format="mp3")

        # 转换为标准 mp3 格式（16kHz 单声道 PCM）
        audio = audio.set_frame_rate(16000).set_channels(1)
        mp3_stream = io.BytesIO()
        audio.export(mp3_stream, format="mp3", bitrate="16k")

        return mp3_stream.getvalue()  # 返回 mp3 字节流

    async def siliconflow_tts(self, text):
        """
        使用 SiliconFlow 远程服务进行语音合成。

        参数:
            text (str): 待合成的文本内容

        返回:
            bytes: 合成后的 mp3 格式音频字节流
        """
        response = await self.siliconflow_client.audio.speech.create(
            model=config.get_config('SILICONFLOW.SPEECH_SYN'),  # 获取模型名称
            voice=self.voice,   # 获取语音角色
            input=text,         # 合成文本
            response_format="mp3",  # 输出格式为 mp3
            speed=1.0          # 语速设置
        )

        return await response.aread()

    def stop(self):
        """
        停止 TTS 主循环。
        """
        self.tts_running = False
        self.start_flag = False
        logger.info("已停止语音合成")


class PlayText(QThread):
    # 信号定义：供主线程监听播放状态
    play_start = pyqtSignal()       # 播放开始
    play_finish = pyqtSignal()      # 播放完成
    play_show = pyqtSignal(str)     # 正在播放的文本内容
    play_error = pyqtSignal(str, str)  # 播放异常发生时通知

    def __init__(self, audio_queue):
        """
        初始化语音播报线程。

        参数:
            audio_queue (queue.Queue): 音频数据输入队列，包含 {text: audio_data} 的字典结构。
        """
        super().__init__()
        self.audio_queue = audio_queue   # 接收音频数据的队列
        self.play_running = True         # 控制播放循环是否运行
        self.start_flag = True           # 是否是第一次播放
        self.setObjectName("play_thread")  # 设置线程名称，便于日志调试
        self.current_channel = None      # 当前播放的音频通道（pygame.mixer.Channel）

        logger.info("已启动语音播报线程")


    def run(self):
        """
        线程主函数：持续监听音频队列，取出音频并播放。
        支持结束标志 '__END_OF_SPEECH__'。
        """
        self.play_running = True
        while self.play_running:
            try:
                data = self.audio_queue.get_nowait()
                if data:
                    text = next(iter(data.keys()))
                    if text == '__END_OF_SPEECH__':
                        # 接收到播放结束标志
                        self.play_finish.emit()          # 发出播放完成信号
                        self.start_flag = True          # 重置为首次播放状态
                        logger.info("播放完成")
                        time.sleep(0.001)
                        continue

                    # 获取对应的音频数据
                    audio_data = next(iter(data.values()))

                    # 使用 pydub 加载音频数据（io.BytesIO 流）
                    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")

                    # 创建临时 mp3 文件供 pygame 播放
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3:
                        audio_segment.export(temp_mp3.name, format="mp3")
                        temp_mp3_path = temp_mp3.name

                    # 发出“播放显示”信号
                    self.play_show.emit(text)
                    time.sleep(0.001)

                    # 如果是第一次播放，则发出“播放开始”信号
                    if self.start_flag:
                        self.play_start.emit()
                        time.sleep(0.001)
                        self.start_flag = False

                    # 使用 pygame 播放音频文件
                    logger.info(f"开始播放: {text}")
                    sound = pygame.mixer.Sound(temp_mp3_path)  # 加载音频文件
                    self.current_channel = sound.play()        # 开始播放并记录当前通道

                    # 等待播放完成或被外部停止
                    while self.current_channel.get_busy():
                        if not self.play_running:
                            self.current_channel.stop()
                            break
                        time.sleep(0.01)
                    time.sleep(0.001)

            except queue.Empty:
                # 队列为空则短暂休眠
                time.sleep(0.01)

            except Exception as e:
                # 异常处理并发出错误信号
                logger.error(f"音频播放异常: {e}")
                self.play_error.emit(self.objectName(), f'语音播报失败: {e}')
                time.sleep(0.001)

    def stop(self):
        """
        停止当前播放，并终止播放线程。
        """
        self.play_running = False     # 结束播放循环
        self.start_flag = True        # 重置为首次播放状态
        if self.current_channel:
            self.current_channel.stop()  # 停止当前播放通道
        logger.info("已停止语音播报线程")


class PlayWakeUp(QThread):
    def __init__(self):
        """
        初始化唤醒语音播放线程。
        """
        super().__init__()
        self.file_path = None   # 待播放的音频文件路径
        self.channel = None     # 当前播放的音频通道（pygame.mixer.Channel）

    def get_file_path(self, file_path):
        """
        设置要播放的音频文件路径。

        参数:
            file_path (str): 音频文件的绝对或相对路径。
        """
        self.file_path = file_path


    def run(self):
        """
        线程主函数：加载并播放指定的音频文件。
        播放期间持续检测是否仍在播放，防止提前退出。
        """
        try:
            logger.info("开始播放唤醒语音...")

            # 加载音频文件
            sound = pygame.mixer.Sound(self.file_path)

            # 开始播放音频，并记录当前通道
            self.channel = sound.play()

            # 轮询等待播放完成
            while self.channel.get_busy():
                self.msleep(10)  # 短暂休眠避免 CPU 占用过高

        except Exception as e:
            logger.error(f"唤醒语音播放失败: {e}")
