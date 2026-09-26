# 导入所需的库
import asyncio  # 支持异步操作
import os  # 文件路径处理
import re  # 正则表达式处理
import edge_tts  # Edge 本地语音合成库
import pyaudio  # 录音输入输出库
from openai import OpenAI  # 兼容 SiliconFlow 的 OpenAI 客户端
import queue  # 队列，用于句子缓冲
import io  # 字节流处理
import time  # 时间处理
import tempfile  # 创建临时文件
from pydub import AudioSegment  # 音频格式转换库
import pygame  # 播放音频


class Recorder:
    """
    录音器类，用于录制音频并保存为MP3文件
    """
    def __init__(self):
        """初始化录音器对象"""
        self.is_recording = False  # 录音标志
        self.FORMAT = pyaudio.paInt16  # 音频格式 16 位
        self.CHANNELS = 1  # 单声道
        self.RATE = 16000  # 采样率 16kHz
        self.CHUNK = 1024  # 每帧大小

        self.audio = None  # PyAudio 实例
        self.stream = None  # 录音流
        self.frames = []  # 存放音频数据帧

        os.makedirs('./temp', exist_ok=True)  # 创建临时目录
        self.output_file = "./temp/recorded_audio.mp3"  # 音频保存路径

    def start(self, duration_sec=10):
        """
        开始录音，自动在 duration_sec 秒后停止
        
        Args:
            duration_sec (int): 录音持续时间（秒），默认10秒
            
        Returns:
            bool: 录音是否成功启动
        """
        self.audio = pyaudio.PyAudio()  # 初始化 PyAudio 对象，用于音频流操作
        self.frames = []  # 用于存储录音数据帧的列表

        try:
            self.stream = self.audio.open(  # 打开音频流，准备录音
                format=self.FORMAT,  # 音频格式，比如 paInt16
                channels=self.CHANNELS,  # 音频通道数，通常为单声道或立体声
                rate=self.RATE,  # 采样率，比如 44100 Hz
                input=True,  # 指明这是输入流（录音）
                frames_per_buffer=self.CHUNK  # 每个缓冲区的帧数，控制数据块大小
            )
        except Exception as e:
            print(f"无法打开麦克风: {e}")  # 捕获异常并提示无法打开麦克风
            return False  # 录音未能启动，返回 False

        self.is_recording = True  # 标记正在录音状态为 True
        print(f"开始录音，最长 {duration_sec} 秒...")  # 打印录音开始提示信息

        start_time = time.time()  # 记录录音开始的时间戳
        try:
            while self.is_recording:  # 循环录音，直到停止标志为 False
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)  # 从音频流读取一块数据
                self.frames.append(data)  # 将读取的数据块追加到帧列表中

                if time.time() - start_time >= duration_sec:  # 判断是否达到设定的录音时长
                    print("录音时间到，自动停止。")  # 打印自动停止提示
                    self.stop()  # 调用停止录音方法，结束录音
        except Exception as e:
            print(f"录音出错: {e}")  # 捕获录音过程中异常并打印错误
            self.stop()  # 出错时安全停止录音
        return True  # 成功开始录音返回 True

    def stop(self):
        """停止录音并保存为 mp3 文件"""
        self.is_recording = False  # 将录音状态标记为 False，停止录音循环
        if self.stream:  # 如果音频流存在
            self.stream.stop_stream()  # 停止音频流数据传输
            self.stream.close()  # 关闭音频流释放资源
        if self.audio:  # 如果 PyAudio 对象存在
            self.audio.terminate()  # 终止 PyAudio 释放资源

        self.save_to_mp3()  # 调用保存方法，将录音数据写入 mp3 文件

    def save_to_mp3(self):
        """将录音数据保存为 mp3 文件"""
        try:
            # 将所有音频帧数据连接成一个字节串
            audio_data = b''.join(self.frames)

            # PCM数据长度必须是偶数（16bit=2字节），如果为奇数则去掉最后一个字节
            if len(audio_data) % 2 != 0:
                audio_data = audio_data[:-1]

            # 使用pydub将PCM数据转换为AudioSegment对象
            audio = AudioSegment(
                data=audio_data,  # 音频数据
                sample_width=2,  # 采样宽度：16bit = 2字节
                frame_rate=self.RATE,  # 采样率：16kHz
                channels=self.CHANNELS  # 声道数：单声道
            )

            # 导出为MP3文件，设置比特率为128k
            audio.export(self.output_file, format="mp3", bitrate="128k")
            print(f"录音保存为 {self.output_file}")

        except Exception as e:
            print(f"保存录音失败: {e}")


class SoundToText:
    """
    语音识别类，将音频文件转换为文本
    """
    def __init__(self, client):
        """初始化语音识别模块"""
        self.client = client  # OpenAI客户端实例
        self.model = 'FunAudioLLM/SenseVoiceSmall'  # 云端使用的语音识别模型名称
        self.path = None  # 音频文件路径

    def get_path(self, path: str):
        """设置音频文件路径"""
        self.path = path  # 赋值音频文件路径，供识别时读取

    def run(self):
        """
        根据当前配置使用本地或云端模型识别音频文件。
        :return: 转写的文本内容
        """
        try:
            # 检查路径是否设置且文件是否存在
            if not self.path or not os.path.exists(self.path):
                raise FileNotFoundError(f"音频文件不存在: {self.path}")

            result = self._recognize_with_client()  # 调用云端识别方法

            # 打印识别结果
            print(f"[SoundToText] 识别结果：{result}")
            return result  # 返回结果

        except Exception as e:
            # 捕获并打印异常信息
            print(f"[SoundToText] 识别失败：{e}")
            return ""  # 返回空字符串表示失败

    def _recognize_with_client(self):
        """
        使用云端 API（SiliconFlow）进行语音识别。
        :return: 返回识别文本
        """
        try:
            # 读取本地音频文件内容
            with open(self.path, "rb") as f:
                # 调用 SiliconFlow API 发起识别请求
                response = self.client.audio.transcriptions.create(
                    file=f,  # 使用正确的文件元组
                    model=self.model  # 指定模型名称
                )

            return response.text  # 返回识别文本

        except Exception as e:
            # 捕获并打印异常信息
            print(f"[SoundToText] 云端识别失败: {e}")
            return ""  # 返回空字符串


class ChatWithLLM:
    """
    与大语言模型对话的类，处理用户输入并生成回复
    """
    def __init__(self, client, sentence_queue):
        """
        初始化聊天模块
        
        Args:
            client: 大语言模型API客户端实例
            sentence_queue: 用于存放分割后的句子的队列
        """
        self.client = client  # 大语言模型API客户端实例，用于发送请求
        self.sentence_queue = sentence_queue  # 用于存放分割后的句子的队列，方便异步处理
        self.text = ''  # 用户输入的文本，待发送给模型
        self.token_buffer = ''  # 缓冲区，存储尚未组成完整句子的模型输出片段

    def get_text(self, text):
        """
        设置要发送给模型的文本内容
        
        Args:
            text (str): 用户输入的文本
        """
        self.text = text  # 设置要发送给模型的文本内容

    def run(self):
        """
        运行聊天模型，生成回复并分句处理
        """
        # 构造对话消息，包含系统角色设定和用户输入
        messages = [
            {"role": "system", "content": """
                                你叫小布，是一位聪明、亲切的智能语音助手。
                                你说话简洁有力、逻辑清晰，风格自然活泼，懂技术但不死板，会穿插网络梗，但不使用低俗语言。
                                回复时禁止回复表情包、颜文字等不擅长播报的内容，只能回复口语化的内容。                                    
                                """},  # 系统角色，设定模型行为风格和限制
            {"role": "user", "content": f'{self.text} </no_think>'},  # 用户输入文本，加上特殊标记提示模型
        ]
        # 调用大模型的chat接口，开启流式返回
        response = self.client.chat.completions.create(
            model='Qwen/Qwen3-8B',
            messages=messages,
            stream=True)

        # 迭代接收模型流式输出
        for chunk in response:
            result = chunk.choices[0].delta.content  # 获取当前输出的文本增量
            if result and result.strip() not in ('<think>', '</think>', ''):  # 过滤特殊标记及空字符串
                self.token_buffer += result  # 将增量文本加入缓冲区
                if len(self.token_buffer) > 10:  # 当缓冲区内容长度超过10字符时尝试分句
                    sentence, self.token_buffer = self.split_token_to_sentence(self.token_buffer)
                    if sentence:  # 如果成功分割出完整句子
                        self.sentence_queue.put(sentence)  # 将句子放入队列，供后续处理或播放

    @staticmethod
    def split_token_to_sentence(token_buffer, max_len=40):
        """
        将模型输出的文本缓冲区分割成完整句子
        
        Args:
            token_buffer (str): 文本缓冲区
            max_len (int): 最大缓冲区长度，默认40
            
        Returns:
            tuple: (完整句子, 剩余缓冲区文本)
        """
        # 匹配以句号、感叹号、问号、波浪号结尾的强语气句子的正则表达式
        strong_pattern = r'([^。！？～~]*[。！？～~])'  
        strong_sentences = re.findall(strong_pattern, token_buffer)

        if strong_sentences:  # 如果匹配到强语气句子
            last_sentence = strong_sentences[-1].strip()  # 取最后一个完整句子
            # 计算剩余未组成完整句子的文本
            remaining_buffer = token_buffer[token_buffer.rfind(last_sentence) + len(last_sentence):]
            return last_sentence, remaining_buffer  # 返回完整句子和剩余缓冲文本

        if len(token_buffer) >= max_len:  # 如果缓冲区过长但无强语气句子，尝试用逗号分割
            comma_index = token_buffer.rfind('，', 0, max_len)  # 在max_len范围内找最后一个逗号
            if comma_index != -1:
                sentence = token_buffer[:comma_index + 1].strip()  # 截取逗号前的句子片段
                remaining_buffer = token_buffer[comma_index + 1:]  # 余下部分作为新缓冲区
                return sentence, remaining_buffer
            else:
                return None, token_buffer  # 未找到逗号，返回None表示无完整句子

        return None, token_buffer  # 缓冲区长度不足，继续等待更多token


class TextToSound:
    """
    文本转语音类，支持本地和云端两种语音合成方式
    """
    def __init__(self, tts_provider, siliconflow_client=None):
        """
        初始化文本转语音模块
        
        Args:
            tts_provider (str): 语音合成服务提供商 ('LOCAL_SERVICE' 或 'SILICONFLOW')
            siliconflow_client: SiliconFlow TTS 客户端实例（可选）
        """
        self.siliconflow_client = siliconflow_client  # SiliconFlow TTS 客户端实例，支持云端语音合成
        self.tts_provider = tts_provider  # 选择的语音合成服务提供商，LOCAL_SERVICE 或 SILICONFLOW
        self.local_voice = 'zh-CN-XiaoyiNeural'  # 本地Edge-TTS使用的中文语音名称
        self.siliconflow_voice = 'FunAudioLLM/CosyVoice2-0.5B:anna'  # SiliconFlow指定的声音模型和声音名称
        self.siliconflow_model = 'FunAudioLLM/CosyVoice2-0.5B'  # SiliconFlow使用的语音合成模型

    async def run(self, text: str) -> bytes:
        """
        主入口：传入文本，返回合成后的 mp3 音频字节。
        
        Args:
            text (str): 需要合成语音的文本内容
            
        Returns:
            bytes: 合成的音频数据（MP3格式）
        """
        max_retries = 2  # 最多重试两次
        # 最多尝试两次合成
        for attempt in range(max_retries):  
            try:
                if self.tts_provider == 'LOCAL_SERVICE':  # 使用本地Edge-TTS合成
                    return await self.local_tts(text)
                elif self.tts_provider == 'SILICONFLOW':  # 使用云端SiliconFlow合成
                    return await self.siliconflow_tts(text)
            except Exception as e:
                print(f"[TextToSound] 第 {attempt + 1} 次合成失败: {e}")  # 出错时打印异常信息
                await asyncio.sleep(1)  # 失败后等待1秒重试
        return b''  # 两次尝试失败后返回空字节串

    async def local_tts(self, text: str) -> bytes:
        """
        使用 edge-tts 本地服务生成语音，统一输出MP3格式

        Args:
            text (str): 需要合成语音的文本内容

        Returns:
            bytes: 合成的音频数据（MP3格式）
        """
        # 创建语音合成器实例，配置语音参数
        communicate = edge_tts.Communicate(
            text=text,  # 要合成的文本
            voice=self.local_voice,  # 使用的语音角色
            rate="+0%",  # 语速控制：0%表示正常速度
            pitch="+0Hz",  # 音调控制：0Hz表示正常音调
            volume="+0%",  # 音量控制：0%表示正常音量
        )  # 初始化语音合成器

        # 存储音频数据块的列表
        chunks = []

        # 异步流式接收音频数据
        async for chunk in communicate.stream():
            # 只处理音频类型的数据块
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])  # 将音频数据添加到列表中

        # 将所有音频数据块连接成完整的音频数据
        audio_data = b"".join(chunks)
        return audio_data  # 返回MP3格式的音频数据

    async def siliconflow_tts(self, text: str) -> bytes:
        """
        使用 SiliconFlow TTS API 合成语音，输出MP3格式

        Args:
            text (str): 需要合成语音的文本内容

        Returns:
            bytes: 合成的音频数据（MP3格式）
        """
        # 创建语音合成请求（使用指定模型和 voice，指定返回 mp3 格式）
        response = self.siliconflow_client.audio.speech.create(
            model=self.siliconflow_model,  # 指定使用的语音合成模型
            voice=self.siliconflow_voice,  # 指定语音角色
            input=text,  # 输入的文本内容
            response_format="mp3",  # 指定返回 mp3 格式
            speed=1.0  # 合成语速为 1.0 倍速（正常速度）
        )

        # 异步读取音频内容并返回（字节形式）
        return await response.aread()  # 异步读取响应内容并返回


def play_audio(audio_data):
    """
    同步播放音频文件，阻塞直到播放完成。
    
    Args:
        audio_data: mp3 格式的音频字节流
    """
    # 创建一个后缀为.mp3的不自动删除的临时文件，用于保存音频
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_mp3:
        temp_mp3_path = temp_mp3.name  # 记录临时文件路径

    try:
        # 从字节流读取mp3音频数据，生成AudioSegment对象
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
        # 导出音频为mp3格式到临时文件，确保文件格式正确
        audio_segment.export(temp_mp3_path, format="mp3")

        sound = pygame.mixer.Sound(temp_mp3_path)  # 从临时文件加载声音对象
        channel = sound.play()  # 播放声音，返回频道对象

        while channel.get_busy():  # 当声音正在播放时持续阻塞
            time.sleep(0.1)  # 休眠100毫秒避免CPU占用过高

    finally:
        # 播放完毕后，确保删除临时文件，释放磁盘空间
        if os.path.exists(temp_mp3_path):
            os.remove(temp_mp3_path)


def main():
    """
    主函数：实现完整的语音对话流程
    """
    pygame.mixer.init()  # 初始化pygame混音器模块
    recorder = Recorder()  # 初始化录音器实例

    client = OpenAI(  # 创建OpenAI客户端实例，用于聊天
        api_key='YOUR_SILICONFLOW_API_KEY',
        base_url='https://api.siliconflow.cn/v1'
    )
    sound_to_text = SoundToText(client)  # 初始化语音识别模块，使用云端模型
    sentence_queue = queue.Queue()  # 创建队列用于存储分句的模型回复
    chat_with_llm = ChatWithLLM(client, sentence_queue)  # 初始化聊天模块，传入客户端和队列
    text_to_sound = TextToSound(tts_provider='LOCAL_SERVICE')  # 初始化文本转语音模块，使用本地合成

    try:
        while True:  # 循环进行对话
            print("\n请说话（最长5秒）...")
            if not recorder.start(duration_sec=5):  # 开始录音，最多5秒，失败则重新开始
                continue

            sound_to_text.get_path(recorder.output_file)  # 设置录音文件路径到语音识别模块
            user_input = sound_to_text.run()  # 执行语音识别，获得用户输入文本
            if not user_input:
                print("未识别到有效语音输入")
                continue

            print(f"你说的是: {user_input}")

            chat_with_llm.get_text(user_input)  # 设置聊天模型的输入文本
            chat_with_llm.run()  # 运行聊天模型，开始生成回复

            llm_response = ""
            # 从队列读取模型回复的分句并拼接
            while not sentence_queue.empty():  
                llm_response += sentence_queue.get()

            if not llm_response:
                print("没有需要播报的内容")
                continue

            print(f"回复内容: {llm_response}")
            try:
                loop = asyncio.get_event_loop()  # 获取当前事件循环
                # 异步调用TTS合成
                audio_data = loop.run_until_complete(text_to_sound.run(llm_response))  
                if audio_data:
                    play_audio(audio_data)  # 同步播放合成音频
                else:
                    print("语音合成失败")
            except Exception as e:
                print(f"语音合成异常: {e}")

    finally:
        pygame.mixer.quit()  # 退出pygame混音器，释放音频资源


# 程序入口点
if __name__ == "__main__":
    main()  # 程序入口，调用main函数启动应用
