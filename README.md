# 小布 · 多模态智能语音助手

基于大模型的桌面端多模态语音助手，打通「**语音唤醒 → 语音识别(ASR) → 大模型对话(LLM) → 语音合成(TTS) → 语音播报**」完整语音交互闭环，并扩展了摄像头视觉问答与 Agent 工具调用能力，基于 PyQt5 提供桌面图形界面。

## 功能特性

- **离线语音唤醒**：基于 Vosk 中文小模型常驻监听"小布小布"唤醒词，pypinyin 无声调拼音匹配，容忍同音字，低功耗、零流量
- **VAD 语音活动检测**：webrtcvad + 能量阈值双重判定，自动识别说话起止，配合前后缓冲帧与超时保护
- **高精度语音识别**：集成本地 SenseVoiceSmall 模型 / 在线 ASR 接口双通道
- **流式对话与播报**：大模型 token 流式输出，正则分句 + 句子/音频双队列流水线，边生成边合成边播报，显著降低首句等待延迟
- **视觉多模态问答**：调用 Qwen2.5-VL，基于摄像头画面回答"这是什么"等视觉问题
- **Agent 工具调用**：基于 Function Calling 注册天气查询、视觉问答工具，四态状态机协调资源调度

## 技术栈

| 模块 | 技术选型 |
|---|---|
| 桌面 GUI | PyQt5、qasync（Qt 事件循环与 asyncio 融合） |
| 并发模型 | QThread 多 Worker + pyqtSignal 信号槽、queue 线程安全队列 |
| 离线唤醒 | Vosk（vosk-model-small-cn-0.22）、pypinyin |
| 语音活动检测 | webrtcvad |
| 语音识别 ASR | FunASR + SenseVoiceSmall（本地）/ SiliconFlow 接口 |
| 大模型 | Qwen3-8B（对话）、Qwen2.5-VL-7B（视觉） |
| 语音合成 TTS | edge-tts（本地免费）/ CosyVoice2 |
| Agent | OpenAI Function Calling、心知天气 API |
| 其他 | OpenCV（摄像头）、pyaudio/pydub/pygame（音频）、paho-mqtt |

## 系统架构

```
用户说"小布小布"
      │
      ▼
[唤醒线程] Vosk 拼音匹配 ──► 状态: IDLE → LISTENING
      │
      ▼
[录音线程] VAD 自动断句（起始帧/结束帧/超时保护）
      │  完整语音
      ▼
[识别线程] SenseVoiceSmall ASR ──► 文本
      │
      ▼
[对话线程] Qwen3-8B 流式生成 ──► 正则分句 ──► 句子队列(maxsize=20)
      │                                         │
      │                              Function Calling?
      │                              ├─ 是: 调用天气/视觉工具，结果回灌 LLM
      │                              └─ 否: 直接成句
      ▼                                         ▼
[合成线程] edge-tts 按句合成音频 ──► 音频队列(maxsize=20)
      │
      ▼
[播放线程] 逐句播报 ──► 状态: SPEAKING → IDLE
```

- **状态机**：`IDLE → LISTENING → THINKING → SPEAKING`，唤醒时自动取消在途任务
- **流水线**：生成 / 合成 / 播放三环节时间重叠，首句延迟较同步串行模式降低约 50%

## 目录结构

```
多模态智能语音助手/
├── README.md
├── requirements.txt
├── .gitignore
│
├── examples/                     # 分模块教学示例（可独立运行）
│   ├── 01_vision_multimodal/     # 第1章 视觉多模态大模型调用
│   ├── 02_speech_recognition/    # 第2章 录音与语音识别 ASR
│   ├── 03_text_to_speech/        # 第3章 语音合成 TTS
│   ├── 04_asr_llm_tts/           # 第4章 ASR+LLM+TTS 命令行对话
│   ├── 06_offline_wakeup/        # 第6章 Vosk 离线唤醒词检测
│   └── 07_vad_detection/         # 第7章 VAD 音频输入检测
│
└── app/                          # 完整桌面应用（递进的三个版本）
    ├── v1_pyqt_assistant/        # 第5章 PyQt5 UI 版对话助手
    ├── v2_wakeup_assistant/      # 第8章 接入离线唤醒 + VAD
    └── v3_multimodal_agent/      # 第9章 最终版：视觉多模态 + Agent 工具
        ├── main.py               # 程序入口
        ├── config/config.yaml    # 模型 / 服务 / 密钥配置
        ├── UI/                   # PyQt5 界面
        ├── utils/                # 录音、识别、对话、合成、唤醒、摄像头等 Worker
        ├── tools/                # Function Calling 工具（天气、视觉问答）
        └── resources/            # 字体、图标、唤醒应答音
```

## 快速开始

### 1. 环境要求

- Python 3.10 ~ 3.11（推荐 3.11）
- Windows 10/11（含麦克风、摄像头）
- ffmpeg（pydub 音频格式转换依赖，安装后加入系统 PATH）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

> Windows 下若 `webrtcvad` 安装失败（缺 C++ 编译环境），改装预编译版本：
> ```bash
> pip install webrtcvad-wheels
> ```

### 3. 编译 Qt 资源文件

`static_rc.py` 是 Qt 资源编译产物（未纳入 Git），首次运行前需在**每个 app 版本目录**下生成一次：

```bash
cd app/v3_multimodal_agent
pyrcc5 resources/static.qrc -o resources/static_rc.py
```

### 4. 下载模型（约 1GB，未纳入 Git）

模型文件体积过大，已在 `.gitignore` 中排除，请按下表自行下载并放置：

| 模型 | 下载地址 | 放置位置（相对 app 各版本目录） |
|---|---|---|
| vosk-model-small-cn-0.22（约 42MB） | https://alphacephei.com/vosk/models | `models/vosk-model-small-cn-0.22/` |
| SenseVoiceSmall（约 900MB） | ModelScope 搜索 `iic/SenseVoiceSmall` | `models/iic/SenseVoiceSmall/` |

以最终版为例，目录应为：

```
app/v3_multimodal_agent/models/
├── vosk-model-small-cn-0.22/
└── iic/SenseVoiceSmall/
```

### 5. 配置 API 密钥

仓库中所有密钥均已替换为占位符，使用前需自行申请并填入：

1. **硅基流动 SiliconFlow**（大模型对话 / ASR / TTS / 视觉）：https://cloud.siliconflow.cn 注册获取 API Key
   - 填入各版本的 `config/config.yaml`，将 `YOUR_SILICONFLOW_API_KEY` 替换为你的密钥
   - 教学示例脚本（examples 01~04）中同样替换 `YOUR_SILICONFLOW_API_KEY`
2. **心知天气**（天气工具，可选）：https://www.seniverse.com 申请密钥后设置环境变量
   ```powershell
   # Windows PowerShell（临时生效）
   $env:WEATHER_API_KEY="你的心知天气密钥"
   ```

### 6. 运行

```bash
cd app/v3_multimodal_agent
python main.py
```

启动后点击"开始对话"，说"**小布小布**"，听到"我在呢"应答后即可语音提问，例如：

- "今天北京天气怎么样？"（触发天气工具）
- 拿起一个物品问摄像头："帮我看看这是什么？"（触发视觉问答工具）

## 版本演进

| 版本 | 新增能力 |
|---|---|
| examples 01~04 | 分别打通视觉、ASR、TTS 单模块及命令行对话闭环 |
| examples 06~07 | 离线唤醒词检测、VAD 端点检测 |
| app/v1（第5章） | PyQt5 图形界面 + 多线程异步架构 + 摄像头 |
| app/v2（第8章） | Vosk 离线唤醒 + webrtcvad 自动断句 |
| app/v3（第9章） | Qwen2.5-VL 视觉多模态 + Function Calling Agent 工具链 |

## 说明

- 本项目为学习实践项目，模型版权归原作者所有，请遵循对应模型许可协议使用
- 请勿将真实 API Key 硬编码后提交到公开仓库
