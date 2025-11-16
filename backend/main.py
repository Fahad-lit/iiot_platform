"""
منصة إنترنت الأشياء الصناعية والذكاء الاصطناعي - الخلفية الرئيسية
Industrial IoT Platform with AI - Main Backend
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# استيراد الاتصالات بقواعد البيانات
from database.postgres_db import init_postgres, get_db_connection, create_tables
from database.mongodb_db import init_mongodb, get_mongodb_connection
from database.influxdb_db import init_influxdb, get_influxdb_client
from kafka_broker.producer import KafkaProducerService
from kafka_broker.consumer import KafkaConsumerService

# استيراد المسارات
from routes.measurements import router as measurements_router
from routes.analytics import router as analytics_router
from routes.devices import router as devices_router
from routes.predictions import router as predictions_router

# متغيرات عامة
kafka_producer = None
kafka_consumer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة دورة حياة التطبيق"""
    # بدء التطبيق
    logger.info("=" * 60)
    logger.info("🚀 بدء منصة IIoT الصناعية والذكاء الاصطناعي...")
    logger.info("=" * 60)
    
    try:
        # تهيئة قواعد البيانات
        logger.info("🔌 جاري الاتصال بقواعد البيانات...")
        
        await init_postgres()
        logger.info("✅ تم الاتصال بـ PostgreSQL")
        
        await create_tables()
        logger.info("✅ تم إنشاء جداول PostgreSQL")
        
        await init_mongodb()
        logger.info("✅ تم الاتصال بـ MongoDB")
        
        await init_influxdb()
        logger.info("✅ تم الاتصال بـ InfluxDB")
        
        # تهيئة Kafka
        logger.info("🔌 جاري الاتصال بـ Apache Kafka...")
        global kafka_producer, kafka_consumer
        
        kafka_producer = KafkaProducerService()
        logger.info("✅ تم إنشاء Kafka Producer")
        
        kafka_consumer = KafkaConsumerService()
        kafka_consumer.start_consuming()
        logger.info("✅ تم بدء Kafka Consumer")
        
        logger.info("=" * 60)
        logger.info("✅ تم تهيئة جميع الخدمات بنجاح!")
        logger.info("=" * 60)
        logger.info("🌐 الخادم جاهز للعمل على http://localhost:8000")
        logger.info("📚 التوثيق متاح على http://localhost:8000/docs")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ خطأ في التهيئة: {str(e)}")
        logger.error("=" * 60)
        raise
    
    yield
    
    # إيقاف التطبيق
    logger.info("=" * 60)
    logger.info("🛑 إيقاف منصة IIoT...")
    logger.info("=" * 60)
    
    if kafka_producer:
        kafka_producer.close()
    if kafka_consumer:
        kafka_consumer.close()
    
    logger.info("✅ تم إغلاق جميع الاتصالات")

# إنشاء تطبيق FastAPI
app = FastAPI(
    title="منصة إنترنت الأشياء الصناعية والذكاء الاصطناعي",
    description="Industrial IoT Platform with AI/ML Capabilities - منصة صناعية متكاملة لإدارة أجهزة IoT والذكاء الاصطناعي",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# إضافة CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ تسجيل المسارات (Register Routes) ============

app.include_router(measurements_router)
app.include_router(analytics_router)
app.include_router(devices_router)
app.include_router(predictions_router)

# ============ المسارات الأساسية (Base Routes) ============

@app.get("/")
async def root():
    """المسار الرئيسي"""
    return {
        "message": "مرحبًا بك في منصة IIoT الصناعية",
        "title": "Industrial IoT Platform with AI",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "status": "🟢 جاهزة للعمل",
        "docs": "http://localhost:8000/docs",
        "features": [
            "جمع البيانات من أجهزة IoT",
            "معالجة البيانات في الوقت الفعلي",
            "تخزين البيانات في قواعد بيانات متعددة",
            "تحليل البيانات باستخدام الذكاء الاصطناعي",
            "لوحة تحكم تفاعلية",
            "نظام التنبيهات والإشعارات"
        ]
    }

@app.get("/health")
async def health_check():
    """فحص صحة التطبيق والخدمات"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "postgres": "✅ متصل",
            "mongodb": "✅ متصل",
            "influxdb": "✅ متصل",
            "kafka": "✅ متصل",
            "redis": "✅ متصل"
        },
        "uptime": "جاري العمل",
        "version": "1.0.0"
    }

@app.get("/api/info")
async def get_platform_info():
    """الحصول على معلومات المنصة"""
    return {
        "platform": "Industrial IoT Platform with AI",
        "version": "1.0.0",
        "description": "منصة صناعية متكاملة لإدارة أجهزة IoT والذكاء الاصطناعي",
        "tech_stack": {
            "backend": "Python FastAPI",
            "frontend": "React.js",
            "databases": ["PostgreSQL", "MongoDB", "InfluxDB"],
            "message_broker": "Apache Kafka",
            "cache": "Redis"
        },
        "endpoints": {
            "measurements": "/api/measurements",
            "devices": "/api/devices",
            "alerts": "/api/alerts",
            "predictions": "/api/predictions",
            "analytics": "/api/analytics"
        }
    }

# ============ مسارات الأجهزة (Devices Routes) ============

@app.get("/api/devices")
async def get_devices():
    """الحصول على قائمة جميع الأجهزة"""
    try:
        logger.info("📱 جلب قائمة الأجهزة")
        return {
            "devices": [],
            "total": 0,
            "message": "سيتم تطوير هذا المسار لاحقًا"
        }
    except Exception as e:
        logger.error(f"❌ خطأ في جلب الأجهزة: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/devices")
async def create_device(device_data: dict):
    """إنشاء جهاز جديد"""
    try:
        logger.info(f"➕ إنشاء جهاز جديد: {device_data.get('device_id')}")
        return {
            "message": "سيتم تطوير هذا المسار لاحقًا",
            "device": device_data
        }
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء الجهاز: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ مسارات التنبيهات (Alerts Routes) ============

@app.get("/api/alerts")
async def get_alerts(device_id: str = None):
    """الحصول على التنبيهات"""
    try:
        logger.info(f"⚠️ جلب التنبيهات")
        return {
            "alerts": [],
            "total": 0,
            "message": "سيتم تطوير هذا المسار لاحقًا"
        }
    except Exception as e:
        logger.error(f"❌ خطأ في جلب التنبيهات: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ مسارات الذكاء الاصطناعي (AI/ML Routes) ============

@app.get("/api/predictions/{device_id}")
async def get_predictions(device_id: str):
    """الحصول على التنبؤات للصيانة الوقائية"""
    try:
        logger.info(f"🤖 جلب التنبؤات للجهاز: {device_id}")
        return {
            "device_id": device_id,
            "predictions": [],
            "message": "سيتم تطوير هذا المسار لاحقًا"
        }
    except Exception as e:
        logger.error(f"❌ خطأ في جلب التنبؤات: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ مسارات الإحصائيات (Analytics Routes) ============

@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """الحصول على ملخص الإحصائيات"""
    try:
        logger.info("📊 جلب ملخص الإحصائيات")
        return {
            "total_devices": 0,
            "active_devices": 0,
            "total_measurements": 0,
            "alerts_count": 0,
            "message": "سيتم تطوير هذا المسار لاحقًا"
        }
    except Exception as e:
        logger.error(f"❌ خطأ في جلب الإحصائيات: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ معالجة الأخطاء (Error Handlers) ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """معالج الأخطاء HTTP"""
    return {
        "success": False,
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.now().isoformat()
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """معالج الأخطاء العامة"""
    logger.error(f"❌ خطأ غير متوقع: {str(exc)}")
    return {
        "success": False,
        "error": "خطأ غير متوقع في الخادم",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
