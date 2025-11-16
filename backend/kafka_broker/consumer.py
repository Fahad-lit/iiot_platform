"""
مستهلك Kafka لاستقبال البيانات
Kafka Consumer for Receiving Data
"""

from kafka import KafkaConsumer
import json
import logging
import os
from threading import Thread

logger = logging.getLogger(__name__)

class KafkaConsumerService:
    """خدمة مستهلك Kafka"""
    
    def __init__(self, topics: list = None):
        self.kafka_host = os.getenv("KAFKA_HOST", "localhost")
        self.kafka_port = os.getenv("KAFKA_PORT", "9092")
        self.topics = topics or ["measurements", "alerts", "commands"]
        self.consumer = None
        self.running = False
        self.connect()
    
    def connect(self):
        """الاتصال بـ Kafka"""
        try:
            self.consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=[f"{self.kafka_host}:{self.kafka_port}"],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id="iiot_consumer_group",
                auto_offset_reset='earliest',
                enable_auto_commit=True
            )
            logger.info(f"✅ تم الاتصال بـ Kafka Consumer على {self.kafka_host}:{self.kafka_port}")
            logger.info(f"✅ الاشتراك في المواضيع: {', '.join(self.topics)}")
        except Exception as e:
            logger.error(f"❌ خطأ في الاتصال بـ Kafka: {str(e)}")
            raise
    
    def start_consuming(self):
        """بدء استهلاك الرسائل"""
        self.running = True
        consumer_thread = Thread(target=self._consume_messages, daemon=True)
        consumer_thread.start()
        logger.info("✅ تم بدء استهلاك الرسائل من Kafka")
    
    def _consume_messages(self):
        """استهلاك الرسائل من Kafka"""
        try:
            for message in self.consumer:
                if not self.running:
                    break
                
                logger.info(f"📨 تم استقبال رسالة من الموضوع '{message.topic}':")
                logger.info(f"   البيانات: {message.value}")
                
                # معالجة الرسالة بناءً على نوع الموضوع
                self._process_message(message.topic, message.value)
        
        except Exception as e:
            logger.error(f"❌ خطأ في استهلاك الرسائل: {str(e)}")
    
    def _process_message(self, topic: str, message: dict):
        """معالجة الرسالة"""
        try:
            if topic == "measurements":
                logger.info(f"📊 معالجة قياس: {message}")
                # سيتم تطوير معالجة القياسات لاحقًا
            
            elif topic == "alerts":
                logger.info(f"⚠️ معالجة تنبيه: {message}")
                # سيتم تطوير معالجة التنبيهات لاحقًا
            
            elif topic == "commands":
                logger.info(f"🎮 معالجة أمر: {message}")
                # سيتم تطوير معالجة الأوامر لاحقًا
        
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الرسالة: {str(e)}")
    
    def stop_consuming(self):
        """إيقاف استهلاك الرسائل"""
        self.running = False
        logger.info("✅ تم إيقاف استهلاك الرسائل")
    
    def close(self):
        """إغلاق الاتصال"""
        self.stop_consuming()
        if self.consumer:
            self.consumer.close()
            logger.info("✅ تم إغلاق Kafka Consumer")
