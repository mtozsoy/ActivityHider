import pygetwindow as gw

class SystemMonitor:
    def __init__(self):
        # İşletim sisteminin kendi arka plan servislerini filtrelemek için bir yoksayma listesi
        self.ignore_list = ["Program Manager", "Settings", "Taskbar"]

    def get_active_context(self):
        """Şu an ekranda görünür olan pencerelerin başlıklarını listeler ve en öndekini vurgular."""
        active_windows = []
        foreground = "Bilinmiyor"
        
        try:
            # Kullanıcının tam şu an baktığı aktif pencere
            fw = gw.getActiveWindow()
            if fw and fw.title and fw.title not in self.ignore_list:
                foreground = fw.title
        except Exception:
            pass

        windows = gw.getAllWindows()
        
        for win in windows:
            # Sadece başlığı olan, ekranda görünür olan ve yoksayma listesinde olmayanları al
            if win.title and win.visible and win.width > 0:
                if win.title not in self.ignore_list and win.title != foreground:
                    active_windows.append(win.title)
                    
        return {
            "on_plandaki_aktif_pencere": foreground,
            "arkaplandaki_diger_pencereler": active_windows[:5] # Sadece üstteki 5 pencere yeterli
        }

# Test etmek için küçük bir blok
if __name__ == "__main__":
    monitor = SystemMonitor()
    suan_acik_olanlar = monitor.get_active_context()
    
    print("Yakalanan Pencereler:")
    for pencere in suan_acik_olanlar:
        print(f"- {pencere}")