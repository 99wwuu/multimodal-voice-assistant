from PyQt5.QtCore import QThread, pyqtSignal
from openai import AsyncOpenAI
from utils.logging_manager import get_logger

logger = get_logger(__name__)


class ClientChange(QThread):
    # 自定义信号：finished，用于在任务完成后返回创建好的客户端对象（OpenAI 实例）
    finished = pyqtSignal(object)

    # 初始化方法，接收两个参数：
    # - url: API 服务地址（如 SiliconFlow 的 URL）
    # - api_key: API 密钥
    def __init__(self, url, api_key):
        super().__init__()
        self.url = url      # 存储 URL 地址
        self.api_key = api_key  # 存储 API 密钥

    # run 方法是 QThread 的核心方法，线程从这里开始执行任务
    def run(self):
        try:
            # 创建一个新的 OpenAI 客户端实例，使用传入的 API Key 和 Base URL
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.url
            )
            # 发出 finished 信号，并携带创建好的 client 对象
            self.finished.emit(client)
            logger.info("更改客户端成功！")
        except Exception as e:
            # 如果发生异常（例如网络问题或无效密钥），打印错误信息
            logger.error("更改客户端失败：", e)
