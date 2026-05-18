import os
import json
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv(override=True)  # .env dosyasındaki API anahtarını yükle

class DynamicProfiler:
    def __init__(self):
        # GitHub Models (OpenAI SDK) bağlantısını başlatıyoruz
        token = os.environ.get("GITHUB_API_KEY") or os.environ.get("GITHUB_TOKEN")
        
        if not token:
            raise ValueError("[!] GITHUB_API_KEY ortam değişkeni bulunamadı. Lütfen .env dosyasına ekleyin.")
        
        self.client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=token,
        )
        # Hız ve mantık için gpt-4o kullanıyoruz
        self.model = "gpt-4o"
        
        self.last_used_app = None
        self.consecutive_count = 0

    def record_usage(self, target_exe):
        """Kullanıcı panik tuşuna bastığında bu fonksiyon çağrılır ve sayacı günceller."""
        if target_exe == self.last_used_app:
            self.consecutive_count += 1
        else:
            self.last_used_app = target_exe
            self.consecutive_count = 1

    def get_decision(self, active_windows):
        """SystemMonitor'den gelen pencereleri alıp Llama 3.3 70B'ye sorar."""
        
        try:
            from config_manager import load_config
            config = load_config()
            limit = config.get("max_consecutive_uses", 2)
            
            blacklisted_app = None
            if self.consecutive_count >= limit and self.last_used_app:
                blacklisted_app = self.last_used_app

            with open("app_pool.json", "r", encoding="utf-8") as f:
                hedef_havuzu_ham = json.load(f)
                
                # Sadece bilgisayarda GERÇEKTEN var olan dosyaları havuza ekleyelim
                hedef_havuzu = {}
                for kategori, yollar in hedef_havuzu_ham.items():
                    gecerli_yollar = []
                    for yol in yollar:
                        # Eğer bu uygulama limitini doldurduysa havuza ekleme!
                        if blacklisted_app and os.path.normpath(yol) == os.path.normpath(blacklisted_app):
                            continue
                            
                        # Riot Games uygulamaları direkt .exe'den başlatılamaz (WinError 5 verir). Sadece kısayollara izin ver.
                        if "Riot Games" in yol and yol.lower().endswith(".exe"):
                            continue
                        
                        if os.path.exists(yol):
                            gecerli_yollar.append(yol)
                            
                    if gecerli_yollar:
                        hedef_havuzu[kategori] = gecerli_yollar
                        
                # Eğer geçerli hiçbir yol kalmadıysa yedek havuza dön
                if not hedef_havuzu:
                    raise FileNotFoundError
        except FileNotFoundError:
            hedef_havuzu = {
                "odaklanma_ve_calisma": ["notepad.exe", "explorer.exe"], 
                "oyun_ve_eglence": ["calc.exe"]
            }
            
        # Düşünce Zinciri (Chain of Thought) Promptu
        prompt = f"""
        Şu an kullanıcının TAM OLARAK BAKTIĞI / OYNADIĞI aktif pencere: {active_windows.get('on_plandaki_aktif_pencere', 'Bilinmiyor')}
        Arka planda açık olan diğer pencereler: {active_windows.get('arkaplandaki_diger_pencereler', [])}
        
        UYGULAMA HAVUZU:
        {hedef_havuzu}
        
        GÖREVİN:
        1. Kullanıcının şu anki durumunu analiz et (Oyun/Eğlence mi yoksa Çalışma/Odaklanma mı?).
        2. Kullanıcının ekrandaki mevcut aktivitesini EN İYİ GİZLEYECEK ZIT veya ALAKASIZ bir kategoriden uygulama seç!
           - Eğer kullanıcı OYUN OYNUYORSA veya EĞLENİYORSA -> 'odaklanma_ve_calisma' kategorisinden bir uygulama seç.
           - Eğer kullanıcı ÇALIŞIYOR VEYA ODAKLANIYORSA -> 'oyun_ve_eglence' kategorisinden bir uygulama seç. (Sanki hep oyun oynuyormuş izlenimi ver).
        3. TEKRAR YASAĞI: Seçeceğin hedef uygulama (target_exe), kullanıcının şu an baktığı pencereyle kesinlikle aynı olamaz. (Örn: Ekranda Dosya Gezgini açıksa explorer.exe seçme!).
        
        Aşağıdaki JSON formatında kesin bir yanıt dön:
        {{
            "analiz_edilen_baglam": "çalışma veya eğlence",
            "secilen_kategori": "seçtiğin_kategorinin_tam_adı",
            "hedef_uygulama_nedeni": "Neden bunu seçtiğinin tek cümlelik mantığı",
            "target_exe": "seçilen_tam_dosya_yolu"
        }}
        """

        try:
            print("[*] GPT-4o durumu analiz ediyor ve zıt kategoriyi belirliyor...")
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Sen ultra zeki, adım adım mantık kuran bir bağlam analiz asistanısın. Yanıtın kesinlikle sadece geçerli bir JSON olmalıdır."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.7, 
                response_format={"type": "json_object"}
            )
            
            karar = json.loads(chat_completion.choices[0].message.content)
            
            # Ne düşündüğünü ekrana yazdıralım ki zekasını görelim
            print(f"[*] AI Analizi: {karar.get('analiz_edilen_baglam')} -> {karar.get('secilen_kategori')}")
            print(f"[*] Sebep: {karar.get('hedef_uygulama_nedeni')}")
            
            return karar
            
        except Exception as e:
            print(f"[!] AI Karar Hatası: {e}")
            import random
            
            # Hata durumunda, kullanıcının aktif penceresini kontrol edip ters bir şey seçelim
            active_title = str(active_windows.get('on_plandaki_aktif_pencere', '')).lower()
            
            # Eğer kullanıcı çalışma tarzı bir şeydeyse oyun/eğlence seç, değilse çalışma seç
            is_working = any(word in active_title for word in [
                "code", "explorer", "gezgini", "chrome", "edge", "belge", 
                "studio", "antigravity", "idea", "pycharm", "devenv", "brave"
            ])
            if is_working:
                safe_pool = hedef_havuzu.get("oyun_ve_eglence", ["calc.exe"])
            else:
                safe_pool = hedef_havuzu.get("odaklanma_ve_calisma", ["notepad.exe"])
                
            # Eğer hala havuzda explorer.exe varsa ve şu an explorer'daysa, onu çıkar
            if "dosya gezgini" in active_title or "explorer" in active_title:
                safe_pool = [app for app in safe_pool if "explorer.exe" not in app.lower()]
                
            if not safe_pool:
                safe_pool = ["notepad.exe"]

            fallback_app = random.choice(safe_pool)
            return {"target_exe": fallback_app}

# Test bloğu
if __name__ == "__main__":
    ai = DynamicProfiler()
    test_verisi = ["Counter-Strike 2", "Discord", "Google Chrome"]
    sonuc = ai.get_decision(test_verisi)
    print(f"Yapay Zekanın Kararı: {sonuc}")