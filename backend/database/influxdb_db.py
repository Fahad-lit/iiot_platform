"""
اتصال قاعدة البيانات الزمنية InfluxDB
InfluxDB Time-Series Database Connection
"""

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import logging

logger = logging.getLogger(__name__)

# متغيرات الاتصال
INFLUX_HOST = os.getenv("INFLUX_HOST", "localhost")
INFLUX_PORT = os.getenv("INFLUX_PORT", "8086")
INFLUX_ORG = os.getenv("INFLUX_ORG", "iiot_org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "iiot_measurements")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "iiot_token")
INFLUX_USER = os.getenv("INFLUX_USER", "iiot_user")
INFLUX_PASSWORD = os.getenv("INFLUX_PASSWORD", "iiot_secure_password_123")

# متغير الاتصال العام
influx_client = None
write_api = None
query_api = None

async def init_influxdb():
    """تهيئة الاتصال بـ InfluxDB"""
    global influx_client, write_api, query_api
    try:
        url = f"http://{INFLUX_HOST}:{INFLUX_PORT}"
        
        influx_client = InfluxDBClient(
            url=url,
            username=INFLUX_USER,
            password=INFLUX_PASSWORD,
            org=INFLUX_ORG
        )
        
        # اختبار الاتصال
        health = influx_client.health()
        if health.status == "pass":
            write_api = influx_client.write_api(write_type=SYNCHRONOUS)
            query_api = influx_client.query_api()
            logger.info("✅ تم الاتصال بـ InfluxDB بنجاح")
        else:
            raise Exception("InfluxDB health check failed")
        
    except Exception as e:
        logger.error(f"❌ خطأ في الاتصال بـ InfluxDB: {str(e)}")
        raise

async def get_influxdb_client():
    """الحصول على عميل InfluxDB"""
    global influx_client
    if influx_client is None:
        await init_influxdb()
    return influx_client

async def get_write_api():
    """الحصول على API الكتابة"""
    global write_api
    if write_api is None:
        await init_influxdb()
    return write_api

async def get_query_api():
    """الحصول على API الاستعلام"""
    global query_api
    if query_api is None:
        await init_influxdb()
    return query_api

async def close_influxdb():
    """إغلاق الاتصال بـ InfluxDB"""
    global influx_client
    if influx_client:
        influx_client.close()
        logger.info("✅ تم إغلاق الاتصال بـ InfluxDB")

async def write_measurement(measurement_name: str, tags: dict, fields: dict, timestamp=None):
    """كتابة قياس إلى InfluxDB"""
    try:
        write_api = await get_write_api()
        
        from influxdb_client.client.write_api import Point
        
        point = Point(measurement_name)
        
        # إضافة الوسوم
        for key, value in tags.items():
            point.tag(key, value)
        
        # إضافة الحقول
        for key, value in fields.items():
            if isinstance(value, (int, float)):
                point.field(key, value)
            else:
                point.field(key, str(value))
        
        # إضافة الطابع الزمني
        if timestamp:
            point.time(timestamp)
        
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        logger.debug(f"✅ تم كتابة القياس: {measurement_name}")
        
    except Exception as e:
        logger.error(f"❌ خطأ في كتابة القياس: {str(e)}")
        raise

async def query_measurements(measurement_name: str, device_id: str, time_range: str = "-1h"):
    """الاستعلام عن القياسات"""
    try:
        query_api = await get_query_api()
        
        query = f"""
        from(bucket:"{INFLUX_BUCKET}")
            |> range(start: {time_range})
            |> filter(fn: (r) => r._measurement == "{measurement_name}")
            |> filter(fn: (r) => r.device_id == "{device_id}")
        """
        
        result = query_api.query(org=INFLUX_ORG, query=query)
        
        measurements = []
        for table in result:
            for record in table.records:
                measurements.append({
                    "time": record.get_time(),
                    "value": record.get_value(),
                    "field": record.get_field()
                })
        
        return measurements
        
    except Exception as e:
        logger.error(f"❌ خطأ في الاستعلام: {str(e)}")
        raise
