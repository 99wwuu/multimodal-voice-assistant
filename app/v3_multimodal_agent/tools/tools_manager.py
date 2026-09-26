from tools.get_weather import weather_tool
from tools.camera_eyes import camera_eyes

tool_list = [
    {
        "type": "function",
        "function": {
            "description": "获取天气状况的天气工具，当用户希望获取某城市的天气状况时，需要调用此工具。",
            "name": "get_weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": '要获取天气的城市名称，比如北京、上海。'
                    }
                },
                "required": ["city"]
            }
        },
    },
    {
        "type": "function",
        "function": {
            "name": "VQA",
            "description": "This tool can answer the input question based on the image.",
        },
    },
]

callback_list = {
    'get_weather': weather_tool.run,
    'VQA': camera_eyes.run,
}