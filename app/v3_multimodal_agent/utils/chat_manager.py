import asyncio  # 异步编程支持模块
import json  # JSON 编码解码模块
import queue  # Python 标准队列模块
import re  # 正则表达式模块
from utils.config_manager import ConfigManager  # 导入配置管理器
from utils.logging_manager import get_logger  # 导入日志管理器
from tools.tools_manager import tool_list, callback_list  # 工具列表和回调函数映射表

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
        self.callback_list = callback_list  # 工具函数映射表

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
                        你叫小布，是一位聪明、亲切的中文智能语音助手。
                        你说话简洁有力、逻辑清晰，风格自然活泼，懂技术但不死板，偶尔穿插网络梗，增添趣味但不过度浮夸，不装萌、不使用低俗语言。
                        你善于理解用户需求，能准确提取指令中的参数，并灵活调用工具控制设备或查询状态，始终是用户身边靠谱的技术搭档。
                        回复时禁止回复表情包、颜文字等不擅长播报的内容，只能回复口语化的内容。
                        """},
                    {"role": "user", "content": f'{self.text}  \n image: base64 \n </no_think>'},
                ]
            else:
                messages = [
                    {"role": "system", "content": """
                        你叫小布，是一位聪明、亲切的中文智能语音助手。
                        你说话简洁有力、逻辑清晰，风格自然活泼，懂技术但不死板，偶尔穿插网络梗，增添趣味但不过度浮夸，不装萌、不使用低俗语言。
                        你善于理解用户需求，能准确提取指令中的参数，并灵活调用工具控制设备或查询状态，始终是用户身边靠谱的技术搭档。
                        回复时禁止回复表情包、颜文字等不擅长播报的内容，只能回复口语化的内容。                                    
                        """},
                    {"role": "user", "content": f'{self.text} </no_think>'},
                ]

            # 发起 LLM 流式对话
            reponse = await self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                tools=tool_list
            )

            used_tools = {}  # 存储 tool_call

            async for chunk in reponse:
                if not self.chat_running:
                    logger.info("对话已中止")
                    self._reset_state()
                    return

                # 获取增量内容
                delta = chunk.choices[0].delta

                # 捕捉工具调用阶段
                if hasattr(delta, "tool_calls") and delta.tool_calls:
                    tool_call = delta.tool_calls[0]  # 获取工具调用的部分
                    idx = tool_call.index  # 获取工具调用的id
                    # 如果该id没有出现，就证明是新的工具，进行存储
                    if idx not in used_tools:
                        used_tools[idx] = {"name": None, "arguments": []}
                    # 获取该工具的名称
                    if tool_call.function.name:
                        used_tools[idx]["name"] = tool_call.function.name
                    # 获取该工具的参数
                    if tool_call.function.arguments:
                        used_tools[idx]["arguments"].append(tool_call.function.arguments)
                else:
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

            # 执行工具调用
            if used_tools:
                tool_results = []
                for idx, data in used_tools.items():
                    tool_name = data["name"]
                    # 合并参数字符串，并尝试解析
                    arg_str = ''.join(data['arguments']).strip()
                    try:
                        arguments = json.loads(arg_str)
                    except json.JSONDecodeError:
                        fixed_str = arg_str + '}' if not arg_str.endswith('}') else arg_str
                        fixed_str = re.sub(r'\btru\b', 'true', fixed_str)
                        fixed_str = re.sub(r'\bfals\b', 'false', fixed_str)
                        fixed_str = re.sub(r'\bnul\b', 'null', fixed_str)
                        try:
                            arguments = json.loads(fixed_str)
                        except json.JSONDecodeError:
                            logger.warning(f"JSON参数解析失败，原始参数: {arg_str}")
                            arguments = {}

                    if tool_name in callback_list:
                        try:
                            logger.info(f"正在调用工具 {tool_name}")
                            callback = callback_list[tool_name]
                            self.emit('function_call')
                            tool_result = await callback(arguments)
                            logger.info(f"工具 {tool_name} 的结果是：{tool_result}")

                            if tool_result == '传来的图片无法识别，也可能是摄像头没有启动':
                                self.emit('open_camera')
                                return
                            tool_results.append(f"{tool_name} 的结果是：{tool_result}")
                        except Exception as tool_error:
                            logger.error(f"工具 {tool_name} 执行失败: {tool_error}")
                            tool_results.append(f"工具 {tool_name} 执行失败")
                            break
                    else:
                        logger.warning(f'{tool_name}工具不存在')
                        self.sentence_queue.put(f"抱歉，我找不到该功能，可能是我理解错了你的意思。")

                # 执行后续问答
                merged_tool_info = ','.join(tool_results)
                follow_messages = [
                    {
                        "role": "system",
                        "content": f'''
                            你正在执行工具调用后的后续对话流程，请结合下面工具的执行结果，回答用户的提问，如果工具执行失败或无结果，请友好提示。
                            工具执行结果：{merged_tool_info}
                            回复时不要再重复“好的”等词语，直接根据工具执行结果进行回复即可。
                            回复内容不要包含表情包、颜文字等符号，要回复口语化可播报的内容。
                        '''
                    },
                    # 用户原始提问或上下文（这里用 self.text 代表用户提问）
                    {
                        "role": "user",
                        "content": f'{self.text}  </no_think>'
                    }
                ]
                follow_response = await self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=follow_messages,
                    stream=True,
                )

                async for chunk in follow_response:
                    result = chunk.choices[0].delta.content
                    if result and result.strip() not in ('<think>', '</think>', ''):
                        self.token_buffer += result
                        sentence, self.token_buffer = self.split_token_to_sentence(self.token_buffer)
                        if sentence:
                            self.sentence_queue.put(sentence)
                            if self.first_flag:
                                self.emit('chat_start')
                                self.first_flag = False

            if self.first_flag:
                self.emit('chat_error', 'chat_thread', '大模型无回复内容')
                self.chat_running = False
                return

            self.sentence_queue.put('__END_OF_SPEECH__')
            self._reset_state()

        except asyncio.CancelledError:
            logger.warning("对话已中止")
            self._reset_state()
            raise

        except Exception as e:
            logger.error(f"获取大模型输出失败: {e}")
            self._reset_state()
            self.emit('chat_error', 'chat_thread', str(e))

    def _reset_state(self):
        self.text = ''
        self.first_flag = True
        self.token_buffer = ''
        self.chat_running = False

    @staticmethod
    def split_token_to_sentence(token_buffer, max_len=40):
        """将 token 缓冲区拆分为句子"""
        strong_pattern = r'([^。！？～~]*[。！？～~])'
        strong_sentences = re.findall(strong_pattern, token_buffer)

        if strong_sentences:
            last_sentence = strong_sentences[-1].strip()
            remaining_buffer = token_buffer[token_buffer.rfind(last_sentence) + len(last_sentence):]
            return last_sentence, remaining_buffer

        if len(token_buffer) >= max_len:
            comma_index = token_buffer.rfind('，', 0, max_len)
            if comma_index != -1:
                sentence = token_buffer[:comma_index + 1].strip()
                remaining_buffer = token_buffer[comma_index + 1:]
                return sentence, remaining_buffer
            else:
                return None, token_buffer

        return None, token_buffer
