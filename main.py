# -*- coding: utf-8 -*-
"""
main.py
HOT FOTA - سيستم إدارة صالون حلاقة (Dark Mode) - واجهة رسومية Tkinter
تشغيل السيستم:  python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import webbrowser

from database import Database
from models import Cart, Service
from ai_assistant import SmartAssistant

# --------------------------------------------------------- روابط السوشيال ميديا
# غيّر اللينكات دي بروابط صفحاتك الحقيقية. لو مش عايز أيقونة معينة تظهر،
# احذف السطر بتاعها من الـ dict وخلاص.
SOCIAL_LINKS = {
    "📘": "https://facebook.com/hotfota",          # فيسبوك
    "📸": "https://instagram.com/hotfota",          # إنستجرام
    "🟢": "https://wa.me/201000000000",             # واتساب (حط رقمك بصيغة دولية بدون +)
    "🎵": "https://tiktok.com/@hotfota",            # تيك توك
}

# ----------------------------------------------------------------- الألوان
BG = "#121212"          # خلفية الشاشة الرئيسية
PANEL = "#1c1c1c"        # خلفية البانلز/التبويبات
CARD = "#242424"        # خلفية الليست بوكس / الجداول / الحقول
GOLD = "#d4af37"        # لون ذهبي (موس/شفرة) - اللون المميز
GOLD_DARK = "#b8952e"
RED = "#c0392b"         # أحمر عمود الحلاق التقليدي
BLUE = "#2f5fa8"        # أزرق عمود الحلاق التقليدي
TEXT = "#f2f2f2"
MUTED = "#9e9e9e"
SUCCESS = "#1e7d32"
DANGER = "#8b2f2f"

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_H2 = ("Segoe UI", 13, "bold")
FONT_NORMAL = ("Segoe UI", 11)
FONT_SMALL_ITALIC = ("Segoe UI", 10, "italic")

BARBER_DIVIDER = "✂️ 🪒 💈 ♨️ 🧴 💇"


class BarbershopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🪒 HOT FOTA | صالون حلاقة 💈")
        self.geometry("820x600")
        self.configure(bg=BG)

        self.db = Database()
        self.assistant = SmartAssistant()
        self.cart = Cart()
        self.customer = None  # (id, name, phone) بعد تسجيل الدخول
        self.services_map = {}  # id -> Service

        self._setup_theme()
        self._build_ui()
        self._refresh_services_list()
        self._refresh_barbers_combo()

    # ------------------------------------------------------------- الثيم الداكن
    def _setup_theme(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=PANEL,
            foreground=TEXT,
            padding=(16, 10),
            font=("Segoe UI", 11, "bold"),
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", GOLD)],
            foreground=[("selected", "#141414")],
        )

        style.configure(
            "Treeview",
            background=CARD,
            fieldbackground=CARD,
            foreground=TEXT,
            rowheight=26,
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=PANEL,
            foreground=GOLD,
            font=("Segoe UI", 11, "bold"),
        )
        style.map("Treeview", background=[("selected", GOLD)], foreground=[("selected", "#141414")])

        style.configure(
            "TCombobox",
            fieldbackground=CARD,
            background=CARD,
            foreground=TEXT,
            arrowcolor=GOLD,
        )
        self.option_add("*TCombobox*Listbox.background", CARD)
        self.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.option_add("*TCombobox*Listbox.selectBackground", GOLD)
        self.option_add("*TCombobox*Listbox.selectForeground", "#141414")

    def _label(self, parent, text, font=FONT_NORMAL, fg=TEXT, bg=PANEL, **kw):
        return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kw)

    def _button(self, parent, text, command, bg=GOLD, fg="#141414", width=None, **kw):
        return tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg,
            activebackground=GOLD_DARK, activeforeground="#141414",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=8, pady=4,
            width=width, cursor="hand2", **kw,
        )

    def _entry(self, parent, width=25, show=None):
        return tk.Entry(
            parent, width=width, bg=CARD, fg=TEXT, insertbackground=TEXT,
            relief="flat", show=show, font=FONT_NORMAL,
        )

    def _listbox(self, parent, height=10, width=40):
        return tk.Listbox(
            parent, height=height, width=width, bg=CARD, fg=TEXT,
            selectbackground=GOLD, selectforeground="#141414",
            relief="flat", font=FONT_NORMAL, highlightthickness=0,
        )

    def _frame(self, parent, bg=PANEL):
        return tk.Frame(parent, bg=bg)

    # ------------------------------------------------------------- UI شكل عام
    def _build_ui(self):
        header = self._frame(self, bg=PANEL)
        header.pack(fill="x")
        self._label(header, "🪒  HOT  FOTA  💈", font=FONT_TITLE, fg=GOLD, bg=PANEL).pack(pady=(10, 0))
        self._label(header, BARBER_DIVIDER, font=("Segoe UI", 12), fg=MUTED, bg=PANEL).pack(pady=(0, 8))

        self.status_var = tk.StringVar(value="🔒 لسه ما سجلتش دخول")
        status_bar = self._label(self, "", font=("Segoe UI", 10), fg=TEXT, bg="#0d0d0d", anchor="e",
                                  textvariable=self.status_var)
        status_bar.pack(fill="x", ipady=4)

        self._build_social_footer()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_login = self._frame(self.notebook)
        self.tab_shop = self._frame(self.notebook)
        self.tab_booking = self._frame(self.notebook)
        self.tab_my_appts = self._frame(self.notebook)
        self.tab_admin = self._frame(self.notebook)

        self.notebook.add(self.tab_login, text="🔑 تسجيل الدخول")
        self.notebook.add(self.tab_shop, text="✂️ الخدمات والسلة")
        self.notebook.add(self.tab_booking, text="📅 الحجز")
        self.notebook.add(self.tab_my_appts, text="🗓 مواعيدي")
        self.notebook.add(self.tab_admin, text="💈 إدارة الصالون")

        self._build_login_tab()
        self._build_shop_tab()
        self._build_booking_tab()
        self._build_my_appts_tab()
        self._build_admin_tab()

    # -------------------------------------------------------- فوتر السوشيال ميديا
    def _build_social_footer(self):
        footer = self._frame(self, bg="#0d0d0d")
        footer.pack(fill="x", side="bottom")

        self._label(footer, "تابعونا:", font=("Segoe UI", 10), fg=MUTED, bg="#0d0d0d").pack(
            side="right", padx=(0, 8), pady=8
        )

        for icon, url in SOCIAL_LINKS.items():
            lbl = tk.Label(
                footer, text=icon, font=("Segoe UI Emoji", 16), fg=TEXT, bg="#0d0d0d",
                cursor="hand2",
            )
            lbl.pack(side="right", padx=6, pady=6)
            lbl.bind("<Button-1>", lambda e, link=url: self._open_social_link(link))
            lbl.bind("<Enter>", lambda e, w=lbl: w.config(fg=GOLD))
            lbl.bind("<Leave>", lambda e, w=lbl: w.config(fg=TEXT))

    def _open_social_link(self, url):
        try:
            webbrowser.open(url)
        except Exception:
            messagebox.showerror("خطأ", "معرفناش نفتح الرابط، تأكد إن عندك اتصال بالإنترنت")

    # -------------------------------------------------------- تسجيل الدخول
    def _build_login_tab(self):
        frame = self.tab_login
        self._label(frame, "💈 تسجيل دخول / حساب جديد", font=FONT_TITLE, fg=GOLD).pack(pady=15)

        form = self._frame(frame)
        form.pack(pady=10)

        self._label(form, "👤 الاسم (لو حساب جديد):").grid(row=0, column=0, sticky="e", padx=5, pady=8)
        self.reg_name = self._entry(form)
        self.reg_name.grid(row=0, column=1, padx=5, pady=8)

        self._label(form, "📱 رقم الموبايل:").grid(row=1, column=0, sticky="e", padx=5, pady=8)
        self.reg_phone = self._entry(form)
        self.reg_phone.grid(row=1, column=1, padx=5, pady=8)

        self._label(form, "🔒 كلمة السر:").grid(row=2, column=0, sticky="e", padx=5, pady=8)
        self.reg_password = self._entry(form, show="*")
        self.reg_password.grid(row=2, column=1, padx=5, pady=8)

        btns = self._frame(frame)
        btns.pack(pady=15)
        self._button(btns, "🪒 تسجيل حساب جديد", self._do_register, width=18).grid(row=0, column=0, padx=5)
        self._button(btns, "✂️ دخول", self._login, width=18).grid(row=0, column=1, padx=5)
        self._button(btns, "🚪 تسجيل خروج", self._logout, bg=DANGER, fg=TEXT, width=18).grid(row=0, column=2, padx=5)

    def _do_register(self):
        name = self.reg_name.get().strip()
        phone = self.reg_phone.get().strip()
        password = self.reg_password.get().strip()
        if not name or not phone or not password:
            messagebox.showwarning("تنبيه", "من فضلك املأ كل البيانات")
            return
        if self.db.phone_exists(phone):
            messagebox.showwarning("تنبيه", "الرقم ده مسجل قبل كده، جرب تسجيل الدخول")
            return
        cid = self.db.register_customer(name, phone, password)
        self.customer = (cid, name, phone)
        self._on_login_success()

    def _login(self):
        phone = self.reg_phone.get().strip()
        password = self.reg_password.get().strip()
        row = self.db.login_customer(phone, password)
        if row:
            self.customer = row
            self._on_login_success()
        else:
            messagebox.showerror("خطأ", "بيانات الدخول غلط")

    def _logout(self):
        self.customer = None
        self.cart.clear()
        self.status_var.set("🔒 لسه ما سجلتش دخول")
        self._refresh_cart_view()

    def _on_login_success(self):
        self.status_var.set(f"✅ مسجل دخول: {self.customer[1]}  |  📱 {self.customer[2]}")
        messagebox.showinfo("أهلاً بيك", f"🪒 أهلاً بيك في HOT FOTA يا {self.customer[1]}!")
        self._refresh_my_appointments()

    def _require_login(self) -> bool:
        if self.customer is None:
            messagebox.showwarning("تنبيه", "لازم تسجل دخول الأول")
            self.notebook.select(self.tab_login)
            return False
        return True

    # ------------------------------------------------------- الخدمات والسلة
    def _build_shop_tab(self):
        frame = self.tab_shop
        left = self._frame(frame)
        left.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        right = self._frame(frame)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self._label(left, "✂️ الخدمات المتاحة", font=FONT_H2, fg=GOLD).pack()
        self.services_listbox = self._listbox(left, height=15, width=40)
        self.services_listbox.pack(pady=8)
        self._button(left, "➕ أضف للسلة", self._add_to_cart).pack(pady=5)

        self._label(right, "🧺 السلة (الخدمات المختارة)", font=FONT_H2, fg=GOLD).pack()
        self.cart_listbox = self._listbox(right, height=10, width=40)
        self.cart_listbox.pack(pady=8)
        self._button(right, "🗑 احذف المختار من السلة", self._remove_from_cart, bg=DANGER, fg=TEXT).pack(pady=3)
        self._button(right, "🧹 تفريغ السلة", self._clear_cart, bg=CARD, fg=TEXT).pack(pady=3)

        self.total_var = tk.StringVar(value="💰 الإجمالي: 0 ج.م")
        self._label(right, "", textvariable=self.total_var, font=FONT_H2, fg=GOLD).pack(pady=12)

        self.ai_hint_var = tk.StringVar(value="")
        self._label(right, "", textvariable=self.ai_hint_var, font=FONT_SMALL_ITALIC, fg=MUTED,
                     wraplength=300, justify="right").pack(pady=5)

    def _refresh_services_list(self):
        self.services_listbox.delete(0, tk.END)
        self.services_map = {}
        for sid, name, price, duration in self.db.get_services():
            svc = Service(sid, name, price, duration)
            self.services_map[sid] = svc
            self.services_listbox.insert(tk.END, "  🪒  " + str(svc))
        self._service_order = list(self.services_map.keys())

    def _add_to_cart(self):
        sel = self.services_listbox.curselection()
        if not sel:
            return
        sid = self._service_order[sel[0]]
        self.cart.add_service(self.services_map[sid])
        self._refresh_cart_view()

    def _remove_from_cart(self):
        sel = self.cart_listbox.curselection()
        if not sel:
            return
        service = self.cart.items[sel[0]]
        self.cart.remove_service(service.id)
        self._refresh_cart_view()

    def _clear_cart(self):
        self.cart.clear()
        self._refresh_cart_view()

    def _refresh_cart_view(self):
        self.cart_listbox.delete(0, tk.END)
        for line in self.cart.summary_lines():
            self.cart_listbox.insert(tk.END, "  ✂️  " + line)
        self.total_var.set(
            f"💰 الإجمالي: {self.cart.total_price:.0f} ج.م  |  ⏱ الوقت المتوقع: {self.cart.total_duration} دقيقة"
        )
        self.ai_hint_var.set("💈 " + self.assistant.suggest_for_cart(self.cart.service_names()))

    # ------------------------------------------------------------- الحجز
    def _build_booking_tab(self):
        frame = self.tab_booking
        self._label(frame, "📅 احجز ميعادك", font=FONT_TITLE, fg=GOLD).pack(pady=15)

        form = self._frame(frame)
        form.pack(pady=5)

        self._label(form, "💈 اختار الحلاق:").grid(row=0, column=0, sticky="e", padx=5, pady=8)
        self.barber_combo = ttk.Combobox(form, state="readonly", width=25)
        self.barber_combo.grid(row=0, column=1, padx=5, pady=8)
        self.barber_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_slots())

        self._label(form, "🗓 التاريخ (YYYY-MM-DD):").grid(row=1, column=0, sticky="e", padx=5, pady=8)
        self.date_entry = self._entry(form, width=27)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=1, column=1, padx=5, pady=8)
        self._button(form, "🔍 عرض المواعيد الفاضية", self._refresh_slots).grid(row=1, column=2, padx=5)

        self._label(frame, "⏰ المواعيد الفاضية:", font=FONT_H2, fg=GOLD).pack(pady=(15, 0))
        self.slots_listbox = self._listbox(frame, height=8, width=20)
        self.slots_listbox.pack(pady=8)

        self.slot_hint_var = tk.StringVar(value="")
        self._label(frame, "", textvariable=self.slot_hint_var, font=FONT_SMALL_ITALIC, fg=MUTED).pack()

        self._button(frame, "✅ أكّد الحجز", self._confirm_booking, bg=SUCCESS, fg=TEXT).pack(pady=18, ipadx=10, ipady=4)

    def _refresh_barbers_combo(self):
        self.barbers = self.db.get_barbers()
        self.barber_combo["values"] = [f"{bid} - 💈 {name}" for bid, name in self.barbers]
        if self.barbers:
            self.barber_combo.current(0)

    def _selected_barber_id(self):
        if not self.barber_combo.get():
            return None
        return int(self.barber_combo.get().split(" - ")[0])

    def _refresh_slots(self):
        barber_id = self._selected_barber_id()
        d = self.date_entry.get().strip()
        if not barber_id or not d:
            return
        slots = self.db.get_available_slots(barber_id, d)
        self.slots_listbox.delete(0, tk.END)
        for s in slots:
            self.slots_listbox.insert(tk.END, "  ⏰  " + s)
        self.slot_hint_var.set("💈 " + self.assistant.recommend_time(slots))

    def _confirm_booking(self):
        if not self._require_login():
            return
        if self.cart.is_empty:
            messagebox.showwarning("تنبيه", "السلة فاضية، اختار خدمة الأول من تبويب (الخدمات والسلة)")
            return
        barber_id = self._selected_barber_id()
        d = self.date_entry.get().strip()
        sel = self.slots_listbox.curselection()
        if not barber_id or not d or not sel:
            messagebox.showwarning("تنبيه", "اختار الحلاق والتاريخ والميعاد الأول")
            return
        time_ = self.slots_listbox.get(sel[0]).replace("⏰", "").strip()

        service_ids = [s.id for s in self.cart.items]
        total = self.cart.total_price
        self.db.create_appointment(self.customer[0], barber_id, d, time_, service_ids, total)

        messagebox.showinfo("تم الحجز", f"🪒 تم حجز الميعاد بنجاح يوم {d} الساعة {time_}\n💰 الإجمالي: {total:.0f} ج.م")
        self.cart.clear()
        self._refresh_cart_view()
        self._refresh_slots()
        self._refresh_my_appointments()
        self.notebook.select(self.tab_my_appts)

    # -------------------------------------------------------------- مواعيدي
    def _build_my_appts_tab(self):
        frame = self.tab_my_appts
        self._label(frame, "🗓 مواعيدي المحجوزة", font=FONT_TITLE, fg=GOLD).pack(pady=15)

        columns = ("id", "barber", "date", "time", "status", "price")
        self.my_appts_tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        headers = {"id": "رقم", "barber": "الحلاق", "date": "التاريخ", "time": "الوقت",
                   "status": "الحالة", "price": "السعر"}
        for col in columns:
            self.my_appts_tree.heading(col, text=headers[col])
            self.my_appts_tree.column(col, width=110, anchor="center")
        self.my_appts_tree.pack(pady=10, fill="both", expand=True, padx=10)

        btns = self._frame(frame)
        btns.pack(pady=5)
        self._button(btns, "🔄 تحديث", self._refresh_my_appointments).pack(side="left", padx=10)
        self._button(btns, "❌ إلغاء الميعاد المختار", self._cancel_selected_appointment, bg=DANGER, fg=TEXT).pack(side="left")

    def _refresh_my_appointments(self):
        for row in self.my_appts_tree.get_children():
            self.my_appts_tree.delete(row)
        if self.customer is None:
            return
        for appt in self.db.get_customer_appointments(self.customer[0]):
            aid, barber, d, t, status, price = appt
            self.my_appts_tree.insert("", tk.END, values=(aid, barber, d, t, status, f"{price:.0f}"))

    def _cancel_selected_appointment(self):
        sel = self.my_appts_tree.selection()
        if not sel:
            return
        values = self.my_appts_tree.item(sel[0], "values")
        appt_id = int(values[0])
        self.db.cancel_appointment(appt_id)
        self._refresh_my_appointments()
        self._refresh_slots()

    # ------------------------------------------------------------- الإدارة
    def _build_admin_tab(self):
        frame = self.tab_admin
        self._label(frame, "💈 إدارة الصالون - كل الحجوزات", font=FONT_TITLE, fg=GOLD).pack(pady=15)

        top = self._frame(frame)
        top.pack(pady=5)
        self._label(top, "🗓 فلترة بالتاريخ (اختياري):").grid(row=0, column=0, padx=5)
        self.admin_date_entry = self._entry(top, width=15)
        self.admin_date_entry.grid(row=0, column=1, padx=5)
        self._button(top, "🔍 عرض", self._refresh_admin_view).grid(row=0, column=2, padx=5)
        self._button(top, "📋 عرض الكل", lambda: self._refresh_admin_view(all_=True)).grid(row=0, column=3, padx=5)

        columns = ("id", "customer", "phone", "barber", "date", "time", "status", "price")
        self.admin_tree = ttk.Treeview(frame, columns=columns, show="headings", height=14)
        headers = {"id": "رقم", "customer": "العميل", "phone": "الموبايل", "barber": "الحلاق",
                   "date": "التاريخ", "time": "الوقت", "status": "الحالة", "price": "السعر"}
        for col in columns:
            self.admin_tree.heading(col, text=headers[col])
            self.admin_tree.column(col, width=90, anchor="center")
        self.admin_tree.pack(pady=10, fill="both", expand=True, padx=10)

    def _refresh_admin_view(self, all_=False):
        for row in self.admin_tree.get_children():
            self.admin_tree.delete(row)
        d = None if all_ else (self.admin_date_entry.get().strip() or None)
        for appt in self.db.get_all_appointments(d):
            aid, cname, phone, barber, dte, t, status, price = appt
            self.admin_tree.insert("", tk.END, values=(aid, cname, phone, barber, dte, t, status, f"{price:.0f}"))


if __name__ == "__main__":
    app = BarbershopApp()
    app.mainloop()
