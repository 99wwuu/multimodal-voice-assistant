# 导入异步支持、内存IO操作
import asyncio  # 用于异步编程支持

# 导入 edge-tts 库（微软语音服务）
import edge_tts  # 用于本地文本转语音合成，基于微软Edge浏览器的TTS功能

# 导入 SiliconFlow 客户端（用于远程语音合成）
from openai import AsyncOpenAI  # 异步OpenAI客户端，用于调用SiliconFlow API


# 定义语音合成类
class TextToSound:
    """
    文本转语音类，支持本地edge-tts和远程SiliconFlow两种合成方式
    """
    def __init__(self, tts_provider, siliconflow_client=None):
        """
        初始化语音合成器

        Args:
            tts_provider (str): TTS提供方类型，'LOCAL_SERVICE'或'SILICONFLOW'
            siliconflow_client (AsyncOpenAI, optional): SiliconFlow客户端实例
        """
        # 初始化：接收 TTS 提供方类型和（可选的）siliconflow 客户端
        self.siliconflow_client = siliconflow_client

        # 设置 TTS 提供方，'LOCAL_SERVICE' 表示使用 edge-tts 本地合成
        self.tts_provider = tts_provider

        # edge-tts 默认使用的中文女声 Xiaoyi
        self.local_voice = 'zh-CN-liaoning-XiaobeiNeural'

        # siliconflow 的默认 voice 和模型名称（需确保支持）
        self.siliconflow_voice = 'FunAudioLLM/CosyVoice2-0.5B:alex'
        self.siliconflow_model = 'FunAudioLLM/CosyVoice2-0.5B'

    async def run(self, text: str) -> bytes:
        """
        主入口：传入文本，返回合成后的 mp3 音频字节。

        Args:
            text (str): 需要合成语音的文本内容

        Returns:
            bytes: 合成的音频数据（MP3格式）
        """
        max_retries = 2  # 最多重试两次

        # 重试机制：最多尝试max_retries次
        for attempt in range(max_retries):
            try:
                # 根据配置选择不同的TTS服务
                if self.tts_provider == 'LOCAL_SERVICE':
                    # 使用本地 edge-tts 合成
                    return await self.local_tts(text)
                elif self.tts_provider == 'SILICONFLOW':
                    # 使用远程 siliconflow 合成
                    return await self.siliconflow_tts(text)
            except Exception as e:
                # 出错时打印错误并等待一秒重试
                print(f"[TextToSound] 第 {attempt + 1} 次合成失败: {e}")
                await asyncio.sleep(1)  # 等待1秒后重试

        return b''  # 所有尝试失败，返回空字节

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
            text=text,              # 要合成的文本
            voice=self.local_voice, # 使用的语音角色
            rate="+0%",             # 语速控制：0%表示正常速度
            pitch="+0Hz",           # 音调控制：0Hz表示正常音调
            volume="+0%",           # 音量控制：0%表示正常音量
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
        response = await self.siliconflow_client.audio.speech.create(
            model=self.siliconflow_model,    # 指定使用的语音合成模型
            voice=self.siliconflow_voice,    # 指定语音角色
            input=text,                      # 输入的文本内容
            response_format="mp3",           # 指定返回 mp3 格式
            speed=1.0                        # 合成语速为 1.0 倍速（正常速度）
        )

        # 异步读取音频内容并返回（字节形式）
        return await response.aread()  # 异步读取响应内容并返回


# 主函数：异步运行 TTS 合成并保存文件
async def main():
    """
    主函数：演示如何使用TextToSound类进行语音合成
    """

    # 创建SiliconFlow API客户端实例
    client = AsyncOpenAI(
        api_key='YOUR_SILICONFLOW_API_KEY',  # API密钥
        base_url='https://api.siliconflow.cn/v1'  # SiliconFlow API地址
    )

    # 创建 TTS 实例，使用本地 edge-tts 合成
    tts = TextToSound('LOCAL_SERVICE')
    # 创建 TTS 实例，使用远程 SiliconFlow 合成
    # tts = TextToSound('SILICONFLOW', siliconflow_client=client)

    # 调用合成方法，传入文本，获取返回的音频数据
    mp3_data = await tts.run("你好，欢迎使用语音合成功能！")

    # 将音频数据写入本地文件
    with open("output.mp3", "wb") as f:  # 以二进制写入模式打开文件
        f.write(mp3_data)  # 将MP3音频数据写入文件


if __name__ == '__main__':
    # 使用asyncio.run()运行异步主函数
    asyncio.run(main())
