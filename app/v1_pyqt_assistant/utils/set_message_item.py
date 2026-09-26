from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt


class SetMessageItem(QWidget):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)

        # 创建水平布局并设置边距和对齐方式
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setAlignment(Qt.AlignRight if is_user else Qt.AlignLeft)

        self.message_label = QLabel(text)
        self.message_label.setWordWrap(True)  # 启用自动换行

        # 设置样式表
        self.message_label.setStyleSheet(f"""
            background-color: {'#89d961' if is_user else '#f5f5f5'};
            padding: 8px 12px;
            border-radius: 3px;
            outline: none;
            border: none;
            font: 30px "HarmonyOS Sans SC";
        """)

        # 根据是否是用户消息，设置不同的尺寸策略
        if is_user:
            # 用户消息：宽度优先扩展，高度根据内容自适应
            self.message_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        else:
            # 系统消息：固定宽度，高度根据内容自适应
            fixed_width = 500
            self.message_label.setFixedWidth(fixed_width)
            self.message_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # 将消息标签添加到布局中
        layout.addWidget(self.message_label)

        # 调整气泡宽度以包裹内容
        self.adjust_message_width()

    def adjust_message_width(self):
        """
        动态调整 QLabel 的宽度，使其仅包裹内容。
        """
        # 获取 QLabel 的最佳宽度（考虑字体、内边距等）
        best_width = self.message_label.sizeHint().width()

        # 如果是用户消息，设置宽度为最佳宽度，但不超过最大宽度
        if hasattr(self, 'is_user') and self.is_user:
            max_width = 500  # 用户消息的最大宽度限制
            self.message_label.setFixedWidth(min(best_width, max_width))

        # 强制重新布局
        self.layout().invalidate()
        self.updateGeometry()