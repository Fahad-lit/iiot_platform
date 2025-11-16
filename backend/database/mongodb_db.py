"""
اتصال قاعدة البيانات المستندية MongoDB
MongoDB Document Database Connection
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
import logging

logger = logging.getLogger(__name__)

# متغيرات الاتصال
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_USER = os.getenv("MONGO_USER", "iiot_user")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "iiot_secure_password_123")
MONGO_DB = os.getenv("MONGO_DB", "iiot_db")

# متغير الاتصال العام
mongo_client = None
mongo_db = None

async def init_mongodb():
    """تهيئة الاتصال بـ MongoDB"""
    global mongo_client, mongo_db
    try:
        connection_string = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"
        mongo_client = MongoClient(connection_string)
        
        # اختبار الاتصال
        mongo_client.admin.command('ping')
        
        mongo_db = mongo_client[MONGO_DB]
        logger.info("✅ تم الاتصال بـ MongoDB بنجاح")
        
        # إنشاء المجموعات والفهارس
        await create_collections()
        
    except ConnectionFailure as e:
        logger.error(f"❌ خطأ في الاتصال بـ MongoDB: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ خطأ غير متوقع: {str(e)}")
        raise

async def get_mongodb_connection():
    """الحصول على اتصال MongoDB"""
    global mongo_db
    if mongo_db is None:
        await init_mongodb()
    return mongo_db

async def close_mongodb():
    """إغلاق الاتصال بـ MongoDB"""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("✅ تم إغلاق الاتصال بـ MongoDB")

async def create_collections():
    """إنشاء المجموعات والفهارس"""
    global mongo_db
    try:
        # مجموعة سجلات الأخطاء والأحداث
        if "error_logs" not in mongo_db.list_collection_names():
            mongo_db.create_collection("error_logs")
            mongo_db.error_logs.create_index("timestamp")
            logger.info("✅ تم إنشاء مجموعة error_logs")
        
        # مجموعة مخرجات الذكاء الاصطناعي
        if "ai_predictions" not in mongo_db.list_collection_names():
            mongo_db.create_collection("ai_predictions")
            mongo_db.ai_predictions.create_index("device_id")
            mongo_db.ai_predictions.create_index("created_at")
            logger.info("✅ تم إنشاء مجموعة ai_predictions")
        
        # مجموعة بيانات التكوين الديناميكية
        if "device_configurations" not in mongo_db.list_collection_names():
            mongo_db.create_collection("device_configurations")
            mongo_db.device_configurations.create_index("device_id")
            logger.info("✅ تم إنشاء مجموعة device_configurations")
        
        # مجموعة سجلات الصيانة
        if "maintenance_logs" not in mongo_db.list_collection_names():
            mongo_db.create_collection("maintenance_logs")
            mongo_db.maintenance_logs.create_index("device_id")
            mongo_db.maintenance_logs.create_index("created_at")
            logger.info("✅ تم إنشاء مجموعة maintenance_logs")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء المجموعات: {str(e)}")
        raise
