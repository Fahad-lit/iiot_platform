"""
نماذج البيانات (Pydantic Models) لـ FastAPI
Data Models for FastAPI
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ============ تعريفات الحالات (Enums) ============

class DeviceStatus(str, Enum):
    """حالات الجهاز"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class AlertSeverity(str, Enum):
    """مستويات خطورة التنبيهات"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class DeviceType(str, Enum):
    """أنواع الأجهزة"""
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    CONTROLLER = "controller"
    GATEWAY = "gateway"

# ============ نماذج الأجهزة (Device Models) ============

class DeviceCreate(BaseModel):
    """نموذج إنشاء جهاز جديد"""
    device_id: str = Field(..., min_length=1, max_length=255, description="معرف الجهاز الفريد")
    device_name: str = Field(..., min_length=1, max_length=255, description="اسم الجهاز")
    device_type: DeviceType = Field(..., description="نوع الجهاز")
    location: Optional[str] = Field(None, max_length=255, description="موقع الجهاز")
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "sensor_001",
                "device_name": "حساس درجة الحرارة - المصنع أ",
                "device_type": "sensor",
                "location": "قاعة الإنتاج الأولى"
            }
        }

class Device(DeviceCreate):
    """نموذج الجهاز الكامل"""
    id: int
    status: DeviceStatus = DeviceStatus.ACTIVE
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============ نماذج القياسات (Measurement Models) ============

class MeasurementCreate(BaseModel):
    """نموذج تسجيل قياس جديد"""
    device_id: str = Field(..., description="معرف الجهاز")
    measurement_type: str = Field(..., description="نوع القياس (مثل: temperature, pressure)")
    value: float = Field(..., description="قيمة القياس")
    unit: str = Field(..., description="وحدة القياس (مثل: °C, Pa)")
    timestamp: Optional[datetime] = Field(None, description="الطابع الزمني للقياس")
    metadata: Optional[Dict[str, Any]] = Field(None, description="بيانات إضافية")
    
    @validator('value')
    def validate_value(cls, v):
        """التحقق من صحة قيمة القياس"""
        if not isinstance(v, (int, float)):
            raise ValueError('يجب أن تكون القيمة رقمية')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "sensor_001",
                "measurement_type": "temperature",
                "value": 25.5,
                "unit": "°C",
                "metadata": {
                    "humidity": 60,
                    "pressure": 1013.25
                }
            }
        }

class Measurement(MeasurementCreate):
    """نموذج القياس الكامل"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class MeasurementBatch(BaseModel):
    """نموذج مجموعة من القياسات"""
    measurements: List[MeasurementCreate] = Field(..., description="قائمة القياسات")
    
    class Config:
        json_schema_extra = {
            "example": {
                "measurements": [
                    {
                        "device_id": "sensor_001",
                        "measurement_type": "temperature",
                        "value": 25.5,
                        "unit": "°C"
                    },
                    {
                        "device_id": "sensor_002",
                        "measurement_type": "pressure",
                        "value": 1013.25,
                        "unit": "Pa"
                    }
                ]
            }
        }

# ============ نماذج التنبيهات (Alert Models) ============

class AlertCreate(BaseModel):
    """نموذج إنشاء تنبيه جديد"""
    device_id: str = Field(..., description="معرف الجهاز")
    alert_type: str = Field(..., description="نوع التنبيه")
    severity: AlertSeverity = Field(..., description="مستوى الخطورة")
    message: str = Field(..., description="رسالة التنبيه")
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "sensor_001",
                "alert_type": "temperature_high",
                "severity": "critical",
                "message": "درجة الحرارة تجاوزت الحد الأقصى المسموح به"
            }
        }

class Alert(AlertCreate):
    """نموذج التنبيه الكامل"""
    id: int
    is_resolved: bool = False
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============ نماذج التنبؤات (Prediction Models) ============

class PredictionCreate(BaseModel):
    """نموذج إنشاء تنبؤ جديد"""
    device_id: str = Field(..., description="معرف الجهاز")
    prediction_type: str = Field(..., description="نوع التنبؤ (مثل: failure, maintenance)")
    confidence: float = Field(..., ge=0, le=1, description="درجة الثقة (0-1)")
    predicted_value: Optional[float] = Field(None, description="القيمة المتنبأ بها")
    details: Optional[Dict[str, Any]] = Field(None, description="تفاصيل إضافية")
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "sensor_001",
                "prediction_type": "failure",
                "confidence": 0.85,
                "predicted_value": 45.2,
                "details": {
                    "reason": "تدهور الأداء المستمر",
                    "days_to_failure": 7
                }
            }
        }

class Prediction(PredictionCreate):
    """نموذج التنبؤ الكامل"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ نماذج الإحصائيات (Analytics Models) ============

class DeviceStats(BaseModel):
    """إحصائيات الجهاز"""
    device_id: str
    total_measurements: int
    last_measurement_time: Optional[datetime]
    average_value: Optional[float]
    min_value: Optional[float]
    max_value: Optional[float]
    alert_count: int
    active_alerts: int

class SystemSummary(BaseModel):
    """ملخص النظام"""
    total_devices: int
    active_devices: int
    inactive_devices: int
    total_measurements: int
    total_alerts: int
    unresolved_alerts: int
    average_system_health: float
    timestamp: datetime

# ============ نماذج الاستجابة (Response Models) ============

class SuccessResponse(BaseModel):
    """نموذج استجابة النجاح"""
    success: bool = True
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    """نموذج استجابة الخطأ"""
    success: bool = False
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginatedResponse(BaseModel):
    """نموذج استجابة مع ترقيم الصفحات"""
    data: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

# ============ نماذج المصادقة (Authentication Models) ============

class UserCreate(BaseModel):
    """نموذج إنشاء مستخدم جديد"""
    username: str = Field(..., min_length=3, max_length=255)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=8)

class User(BaseModel):
    """نموذج المستخدم"""
    id: int
    username: str
    email: str
    role: str = "user"
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """نموذج التوكن"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

# ============ نماذج الصحة (Health Models) ============

class ServiceHealth(BaseModel):
    """صحة الخدمة"""
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    response_time_ms: Optional[float] = None
    last_check: datetime

class SystemHealth(BaseModel):
    """صحة النظام الكامل"""
    overall_status: str
    services: Dict[str, ServiceHealth]
    timestamp: datetime
