import os
import psycopg2

class Baza:
    def __init__(self):
        # Railway'dan avtomatik keladigan DATABASE_URL orqali ulanadi
        database_url = os.getenv("DATABASE_URL")
        self.ulanish = psycopg2.connect(database_url)
        self.kurser = self.ulanish.cursor()
        self.jadvallarni_yaratish()

    def jadvallarni_yaratish(self):
        # 1. Foydalanuvchilar jadvali
        self.kurser.execute("""
            CREATE TABLE IF NOT EXISTS foydalanuvchilar (
                telegram_id BIGINT PRIMARY KEY,
                ism_familiya TEXT,
                telefon TEXT,
                tur TEXT DEFAULT 'ovoz_yiguvchi',
                yaratilgan_vaqt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Ovozlar jadvali
        self.kurser.execute("""
            CREATE TABLE IF NOT EXISTS ovozlar (
                id SERIAL PRIMARY KEY,
                yiguvchi_id BIGINT REFERENCES foydalanuvchilar(telegram_id),
                telefon_raqam TEXT,
                holat TEXT DEFAULT 'Jarayonda',
                sabab TEXT DEFAULT '',
                kiritilgan_vaqt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.ulanish.commit()

    # Foydalanuvchini qo'shish
    def foydalanuvchi_qoshish(self, telegram_id, ism_familiya, telefon="", tur="ovoz_yiguvchi"):
        self.kurser.execute("""
            INSERT INTO foydalanuvchilar (telegram_id, ism_familiya, telefon, tur)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (telegram_id) DO UPDATE 
            SET ism_familiya = EXCLUDED.ism_familiya,
                telefon = EXCLUDED.telefon,
                tur = EXCLUDED.tur
        """, (telegram_id, ism_familiya, telefon, tur))
        self.ulanish.commit()

    # Yangi ovoz kiritish
    def ovoz_qoshish(self, yiguvchi_id, telefon_raqam):
        self.kurser.execute("""
            INSERT INTO ovozlar (yiguvchi_id, telefon_raqam, holat)
            VALUES (%s, %s, 'Jarayonda')
            RETURNING id
        """, (yiguvchi_id, telefon_raqam))
        ovoz_id = self.kurser.fetchone()[0]
        self.ulanish.commit()
        return ovoz_id

    # Ovoz holatini o'zgartirish
    def ovoz_holatini_yangilash(self, ovoz_id, yangi_holat, sabab=""):
        self.kurser.execute("""
            UPDATE ovozlar
            SET holat = %s, sabab = %s
            WHERE id = %s
        """, (yangi_holat, sabab, ovoz_id))
        self.ulanish.commit()

    # Ovoz yig'uvchining statistikasi
    def yiguvchi_statistikasi(self, yiguvchi_id):
        self.kurser.execute("""
            SELECT 
                COUNT(*) as jami,
                COALESCE(SUM(CASE WHEN holat = 'Qabul qilindi' THEN 1 ELSE 0 END), 0) as qabul_qilingan,
                COALESCE(SUM(CASE WHEN holat = 'Jarayonda' THEN 1 ELSE 0 END), 0) as jarayonda,
                COALESCE(SUM(CASE WHEN holat = 'Rad etildi' THEN 1 ELSE 0 END), 0) as rad_etilgan
            FROM ovozlar
            WHERE yiguvchi_id = %s
        """, (yiguvchi_id,))
        return self.kurser.fetchone()
