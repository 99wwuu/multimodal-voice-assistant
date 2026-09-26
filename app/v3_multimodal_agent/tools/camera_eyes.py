
import base64
import cv2
from openai import AsyncOpenAI, APIStatusError
from utils.config_manager import ConfigManager
from utils.logging_manager import get_logger


logger = get_logger(__name__)


class ImageAnalyzer:

    def __init__(self):
        self.config = ConfigManager.get_instance()
        self.image_base64 = None

    def get_vl_image(self, image_np):
        _, buffer = cv2.imencode('.png', image_np)  # 将图像编码为 PNG 格式
        # 将图像数据转换为 base64 编码字符串，方便后续使用
        self.image_base64 = base64.b64encode(buffer).decode('utf-8')

    async def run(self, args):
        try:
            self.service = 'SILICONFLOW'
            self.model = self.config.get_config(f'{self.service}.VL')
            self.client = AsyncOpenAI(api_key=self.config.get_config(f'{self.service}.API_KEY'),
                                 base_url=self.config.get_config(f'SILICONFLOW.URL'))
            completion = await self.client.chat.completions.create(
                model='Pro/Qwen/Qwen2.5-VL-7B-Instruct',
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{self.image_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": '简单描述一下这张图像。'
                            }
                        ]
                    }],
                stream=True,
            )
            mesag = ""
            async for chunk in completion:
                if chunk.choices:
                    content = chunk.choices[0].delta.content
                    if content:
                        mesag += content
                else:
                    continue
            return mesag

        except APIStatusError as e:
            # 捕获具体的 HTTP 错误，比如 400、500
            logger.error(f"大模型接口错误，状态码: {e.status_code}, 内容: {e.body}")
            if e.status_code == 400:
                return "传来的图片无法识别，也可能是摄像头没有启动"

        except Exception as e:
            logger.error(e)
            return '多模态大模型识别有误'


camera_eyes = ImageAnalyzer()
