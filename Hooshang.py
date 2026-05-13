import sys
import os
import requests
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QLineEdit, QTextEdit, QRadioButton, QFrame,
    QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFontDatabase, QFont

class HooshangDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("داشبورد هوشنگ")
        self.setGeometry(150, 150, 600, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.load_font()          # بارگذاری فونت وزیر
        self.init_ui()
        self.apply_dark_theme()

        self.is_dragging = False
        self.start_pos = QPoint(0, 0)

    def load_font(self):
        """دانلود و ثبت فونت وزیرمتن (در صورت نیاز)"""
        font_filename = "Vazirmatn-FD-NL-Regular.ttf"
        font_path = os.path.join(os.path.dirname(__file__), font_filename)

        if not os.path.exists(font_path):
            # لینک مستقیم فایل فونت از همان CDN
            url = "https://lib.arvancloud.ir/vazir-font/33.003/Farsi-Digits-Non-Latin/Vazirmatn-FD-NL-Regular.ttf"
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                with open(font_path, 'wb') as f:
                    f.write(response.content)
            except Exception as e:
                print(f"خطا در دانلود فونت: {e}")
                return

        # ثبت فونت در برنامه
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print("ثبت فونت با خطا مواجه شد")
        else:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                self.font_family = font_families[0]  # معمولاً 'Vazirmatn FD NL'
            else:
                self.font_family = "Vazirmatn FD NL"

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # هدر
        header_frame = QFrame()
        header = QHBoxLayout(header_frame)
        header.setContentsMargins(15, 10, 15, 10)

        self.dark_btn = QPushButton("🌙")
        self.light_btn = QPushButton("☀️")
        self.close_btn = QPushButton("❌")
        self.rgb_label = QLabel("به هوشنگ خوش اومدی!")
        self.rgb_label.setAlignment(Qt.AlignCenter)

        for btn in [self.dark_btn, self.light_btn, self.close_btn]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedWidth(40)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.2);
                    border-radius: 20px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.3);
                }
            """)

        self.dark_btn.clicked.connect(self.apply_dark_theme)
        self.light_btn.clicked.connect(self.apply_light_theme)
        self.close_btn.clicked.connect(self.close)

        header.addWidget(self.dark_btn)
        header.addWidget(self.light_btn)
        header.addWidget(self.rgb_label, stretch=1)
        header.addWidget(self.close_btn)

        # درس‌ها
        subject_frame = QFrame()
        subject_grid = QGridLayout(subject_frame)
        subject_grid.setSpacing(10)

        self.subject_buttons = []
        subjects = ["اجتماعی", "فارسی", "علوم", "عربی", "هدیه", "ریاضی", "قرآن", "زبان"]
        for i, subject in enumerate(subjects):
            rb = QRadioButton(f"  {subject}")
            rb.setCursor(Qt.PointingHandCursor)
            self.subject_buttons.append(rb)
            subject_grid.addWidget(rb, i // 4, i % 4)
        self.subject_buttons[0].setChecked(True)

        # ورودی
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)

        self.time_have = QLineEdit()
        self.time_have.setPlaceholderText("چقدر وقت داری برای درس خوندن؟ (ساعت)")
        self.lesson_count = QLineEdit()
        self.lesson_count.setPlaceholderText("چند تا درس باید بخونی؟")

        for inp in [self.time_have, self.lesson_count]:
            inp.setMinimumHeight(45)
            input_layout.addWidget(inp)

        # خروجی
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        output_frame = QFrame()
        output_layout = QVBoxLayout(output_frame)

        self.log_output = QTextEdit()
        self.log_output.setPlaceholderText("📜 نتیجه برنامه‌ریزی اینجا نمایش داده می‌شود...")
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(200)
        output_layout.addWidget(self.log_output)

        scroll.setWidget(output_frame)

        # دکمه‌ها
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("🚀 شروع برنامه‌ریزی")
        self.export_btn = QPushButton("💾 ذخیره برنامه")
        self.clear_btn = QPushButton("🗑️ پاک کردن")

        for btn in [self.start_btn, self.export_btn, self.clear_btn]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(50)
            button_layout.addWidget(btn)

        self.start_btn.clicked.connect(self.generate_study_plan)
        self.export_btn.clicked.connect(self.export_study_plan)
        self.clear_btn.clicked.connect(self.clear_output)

        # افزودن به چیدمان کلی
        self.main_layout.addWidget(header_frame)
        self.main_layout.addWidget(subject_frame)
        self.main_layout.addWidget(input_frame)
        self.main_layout.addWidget(scroll)
        self.main_layout.addLayout(button_layout)

        self.setLayout(self.main_layout)

    # ========== Mouse events for window dragging ==========
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.start_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPos() - self.start_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            event.accept()
    # =====================================================

    def apply_dark_theme(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #1a1a2e;
                color: #e0e0e0;
                font-family: '{getattr(self, "font_family", "sans-serif")}';
            }}
            QLineEdit {{
                background-color: #16213e;
                border: 2px solid #0f3460;
                color: #fff;
                padding: 8px;
                border-radius: 12px;
                font-size: 14px;
            }}
            QTextEdit {{
                background-color: #16213e;
                border: 2px solid #0f3460;
                color: #fff;
                padding: 10px;
                border-radius: 12px;
                font-size: 14px;
            }}
            QPushButton {{
                background-color: #0f3460;
                color: white;
                border-radius: 12px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #16213e;
            }}
            QRadioButton {{
                color: #e0e0e0;
                padding: 8px;
                font-size: 14px;
            }}
            QRadioButton::indicator {{
                width: 15px;
                height: 15px;
            }}
            QRadioButton::indicator:checked {{
                background-color: #0f3460;
                border: 2px solid #e0e0e0;
                border-radius: 7px;
            }}
        """)

    def apply_light_theme(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #f0f2f5;
                color: #2d3436;
                font-family: '{getattr(self, "font_family", "sans-serif")}';
            }}
            QLineEdit {{
                background-color: white;
                border: 2px solid #dfe6e9;
                color: #2d3436;
                padding: 8px;
                border-radius: 12px;
                font-size: 14px;
            }}
            QTextEdit {{
                background-color: white;
                border: 2px solid #dfe6e9;
                color: #2d3436;
                padding: 10px;
                border-radius: 12px;
                font-size: 14px;
            }}
            QPushButton {{
                background-color: #6c5ce7;
                color: white;
                border-radius: 12px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #5f48e5;
            }}
            QRadioButton {{
                color: #2d3436;
                padding: 8px;
                font-size: 14px;
            }}
            QRadioButton::indicator {{
                width: 15px;
                height: 15px;
            }}
            QRadioButton::indicator:checked {{
                background-color: #6c5ce7;
                border: 2px solid #2d3436;
                border-radius: 7px;
            }}
        """)

    def generate_study_plan(self):
        subject = next((rb.text().strip() for rb in self.subject_buttons if rb.isChecked()), "درس")
        time_have = self.time_have.text()
        lesson_count = self.lesson_count.text()

        try:
            time_have_float = float(time_have)
            lesson_count_int = int(lesson_count)
        except ValueError:
            self.log_output.setPlainText("❌ لطفاً زمان و تعداد درس را به‌صورت عدد وارد کن.")
            return

        if lesson_count_int <= 0 or time_have_float <= 0:
            self.log_output.setPlainText("❌ مقدار زمان و تعداد درس باید بیشتر از صفر باشد.")
            return

        break_ratio = 0.15
        total_lessons = lesson_count_int
        total_breaks = lesson_count_int - 1
        unit_blocks = total_lessons + (total_breaks * break_ratio)
        unit_time = time_have_float / unit_blocks

        lesson_time = unit_time
        break_time = unit_time * break_ratio

        plan = f"📌 برنامه‌ریزی برای درس: {subject}\n"
        plan += f"\n📝 تعداد درس‌ها: {lesson_count_int}"
        plan += f"\n🕒 کل زمان مطالعه: {time_have_float:.2f} ساعت\n"
        plan += f"\n📋 زمان‌بندی پیشنهادی:\n"

        total_used = 0
        for i in range(lesson_count_int):
            plan += f"  📖 درس {i+1}: {lesson_time:.2f} ساعت\n"
            total_used += lesson_time
            if i < lesson_count_int - 1:
                plan += f"    ☕ استراحت: {break_time:.2f} ساعت\n"
                total_used += break_time

        plan += f"\n🔚 مجموع زمان (با استراحت): {total_used:.2f} ساعت\n"
        plan += "\n📚 نکات:\n"
        plan += "- محیط آرام برای مطالعه انتخاب کن.\n"
        plan += "- از تایمر استفاده کن (مثل تکنیک پومودورو).\n"
        plan += "- یادداشت‌برداری و مرور را فراموش نکن!\n"

        self.log_output.setPlainText(plan)

    def export_study_plan(self):
        if not self.log_output.toPlainText().strip():
            return

        study_plan = self.log_output.toPlainText()
        subject = next((rb.text().strip() for rb in self.subject_buttons if rb.isChecked()), "برنامه")

        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{subject}_{now}.txt"

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(study_plan)

    def clear_output(self):
        self.log_output.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HooshangDashboard()
    window.show()
    sys.exit(app.exec_())
