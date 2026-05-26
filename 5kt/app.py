import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox,
    QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class CurrencyConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конвертер валют")
        self.setFixedSize(500, 450)
        
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #1a1a2e, stop:1 #16213e);
                color: #eeeeee;
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0f3460;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit {
                background: #0f3460;
                border: 1px solid #e94560;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #eeeeee;
            }
            QLineEdit:focus {
                border: 2px solid #e94560;
            }
            QComboBox {
                background: #0f3460;
                border: 1px solid #e94560;
                border-radius: 8px;
                padding: 6px 10px;
                min-width: 80px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #e94560;
                margin-right: 5px;
            }
            QPushButton {
                background: #e94560;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #ff6b8b;
            }
            QPushButton:pressed {
                background: #c73e54;
            }
            QLabel {
                color: #eeeeee;
            }
            #result_label {
                background: #0f3460;
                border-radius: 10px;
                padding: 15px;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        
        self.init_ui()
        self.load_currencies()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("💱 Конвертер валют")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        group = QGroupBox("Конвертация")
        grid = QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(QLabel("Сумма:"), 0, 0)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Введите сумму...")
        grid.addWidget(self.amount_input, 0, 1)
        
        grid.addWidget(QLabel("Из валюты:"), 1, 0)
        self.from_currency = QComboBox()
        grid.addWidget(self.from_currency, 1, 1)
        
        grid.addWidget(QLabel("В валюту:"), 2, 0)
        self.to_currency = QComboBox()
        grid.addWidget(self.to_currency, 2, 1)
        
        self.convert_btn = QPushButton("🔄 Конвертировать")
        self.convert_btn.clicked.connect(self.convert)
        grid.addWidget(self.convert_btn, 3, 0, 1, 2)
        
        group.setLayout(grid)
        layout.addWidget(group)
        
        self.refresh_btn = QPushButton("📊 Обновить курсы валют")
        self.refresh_btn.clicked.connect(self.refresh_rates)
        layout.addWidget(self.refresh_btn)
        
        self.result_label = QLabel("Здесь появится результат конвертации")
        self.result_label.setObjectName("result_label")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)
        
        self.rates_label = QLabel("Курсы загружаются...")
        self.rates_label.setAlignment(Qt.AlignCenter)
        self.rates_label.setWordWrap(True)
        layout.addWidget(self.rates_label)
        
        self.setLayout(layout)
    
    def load_currencies(self):
        try:
            response = requests.get("http://127.0.0.1:8000/currencies", timeout=5)
            if response.status_code == 200:
                currencies = response.json().get("currencies", [])
                self.from_currency.clear()
                self.to_currency.clear()
                self.from_currency.addItems(currencies)
                self.to_currency.addItems(currencies)
                self.refresh_rates()
            else:
                self.show_error("Не удалось загрузить список валют")
        except Exception as e:
            self.show_error(f"Нет соединения с сервером\nЗапустите server.py\nОшибка: {str(e)}")
    
    def refresh_rates(self):
        try:
            response = requests.get("http://127.0.0.1:8000/rates", timeout=5)
            if response.status_code == 200:
                data = response.json()
                rates = data.get("rates", {})
                
                rates_text = "💵 Текущие курсы (относительно USD):\n"
                for currency, rate in rates.items():
                    rates_text += f"  • {currency}: {rate:.4f}\n"
                
                if data.get("base"):
                    rates_text += f"\nБазовая валюта: {data['base']}"
                
                self.rates_label.setText(rates_text)
            else:
                self.rates_label.setText("Не удалось загрузить курсы")
        except Exception as e:
            self.rates_label.setText(f"Ошибка загрузки курсов: {str(e)}")
    
    def convert(self):
        try:
            amount = float(self.amount_input.text().strip())
            if amount <= 0:
                self.show_error("Сумма должна быть больше нуля")
                return
        except ValueError:
            self.show_error("Пожалуйста, введите корректное число")
            return
        
        from_curr = self.from_currency.currentText()
        to_curr = self.to_currency.currentText()
        
        if not from_curr or not to_curr:
            self.show_error("Пожалуйста, выберите валюты")
            return
        
        try:
            response = requests.get(
                "http://127.0.0.1:8000/convert",
                params={
                    "from_currency": from_curr,
                    "to_currency": to_curr,
                    "amount": amount
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                result_text = f"""
                ✨ Результат конвертации ✨
                
                {data['amount']} {data['from']} = 
                {data['converted_amount']} {data['to']}
                
                📈 Курс: 1 {data['from']} = {data['rate']} {data['to']}
                ℹ️ {data['timestamp']}
                """
                
                self.result_label.setText(result_text)
                
                self.result_label.setStyleSheet("""
                    background: #0f3460;
                    border-radius: 10px;
                    padding: 15px;
                    font-size: 18px;
                    font-weight: bold;
                    color: #4CAF50;
                """)
                
            else:
                error_detail = response.json().get("detail", "Неизвестная ошибка")
                self.show_error(error_detail)
                
        except requests.exceptions.ConnectionError:
            self.show_error("Нет соединения с сервером!\nЗапустите server.py")
        except Exception as e:
            self.show_error(f"Ошибка: {str(e)}")
    
    def show_error(self, message):
        self.result_label.setText(f"❌ Ошибка:\n{message}")
        self.result_label.setStyleSheet("""
            background: #0f3460;
            border-radius: 10px;
            padding: 15px;
            font-size: 16px;
            font-weight: bold;
            color: #ff6b6b;
        """)
        QMessageBox.warning(self, "Ошибка", message)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName("Currency Converter")
    window = CurrencyConverter()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()