import json
import pyaudio
from pypinyin import lazy_pinyin
from vosk import Model, KaldiRecognizer
from PyQt5.QtCore import QThread, pyqtSignal
from utils.config_manager import ConfigManager
from utils.logging_manager import get_logger

logger = get_logger(__name__)
config = ConfigManager.get_instance()


class AssistantState:
    # 空闲状态：助手未执行任何任务，等待用户输入
    IDLE = "IDLE"

    # 倾听状态：助手正在监听用户的语音输入
    LISTENING = "LISTENING"

    # 思考状态：助手已接收到语音输入，正在进行语音识别、理解或调用大模型生成回复
    THINKING = "THINKING"

    # 说话状态：助手正在通过 TTS 播放对用户问题的回答
    SPEAKING = "SPEAKING"


class WakeWordDetector(QThread):
    wake_detected = pyqtSignal()

    def __init__(self, sample_rate=16000):
        super().__init__()
        self.sample_rate = sample_rate
        self.wake_words = config.get_config('WAKE_WORD_OPTIONS.WAKE_WORDS')
        self.running = False

        model_path = config.get_config('WAKE_WORD_OPTIONS.MODEL_PATH')
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
        self.recognizer.SetWords(True)

        self.audio = None
        self.stream = None
        self.frame_duration = 20  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)

    def run(self):
        self.audio = pyaudio.PyAudio()
        self.running = True

        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=self.sample_rate,
                                      input=True,
                                      frames_per_buffer=self.frame_size)

        while self.running:
            data = self.stream.read(self.frame_size, exception_on_overflow=False)
            self._process(data)

        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def stop(self):
        self.running = False
        self.wait()

    def _process(self, data):
        # 实时检测 partial 部分，提升响应速度
        if self.recognizer.AcceptWaveform(data):
            full_result = json.loads(self.recognizer.Result()).get("text", "")
            self._check_wake_word(full_result, is_partial=False)

        partial_text = json.loads(self.recognizer.PartialResult()).get("partial", "")
        self._check_wake_word(partial_text, is_partial=True)

    def _check_wake_word(self, text, is_partial=False):
        text = text.strip().replace(" ", "")
        if not text:
            return

        text_pinyin = ''.join(lazy_pinyin(text))  # 转为无空格拼音
        for word in self.wake_words:
            word_pinyin = ''.join(lazy_pinyin(word))
            if word_pinyin in text_pinyin:
                logger.info(f"唤醒词检测成功: {word}（partial={is_partial}）")
                self.wake_detected.emit()
                self.recognizer.Reset()
                break
