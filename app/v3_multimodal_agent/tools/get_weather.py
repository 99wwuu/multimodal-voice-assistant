import os

import requests
from pydantic import Field


# 定义心知天气API的工具类
class WeatherTool:
    city: str = Field(description="City name, include city and county")

    def __init__(self, api_key) -> None:
        self.api_key = api_key

    async def run(self, args):
        city = args['city']
        url = f"https://api.seniverse.com/v3/weather/now.json?key={self.api_key}&location={city}&language=zh-Hans&unit=c"
        # 构建 API 请求 URL 返回结果
        response = requests.get(url)
        if response.status_code == 200:  # 请求成功
            data = response.json()  # 解析返回的JSON
            return data  # 返回格式化后的天气信息
        else:
            return f"无法获取{city}的天气信息。"


# 从环境变量读取心知天气密钥，请勿将真实密钥硬编码提交到 GitHub
api_key = os.getenv("WEATHER_API_KEY", "YOUR_SENIVERSE_API_KEY")
weather_tool = WeatherTool(api_key)