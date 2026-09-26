# 导入所需的库
import io               # 用于内存字节流操作
import time             # 用于时间相关操作
import pyaudio          # 用于音频输入输出处理
from openai import OpenAI      # 用于调用SiliconFlow API
from pydub import AudioSegment # 用于音频格式转换和处理


class Recorder:
    """
    录音器类，用于录制音频并以内存字节流形式返回，不保存到磁盘文件
    """

    def __init__(self):
        """
        初始化录音器参数
        """
        # 录音状态标志
        self.is_recording = False

        # 音频参数设置
        self.FORMAT = pyaudio.paInt16   # 音频格式：16位整数
        self.CHANNELS = 1               # 声道数：单声道
        self.RATE = 16000               # 采样率：16kHz
        self.CHUNK = 1024               # 音频块大小：每次读取的样本数

        # 音频对象初始化
        self.audio = None               # PyAudio实例
        self.stream = None              # 音频流对象
        self.frames = []                # 存储音频数据的帧列表

    def run(self, duration_sec=10):
        """
        开始录音，并在指定时长后自动停止

        Args:
            duration_sec (int): 录音持续时间（秒），默认10秒

        Returns:
            io.BytesIO: 包含录音数据的内存字节流对象，失败时返回None
        """
        # 创建PyAudio实例
        self.audio = pyaudio.PyAudio()
        # 清空之前的音频帧数据
        self.frames = []

        try:
            # 打开音频输入流
            self.stream = self.audio.open(
                format=self.FORMAT,         # 设置音频格式
                channels=self.CHANNELS,     # 设置声道数
                rate=self.RATE,             # 设置采样率
                input=True,                 # 设置为输入流（录音模式）
                frames_per_buffer=self.CHUNK  # 设置缓冲区大小
            )
        except Exception as e:
            # 处理无法打开麦克风的异常
            print(f"无法打开麦克风: {e}")
            return None

        # 设置录音状态为进行中
        self.is_recording = True
        print(f"开始录音，最长 {duration_sec} 秒...")

        # 记录开始录音的时间
        start_time = time.time()

        try:
            # 持续录音直到达到指定时长
            while self.is_recording:
                # 从音频流中读取数据块
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                # 将读取的数据添加到帧列表中
                self.frames.append(data)

                # 检查是否达到指定录音时长
                if time.time() - start_time >= duration_sec:
                    print("录音时间到，自动停止。")
                    self.stop()  # 停止录音
        except Exception as e:
            # 处理录音过程中的异常
            print(f"录音出错: {e}")
            self.stop()  # 发生错误时停止录音

        # 返回音频字节流数据
        return self.get_audio_bytes()

    def stop(self):
        """
        停止录音并释放相关资源
        """
        # 设置录音状态为停止
        self.is_recording = False

        # 关闭音频流
        if self.stream:
            self.stream.stop_stream()   # 停止音频流
            self.stream.close()         # 关闭音频流

        # 终止PyAudio实例
        if self.audio:
            self.audio.terminate()

    def get_audio_bytes(self) -> io.BytesIO:
        """
        将录制的音频数据转换为内存字节流对象

        Returns:
            io.BytesIO: 包含MP3格式音频数据的内存字节流对象
        """
        # 将所有音频帧数据连接成一个字节串
        audio_data = b''.join(self.frames)

        # 确保音频数据长度为偶数（避免解码错误）
        if len(audio_data) % 2 != 0:
            audio_data = audio_data[:-1]

        # 使用AudioSegment创建音频对象
        audio = AudioSegment(
            data=audio_data,        # 音频数据
            sample_width=2,         # 样本宽度：2字节（16位）
            frame_rate=self.RATE,   # 采样率
            channels=self.CHANNELS  # 声道数
        )

        # 创建内存字节流缓冲区
        buffer = io.BytesIO()
        # 将音频数据导出为MP3格式到内存缓冲区
        audio.export(buffer, format="mp3", bitrate="128k")
        # 将缓冲区指针重置到开始位置
        buffer.seek(0)
        # 返回包含音频数据的内存字节流对象
        return buffer


class SoundToText:
    """
    语音转文本类，直接使用内存中的音频数据进行语音识别
    """

    def __init__(self):
        """
        初始化语音识别模块
        """
        # 创建 OpenAI 客户端实例，配置为连接 SiliconFlow 的 API 地址
        self.client = OpenAI(
            api_key="YOUR_SILICONFLOW_API_KEY",  # API密钥
            base_url="https://api.siliconflow.cn/v1"  # SiliconFlow 的 API 网关地址
        )
        # 设置使用的语音识别模型名称
        self.model = "FunAudioLLM/SenseVoiceSmall"

    def run(self, audio_buffer: io.BytesIO):
        """
        使用云端API对内存中的音频数据进行语音识别

        Args:
            audio_buffer (io.BytesIO): 包含音频数据的内存字节流对象

        Returns:
            str: 识别出的文本内容，失败时返回空字符串
        """
        try:
            # 构造文件元组，包含文件名、文件对象和MIME类型
            file_tuple = ("audio.mp3", audio_buffer, "audio/mp3")

            # 调用 SiliconFlow API 发起识别请求
            response = self.client.audio.transcriptions.create(
                file=file_tuple,    # 传递音频文件元组
                model=self.model    # 指定模型名称
            )

            # 打印识别结果
            print(f"[SoundToText] 识别结果：{response.text}")
            # 返回识别文本
            return response.text

        except Exception as e:
            # 捕获并打印异常信息
            print(f"[SoundToText] 识别失败: {e}")
            # 发生异常时返回空字符串
            return ""


# 程序入口点
if __name__ == "__main__":
    # 创建录音器实例
    recorder = Recorder()
    # 开始录音，持续5秒，获取音频字节流数据
    audio_buffer = recorder.run(duration_sec=5)

    # 创建语音识别实例
    stt = SoundToText()
    # 对音频字节流数据进行语音识别
    text = stt.run(audio_buffer)
    # 打印最终识别文本
    print("最终识别文本:", text)
