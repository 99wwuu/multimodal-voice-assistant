import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from utils.logging_manager import get_logger
from utils.config_manager import ConfigManager


config = ConfigManager.get_instance()
logger = get_logger(__name__)


class CameraProcessor(QThread):

    # 自定义信号，用于发送帧数据
    camera_frame = pyqtSignal(QPixmap)

    # 自定义信号，用于发送错误信息
    camera_error = pyqtSignal(str, str)

    # 初始化
    def __init__(self):
        # 调用父类的初始化方法
        super().__init__()
        # 获取摄像头编号
        self.camera_index = config.get_config('CAMERA.camera_index')
        # 初始化视频捕获对象（后续会使用OpenCV的videoCapture对象来替代）
        self.cap = None
        # 控制线程运行状态的标志，初始化为False，表示为不运行
        self.camera_running = False
        # 设置线程名称
        self.setObjectName('camera_thread')

    # run 方法是 QThread 的核心方法，线程从这里开始执行
    def run(self):
        try:
            # 打开摄像头设备
            self.cap = cv2.VideoCapture(self.camera_index)
            # 将摄像头的打开状态设置为线程的运行状态
            self.camera_running = self.cap.isOpened()
            # 如果摄像头未成功打开，发送错误信号并提示无法打开摄像头
            if not self.camera_running:
                msg = f'无法打开编号为{self.camera_index}的摄像头，请重新检查摄像头设备'
                logger.error(msg)
                self.camera_error.emit(self.objectName(), msg)   # type: ignore
                return  # 避免继续进入 while 循环

            # 如果摄像头成功打开，那么就循环读取摄像头的帧数据
            while self.camera_running:
                # 读取一帧图像，返回两个值，第一个是布尔值，表示是否成功读取帧数据，第二个是帧数据
                ret, frame = self.cap.read()
                # 如果读取失败，发送错误信号并退出循环
                if not ret:
                    self.camera_error.emit(self.objectName(), '无法读取摄像头数据，请检查摄像头设备是否正常')   # type: ignore
                    self.camera_running = False
                    logger.error('无法读取摄像头数据，请检查摄像头设备是否正常')
                    return
                # frame = cv2.flip(frame, 1)
                # 根据需要修改图片的大小
                rgb_frame = cv2.resize(frame, (800, 600))
                # 发送RGB格式数据，方便后续大模型调用工具使用
                rgb_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2RGB)

                # 如果读取正常，将帧数据转换为QImage对象，并转换为QPixmap对象
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w  # 手动计算步长
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                # 将 QImage 转换为 QPixmap
                pixmap = QPixmap.fromImage(qt_image)
                # 如果线程仍在运行，就通过信号将帧数据发送出去，这里判断是因为后续关闭时会直接修改camera_running，所以需要在判断一次
                if self.camera_running:
                    self.camera_frame.emit(pixmap)   # type: ignore
                # 休眠，控制帧率
                # time.sleep(0.1)
            # 如果循环结束，就释放摄像头资源
            self.cap.release()
        except Exception as e:
            # 如果捕获到异常，通过信号将异常传递出去
            self.camera_error.emit(self.objectName(), f'摄像头数据处理子线程出现问题: {e}')   # type: ignore
            raise e

    # 中止子线程的运行
    def stop(self):
        # 将camera_running改为False，停止摄像头处理子线程
        self.camera_running = False
