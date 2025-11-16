"""
اتصال قاعدة البيانات العلائقية PostgreSQL
PostgreSQL Relational Database Connection
"""

import psycopg2
from psycopg2.pool import SimpleConnectionPool
import os
import logging

logger = logging.getLogger(__name__)

# متغيرات الاتصال
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "iiot_db")
DB_USER = os.getenv("POSTGRES_USER", "iiot_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "iiot_secure_password_123")

# مجموعة الاتصالات
connection_pool = None

async def init_postgres():
    """تهيئة الاتصال بـ PostgreSQL"""
    global connection_pool
    try:
        connection_pool = SimpleConnectionPool(
            1, 20,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info("✅ تم إنشاء مجموعة الاتصالات بـ PostgreSQL")
    except Exception as e:
        logger.error(f"❌ خطأ في الاتصال بـ PostgreSQL: {str(e)}")
        raise

async def get_db_connection():
    """الحصول على اتصال من المجموعة"""
    global connection_pool
    if connection_pool is None:
        await init_postgres()
    return connection_pool.getconn()

def return_db_connection(conn):
    """إرجاع الاتصال إلى المجموعة"""
    global connection_pool
    if connection_pool:
        connection_pool.putconn(conn)

async def close_postgres():
    """إغلاق جميع الاتصالات"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        logger.info("✅ تم إغلاق جميع اتصالات PostgreSQL")

# ============ جداول قاعدة البيانات ============

CREATE_TABLES_SQL = """
-- جدول الأجهزة
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    device_name VARCHAR(255) NOT NULL,
    device_type VARCHAR(100),
    location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول المستخدمين
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول التنبيهات
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) NOT NULL,
    alert_type VARCHAR(100),
    severity VARCHAR(50),
    message TEXT,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

-- جدول سجلات الأحداث
CREATE TABLE IF NOT EXISTS event_logs (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255),
    event_type VARCHAR(100),
    event_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

-- جدول إعدادات الأجهزة
CREATE TABLE IF NOT EXISTS device_config (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    config_data JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

-- إنشاء الفهارس
CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);
CREATE INDEX IF NOT EXISTS idx_alerts_device ON alerts(device_id);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON alerts(is_resolved);
CREATE INDEX IF NOT EXISTS idx_event_logs_device ON event_logs(device_id);
CREATE INDEX IF NOT EXISTS idx_event_logs_created ON event_logs(created_at);
"""

async def create_tables():
    """إنشاء جداول قاعدة البيانات"""
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()
        cursor.execute(CREATE_TABLES_SQL)
        conn.commit()
        cursor.close()
        return_db_connection(conn)
        logger.info("✅ تم إنشاء جداول قاعدة البيانات")
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء الجداول: {str(e)}")
        raise
