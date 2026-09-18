# -*- coding: utf-8 -*-
"""
models.py
الكلاسات الأساسية (OOP) لسيستم الحلاق:
Service, Customer, Barber, Cart, Appointment
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Service:
    """خدمة زي: قصة شعر / حلاقة دقن / فوطة سخنة ...الخ"""
    id: int
    name: str
    price: float
    duration_minutes: int

    def __str__(self):
        return f"{self.name} - {self.price:.0f} ج.م ({self.duration_minutes} دقيقة)"


@dataclass
class Customer:
    """العميل اللي بيستخدم السيستم (بياناته بتتخزن في قاعدة البيانات)"""
    id: int
    name: str
    phone: str


@dataclass
class Barber:
    """الحلاق اللي هيقدم الخدمة"""
    id: int
    name: str


class Cart:
    """
    عربة/سلة المشتريات (زي السوبر ماركت) بس للخدمات.
    العميل بيضيف خدمات فيها ويطلع السعر الإجمالي والوقت المتوقع.
    """

    def __init__(self):
        self.items: List[Service] = []

    def add_service(self, service: Service):
        self.items.append(service)

    def remove_service(self, service_id: int):
        self.items = [s for s in self.items if s.id != service_id]

    def clear(self):
        self.items.clear()

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0

    @property
    def total_price(self) -> float:
        return sum(s.price for s in self.items)

    @property
    def total_duration(self) -> int:
        return sum(s.duration_minutes for s in self.items)

    def service_names(self) -> List[str]:
        return [s.name for s in self.items]

    def summary_lines(self) -> List[str]:
        lines = [f"{s.name}  —  {s.price:.0f} ج.م" for s in self.items]
        return lines


@dataclass
class Appointment:
    """حجز/ميعاد لعميل عند حلاق معين في تاريخ ووقت معين"""
    id: int
    customer_name: str
    barber_name: str
    date: str
    time: str
    status: str
    total_price: float
