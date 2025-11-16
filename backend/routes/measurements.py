"""
مسارات API لإدارة القياسات
API Routes for Measurements Management
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
import logging
from models import MeasurementCreate, Measurement, MeasurementBatch, SuccessResponse, ErrorResponse
from services.ingestion_service import ingestion_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/measurements",
    tags=["measurements"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=SuccessResponse)
async def record_measurement(measurement: MeasurementCreate):
    """
    تسجيل قياس جديد
    
    - **device_id**: معرف الجهاز (مطلوب)
    - **measurement_type**: نوع القياس مثل temperature, pressure (مطلوب)
    - **value**: قيمة القياس (مطلوب)
    - **unit**: وحدة القياس مثل °C, Pa (مطلوب)
    - **timestamp**: الطابع الزمني (اختياري، سيتم استخدام الوقت الحالي إذا لم يتم تحديده)
    - **metadata**: بيانات إضافية (اختياري)
    """
    try:
        result = await ingestion_service.ingest_measurement(measurement.dict())
        
        if result['success']:
            return SuccessResponse(
                success=True,
                message="تم تسجيل القياس بنجاح",
                data={"device_id": measurement.device_id, "timestamp": datetime.now()}
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get('errors', [result.get('error', 'خطأ غير معروف')])
            )
    
    except Exception as e:
        logger.error(f"❌ خطأ في تسجيل القياس: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")

@router.post("/batch", response_model=SuccessResponse)
async def record_batch_measurements(batch: MeasurementBatch):
    """
    تسجيل مجموعة من القياسات دفعة واحدة
    
    يتيح إرسال عدة قياسات في طلب واحد لتحسين الأداء
    """
    try:
        result = await ingestion_service.ingest_batch(
            [m.dict() for m in batch.measurements]
        )
        
        return SuccessResponse(
            success=result['success'],
            message=f"تمت معالجة المجموعة: {result['successful']} نجح، {result['failed']} فشل",
            data=result
        )
    
    except Exception as e:
        logger.error(f"❌ خطأ في تسجيل مجموعة القياسات: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")

@router.get("/{device_id}")
async def get_device_measurements(
    device_id: str,
    limit: int = Query(100, ge=1, le=1000, description="عدد القياسات المطلوبة"),
    offset: int = Query(0, ge=0, description="عدد القياسات المتخطاة"),
    measurement_type: Optional[str] = Query(None, description="تصفية حسب نوع القياس")
):
    """
    الحصول على قياسات جهاز معين
    
    - **device_id**: معرف الجهاز (مطلوب)
    - **limit**: عدد النتائج المطلوبة (افتراضي: 100)
    - **offset**: عدد النتائج المتخطاة للترقيم (افتراضي: 0)
    - **measurement_type**: تصفية حسب نوع القياس (اختياري)
    """
    try:
        logger.info(f"📊 جلب القياسات للجهاز: {device_id}")
        
        # سيتم تطوير هذا المسار لاحقًا للاتصال بـ InfluxDB
        return {
            "device_id": device_id,
            "measurements": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "message": "سيتم تطوير هذا المسار لاحقًا"
        }
    
    except Exception as e:
        logger.error(f"❌ خطأ في جلب القياسات: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")

@router.get("/{device_id}/latest")
async def get_latest_measurement(device_id: str):
    """
    الحصول على آخر قياس لجهاز معين
    """
    try:
        logger.info(f"📊 جلب آخر قياس للجهاز: {device_id}")
        
        # سيتم تطوير هذا المسار لاحقًا
        return {
            "device_id": device_id,
            "measurement": None,
            "message": "سيتم تطوير هذا المسار لاحقًا"
        }
    
    except Exception as e:
        logger.error(f"❌ خطأ في جلب آخر قياس: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")

@router.get("/{device_id}/statistics")
async def get_measurement_statistics(
    device_id: str,
    time_range: str = Query("24h", description="النطاق الزمني (مثل: 1h, 24h, 7d)")
):
    """
    الحصول على إحصائيات القياسات لجهاز معين
    
    يعيد: المتوسط، الحد الأدنى، الحد الأقصى، الانحراف المعياري
    """
    try:
        logger.info(f"📊 جلب إحصائيات القياسات للجهاز: {device_id}")
        
        # سيتم تطوير هذا المسار لاحقًا
        return {
            "device_id": device_id,
            "time_range": time_range,
            "statistics": {
                "average": None,
                "min": None,
                "max": None,
                "std_dev": None,
                "count": 0
            },
            "message": "سيتم تطوير هذا المسار لاحقًا"
        }
    
    except Exception as e:
        logger.error(f"❌ خطأ في جلب الإحصائيات: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")

@router.delete("/{device_id}/measurements")
async def delete_device_measurements(
    device_id: str,
    before: Optional[datetime] = Query(None, description="حذف القياسات قبل هذا التاريخ")
):
    """
    حذف قياسات جهاز معين
    
    تحذير: هذه العملية لا يمكن التراجع عنها!
    """
    try:
        logger.warning(f"⚠️ حذف القياسات للجهاز: {device_id}")
        
        # سيتم تطوير هذا المسار لاحقًا
        return {
            "success": True,
            "message": "سيتم تطوير هذا المسار لاحقًا",
            "device_id": device_id
        }
    
    except Exception as e:
        logger.error(f"❌ خطأ في حذف القياسات: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")
