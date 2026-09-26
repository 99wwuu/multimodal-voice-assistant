import json  
import pyaudio  
from pypinyin import lazy_pinyin  
from vosk import Model, KaldiRecognizer  


class WakeWordDetector:
    """
    基于 Vosk 的唤醒词检测器
    支持中文唤醒词，通过拼音匹配实现
    """

    def __init__(self, sample_rate=16000, on_wake_callback=None):
        """
        初始化唤醒词检测器

        Args:
            sample_rate (int): 音频采样率，默认16kHz
            on_wake_callback (Callable): 检测到唤醒词时的回调函数
        """
        super().__init__()
        self.sample_rate = sample_rate  # 采样率
        self.running = False  # 是否正在监听
        self.on_wake_callback = on_wake_callback  # 唤醒回调函数

        # 加载 Vosk 模型
        model_path = 'models/vosk-model-small-cn-0.22'  # 模型路径
        self.model = Model(model_path)

        # 初始化识别器
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
        self.recognizer.SetWords(True)  # 设置返回词级信息

        # 音频流相关
        self.audio = None
        self.stream = None

        # 帧参数：每帧 20ms
        self.frame_duration = 20  # 帧时长（毫秒）
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)  # 帧大小（采样点数）

        # 唤醒词列表，可添加多个
        self.wake_words = ['小布小布']

    def run(self):
        """
        启动监听线程，实时捕获音频并识别唤醒词
        """
        self.audio = pyaudio.PyAudio()  # 初始化 PyAudio
        self.running = True  # 设置监听标志为 True

        # 打开音频输入流
        self.stream = self.audio.open(
            format=pyaudio.paInt16,  # 16位采样
            channels=1,  # 单声道
            rate=self.sample_rate,  # 采样率
            input=True,  # 输入模式
            frames_per_buffer=self.frame_size  # 每帧大小
        )

        # 循环读取音频并处理
        while self.running:
            data = self.stream.read(self.frame_size, exception_on_overflow=False)  # 读取一帧音频
            self._process(data)  # 处理音频帧

        # 停止并关闭音频流
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def stop(self):
        """停止唤醒监听"""
        self.running = False

    def _process(self, data):
        """
        处理每帧音频，进行识别并检测唤醒词

        Args:
            data (bytes): 音频帧字节流
        """
        # 完整语音识别结果
        if self.recognizer.AcceptWaveform(data):
            full_result = json.loads(self.recognizer.Result()).get("text", "")
            self._check_wake_word(full_result, is_partial=False)


        # 部分识别结果（用于实时检测）
        partial_text = json.loads(self.recognizer.PartialResult()).get("partial", "")
        self._check_wake_word(partial_text, is_partial=True)

    def _check_wake_word(self, text, is_partial=False):
        """
        检查识别文本中是否包含唤醒词

        Args:
            text (str): 识别结果文本
            is_partial (bool): 是否为部分识别结果
        """
        text = text.strip().replace(" ", "")  # 去除空格
        if not text:
            return

        # 转为拼音进行匹配，避免空格或汉字差异影响
        text_pinyin = ''.join(lazy_pinyin(text))
        print('实时语音输入的拼音：', text_pinyin)
        for word in self.wake_words:
            word_pinyin = ''.join(lazy_pinyin(word))
            print(f"唤醒词拼音：{word_pinyin}")
            if word_pinyin in text_pinyin:
                print(f"✅ 唤醒词：{word}")

                # 调用回调函数
                if callable(self.on_wake_callback):
                    self.on_wake_callback()

                # 识别器重置，避免重复触发
                self.recognizer.Reset()
                break


# 测试回调函数
def on_wake():
    print("✅ 成功触发唤醒回调函数！！！")


if __name__ == "__main__":
    detector = WakeWordDetector(
        sample_rate=16000,
        on_wake_callback=on_wake  # 设置唤醒回调
    )

    print("👂 正在监听唤醒词（例如：小布小布）...")
    try:
        detector.run()  # 启动监听
    except KeyboardInterrupt:
        print("\n🛑 正在停止唤醒监听...")
        detector.stop()
