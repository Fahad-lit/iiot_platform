"""
خدمة التحليلات الأساسية (Analytics Service)
Provides data analysis and statistics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics
from database.influxdb_db import query_measurements
from database.mongodb_db import get_mongodb_connection
from database.postgres_db import get_db_connection

logger = logging.getLogger(__name__)

class AnalyticsService:
    """خدمة التحليلات والإحصائيات"""
    
    async def get_device_statistics(
        self,
        device_id: str,
        measurement_type: str,
        time_range: str = "-24h"
    ) -> Dict[str, Any]:
        """الحصول على إحصائيات الجهاز"""
        try:
            logger.info(f"📊 حساب إحصائيات الجهاز: {device_id}")
            
            # جلب البيانات من InfluxDB
            measurements = await query_measurements(measurement_type, device_id, time_range)
            
            if not measurements:
                return {
                    "device_id": device_id,
                    "measurement_type": measurement_type,
                    "time_range": time_range,
                    "count": 0,
                    "message": "لا توجد بيانات للفترة المحددة"
                }
            
            # استخراج القيم
            values = [m['value'] for m in measurements if isinstance(m['value'], (int, float))]
            
            if not values:
                return {
                    "device_id": device_id,
                    "measurement_type": measurement_type,
                    "count": 0,
                    "message": "لا توجد قيم رقمية"
                }
            
            # حساب الإحصائيات
            stats = {
                "device_id": device_id,
                "measurement_type": measurement_type,
                "time_range": time_range,
                "count": len(values),
                "average": round(statistics.mean(values), 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "median": round(statistics.median(values), 2),
                "std_dev": round(statistics.stdev(values), 2) if len(values) > 1 else 0,
                "sum": round(sum(values), 2),
                "first_value": round(values[0], 2),
                "last_value": round(values[-1], 2),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ تم حساب الإحصائيات بنجاح")
            return stats
        
        except Exception as e:
            logger.error(f"❌ خطأ في حساب الإحصائيات: {str(e)}")
            return {
                "error": str(e),
                "device_id": device_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_system_summary(self) -> Dict[str, Any]:
        """الحصول على ملخص النظام"""
        try:
            logger.info("📊 حساب ملخص النظام")
            
            conn = await get_db_connection()
            cursor = conn.cursor()
            
            # عدد الأجهزة
            cursor.execute("SELECT COUNT(*) FROM devices WHERE status = 'active'")
            active_devices = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM devices")
            total_devices = cursor.fetchone()[0]
            
            # عدد التنبيهات
            cursor.execute("SELECT COUNT(*) FROM alerts WHERE is_resolved = FALSE")
            unresolved_alerts = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM alerts")
            total_alerts = cursor.fetchone()[0]
            
            cursor.close()
            
            # جلب عدد القياسات من MongoDB
            db = await get_mongodb_connection()
            total_measurements = db.measurement_logs.count_documents({})
            
            summary = {
                "total_devices": total_devices,
                "active_devices": active_devices,
                "inactive_devices": total_devices - active_devices,
                "total_measurements": total_measurements,
                "total_alerts": total_alerts,
                "unresolved_alerts": unresolved_alerts,
                "system_health": self._calculate_system_health(
                    active_devices, total_devices, unresolved_alerts
                ),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ تم حساب ملخص النظام بنجاح")
            return summary
        
        except Exception as e:
            logger.error(f"❌ خطأ في حساب ملخص النظام: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_device_health_status(self, device_id: str) -> Dict[str, Any]:
        """الحصول على حالة صحة الجهاز"""
        try:
            logger.info(f"❤️ حساب حالة صحة الجهاز: {device_id}")
            
            conn = await get_db_connection()
            cursor = conn.cursor()
            
            # جلب معلومات الجهاز
            cursor.execute(
                "SELECT status FROM devices WHERE device_id = %s",
                (device_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                cursor.close()
                return {
                    "error": "الجهاز غير موجود",
                    "device_id": device_id
                }
            
            device_status = result[0]
            
            # عدد التنبيهات النشطة
            cursor.execute(
                "SELECT COUNT(*) FROM alerts WHERE device_id = %s AND is_resolved = FALSE",
                (device_id,)
            )
            active_alerts = cursor.fetchone()[0]
            
            # آخر وقت تحديث
            cursor.execute(
                "SELECT created_at FROM event_logs WHERE device_id = %s ORDER BY created_at DESC LIMIT 1",
                (device_id,)
            )
            last_update = cursor.fetchone()
            
            cursor.close()
            
            # حساب درجة الصحة
            health_score = self._calculate_device_health_score(device_status, active_alerts)
            
            health_status = {
                "device_id": device_id,
                "status": device_status,
                "health_score": health_score,
                "active_alerts": active_alerts,
                "last_update": last_update[0].isoformat() if last_update else None,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ تم حساب حالة الصحة بنجاح")
            return health_status
        
        except Exception as e:
            logger.error(f"❌ خطأ في حساب حالة الصحة: {str(e)}")
            return {
                "error": str(e),
                "device_id": device_id
            }
    
    async def get_trend_analysis(
        self,
        device_id: str,
        measurement_type: str,
        time_range: str = "-7d"
    ) -> Dict[str, Any]:
        """تحليل الاتجاهات"""
        try:
            logger.info(f"📈 تحليل الاتجاهات للجهاز: {device_id}")
            
            # جلب البيانات من InfluxDB
            measurements = await query_measurements(measurement_type, device_id, time_range)
            
            if len(measurements) < 2:
                return {
                    "device_id": device_id,
                    "measurement_type": measurement_type,
                    "message": "بيانات غير كافية لتحليل الاتجاهات"
                }
            
            # استخراج القيم
            values = [m['value'] for m in measurements if isinstance(m['value'], (int, float))]
            
            # حساب الاتجاه
            if len(values) >= 2:
                first_half_avg = statistics.mean(values[:len(values)//2])
                second_half_avg = statistics.mean(values[len(values)//2:])
                trend = "صاعد" if second_half_avg > first_half_avg else "هابط"
                trend_percentage = round(
                    ((second_half_avg - first_half_avg) / first_half_avg * 100),
                    2
                )
            else:
                trend = "مستقر"
                trend_percentage = 0
            
            trend_analysis = {
                "device_id": device_id,
                "measurement_type": measurement_type,
                "time_range": time_range,
                "trend": trend,
                "trend_percentage": trend_percentage,
                "data_points": len(values),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ تم تحليل الاتجاهات بنجاح")
            return trend_analysis
        
        except Exception as e:
            logger.error(f"❌ خطأ في تحليل الاتجاهات: {str(e)}")
            return {
                "error": str(e),
                "device_id": device_id
            }
    
    async def get_anomaly_detection(
        self,
        device_id: str,
        measurement_type: str,
        threshold: float = 2.0
    ) -> Dict[str, Any]:
        """كشف الشذوذ (Anomaly Detection)"""
        try:
            logger.info(f"🔍 كشف الشذوذ للجهاز: {device_id}")
            
            # جلب البيانات من InfluxDB
            measurements = await query_measurements(measurement_type, device_id, "-24h")
            
            if len(measurements) < 3:
                return {
                    "device_id": device_id,
                    "measurement_type": measurement_type,
                    "message": "بيانات غير كافية لكشف الشذوذ"
                }
            
            # استخراج القيم
            values = [m['value'] for m in measurements if isinstance(m['value'], (int, float))]
            
            # حساب المتوسط والانحراف المعياري
            mean_val = statistics.mean(values)\n            std_dev = statistics.stdev(values) if len(values) > 1 else 0\n            \n            # تحديد القيم الشاذة\n            anomalies = []\n            for i, val in enumerate(values):\n                z_score = abs((val - mean_val) / std_dev) if std_dev > 0 else 0\n                if z_score > threshold:\n                    anomalies.append({\n                        \"index\": i,\n                        \"value\": val,\n                        \"z_score\": round(z_score, 2)\n                    })\n            \n            anomaly_result = {\n                \"device_id\": device_id,\n                \"measurement_type\": measurement_type,\n                \"total_measurements\": len(values),\n                \"anomalies_count\": len(anomalies),\n                \"anomalies\": anomalies,\n                \"threshold\": threshold,\n                \"timestamp\": datetime.now().isoformat()\n            }\n            \n            logger.info(f\"✅ تم كشف {len(anomalies)} شذوذ\")\n            return anomaly_result\n        \n        except Exception as e:\n            logger.error(f\"❌ خطأ في كشف الشذوذ: {str(e)}\")\n            return {\n                \"error\": str(e),\n                \"device_id\": device_id\n            }\n    \n    def _calculate_system_health(self, active: int, total: int, alerts: int) -> float:\n        \"\"\"حساب درجة صحة النظام\"\"\"\n        if total == 0:\n            return 100.0\n        \n        device_health = (active / total) * 100\n        alert_penalty = min(alerts * 5, 50)  # كل تنبيه = 5 نقاط طرح\n        \n        health = device_health - alert_penalty\n        return max(0, min(100, health))\n    \n    def _calculate_device_health_score(self, status: str, active_alerts: int) -> float:\n        \"\"\"حساب درجة صحة الجهاز\"\"\"\n        status_scores = {\n            \"active\": 100,\n            \"inactive\": 50,\n            \"maintenance\": 75,\n            \"error\": 0\n        }\n        \n        base_score = status_scores.get(status, 50)\n        alert_penalty = min(active_alerts * 10, 50)\n        \n        health = base_score - alert_penalty\n        return max(0, min(100, health))\n\n# إنشاء نسخة واحدة من الخدمة\nanalytics_service = AnalyticsService()\n
