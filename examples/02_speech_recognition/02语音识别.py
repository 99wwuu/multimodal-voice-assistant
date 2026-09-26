# 导入操作系统相关库（如路径检查）
import os

# 导入 OpenAI SDK，这里用于调用 SiliconFlow 的 API（兼容接口）
from openai import OpenAI


class SoundToText:
    """
    语音转文本模块，使用云端模型（SiliconFlow API）。
    该类负责将音频文件转换为文本内容
    """

    def __init__(self):
        """
        初始化语音识别模块。
        创建OpenAI客户端实例并配置相关参数
        """
        # 创建 OpenAI 客户端实例，配置为连接 SiliconFlow 的 API 地址
        self.client = OpenAI(
            api_key='YOUR_SILICONFLOW_API_KEY',  # 替换为你的 API Key
            base_url='https://api.siliconflow.cn/v1'  # SiliconFlow 的 API 网关地址
        )
        # 设置使用的语音识别模型名称
        self.model = 'FunAudioLLM/SenseVoiceSmall'  # 云端使用的语音识别模型名称
        # 初始化音频文件路径为None
        self.path = None  # 音频文件路径

    def get_path(self, path: str):
        """
        设置要识别的音频文件路径。
        :param path: 音频文件路径
        """
        self.path = path  # 设置路径
        print(f"[SoundToText] 设置音频路径: {self.path}")  # 打印确认信息

    def run(self):
        """
        根据当前配置使用云端模型识别音频文件。
        执行完整的语音识别流程
        :return: 转写的文本内容，失败时返回空字符串
        """
        try:
            # 检查路径是否设置且文件是否存在
            if not self.path or not os.path.exists(self.path):
                # 如果路径未设置或文件不存在，抛出文件未找到异常
                raise FileNotFoundError(f"音频文件不存在: {self.path}")

            # 调用云端识别方法进行语音识别
            result = self._recognize_with_client()  # 调用云端识别方法

            # 打印识别结果
            print(f"[SoundToText] 识别结果：{result}")
            # 返回识别结果
            return result  # 返回结果

        except Exception as e:
            # 捕获并打印异常信息
            print(f"[SoundToText] 识别失败，{e}")
            # 发生异常时返回空字符串表示失败
            return ""  # 返回空字符串表示失败

    def _recognize_with_client(self):
        """
        使用云端 API（SiliconFlow）进行语音识别。
        :return: 返回识别文本，失败时返回空字符串
        """
        try:
            # 以二进制只读模式打开本地音频文件
            with open(self.path, "rb") as f:
                # 调用 SiliconFlow API 发起识别请求
                response = self.client.audio.transcriptions.create(
                    file=f,  # 传递音频文件对象
                    model=self.model  # 指定使用的语音识别模型名称
                )

            # 返回API响应中的文本内容
            return response.text  # 返回识别文本

        except Exception as e:
            # 捕获并打印异常信息
            print(f"[SoundToText] 云端识别失败: {e}")
            # 发生异常时返回空字符串
            return ""  # 返回空字符串表示识别失败


# ---------------- 示例用法 ------------------
if __name__ == '__main__':
    # ✅ 云端识别方式（调用 SiliconFlow）
    stt = SoundToText()  # 初始化为使用云端模型
    stt.get_path("./temp/recorded_audio.mp3")  # 设置音频路径
    text = stt.run()  # 执行识别
