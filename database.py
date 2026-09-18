# -*- coding: utf-8 -*-
"""
database.py
طبقة قاعدة البيانات (SQLite) - أي حد يستخدم السيستم بياناته بتتخزن هنا:
عملاء، حلاقين، خدمات، مواعيد.
"""

import sqlite3
import os


class Database:
    ALL_SLOTS = [f"{h:02d}:{m:02d}" for h in range(10, 22) for m in (0, 30)]

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "barbershop.db")
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()
        self._seed_defaults()

    # ---------------------------------------------------------------- setup
    def _create_tables(self):
        c = self.conn.cursor()
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS barbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                duration_minutes INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                barber_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'محجوز',
                total_price REAL NOT NULL,
                FOREIGN KEY(customer_id) REFERENCES customers(id),
                FOREIGN KEY(barber_id) REFERENCES barbers(id)
            );

            CREATE TABLE IF NOT EXISTS appointment_services (
                appointment_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                FOREIGN KEY(appointment_id) REFERENCES appointments(id),
                FOREIGN KEY(service_id) REFERENCES services(id)
            );
            """
        )
        self.conn.commit()

    def _seed_defaults(self):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM services")
        if c.fetchone()[0] == 0:
            defaults = [
                ("قصة شعر", 50, 30),
                ("حلاقة دقن", 30, 20),
                ("شعر ودقن", 70, 45),
                ("فوطة سخنة", 20, 10),
                ("شعر ودقن وفوطة سخنة", 85, 55),
                ("صبغة شعر", 100, 40),
            ]
            c.executemany(
                "INSERT INTO services (name, price, duration_minutes) VALUES (?,?,?)",
                defaults,
            )
        c.execute("SELECT COUNT(*) FROM barbers")
        if c.fetchone()[0] == 0:
            c.executemany(
                "INSERT INTO barbers (name) VALUES (?)",
                [("أحمد",), ("محمود",), ("كريم",)],
            )
        self.conn.commit()

    # ----------------------------------------------------------- customers
    def register_customer(self, name, phone, password):
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO customers (name, phone, password) VALUES (?,?,?)",
            (name, phone, password),
        )
        self.conn.commit()
        return c.lastrowid

    def login_customer(self, phone, password):
        c = self.conn.cursor()
        c.execute(
            "SELECT id, name, phone FROM customers WHERE phone=? AND password=?",
            (phone, password),
        )
        return c.fetchone()

    def phone_exists(self, phone):
        c = self.conn.cursor()
        c.execute("SELECT id FROM customers WHERE phone=?", (phone,))
        return c.fetchone() is not None

    # -------------------------------------------------------------- lookups
    def get_services(self):
        c = self.conn.cursor()
        c.execute("SELECT id, name, price, duration_minutes FROM services")
        return c.fetchall()

    def get_barbers(self):
        c = self.conn.cursor()
        c.execute("SELECT id, name FROM barbers")
        return c.fetchall()

    # ----------------------------------------------------------- schedule
    def get_booked_slots(self, barber_id, date):
        c = self.conn.cursor()
        c.execute(
            "SELECT time FROM appointments WHERE barber_id=? AND date=? AND status='محجوز'",
            (barber_id, date),
        )
        return {row[0] for row in c.fetchall()}

    def get_available_slots(self, barber_id, date):
        booked = self.get_booked_slots(barber_id, date)
        return [s for s in self.ALL_SLOTS if s not in booked]

    # -------------------------------------------------------- appointments
    def create_appointment(self, customer_id, barber_id, date, time_, service_ids, total_price):
        c = self.conn.cursor()
        c.execute(
            """INSERT INTO appointments (customer_id, barber_id, date, time, total_price)
               VALUES (?,?,?,?,?)""",
            (customer_id, barber_id, date, time_, total_price),
        )
        appt_id = c.lastrowid
        c.executemany(
            "INSERT INTO appointment_services (appointment_id, service_id) VALUES (?,?)",
            [(appt_id, sid) for sid in service_ids],
        )
        self.conn.commit()
        return appt_id

    def get_customer_appointments(self, customer_id):
        c = self.conn.cursor()
        c.execute(
            """SELECT a.id, b.name, a.date, a.time, a.status, a.total_price
               FROM appointments a
               JOIN barbers b ON a.barber_id = b.id
               WHERE a.customer_id=?
               ORDER BY a.date, a.time""",
            (customer_id,),
        )
        return c.fetchall()

    def cancel_appointment(self, appointment_id):
        c = self.conn.cursor()
        c.execute("UPDATE appointments SET status='ملغي' WHERE id=?", (appointment_id,))
        self.conn.commit()

    def get_all_appointments(self, date=None):
        c = self.conn.cursor()
        if date:
            c.execute(
                """SELECT a.id, c.name, c.phone, b.name, a.date, a.time, a.status, a.total_price
                   FROM appointments a
                   JOIN customers c ON a.customer_id = c.id
                   JOIN barbers b ON a.barber_id = b.id
                   WHERE a.date=?
                   ORDER BY a.time""",
                (date,),
            )
        else:
            c.execute(
                """SELECT a.id, c.name, c.phone, b.name, a.date, a.time, a.status, a.total_price
                   FROM appointments a
                   JOIN customers c ON a.customer_id = c.id
                   JOIN barbers b ON a.barber_id = b.id
                   ORDER BY a.date, a.time"""
            )
        return c.fetchall()

    def close(self):
        self.conn.close()
