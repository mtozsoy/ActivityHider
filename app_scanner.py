import os
import json
import win32com.client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

class AIAppScanner:
    def __init__(self):
        self.config_file = "app_pool.json"
        token = os.environ.get("GITHUB_API_KEY") or os.environ.get("GITHUB_TOKEN")
        self.client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=token,
        )
        self.model = "gpt-4o"

    def get_installed_apps(self):
        """Başlat menüsü ve masaüstü kısayollarını tarar"""
        print("[*] Bilgisayardaki yüklü programlar (kısayollar) taranıyor...")
        apps = set()
        
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
        except Exception as e:
            print(f"[!] WScript.Shell başlatılamadı: {e}")
            return []
            
        directories = [
            os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), r"Microsoft\Windows\Start Menu\Programs"),
            os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs"),
            os.path.join(os.environ.get("PUBLIC", "C:\\Users\\Public"), r"Desktop"),
            os.path.join(os.environ.get("USERPROFILE", ""), r"Desktop")
        ]
        
        for directory in directories:
            if not directory or not os.path.exists(directory):
                continue
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_lower = file.lower()
                    
                    # 1. İnternet Kısayolları (.url) - Steam ve Epic Games oyunları genelde böyledir
                    if file_lower.endswith(".url"):
                        apps.add(os.path.join(root, file))
                        continue
                        
                    # 2. Normal Kısayollar (.lnk)
                    if file_lower.endswith(".lnk"):
                        lnk_path = os.path.join(root, file)
                        try:
                            shortcut = shell.CreateShortCut(lnk_path)
                            target_path = shortcut.Targetpath
                            
                            # Sadece .exe dosyalarını al, kaldırıcıları atla
                            if target_path.lower().endswith(".exe"):
                                if "uninstall" not in target_path.lower() and "unins" not in target_path.lower():
                                    apps.add(target_path)
                        except Exception:
                            pass
                            
        # 3. Popüler oyun klasörlerini manuel olarak hızlıca tara (Sadece Riot Games, Valorant/LoL için)
        riot_dir = r"C:\Riot Games"
        if os.path.exists(riot_dir):
            for root, dirs, files in os.walk(riot_dir):
                depth = root[len(riot_dir):].count(os.sep)
                if depth > 2: # Çok derine inme
                    dirs.clear()
                    continue
                for file in files:
                    if file.lower().endswith(".exe") and "crash" not in file.lower() and "unins" not in file.lower():
                        apps.add(os.path.join(root, file))
                            
        return list(apps)

    def scan_with_ai(self):
        installed_apps = self.get_installed_apps()
        
        # Çok fazla kısayol olabilir, prompt'u daha temiz yazıyoruz
        prompt = f"""
        Aşağıda kullanıcının bilgisayarında yüklü olan programların listesi (kısayol hedefleri) bulunuyor:
        {installed_apps}
        
        GÖREVİN:
        Bu listedeki uygulamaları analiz et ve sadece KULLANILABİLİR olan ana programları 2 kategoriye ayır.
        
        KATI KURALLAR:
        1. TARAYICI KURALI: İçinde 'brave', 'chrome', 'firefox', 'msedge' geçenleri KESİNLİKLE 'odaklanma_ve_calisma' kategorisine ekle (araştırma amaçlı).
        2. IDE/OFİS KURALI: Kodlama (code.exe, idea64.exe, devenv) ve Ofis (winword, excel) araçlarını 'odaklanma_ve_calisma'ya ekle.
        3. OYUN/EĞLENCE KURALI: Oyunları (Steam, Epic, Riot, LeagueClient, VALORANT, TLauncher vb.), İletişim (discord) ve Medya araçlarını (Spotify, vlc) 'oyun_ve_eglence'ye ekle.
        4. KISAYOL KURALI (.url): Listedeki '.url' uzantılı dosyalar (Örn: Counter-Strike 2.url, Grand Theft Auto V.url) birer OYUNDUR! Bunları KESİNLİKLE 'oyun_ve_eglence'ye ekle.
        5. ÇÖP FİLTRESİ: Kalan diğer tüm alakasız uygulamaları, uninstall dosyalarını, helper'ları ve gereksiz araçları YUT. Onları JSON'a KESİNLİKLE ekleme.
        
        ÇIKTI FORMATI:
        {{
            "odaklanma_ve_calisma": ["dosya_yolu_1", "dosya_yolu_2"],
            "oyun_ve_eglence": ["dosya_yolu_3", "dosya_yolu_4"]
        }}
        """

        try:
            print("[*] Kısayol listesi kategorize edilmek üzere GPT-4o'ya gönderiliyor...")
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Sen listeyi olabildiğince küçülten, sadece işe yarar uygulamaları seçen bir asistansın. Yanıtın kesinlikle sadece geçerli JSON olmalıdır."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.0, # Sıfır yaratıcılık, tamamen robotik mantık
                response_format={"type": "json_object"}
            )
            
            ai_havuz = json.loads(chat_completion.choices[0].message.content)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(ai_havuz, f, indent=4, ensure_ascii=False)
                
            print(f"[+] Taramalar tamamlandı! Zengin uygulama havuzu '{self.config_file}' dosyasına yazıldı.")
            print(json.dumps(ai_havuz, indent=4))
            
            return ai_havuz
            
        except Exception as e:
            print(f"[!] AI Tarama Hatası: {e}")
            return None

if __name__ == "__main__":
    scanner = AIAppScanner()
    scanner.scan_with_ai()