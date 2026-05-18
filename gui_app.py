import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QSystemTrayIcon, 
                             QMenu, QFrame, QTabWidget, QSpinBox, QListWidget, QListWidgetItem, QFileDialog, QMessageBox)
from PyQt6.QtGui import QIcon, QFont, QAction, QColor, QPainter, QPixmap
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
import qdarkstyle

# Ana dizinden main mantığını import ediyoruz
# main.py dosyasındaki sınıfı buraya uygun hale getireceğiz.

class AIStatusThread(QThread):
    """Arka planda AI durumunu kontrol edip UI'a bildiren thread"""
    status_updated = pyqtSignal(str)

    def __init__(self, orchestrator):
        super().__init__()
        self.orchestrator = orchestrator
        self.is_running = True

    def run(self):
        while self.is_running:
            # AI'nin hazırladığı hedef uygulamayı ve şu anki aktif pencereyi UI'a gönder
            target = getattr(self.orchestrator, 'prepared_target_exe', 'Hesaplanıyor...')
            active = getattr(self.orchestrator, 'current_active_window', 'Bilinmiyor')
            
            # HTML formatında daha şık ve düzenli bir görünüm
            display_text = (
                f"<div style='text-align: center; line-height: 1.2;'>"
                f"<span style='color: #888888; font-size: 11px;'>Gizlenecek Pencere:</span><br>"
                f"<span style='color: #FFB74D; font-size: 13px; font-weight: bold;'>{active}</span><br>"
                f"<br>"
                f"<span style='color: #888888; font-size: 11px;'>Kamuflaj Uygulaması:</span><br>"
                f"<span style='color: #00E676; font-size: 13px; font-weight: bold;'>{target}</span>"
                f"</div>"
            )
            self.status_updated.emit(display_text)
            self.msleep(2000)  # Her 2 saniyede bir UI'ı güncelle

import json
from config_manager import load_config, save_config

class ScannerThread(QThread):
    scan_completed = pyqtSignal(dict)
    scan_failed = pyqtSignal(str)

    def run(self):
        try:
            from app_scanner import AIAppScanner
            scanner = AIAppScanner()
            result = scanner.scan_with_ai()
            if result:
                self.scan_completed.emit(result)
            else:
                self.scan_failed.emit("Tarama sonucu boş veya AI bağlantısında hata oluştu.")
        except Exception as e:
            self.scan_failed.emit(str(e))

class ActivityHiderGUI(QMainWindow):
    def __init__(self, orchestrator):
        super().__init__()
        self.orchestrator = orchestrator
        self.config = load_config()
        
        self.setWindowTitle("Activity Hider - AI Panic Mode")
        self.setFixedSize(600, 500)
        
        self.init_ui()
        self.init_tray()

        self.ai_thread = AIStatusThread(self.orchestrator)
        self.ai_thread.status_updated.connect(self.update_ai_status)
        self.ai_thread.start()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.main_tab = QWidget()
        self.settings_tab = QWidget()
        
        self.tabs.addTab(self.main_tab, "Ana Ekran")
        self.tabs.addTab(self.settings_tab, "Ayarlar")
        
        self.init_main_tab()
        self.init_settings_tab()

    def init_main_tab(self):
        main_layout = QVBoxLayout(self.main_tab)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title_label = QLabel("ACTIVITY HIDER")
        title_font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #4CAF50;")
        main_layout.addWidget(title_label)

        sub_label = QLabel("AI-Powered Context Awareness")
        sub_font = QFont("Segoe UI", 10)
        sub_label.setFont(sub_font)
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_label.setStyleSheet("color: #AAAAAA; margin-bottom: 10px;")
        main_layout.addWidget(sub_label)

        status_frame = QFrame()
        status_frame.setStyleSheet("QFrame { background-color: #2A2A2A; border-radius: 10px; border: 1px solid #3A3A3A; }")
        status_layout = QVBoxLayout(status_frame)
        
        self.status_title = QLabel("Canlı Sistem Durumu:")
        self.status_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.status_title.setStyleSheet("color: #888888; border: none; background: transparent;")
        
        self.target_label = QLabel("Analiz ediliyor...")
        self.target_label.setFont(QFont("Segoe UI", 10))
        self.target_label.setStyleSheet("border: none; background: transparent;")
        self.target_label.setTextFormat(Qt.TextFormat.RichText)
        self.target_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.target_label.setWordWrap(True)
        self.target_label.setMinimumHeight(120)

        status_layout.addWidget(self.status_title)
        status_layout.addWidget(self.target_label)
        main_layout.addWidget(status_frame)

        hotkey_frame = QFrame()
        hotkey_layout = QHBoxLayout(hotkey_frame)
        hotkey_layout.setContentsMargins(0, 0, 0, 0)
        
        hotkey_title = QLabel("Panic Hotkey:")
        hotkey_title.setFont(QFont("Segoe UI", 10))
        hotkey_title.setStyleSheet("color: #CCCCCC;")
        
        self.hotkey_value = QLabel(self.orchestrator.hotkey.upper())
        self.hotkey_value.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.hotkey_value.setStyleSheet("color: #FF5252; background-color: #2A2A2A; padding: 5px 15px; border-radius: 5px;")
        
        hotkey_layout.addWidget(hotkey_title)
        hotkey_layout.addStretch()
        hotkey_layout.addWidget(self.hotkey_value)
        main_layout.addWidget(hotkey_frame)

        main_layout.addStretch()

        self.hide_btn = QPushButton("Hide to Tray")
        self.hide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hide_btn.setStyleSheet("QPushButton { background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 5px; font-weight: bold; } QPushButton:hover { background-color: #444444; }")
        self.hide_btn.clicked.connect(self.hide)
        main_layout.addWidget(self.hide_btn)

    def init_settings_tab(self):
        settings_layout = QVBoxLayout(self.settings_tab)
        
        # Limit ayarı
        limit_layout = QHBoxLayout()
        limit_label = QLabel("Aynı Kamuflajı Tekrar Kullanma Limiti:")
        self.limit_spinbox = QSpinBox()
        self.limit_spinbox.setMinimum(1)
        self.limit_spinbox.setMaximum(10)
        self.limit_spinbox.setValue(self.config.get("max_consecutive_uses", 2))
        
        limit_layout.addWidget(limit_label)
        limit_layout.addWidget(self.limit_spinbox)
        settings_layout.addLayout(limit_layout)
        
        # Havuz Yönetimi Başlığı
        pool_label = QLabel("Uygulama Havuzu Yöneticisi")
        pool_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        settings_layout.addWidget(pool_label)
        
        self.scan_btn = QPushButton("Yapay Zeka ile Sistemi Tara (Önerilenleri Bul)")
        self.scan_btn.clicked.connect(self.start_ai_scan)
        settings_layout.addWidget(self.scan_btn)
        
        self.app_list = QListWidget()
        self.app_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.load_app_pool_to_list()
        settings_layout.addWidget(self.app_list)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        self.add_app_btn = QPushButton("Manuel Uygulama Ekle")
        self.add_app_btn.clicked.connect(self.add_custom_app)
        
        self.remove_app_btn = QPushButton("Seçilenleri Sil")
        self.remove_app_btn.clicked.connect(self.remove_selected_app)
        
        self.clear_all_btn = QPushButton("Tümünü Temizle")
        self.clear_all_btn.clicked.connect(self.app_list.clear)
        
        btn_layout.addWidget(self.add_app_btn)
        btn_layout.addWidget(self.remove_app_btn)
        btn_layout.addWidget(self.clear_all_btn)
        settings_layout.addLayout(btn_layout)
        
        self.save_btn = QPushButton("Ayarları Kaydet")
        self.save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        self.save_btn.clicked.connect(self.save_settings)
        settings_layout.addWidget(self.save_btn)

    def load_app_pool_to_list(self):
        self.app_list.clear()
        try:
            with open("app_pool.json", "r", encoding="utf-8") as f:
                pool = json.load(f)
                for cat, apps in pool.items():
                    for app in apps:
                        item = QListWidgetItem(f"[{cat}] {app}")
                        item.setData(Qt.ItemDataRole.UserRole, (cat, app))
                        self.app_list.addItem(item)
        except Exception:
            pass

    def start_ai_scan(self):
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("Taranıyor, lütfen bekleyin...")
        self.scanner_thread = ScannerThread()
        self.scanner_thread.scan_completed.connect(self.on_scan_completed)
        self.scanner_thread.scan_failed.connect(self.on_scan_failed)
        self.scanner_thread.start()

    def on_scan_completed(self, result):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Yapay Zeka ile Sistemi Tara (Önerilenleri Bul)")
        self.load_app_pool_to_list()
        QMessageBox.information(self, "Başarılı", "Tarama tamamlandı! Yeni liste yüklendi.")

    def on_scan_failed(self, error):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Yapay Zeka ile Sistemi Tara (Önerilenleri Bul)")
        QMessageBox.warning(self, "Hata", f"Tarama başarısız oldu:\n{error}")

    def add_custom_app(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Uygulama Seç", "", "Executable Files (*.exe);;All Files (*)")
        if file_name:
            # Varsayılan olarak odaklanma kategorisine ekleyelim
            cat = "odaklanma_ve_calisma"
            item = QListWidgetItem(f"[{cat}] {file_name}")
            item.setData(Qt.ItemDataRole.UserRole, (cat, file_name))
            self.app_list.addItem(item)

    def remove_selected_app(self):
        for item in self.app_list.selectedItems():
            self.app_list.takeItem(self.app_list.row(item))

    def save_settings(self):
        self.config["max_consecutive_uses"] = self.limit_spinbox.value()
        save_config(self.config)
        
        new_pool = {"odaklanma_ve_calisma": [], "oyun_ve_eglence": []}
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            cat, app_path = item.data(Qt.ItemDataRole.UserRole)
            if cat not in new_pool:
                new_pool[cat] = []
            new_pool[cat].append(app_path)
            
        with open("app_pool.json", "w", encoding="utf-8") as f:
            json.dump(new_pool, f, indent=4, ensure_ascii=False)
            
        QMessageBox.information(self, "Kaydedildi", "Ayarlar ve uygulama havuzu başarıyla kaydedildi.")

    def create_tray_icon(self):
        """Basit bir kırmızı kalkan veya daire ikonu çizelim."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Arka plan dairesi
        painter.setBrush(QColor(40, 40, 40))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 60, 60)
        
        # İç daire (yeşil)
        painter.setBrush(QColor(76, 175, 80))
        painter.drawEllipse(16, 16, 32, 32)
        painter.end()
        
        return QIcon(pixmap)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.create_tray_icon())
        self.tray_icon.setToolTip("Activity Hider - AI Protection Active")
        
        tray_menu = QMenu()
        
        show_action = QAction("Arayüzü Göster", self)
        show_action.triggered.connect(self.show_normal)
        
        quit_action = QAction("Çıkış", self)
        quit_action.triggered.connect(self.quit_app)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Çift tıklayınca pencereyi aç
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_normal()

    def show_normal(self):
        self.show()
        self.activateWindow()

    def update_ai_status(self, target):
        self.target_label.setText(target)

    def closeEvent(self, event):
        # Pencereyi kapatınca çıkmak yerine gizle
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Activity Hider",
            "Uygulama arka planda çalışmaya devam ediyor.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def quit_app(self):
        self.ai_thread.is_running = False
        self.orchestrator.is_running = False
        self.tray_icon.hide()
        QApplication.quit()
        sys.exit()

def launch_gui(orchestrator):
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
    
    gui = ActivityHiderGUI(orchestrator)
    gui.show()
    
    return app.exec()
