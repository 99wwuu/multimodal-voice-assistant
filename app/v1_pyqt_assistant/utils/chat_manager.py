import asyncio  # 异步编程支持模块
import queue  # Python 标准队列模块
import re  # 正则表达式模块
from utils.config_manager import ConfigManager  # 导入配置管理器
from utils.logging_manager import get_logger  # 导入日志管理器

logger = get_logger(__name__)  # 获取当前模块的日志记录器


class ChatWithLLM:
    def __init__(self, client, sentence_queue):
        self.llm_client = client  # LLM 客户端实例，如 OpenAI 或其他服务
        self.sentence_queue = sentence_queue  # 用于传递生成的句子
        self.config = ConfigManager.get_instance()  # 配置管理器

        # 对话状态管理
        self.text = ''  # 当前输入文本
        self.token_buffer = ''  # 累积的 token 缓冲区
        self.model = None  # 当前使用的大模型名称
        self.service = None  # 当前服务类型（如 LOCAL_SERVICE 或 SILICONFLOW）
        self.chat_running = False  # 是否正在进行对话
        self.first_flag = True  # 是否是第一句话，用于触发开始回调
        self.camera_open = False  # 摄像头是否开启

        # 回调注册表
        self.handlers = {
            'chat_start': [],     # 对话开始回调
            'chat_error': [],     # 对话错误回调
            'open_camera': [],    # 打开摄像头回调
            'function_call': []   # 工具调用回调
        }

    # 绑定摄像头打开事件的回调函数
    def on_open_camera(self, handler):
        self.handlers['open_camera'].append(handler)

    # 绑定函数调用事件的回调函数
    def on_function_call(self, handler):
        self.handlers['function_call'].append(handler)

    # 绑定对话开始事件的回调函数
    def on_chat_start(self, handler):
        self.handlers['chat_start'].append(handler)

    # 绑定对话错误事件的回调函数
    def on_chat_error(self, handler):
        self.handlers['chat_error'].append(handler)

    def emit(self, signal_name, *args):
        """触发对应的回调事件"""
        for handler in self.handlers.get(signal_name, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(*args))
                else:
                    handler(*args)
            except Exception as e:
                logger.error(f"执行 {signal_name} 回调失败: {e}")

    def get_text(self, text):
        self.text = text  # 设置输入文本

    def stop(self):
        self.chat_running = False  # 停止对话运行状态

    async def run(self):
        """
        主执行逻辑：
        - 处理用户输入
        - 调用 LLM 获取响应（流式）
        - 提取 tool call 并调用工具
        - 执行后续问答
        """
        if self.chat_running:
            logger.warning("对话正在进行，请勿重复启动！！！")
            self.emit('chat_error', 'chat_thread', "对话正在进行，请勿重复启动！！！")
            return

        try:
            # 清空之前残留的句子队列
            while not self.sentence_queue.empty():
                try:
                    self.sentence_queue.get_nowait()
                except queue.Empty:
                    break

            # 标记为正在对话
            self.chat_running = True
            # 获取当前服务类型
            self.service = self.config.get_config('CHOICE.SERVICE')
            # 获取对应服务的大模型名称
            self.model = self.config.get_config(f'{self.service}.LLM')

            # 构造 LLM 对话上下文
            if self.camera_open:
                messages = [
                    {"role": "system", "content": """
                        你叫小布，是一位聪明、亲切的智能语音助手。
                        你说话简洁有力、逻辑清晰，风格自然活泼，懂技术但不死板，会穿插网络梗，但不使用低俗语言。
                        回复时禁止回复表情包、颜文字等不擅长播报的内容，只能回复口语化的内容。    
                        """},
                    {"role": "user", "content": f'{self.text}  </no_think>'},
                ]
            else:
                messages = [
                    {"role": "system", "content": """
                        你叫小布，是一位聪明、亲切的智能语音助手。
                        你说话简洁有力、逻辑清晰，风格自然活泼，懂技术但不死板，会穿插网络梗，但不使用低俗语言。
                        回复时禁止回复表情包、颜文字等不擅长播报的内容，只能回复口语化的内容。                               
                        """},
                    {"role": "user", "content": f'{self.text} </no_think>'},
                ]

            # 发起 LLM 流式对话
            reponse = await self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )

            async for chunk in reponse:
                if not self.chat_running:
                    logger.info("对话已中止")
                    self._reset_state()
                    return

                # 普通文本内容
                result = chunk.choices[0].delta.content
                # 过滤思考字段或空内容
                if result and result.strip() not in ('<think>', '</think>', ''):
                    # 添加到缓冲区，方便后续切割
                    self.token_buffer += result
                    # 当缓冲区大于10个时，再切割，否则短句子合成会导致时间变长
                    if len(self.token_buffer) > 10:
                        # 切割句子
                        sentence, self.token_buffer = self.split_token_to_sentence(self.token_buffer)
                        if sentence:
                            # 将句子放到队列中
                            self.sentence_queue.put(sentence)
                            if self.first_flag:
                                self.emit('chat_start')
                                self.first_flag = False

            # 如果 first_flag 仍为 True，说明模型没有返回任何内容
            if self.first_flag:
                self.emit('chat_error', 'chat_thread', '大模型无回复内容')
                self.chat_running = False
                return
            # 正常结束时推入对话结束标志，供播放或UI判断
            self.sentence_queue.put('__END_OF_SPEECH__')
            self._reset_state()  # 清空内部状态，准备下轮对话

        except asyncio.CancelledError:
            logger.warning("对话已中止")
            self._reset_state()
            raise  # 主动抛出取消异常，以允许外层逻辑感知取消

        except Exception as e:
            logger.error(f"获取大模型输出失败: {e}")
            self._reset_state()
            self.emit('chat_error', 'chat_thread', str(e))  # 发出错误信号，供 UI/语音提示

    def _reset_state(self):
        """
        重置对话状态：
        - 清空历史输入
        - 重置首次标志位
        - 清空 token 缓冲区
        - 标记对话未运行
        """
        self.text = ''  # 清空用户输入文本
        self.first_flag = True  # 标记为首次响应
        self.token_buffer = ''  # 清空语言模型输出缓冲
        self.chat_running = False  # 标记当前对话未处于活跃状态

    @staticmethod
    def split_token_to_sentence(token_buffer, max_len=40):
        """
        将 token 缓冲区拆分为句子。
        优先按强标点（句号、感叹号、问号等）切分，否则按中文逗号在 max_len 范围内拆分。

        :param token_buffer: 当前累积的文本片段
        :param max_len: 若无完整句号结尾，允许的最大字符数，用于回退切分
        :return: (句子, 剩余缓冲区)，如果未找到完整句子则返回 (None, 原始缓冲区)
        """
        # 正则提取所有以强标点结尾的子句
        strong_pattern = r'([^。！？～~]*[。！？～~])'  # 捕获句子末尾为强标点符号的文本
        strong_sentences = re.findall(strong_pattern, token_buffer)

        if strong_sentences:
            # 取最后一条完整子句作为一句话
            last_sentence = strong_sentences[-1].strip()
            # 从缓冲区中扣除该句，留下剩余部分
            remaining_buffer = token_buffer[
                               token_buffer.rfind(last_sentence) + len(
                                   last_sentence):]
            return last_sentence, remaining_buffer

        # 如果未出现句号，但长度已达到 max_len，尝试按中文逗号切分
        if len(token_buffer) >= max_len:
            comma_index = token_buffer.rfind('，', 0, max_len)
            if comma_index != -1:
                sentence = token_buffer[:comma_index + 1].strip()
                remaining_buffer = token_buffer[comma_index + 1:]
                return sentence, remaining_buffer
            else:
                # 找不到逗号，无法切分，返回None
                return None, token_buffer

        # 缓冲区不满足切句条件，返回None
        return None, token_buffer
