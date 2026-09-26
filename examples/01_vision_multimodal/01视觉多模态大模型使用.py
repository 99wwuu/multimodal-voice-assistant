# 导入所需的库
import base64       # 用于图像数据的编码和解码
import cv2          # OpenCV库，用于图像处理
import asyncio      # 异步编程支持
from openai import AsyncOpenAI, APIStatusError  # 异步OpenAI客户端和异常处理


class ImageAnalyzer:
    """
    图像分析器类，用于调用多模态大模型对图像进行分析
    """

    def __init__(self):
        """
        初始化方法，设置API密钥和基础URL
        """
        self.api_key = 'YOUR_SILICONFLOW_API_KEY'  # SiliconFlow API密钥
        self.base_url = 'https://api.siliconflow.cn/v1'                      # API基础URL
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)  # 创建异步客户端

    async def run(self, image_np):
        """
        异步运行图像分析方法

        Args:
            image_np: numpy数组格式的图像数据

        Returns:
            str: 图像分析结果的文本描述
        """
        try:
            # 将numpy图像数据编码为JPEG格式
            _, buffer = cv2.imencode('.jpg', image_np)

            # 将图像数据转换为 base64 编码字符串，方便后续使用
            self.image_base64 = base64.b64encode(buffer).decode('utf-8')

            # 调用SiliconFlow API创建聊天完成请求
            completion = await self.client.chat.completions.create(
                model='Qwen/Qwen3-Omni-30B-A3B-Thinking',  # 使用Qwen2.5-VL-7B视觉语言模型
                messages=[
                    {
                        "role": "user",           # 用户角色
                        "content": [
                            {
                                "type": "image_url",  # 内容类型为图像URL
                                "image_url": {
                                    # 将base64编码的图像数据作为URL传递
                                    "url": f"data:image/png;base64,{self.image_base64}"
                                }
                            },
                            {
                                "type": "text",       # 内容类型为文本
                                "text": '图片中有几个人'  # 请求模型对图像进行描述
                            }
                        ]
                    }],
                stream=True,  # 启用流式响应
            )

            mesag = ""  # 存储完整的响应消息
            # 异步迭代处理流式响应数据
            async for chunk in completion:
                if chunk.choices:  # 如果响应中有选择项
                    content = chunk.choices[0].delta.content  # 获取响应内容片段
                    if content:   # 如果内容不为空
                        mesag += content  # 累加内容
                        print(mesag, flush=True)  # 实时打印输出
                else:
                    continue  # 跳过空响应
            return mesag  # 返回完整的消息

        # 处理API状态错误
        except APIStatusError as e:
            # 捕获具体的 HTTP 错误，比如 400、500
            if e.status_code == 400:
                return "传来的图片无法识别，也可能是摄像头没有启动"

        # 处理其他异常
        except Exception as e:
            return '多模态大模型识别有误'

# 异步主函数
async def main():
    """
    主函数，用于执行图像分析流程
    """
    # 创建图像分析对象
    image_analyzer = ImageAnalyzer()

    # 加载图像并编码为 base64 格式
    image_np = cv2.imread('./bus.jpg')  # 读取本地图像文件（如需替换路径，自行修改）

    # 调用图像分析方法，发起推理
    await image_analyzer.run(image_np)

# 程序入口点
if __name__ == '__main__':
    asyncio.run(main())  # 运行异步主函数
