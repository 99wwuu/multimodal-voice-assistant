import threading
from pathlib import Path
from typing import Dict, Any
from ruamel.yaml import YAML

from utils.logging_manager import get_logger

logger = get_logger(__name__)


class ConfigManager:
    # 用于存储 ConfigManager 的单例实例
    _instance = None

    # 线程锁对象，确保在多线程环境下 ConfigManager 的实例化是线程安全的
    _lock = threading.Lock()

    # 配置文件所在目录路径，__file__ 表示当前文件（config_manager.py）的位置，
    # Path(__file__).parent.parent 获取当前文件的上两级目录，然后拼接 "config" 文件夹
    CONFIG_DIR = Path(__file__).parent.parent / "config"

    # 配置文件的完整路径，即 config.yaml 文件位于 CONFIG_DIR 目录下
    CONFIG_FILE = CONFIG_DIR / "config.yaml"

    # 创建一个 YAML 对象，用于后续加载和转储 YAML 格式的配置文件
    yaml = YAML()

    # 设置 YAML 输出格式的缩进参数：
    # mapping: 映射（字典）的缩进为 2 个空格；
    # sequence: 序列（列表）的缩进为 4 个空格；
    # offset: 列表项与缩进之间的偏移为 2 个空格
    yaml.indent(mapping=4, sequence=4, offset=2)

    # 设置保留 YAML 文件中的引号，保持原始格式不变
    yaml.preserve_quotes = True

    DEFAULT_CONFIG = '''
# 唤醒词配置
WAKE_WORD_OPTIONS:
    USE_WAKE_WORD: false                                                # 是否启用唤醒词
    WAKE_WORDS:                                                         # 唤醒词列表
    - 小布小布                  
    MODEL_PATH: ./models/vosk-model-small-cn-0.22                       # 唤醒模型路径

# 本地服务配置
LOCAL_SERVICE:
    URL: https://api.siliconflow.cn/v1                                  # 服务地址
    API_KEY: YOUR_SILICONFLOW_API_KEY        # API_KEY
    LLM: Qwen/Qwen3-8B                                                  # 对话模型       
    VL: Pro/Qwen/Qwen2.5-VL-7B-Instruct                                 # 视觉多模态模型
    SPEECH_REC: FunAudioLLM/SenseVoiceSmall                             # 语音识别模型
    VOICE: zh-CN-XiaoxiaoNeural                                         # edge-tts音色

# 硅基流动服务配置
SILICONFLOW:
    URL: https://api.siliconflow.cn/v1                                  # 服务地址
    API_KEY: YOUR_SILICONFLOW_API_KEY        # API_KEY
    LLM: Qwen/Qwen3-8B                                                  # 对话模型
    VL: Pro/Qwen/Qwen2.5-VL-7B-Instruct                                 # 视觉多模态模型
    SPEECH_REC: FunAudioLLM/SenseVoiceSmall                             # 语音识别模型
    SPEECH_SYN: FunAudioLLM/CosyVoice2-0.5B                             # 语音合成模型
    VOICE: FunAudioLLM/CosyVoice2-0.5B:diana                            # 硅基流动音色

# MQTT配置
MQTT_SERVICE:
    BROKER: 127.0.0.1                                                   # MQTT服务器地址
    PORT: 1883                                                          # MQTT服务器端口
    PUB_TOPIC: control                                                  # 发布主题
    SUB_TOPIC: state                                                    # 订阅主题

# 摄像头配置
CAMERA:
    camera_index: 0                                                     # 摄像头索引

# 服务选择
CHOICE:
    SERVICE: LOCAL_SERVICE                                              # 当前使用的服务

# 天气API配置
WEATHER_API_KEY:
    WEATHER_API_KEY: YOUR_SENIVERSE_API_KEY                                  # 天气API密钥
'''

    def __new__(cls):
        # 单例模式的核心：确保只创建一次 ConfigManager 实例
        if cls._instance is None:
            # 如果实例不存在，则调用父类的 __new__ 方法创建一个新的实例
            cls._instance = super().__new__(cls)
        # 返回已有的或新创建的实例
        return cls._instance

    def __init__(self):
        # 防止重复初始化，检查是否已经初始化过
        if hasattr(self, "_initialized"):
            return
        # 标记为已初始化
        self._initialized = True
        # 初始化日志记录器，用于记录配置管理的操作
        logger.info("ConfigManager 正在初始化...")
        # device_activator 可能用于设备激活逻辑，暂时设为 None
        self.device_activator = None
        # 加载配置文件内容到 self.config 中
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        # 尝试加载配置文件，如果失败则返回默认配置
        try:
            # 检查配置文件是否存在
            if not self.CONFIG_FILE.exists():
                # 如果不存在，则创建 config 目录（如果目录已存在则不会报错）
                self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                # 创建默认配置文件，并写入 DEFAULT_CONFIG 的内容
                self.CONFIG_FILE.write_text(self.DEFAULT_CONFIG, encoding="utf-8")
                logger.info("未检测到配置文件，已创建默认配置")

            # 打开并读取配置文件内容
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                config_data = self.yaml.load(f)  # 使用 ruamel.yaml 加载 YAML 数据

            # 获取默认配置的字典表示形式
            default_dict = self.default_config_dict()
            # 合并默认配置和用户自定义配置，确保保留所有必要字段
            merged = self._merge_configs(default_dict, config_data)
            return merged

        except Exception as e:
            # 如果加载失败，记录错误并返回默认配置
            logger.error("加载配置失败: %s", e)
            return self.default_config_dict()

    @staticmethod
    def default_config_dict():
        # 创建一个新的 YAML 解析器实例，用于将 DEFAULT_CONFIG 字符串解析为字典对象
        yaml_loader = YAML()
        # 将默认配置字符串解析为 Python 字典并返回
        return yaml_loader.load(ConfigManager.DEFAULT_CONFIG)

    def save_config(self, config: dict) -> bool:
        # 尝试将传入的配置字典保存到配置文件中
        try:
            # 以写入模式打开配置文件
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                # 使用 ruamel.yaml 将配置字典转储为 YAML 格式并写入文件
                self.yaml.dump(config, f)
            # 如果保存成功，返回 True
            return True
        except Exception as e:
            # 如果保存过程中发生异常，记录错误日志并返回 False
            logger.error("保存配置失败: %s", e)
            return False

    @staticmethod
    def _merge_configs(default: dict, custom: dict) -> dict:
        # 复制默认配置，防止修改原始数据
        result = default.copy()
        # 遍历用户自定义配置中的所有键值对
        for key, value in custom.items():
            # 如果当前键存在于默认配置中且对应的值都是字典类型，则递归合并
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._merge_configs(result[key], value)
            else:
                # 否则直接用自定义配置覆盖默认值
                result[key] = value
        # 返回合并后的配置字典
        return result

    def get_config(self, path: str, default: Any = None) -> Any:
        """
        根据点分格式的路径从配置中获取值。

        :param path: 点分格式的键路径，例如 "WAKE_WORD_OPTIONS.USE_WAKE_WORD"
        :param default: 如果路径无效或键不存在，则返回此默认值
        :return: 获取到的配置值或默认值
        """
        try:
            # 从 self.config 开始逐级查找
            value = self.config
            for key in path.split('.'):
                value = value[key]  # 逐级进入字典
            return value
        except (KeyError, TypeError):
            # 如果路径不存在或者中间不是字典类型，则返回默认值
            return default

    def update_config(self, path: str, value: Any) -> bool:
        """
        根据点分格式的路径更新配置中的某个值，并保存回配置文件。

        :param path: 点分格式的键路径，例如 "WAKE_WORD_OPTIONS.USE_WAKE_WORD"
        :param value: 要设置的新值
        :return: 成功与否的布尔值
        """
        try:
            current = self.config
            *parts, last = path.split('.')  # 分割路径，除最后一项外均为中间部分

            # 遍历路径并确保每一层都是字典（如果不存在则创建）
            for part in parts:
                current = current.setdefault(part, {})

            # 设置最终的值
            current[last] = value

            # 保存整个更新后的配置回 YAML 文件
            return self.save_config(self.config)
        except Exception as e:
            logger.error("更新配置失败: %s", e)
            return False

    def reload_from_file(self):
        """
        从磁盘重新加载配置文件，使内存中的配置与文件保持同步。
        """
        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                self.config = self.yaml.load(f)  # 使用 ruamel.yaml 加载 YAML 数据
            logger.info("配置文件重新加载成功")
        except Exception as e:
            logger.error("配置文件重新加载失败: %s", e)

    @classmethod
    def get_instance(cls):
        """
        提供对 ConfigManager 单例实例的访问。使用线程锁确保在多线程环境下初始化是线程安全的。
        """
        with cls._lock:  # 使用类级别的锁保证线程安全
            if cls._instance is None:
                cls._instance = cls()  # 创建实例
            return cls._instance
