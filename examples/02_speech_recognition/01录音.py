# 导入所需的库
import os               # 用于文件和目录操作
import time             # 用于时间相关操作
import pyaudio          # 用于音频输入输出处理
from pydub import AudioSegment  # 用于音频格式转换和处理


class Recorder:
    """
    录音器类，用于录制音频并保存为MP3格式文件
    """

    def __init__(self):
        """
        初始化录音器参数
        """
        # 录音状态标志
        self.is_recording = False

        # 音频参数设置2
        self.FORMAT = pyaudio.paInt16   # 音频格式：16位整数
        self.CHANNELS = 1               # 声道数：单声道
        self.RATE = 16000               # 采样率：16kHz
        self.CHUNK = 1024               # 音频块大小：每次读取的样本数

        # 音频对象初始化
        self.audio = None               # PyAudio实例
        self.stream = None              # 音频流对象
        self.frames = []                # 存储音频数据的帧列表

        # 创建临时目录并设置输出文件路径
        os.makedirs('./temp', exist_ok=True)            # 创建temp目录用于存储录音文件
        self.output_file = "./temp/recorded_audio.mp3"  # 设置录音文件保存路径

    def run(self, duration_sec=10):
        """
        开始录音，并在指定时长后自动停止

        Args:
            duration_sec (int): 录音持续时间（秒），默认10秒

        Returns:
            bool: 录音是否成功启动
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
                frames_per_buffer=self.CHUNK,  # 设置缓冲区大小
            )
        except Exception as e:
            # 处理无法打开麦克风的异常
            print(f"无法打开麦克风: {e}")
            return False

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
        return True

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

        # 保存录音为MP3文件
        self.save_to_mp3()

    def save_to_mp3(self):
        """
        将录制的音频数据保存为MP3格式文件
        """
        try:
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

            # 导出为MP3格式文件
            audio.export(self.output_file, format="mp3", bitrate="128k")
            print(f"录音保存为 {self.output_file}")

        except Exception as e:
            # 处理保存失败的异常
            print(f"保存录音失败: {e}")


# 程序入口点
if __name__ == "__main__":
    recorder = Recorder()           # 创建录音器实例
    recorder.run(duration_sec=5)    # 开始录音，持续5秒
