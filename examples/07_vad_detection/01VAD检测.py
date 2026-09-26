import os
import time
import numpy as np
import pyaudio
import webrtcvad
from pydub import AudioSegment


class VADVoiceSegmenter:
    """
    基于 WebRTC VAD 的语音活动检测（VAD）录音器
    支持实时录音并自动分割语音段，保存为 MP3 文件

    该类使用 WebRTC 的语音活动检测器来识别音频流中的语音片段，
    自动开始和停止录音，并只保存包含语音的部分，去除静音段。
    """

    def __init__(self):
        """
        初始化 VAD 语音分割器，设置音频参数和检测参数
        """
        super().__init__()

        # -----------------------------
        # 音频录音参数配置
        # -----------------------------
        self.FORMAT = pyaudio.paInt16          # 16位采样格式，每个采样点占2字节
        self.CHANNELS = 1                      # 单声道录音
        self.RATE = 16000                      # 采样率16kHz，WebRTC VAD要求8000, 16000, 32000, 48000之一
        self.CHUNK = 1024                      # 每次从音频流读取的帧大小(字节数)
        self.frame_duration_ms = 20            # 每帧音频的时长为20ms，WebRTC VAD要求10, 20, 30ms之一
        self.frame_size = int(self.RATE * self.frame_duration_ms / 1000)  # 每帧的采样点数(16000*20/1000=320)

        # -----------------------------
        # VAD（语音活动检测器）初始化
        # -----------------------------
        self.vad = webrtcvad.Vad(3)            # 创建VAD对象，灵敏度等级0-3，0最不敏感，3最敏感
        self.energy_threshold = 300            # 音频能量阈值，用于辅助判断静音，避免纯噪声被误判为语音

        # -----------------------------
        # 语音检测窗口参数
        # -----------------------------
        self.speech_window = 10                # 连续多少帧被判定为语音后才确认开始说话(10帧=200ms)
        self.silence_window = self.speech_window * 3  # 连续多少帧静音后判定说话结束(30帧=600ms)
        self.pre_speech_buffer = 10            # 在检测到语音开始前，保留之前10帧音频作为前导缓冲
        self.post_silence_buffer = 10          # 在检测到语音结束后，保留之后10帧音频作为后导缓冲
        self.timeout_seconds = 5               # 最大等待语音超时时间，超过5秒无语音则自动结束

        # -----------------------------
        # 状态变量初始化
        # -----------------------------
        self.is_recording = False              # 标记是否正在进行录音
        self.interrupt_running = True          # 是否启用智能语音检测模式(自动开始/结束)
        self.frames = []                       # 存储录音过程中所有的音频帧数据
        self.pre_speech_frames = []            # 存储检测到语音前的缓冲音频帧
        self.post_silence_frames = []          # 存储检测到语音结束后的缓冲音频帧
        self.speech_count = 0                  # 连续检测到语音帧的计数器
        self.silence_count = 0                 # 连续检测到静音帧的计数器
        self.speaking = False                  # 标记当前是否正在说话(已确认语音开始)
        self.speech_start_index = -1           # 检测到语音开始时在frames中的索引位置
        self.speech_end_index = -1             # 检测到语音结束时在frames中的索引位置
        self.last_voice_time = time.time()     # 上一次检测到语音的时间戳，用于超时检测
        self.save_flag = True                  # 标记是否需要保存录音结果

        # 创建临时文件夹用于保存录音文件
        os.makedirs('./temp', exist_ok=True)

    def run(self):
        """
        主录音循环函数，负责打开音频流、读取音频数据并进行处理
        这是录音器的核心方法，控制整个录音流程
        """
        # 清空之前的音频帧数据
        self.frames.clear()
        # 创建PyAudio对象用于音频处理
        self.audio = pyaudio.PyAudio()

        # -----------------------------
        # 打开音频输入流
        # -----------------------------
        try:
            # 配置并打开音频输入流
            self.stream = self.audio.open(
                format=self.FORMAT,           # 采样格式
                channels=self.CHANNELS,       # 声道数
                rate=self.RATE,               # 采样率
                input=True,                   # 设置为输入流(录音)
                frames_per_buffer=self.CHUNK  # 每次读取的帧大小
            )
        except Exception as e:
            print(f"麦克风初始化失败: {e}")
            return

        # 标记开始录音
        self.is_recording = True

        # 如果启用了中断检测模式，重置检测状态
        if self.interrupt_running:
            self._reset_state()
            self.last_voice_time = time.time()

        try:
            # 持续录音循环
            while self.is_recording:
                # 从音频流中读取一帧数据
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                # 将读取的音频帧添加到存储列表中
                self.frames.append(data)

                # 如果启用了智能语音检测
                if self.interrupt_running:
                    current_time = time.time()

                    # 检查是否超时(长时间没有检测到语音)
                    if current_time - self.last_voice_time > self.timeout_seconds:
                        time.sleep(0.01)
                        break  # 超时则退出录音循环

                    # 对当前音频帧进行语音活动检测处理
                    self._process_audio_data(data)

                # 短暂休眠以降低CPU占用
                time.sleep(0.01)

        except Exception as e:
            print(f"录音数据读取异常: {e}")

        finally:
            # 录音结束后的清理工作
            # 如果需要保存录音，则保存为MP3文件
            if self.save_flag:
                self.save_audio_to_mp3()

            # 安全关闭音频流
            if self.stream:
                self.stream.stop_stream()  # 停止音频流
                self.stream.close()        # 关闭音频流
            if self.audio:
                self.audio.terminate()     # 终止PyAudio

            # 清空音频帧缓存
            self.frames.clear()
            # 关闭中断检测模式
            self.interrupt_running = False

    def _process_audio_data(self, data):
        """
        处理音频数据，进行语音活动检测

        参数:
            data (bytes): 从音频流读取的原始音频数据
        """
        # 将音频数据分割成固定长度的帧
        frames = self._split_to_frames(data)
        # 对每一帧进行语音检测
        for frame in frames:
            # 判断当前帧是否为语音
            is_speech = self._is_speech(frame)
            if is_speech:
                # 如果是语音帧，更新最后语音时间
                self.last_voice_time = time.time()
                # 如果之前未在说话状态，记录语音开始位置
                if not self.speaking:
                    self.speech_start_index = len(self.frames) - 1
                # 处理语音帧逻辑
                self._handle_speech(frame)
            else:
                # 如果是静音帧，处理静音逻辑
                self._handle_silence(frame)

    def _split_to_frames(self, audio_data):
        """
        将连续的音频数据分割成固定长度的帧

        参数:
            audio_data (bytes): 连续的PCM音频数据

        返回:
            list: 分割后的音频帧列表
        """
        # 计算每帧需要的字节数(采样点数*每采样点字节数)
        frame_bytes_needed = self.frame_size * 2  # 16位采样，每采样点2字节
        frames = []
        # 按帧大小分割音频数据
        for i in range(0, len(audio_data), frame_bytes_needed):
            chunk = audio_data[i:i + frame_bytes_needed]
            # 只保留完整帧
            if len(chunk) == frame_bytes_needed:
                frames.append(chunk)
        return frames

    def _is_speech(self, frame):
        """
        判断音频帧是否为语音，结合VAD检测和能量检测

        参数:
            frame (bytes): 单帧音频数据

        返回:
            bool: True表示是语音，False表示是静音
        """
        # 检查帧长度是否正确
        if len(frame) != self.frame_size * 2:
            return False
        try:
            # 使用WebRTC VAD检测是否为语音
            is_speech = self.vad.is_speech(frame, self.RATE)
            # 计算音频帧的能量(振幅的平均值)
            energy = np.mean(np.abs(np.frombuffer(frame, dtype=np.int16)))
            # 结合VAD结果和能量阈值判断是否为有效语音
            return is_speech and energy > self.energy_threshold
        except Exception:
            # 出现异常时默认判断为静音
            return False

    def _handle_speech(self, frame):
        """
        处理检测到语音帧的逻辑

        参数:
            frame (bytes): 检测为语音的音频帧
        """
        # 增加语音帧计数
        self.speech_count += 1
        # 清零静音帧计数
        self.silence_count = 0
        # 清空语音结束后的静音缓冲
        self.post_silence_frames.clear()

        # 如果之前未在说话，且连续语音帧达到阈值，则确认开始说话
        if not self.speaking and self.speech_count >= self.speech_window:
            self.speaking = True  # 标记为正在说话
            self.speaking_start_time = time.time()  # 记录说话开始时间
            self.pre_speech_frames.clear()  # 清空前导缓冲

    def _handle_silence(self, frame):
        """
        处理检测到静音帧的逻辑

        参数:
            frame (bytes): 检测为静音的音频帧
        """
        # 清零语音帧计数
        self.speech_count = 0

        # 如果当前正在说话
        if self.speaking:
            # 增加静音帧计数
            self.silence_count += 1

            # 计算说话持续时间(毫秒)
            speaking_duration = (time.time() - self.speaking_start_time) * 1000

            # 将静音帧添加到后导缓冲
            self.post_silence_frames.append(frame)
            # 如果缓冲帧数超过限制，移除最早的帧
            if len(self.post_silence_frames) > self.post_silence_buffer:
                self.post_silence_frames.pop(0)

            # 判断说话是否结束:连续静音帧达到阈值且说话时间足够长
            if self.silence_count >= self.silence_window and speaking_duration >= 500:
                self.speaking = False  # 标记为停止说话
                self.speech_end_index = len(self.frames)  # 记录语音结束位置
                self._reset_state()  # 重置检测状态
                self.stop(save_flag=True)  # 停止录音并保存
        else:
            # 如果未在说话，将静音帧添加到前导缓冲
            if len(self.pre_speech_frames) >= self.pre_speech_buffer:
                self.pre_speech_frames.pop(0)  # 移除最早的帧
            self.pre_speech_frames.append(frame)  # 添加当前帧

    def _reset_state(self):
        """
        重置语音检测器的内部状态，为下一次检测做准备
        """
        self.speech_count = 0           # 清零语音帧计数
        self.silence_count = 0          # 清零静音帧计数
        self.speaking = False           # 重置说话状态
        self.pre_speech_frames.clear()  # 清空前导缓冲
        self.post_silence_frames.clear() # 清空后导缓冲
        self.last_voice_time = time.time()  # 更新最后语音时间

    def save_audio_to_mp3(self):
        """
        将录音数据保存为MP3格式文件
        根据是否启用智能检测，决定保存完整录音还是仅保存语音段
        """
        try:
            # 如果启用了智能检测且检测到了语音开始和结束位置
            if self.interrupt_running and self.speech_start_index != -1 and self.speech_end_index != -1:
                # 计算保存的音频范围，包含前导和后导缓冲
                start_idx = max(0, self.speech_start_index - self.pre_speech_buffer)
                end_idx = min(len(self.frames), self.speech_end_index + self.post_silence_buffer)
                # 提取相应范围的音频帧
                audio_segment = self.frames[start_idx:end_idx]
                # 合并所有音频帧为连续的字节数据
                audio_data = b''.join(audio_segment)
            else:
                # 保存完整录音数据
                audio_data = b''.join(self.frames)

            # 确保音频数据长度为偶数(MP3要求)
            if len(audio_data) % 2 != 0:
                audio_data = audio_data[:-1]

            # 设置输出文件路径
            output_file = "./temp/recorded_audio.mp3"

            # 使用pydub将PCM数据转换为AudioSegment对象
            audio_segment = AudioSegment(
                data=audio_data,      # 音频数据
                sample_width=2,       # 采样宽度2字节(16位)
                frame_rate=self.RATE, # 采样率
                channels=1            # 单声道
            )
            # 导出为MP3文件
            audio_segment.export(output_file, format="mp3", bitrate="128k")
            print('录音成功保存为 MP3！！！')
            time.sleep(0.1)

        except Exception as e:
            print(f"保存录音文件异常: {e}")

    def stop(self, save_flag):
        """
        停止录音过程

        参数:
            save_flag (bool): 是否保存录音文件
        """
        self.is_recording = False  # 标记停止录音
        self.save_flag = save_flag  # 设置保存标志


def main():
    """
    主函数，用于测试VADVoiceSegmenter功能
    演示如何使用该类进行智能语音检测录音
    """
    print("🎙️ 正在初始化语音检测器...")
    # 创建VAD语音分割器实例
    vad = VADVoiceSegmenter()

    print("🎤 正在启动录音，请说话...")
    try:
        # 开始录音
        vad.run()
    except KeyboardInterrupt:
        # 捕获Ctrl+C中断信号
        print("\n🛑 正在停止录音...")
        # 停止录音并保存
        vad.stop(save_flag=True)
        print("✅ 录音已保存到 ./temp/recorded_audio.mp3")


if __name__ == "__main__":
    # 程序入口点
    main()
