# 单例模式mqtt客户端
import json
import queue
import threading
import uuid
import paho.mqtt.client as mqtt
from utils.config_manager import ConfigManager
from utils.logging_manager import get_logger

config = ConfigManager.get_instance()
logger = get_logger(__name__)


class MQTTClient:
    _instance_lock = threading.Lock()  # 线程锁，确保多线程下安全
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super(MQTTClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, target_ip=None, default_port=None, sub_topic=None, pub_topic=None, q_mqtt_data=None):
        """
        初始化只执行一次
        :param target_ip: MQTT服务器IP
        :param default_port: MQTT端口号
        :param sub_topic: 订阅主题
        :param pub_topic: 发布主题
        :param q_mqtt_data: 消息队列
        """
        if not hasattr(self, 'initialized'):
            self.target_ip = target_ip
            self.default_port = default_port
            self.sub_topic = sub_topic
            self.pub_topic = pub_topic
            self.q_mqtt_data = q_mqtt_data or queue.Queue()
            self.is_connected = False
            self.client = mqtt.Client(client_id=str(uuid.uuid4()))
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message

            try:
                self.client.connect(target_ip, default_port, 60)
                self.is_connected = True
                logger.info("MQTTClient 连接成功")
            except Exception as e:
                logger.error("MQTTClient 连接失败: %s" % e)

            self.client.subscribe(sub_topic, qos=0)
            self.client.loop_start()
            self.initialized = True  # 标记为已初始化

    @classmethod
    def get_instance(cls):
        """
        获取单例对象
        :return: 单例 MQTTClient 实例
        """
        if cls._instance is None:
            logger.error("MQTTClient 尚未初始化，请先调用构造函数创建实例。")
            return
        return cls._instance

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info('MQTT连接成功！！！')
            client.subscribe(self.sub_topic)
        else:
            logger.error("MQTT连接失败，错误码：%s" % rc)

    def on_message(self, client, userdata, msg):
        try:
            mqtt_data = json.loads(msg.payload.decode())
            self.q_mqtt_data.put(mqtt_data)
        except Exception as e:
            logger.error("MQTT消息处理失败: %s" % e)

    def send_mqtt(self, data):
        """
        发送MQTT消息
        :param pub_topic: 主题
        :param data: 数据（建议传入字典并自动转为JSON）
        """
        if self.is_connected:
            self.client.publish(self.pub_topic, payload=json.dumps(data), qos=0)
            return '发送成功'
        else:
            logger.error("MQTT未连接，请检查网络或重新初始化MQTTClient。")
            return '发送失败'

    def reconnect(self, new_broker, new_port, new_sub_topic=None, new_pub_topic=None):
        """
        更换MQTT服务器并重新连接
        :param new_broker: 新服务器地址
        :param new_port: 新端口号
        :param new_sub_topic: 新订阅主题（可选）
        :param new_pub_topic: 新发布主题（可选）
        """
        self.disconnect()
        self.is_connected = False

        self.target_ip = new_broker
        self.default_port = new_port
        self.sub_topic = new_sub_topic if new_sub_topic else self.sub_topic
        self.pub_topic = new_pub_topic if new_pub_topic else self.pub_topic
        try:
            self.client = mqtt.Client(client_id=str(uuid.uuid4()))
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.connect(new_broker, new_port, 60)
            self.client.loop_start()  # ✅ 必须启动 loop 才能收消息
            self.is_connected = True
            logger.info("MQTT重新连接成功")
        except Exception as e:
            logger.error("MQTT连接失败: %s" % e)

    def disconnect(self):
        """断开当前连接"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
            logger.info("已断开MQTT连接")


broker = config.get_config("MQTT_SERVICE.BROKER")
port = config.get_config("MQTT_SERVICE.PORT")
sub_topic = config.get_config("MQTT_SERVICE.SUB_TOPIC")
pub_topic = config.get_config("MQTT_SERVICE.PUB_TOPIC")
mqtt_client = MQTTClient(broker, port, sub_topic, pub_topic)
