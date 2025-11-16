"""
خدمة جمع البيانات (Data Ingestion Service)
Handles data collection, validation, and routing
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
from kafka_broker.producer import KafkaProducerService
from database.influxdb_db import write_measurement
from database.mongodb_db import get_mongodb_connection

logger = logging.getLogger(__name__)

class DataIngestionService:
    """خدمة جمع ومعالجة البيانات"""
    
    def __init__(self):
        self.kafka_producer = KafkaProducerService()
        self.validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """تحميل قواعد التحقق من صحة البيانات"""
        return {
            "temperature": {
                "min": -50,
                "max": 150,
                "unit": "°C"
            },
            "pressure": {
                "min": 0,
                "max": 10000,
                "unit": "Pa"
            },
            "humidity": {
                "min": 0,
                "max": 100,
                "unit": "%"
            },
            "voltage": {
                "min": 0,
                "max": 500,
                "unit": "V"
            },
            "current": {
                "min": 0,
                "max": 1000,
                "unit": "A"
            }
        }
    
    async def ingest_measurement(self, measurement_data: Dict[str, Any]) -> Dict[str, Any]:
        """استقبال ومعالجة قياس واحد"""
        try:
            logger.info(f"📥 استقبال قياس جديد من الجهاز: {measurement_data.get('device_id')}")
            
            # 1. التحقق من صحة البيانات
            validation_result = self._validate_measurement(measurement_data)
            if not validation_result['valid']:
                logger.warning(f"⚠️ فشل التحقق من البيانات: {validation_result['errors']}")
                return {
                    "success": False,
                    "errors": validation_result['errors'],
                    "timestamp": datetime.now().isoformat()
                }
            
            # 2. إضافة الطابع الزمني إذا لم يكن موجودًا
            if 'timestamp' not in measurement_data or not measurement_data['timestamp']:
                measurement_data['timestamp'] = datetime.now()
            
            # 3. إرسال البيانات إلى Kafka
            await self._send_to_kafka(measurement_data)
            
            # 4. كتابة البيانات إلى InfluxDB
            await self._write_to_influxdb(measurement_data)
            
            # 5. تسجيل البيانات في MongoDB
            await self._log_to_mongodb(measurement_data)
            
            logger.info(f"✅ تم معالجة القياس بنجاح: {measurement_data['device_id']}")
            
            return {
                "success": True,
                "message": "تم استقبال القياس بنجاح",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة القياس: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def ingest_batch(self, measurements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """استقبال ومعالجة مجموعة من القياسات"""
        try:
            logger.info(f"📥 استقبال مجموعة من {len(measurements)} قياس")
            
            successful = 0
            failed = 0
            errors = []
            
            for measurement in measurements:
                result = await self.ingest_measurement(measurement)
                if result['success']:
                    successful += 1
                else:
                    failed += 1
                    errors.append(result)
            
            logger.info(f"✅ تمت معالجة المجموعة: {successful} نجح، {failed} فشل")
            
            return {
                "success": True,
                "total": len(measurements),
                "successful": successful,
                "failed": failed,
                "errors": errors if errors else None,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة المجموعة: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _validate_measurement(self, measurement: Dict[str, Any]) -> Dict[str, Any]:
        """التحقق من صحة القياس"""
        errors = []
        
        # التحقق من الحقول المطلوبة
        required_fields = ['device_id', 'measurement_type', 'value', 'unit']
        for field in required_fields:
            if field not in measurement or measurement[field] is None:
                errors.append(f"الحقل '{field}' مطلوب")
        
        if errors:
            return {"valid": False, "errors": errors}
        
        # التحقق من نوع القياس
        measurement_type = measurement.get('measurement_type', '').lower()
        if measurement_type in self.validation_rules:
            rule = self.validation_rules[measurement_type]
            value = measurement.get('value')
            
            if value < rule['min'] or value > rule['max']:
                errors.append(
                    f"القيمة {value} خارج النطاق المسموح به "
                    f"({rule['min']} - {rule['max']}) {rule['unit']}"
                )
        
        # التحقق من أن device_id غير فارغ
        if not measurement.get('device_id', '').strip():
            errors.append("معرف الجهاز لا يمكن أن يكون فارغًا")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _send_to_kafka(self, measurement: Dict[str, Any]) -> bool:
        """إرسال البيانات إلى Kafka"""
        try:
            message = {
                "device_id": measurement.get('device_id'),
                "measurement_type": measurement.get('measurement_type'),
                "value": measurement.get('value'),
                "unit": measurement.get('unit'),
                "timestamp": measurement.get('timestamp').isoformat() if isinstance(measurement.get('timestamp'), datetime) else measurement.get('timestamp'),
                "metadata": measurement.get('metadata', {})
            }
            
            self.kafka_producer.send_message("measurements", message)
            logger.debug(f"📤 تم إرسال البيانات إلى Kafka: {measurement['device_id']}")
            return True
        
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال البيانات إلى Kafka: {str(e)}")
            return False
    
    async def _write_to_influxdb(self, measurement: Dict[str, Any]) -> bool:
        """كتابة البيانات إلى InfluxDB"""
        try:
            tags = {
                "device_id": measurement.get('device_id'),
                "measurement_type": measurement.get('measurement_type'),
                "unit": measurement.get('unit')
            }
            
            fields = {
                "value": float(measurement.get('value'))
            }
            
            # إضافة البيانات الإضافية إلى الحقول
            if measurement.get('metadata'):
                for key, val in measurement['metadata'].items():
                    if isinstance(val, (int, float)):
                        fields[f"meta_{key}"] = val
            
            timestamp = measurement.get('timestamp')
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            
            await write_measurement(
                measurement_name=measurement.get('measurement_type', 'sensor_data'),
                tags=tags,
                fields=fields,
                timestamp=timestamp
            )
            
            logger.debug(f"💾 تم حفظ البيانات في InfluxDB: {measurement['device_id']}")
            return True
        
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ البيانات في InfluxDB: {str(e)}")
            return False
    
    async def _log_to_mongodb(self, measurement: Dict[str, Any]) -> bool:
        """تسجيل البيانات في MongoDB"""
        try:
            db = await get_mongodb_connection()
            
            log_entry = {
                "device_id": measurement.get('device_id'),
                "measurement_type": measurement.get('measurement_type'),
                "value": measurement.get('value'),
                "unit": measurement.get('unit'),
                "timestamp": measurement.get('timestamp'),
                "metadata": measurement.get('metadata', {}),
                "created_at": datetime.now()
            }
            
            result = db.measurement_logs.insert_one(log_entry)
            logger.debug(f"📝 تم تسجيل البيانات في MongoDB: {result.inserted_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ خطأ في تسجيل البيانات في MongoDB: {str(e)}")
            return False

# إنشاء نسخة واحدة من الخدمة
ingestion_service = DataIngestionService()
