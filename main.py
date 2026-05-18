import sys
import io
import ctypes

# Arayüz açılırken arkada açılan CMD ekranını gizle (SW_HIDE = 0)
hwnd = ctypes.windll.kernel32.GetConsoleWindow()
if hwnd:
    ctypes.windll.user32.ShowWindow(hwnd, 0)

# Windows terminal encoding sorununu çöz (cp1254 Türkçe karakterlerle crash oluyordu)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

import keyboard
import time
import win32gui
import win32con
import win32process
import os
import threading
from system_monitor import SystemMonitor
from ai_engine import DynamicProfiler
from gui_app import launch_gui


class BossKeyOrchestrator:
    def __init__(self, hotkey="f12"):
        self.hotkey = hotkey
        # Diğer dosyalarımızdaki sınıfları burada başlatıyoruz
        self.monitor = SystemMonitor()
        self.ai = DynamicProfiler()
        # Kendi process ID'mizi biliyoruz, böylece kendi pencerelerimizi atlayabiliriz
        self.own_pid = os.getpid()
        
        # Önceden hazırlanmış hedef uygulama
        self.prepared_target_exe = "explorer.exe"
        self.current_active_window = "Masaüstü"
        self.is_running = True
        
        # Arka planda sürekli ekranı izleyip karar hazırlayan beyin
        self.brain_thread = threading.Thread(target=self._background_brain_loop, daemon=True)
        self.brain_thread.start()

    def _background_brain_loop(self):
        """Arka planda sürekli çalışarak olası bir panik anı için önceden karar hazırlar."""
        while self.is_running:
            try:
                active_windows = self.monitor.get_active_context()
                if active_windows:
                    self.current_active_window = active_windows.get("on_plandaki_aktif_pencere", "Bilinmiyor")
                    karar = self.ai.get_decision(active_windows)
                    self.prepared_target_exe = karar.get("target_exe", "explorer.exe")
            except Exception:
                pass
            # Her 10 saniyede bir ekranı analiz edip silahı hazırda beklet
            time.sleep(10)

    def _get_all_visible_windows(self):
        """Win32 API ile tüm görünür, normal pencereleri yakalar."""
        windows = []

        def enum_callback(hwnd, _):
            # Pencere görünür mü?
            if not win32gui.IsWindowVisible(hwnd):
                return
            # Pencere minimize mi? (minimize olanları tekrar gizlemeye gerek yok)
            if win32gui.IsIconic(hwnd):
                return
            # Pencere başlığı var mı?
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return
            # Kendi pencerelerimizi (bu script'in penceresi) atla
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid == self.own_pid:
                    return
            except Exception:
                pass
            # Sistem pencerelerini atla
            skip_titles = ["Program Manager", "Taskbar", "Windows Input Experience",
                           "Windows Giriş Deneyimi", "MSCTFIME UI", "Default IME"]
            if title in skip_titles:
                return

            windows.append(hwnd)

        win32gui.EnumWindows(enum_callback, None)
        return windows

    def hide_all_windows(self):
        """Win32 API kullanarak tüm pencereleri minimize eder (küçültür)."""
        print("[!] Pencereler küçültülüyor...")
        windows = self._get_all_visible_windows()

        for hwnd in windows:
            try:
                title = win32gui.GetWindowText(hwnd)
                # SW_MINIMIZE ile pencereyi küçült (taskbar'da kalır, geri açılabilir)
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                print(f"    [-] Küçültüldü: {title}")
            except Exception:
                pass

        # Pencerelerin küçülmesi için çok kısa bir bekleme (hız için 0.1 sn)
        time.sleep(0.1)
        return windows

    def launch_target_app(self, exe_path):
        """Yapay zekanın seçtiği uygulamayı açar ve ön plana getirir."""
        try:
            print(f"[+] Hedef uygulama açılıyor: {exe_path}")
            # os.startfile yol boşluklarıyla sorun yaşamaz ve Windows'un doğal açma mekanizmasını kullanır
            os.startfile(exe_path)
            # Uygulamanın açılıp pencere oluşturmasını bekle
            time.sleep(2)
            # Yeni açılan pencereyi ön plana getir ve maximize et
            try:
                foreground = win32gui.GetForegroundWindow()
                if foreground:
                    win32gui.ShowWindow(foreground, win32con.SW_MAXIMIZE)
                    print(f"[+] Uygulama ön planda ve maximize edildi")
            except Exception:
                pass
        except FileNotFoundError:
            print(f"[!] Uygulama bulunamadı: {exe_path}")
        except Exception as e:
            print(f"[!] Uygulama açılamadı: {e}")

    def execute_panic_sequence(self):
        """Kısayola basıldığında HER ŞEYİ ANINDA YAPAR."""
        print("\n[!!!] PANİK MODU TETİKLENDİ - YILDIRIM HIZI [!!!]")

        # 1. Kaslar: Vakit kaybetmeden anında pencereleri KÜÇÜLT!
        self.hide_all_windows()

        # 2. Yeni uygulamayı aç (Arka plandaki yapay zekanın önceden hazırladığı silahı ateşle)
        target = self.prepared_target_exe
        print(f"[*] Hazırda Bekleyen AI Kararı Uygulanıyor: {target}")
        self.launch_target_app(target)
        self.ai.record_usage(target)
        
        print("[*] Operasyon tamamlandı. Ortalık temiz.")

    def start_listening(self):
        print(f"[*] Sistem devrede. Kısayol: {self.hotkey}")
        # Arka planda klavyeyi dinle (GUI'yi bloklamamak için)
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()

    def _listen_loop(self):
        # Oyunların veya anti-hile sistemlerinin global hook'ları engellemesine karşı
        # güvenilir bir polling (yoklama) döngüsü kullanıyoruz:
        while self.is_running:
            try:
                if keyboard.is_pressed(self.hotkey):
                    self.execute_panic_sequence()
                    # Aynı tuşa arka arkaya basılmasını (spam) önlemek için biraz bekle
                    time.sleep(1.5)
            except Exception:
                pass
            
            # CPU'yu yormamak için çok kısa bir bekleme
            time.sleep(0.05)

import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    if is_admin():
        app = BossKeyOrchestrator()
        app.start_listening()
        # GUI'yi başlat
        launch_gui(app)
    else:
        print("[!] Yönetici izinleri kontrol ediliyor...")
        print("[!] Valorant vb. uygulamaları açabilmek için program yönetici olarak yeniden başlatılıyor. Lütfen ekrandaki UAC iznini onaylayın.")
        # Programı yönetici izni (runas) ile tekrar başlat
        # Parametre 0: SW_HIDE (Arka plan CMD ekranını gizler)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 0)
