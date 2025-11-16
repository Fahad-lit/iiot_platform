"""
منتج Kafka لإرسال البيانات
Kafka Producer for Sending Data
"""

from kafka import KafkaProducer
import json
import logging
import os

logger = logging.getLogger(__name__)

class KafkaProducerService:
    """خدمة منتج Kafka"""
    
    def __init__(self):
        self.kafka_host = os.getenv("KAFKA_HOST", "localhost")
        self.kafka_port = os.getenv("KAFKA_PORT", "9092")
        self.producer = None
        self.connect()
    
    def connect(self):
        """الاتصال بـ Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[f"{self.kafka_host}:{self.kafka_port}"],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3
            )
            logger.info(f"✅ تم الاتصال بـ Kafka Producer على {self.kafka_host}:{self.kafka_port}")
        except Exception as e:
            logger.error(f"❌ خطأ في الاتصال بـ Kafka: {str(e)}")
            raise
    
    def send_message(self, topic: str, message: dict):
        """إرسال رسالة إلى موضوع معين"""
        try:
            future = self.producer.send(topic, message)
            record_metadata = future.get(timeout=10)
            logger.info(f"✅ تم إرسال الرسالة إلى الموضوع '{topic}' على القسم {record_metadata.partition}")
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال الرسالة: {str(e)}")
            return False
    
    def send_batch_messages(self, topic: str, messages: list):
        """إرسال مجموعة من الرسائل"""
        try:
            for message in messages:
                self.producer.send(topic, message)
            self.producer.flush()
            logger.info(f"✅ تم إرسال {len(messages)} رسالة إلى الموضوع '{topic}'")
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال الرسائل: {str(e)}")
            return False
    
    def close(self):
        """إغلاق الاتصال"""
        if self.producer:
            self.producer.close()
            logger.info("✅ تم إغلاق Kafka Producer")
