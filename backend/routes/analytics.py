"""
مسارات API للتحليلات والإحصائيات
API Routes for Analytics and Statistics
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging
from services.analytics_service import analytics_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}}
)

@router.get("/summary")
async def get_system_summary():
    """
    الحصول على ملخص النظام الكامل
    
    يعيد:
    - عدد الأجهزة الكلي والنشط
    - عدد القياسات الكلي
    - عدد التنبيهات المحلولة وغير المحلولة
    - درجة صحة النظام العامة
    """
    try:
        logger.info("📊 جلب ملخص النظام")
        result = await analytics_service.get_system_summary()
        return result
    
    except Exception as e:
        logger.error(f"❌ خطأ في جلب ملخص النظام: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices/{device_id}/statistics")
async def get_device_statistics(
    device_id: str,
    measurement_type: str = Query(..., description="نوع القياس"),
    time_range: str = Query("-24h", description="النطاق الزمني (مثل: -1h, -24h, -7d)")
):
    """
    الحصول على إحصائيات الجهاز
    
    يعيد:
    - المتوسط والحد الأدنى والحد الأقصى
    - الانحراف المعياري والوسيط
    - عدد القياسات
    """
    try:
        logger.info(f"📊 جلب إحصائيات الجهاز: {device_id}")
        result = await analytics_service.get_device_statistics(
            device_id, measurement_type, time_range
        )
        return result
    
    except Exception as e:
        logger.error(f"❌ خطأ في جلب الإحصائيات: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices/{device_id}/health")
async def get_device_health(device_id: str):
    """
    الحصول على حالة صحة الجهاز
    
    يعيد:
    - حالة الجهاز (نشط، غير نشط، صيانة، خطأ)
    - درجة الصحة (0-100)
    - عدد التنبيهات النشطة
    - آخر وقت تحديث
    """
    try:
        logger.info(f"❤️ جلب حالة صحة الجهاز: {device_id}")
        result = await analytics_service.get_device_health_status(device_id)
        return result
    
    except Exception as e:
        logger.error(f"❌ خطأ في جلب حالة الصحة: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices/{device_id}/trends")
async def get_trend_analysis(
    device_id: str,
    measurement_type: str = Query(..., description="نوع القياس"),
    time_range: str = Query("-7d", description="النطاق الزمني")
):
    """
    تحليل الاتجاهات
    
    يعيد:
    - اتجاه البيانات (صاعد/هابط/مستقر)
    - نسبة التغير
    - عدد نقاط البيانات
    """
    try:
        logger.info(f"📈 تحليل اتجاهات الجهاز: {device_id}")
        result = await analytics_service.get_trend_analysis(
            device_id, measurement_type, time_range
        )
        return result
    
    except Exception as e:
        logger.error(f"❌ خطأ في تحليل الاتجاهات: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices/{device_id}/anomalies")
async def detect_anomalies(
    device_id: str,
    measurement_type: str = Query(..., description="نوع القياس"),
    threshold: float = Query(2.0, ge=1.0, le=5.0, description="عتبة كشف الشذوذ (Z-score)")
):
    """
    كشف الشذوذ في البيانات
    
    يستخدم Z-score لتحديد القيم الشاذة
    
    يعيد:
    - عدد الشذوذ المكتشفة
    - تفاصيل كل شذوذ (القيمة والمؤشر)
    """
    try:
        logger.info(f"🔍 كشف شذوذ الجهاز: {device_id}")
        result = await analytics_service.get_anomaly_detection(
            device_id, measurement_type, threshold
        )
        return result
    
    except Exception as e:
        logger.error(f"❌ خطأ في كشف الشذوذ: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices/comparison")
async def compare_devices(
    device_ids: str = Query(..., description="معرفات الأجهزة مفصولة بفواصل"),
    measurement_type: str = Query(..., description="نوع القياس"),
    time_range: str = Query("-24h", description="النطاق الزمني")
):
    """
    مقارنة إحصائيات عدة أجهزة
    
    يتيح مقارنة الأداء بين أجهزة متعددة
    """
    try:
        device_list = [d.strip() for d in device_ids.split(",")]
        logger.info(f"📊 مقارنة أجهزة: {device_list}")
        
        results = []
        for device_id in device_list:
            stats = await analytics_service.get_device_statistics(
                device_id, measurement_type, time_range
            )
            results.append(stats)
        
        return {
            "devices": device_list,
            "measurement_type": measurement_type,
            "time_range": time_range,
            "comparison": results
        }
    
    except Exception as e:
        logger.error(f"❌ خطأ في مقارنة الأجهزة: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
