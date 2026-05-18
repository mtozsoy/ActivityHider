<div align="center">
  <h1>🛡️ Activity Hider (AI-Powered Panic Button)</h1>
  <p>
    <strong>A next-generation, context-aware panic button powered by GPT-4o-mini.</strong><br>
    <em>GPT-4o-mini destekli, bağlama duyarlı yeni nesil panik butonu.</em>
  </p>
  
  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
  [![PyQt6](https://img.shields.io/badge/PyQt-6-green.svg?style=flat-square&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/intro)
  [![OpenAI](https://img.shields.io/badge/AI-GPT--4o--mini-black.svg?style=flat-square&logo=openai&logoColor=white)](https://openai.com/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

  <p>
    <a href="#english">English</a> | <a href="#türkçe">Türkçe</a>
  </p>
</div>

<hr>

<h2 id="english">🇬🇧 English</h2>

Have you ever needed to instantly hide your screen when someone walks into the room? <br>
<i>Activity Hider doesn't just hide your game; it analyzes your context using AI and instantly brings up a completely unrelated, safe application to perfectly camouflage your activity!</i>

### ✨ Features
- 🧠 **Context-Aware AI Decisions:** Powered by GitHub Models (GPT-4o-mini), the application analyzes what you are currently doing (e.g., gaming vs. coding) and instantly opens an app from the **opposite** category to provide the perfect alibi.
- ⚡ **Lightning Fast Execution:** Minimizes all active windows in milliseconds and maximizes your "decoy" application seamlessly using low-level Win32 APIs.
- 🕵️ **Silent Background Operation:** Lives entirely in your system tray without any annoying console windows. 
- 🚀 **UAC-Bypass Auto Start:** Registers itself to Windows Task Scheduler with the highest privileges, ensuring it starts silently on boot without triggering UAC prompts.
- 🎛️ **Modern GUI Settings:** A sleek, PyQt6-based dashboard to manage your camouflage app pool, run AI system scans, and configure repeat limits.

### 🛠️ Installation
```bash
git clone https://github.com/mtozsoy/ActivityHider.git
cd ActivityHider
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install PyQt6 qdarkstyle openai pywin32 keyboard python-dotenv
```
Create a `.env` file in the root directory and add your GitHub token:
```env
GITHUB_TOKEN=ghp_your_personal_access_token_here
```

### 🎮 Usage
Run `python main.py`. The app minimizes to your system tray. Double-click the tray icon to open settings and scan for apps. Press the **F12** hotkey anytime to trigger the panic sequence!

<hr>

<h2 id="türkçe">🇹🇷 Türkçe</h2>

Odaya biri girdiğinde ekranınızı anında gizlemeniz gerektiği oldu mu? <br>
<i>Activity Hider sadece oyununuzu gizlemekle kalmaz; yapay zeka kullanarak o an ne yaptığınızı analiz eder ve etkinliğinizi mükemmel bir şekilde kamufle etmek için anında tamamen alakasız, masum bir uygulama açar!</i>

### ✨ Özellikler
- 🧠 **Yapay Zeka Destekli Kararlar:** GitHub Models (GPT-4o-mini) tarafından desteklenen sistem, o an ne yaptığınızı (ör. oyun oynamak vs. kod yazmak) analiz eder ve size mükemmel bir mazeret sağlamak için **tam zıttı** kategoriden bir uygulama açar.
- ⚡ **Işık Hızında Çalışma:** Düşük seviye Win32 API'lerini kullanarak tüm aktif pencereleri milisaniyeler içinde simge durumuna küçültür ve "kamuflaj" uygulamanızı ekrana getirir.
- 🕵️ **Sessiz Arka Plan İşlemi:** Can sıkıcı siyah CMD ekranları olmadan tamamen sağ alttaki sistem tepsisinde (system tray) yaşar.
- 🚀 **UAC (Yönetici) Atlayarak Otomatik Başlatma:** Kendisini en yüksek ayrıcalıklarla Windows Görev Zamanlayıcısına kaydeder ve bilgisayar açılışında rahatsız edici "Evet/Hayır" uyarıları vermeden sessizce başlar.
- 🎛️ **Modern Arayüz (GUI):** Kamuflaj havuzunuzu yönetmek, yapay zeka ile sistemi tarayıp otomatik liste oluşturmak ve tekrarlama limitlerini ayarlamak için PyQt6 tabanlı şık bir kontrol paneli.

### 🛠️ Kurulum
```bash
git clone https://github.com/mtozsoy/ActivityHider.git
cd ActivityHider
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install PyQt6 qdarkstyle openai pywin32 keyboard python-dotenv
```
Ana dizinde bir `.env` dosyası oluşturun ve GitHub API token'ınızı ekleyin:
```env
GITHUB_TOKEN=ghp_kisisel_erisim_anahtariniz_buraya
```

### 🎮 Kullanım
`python main.py` komutuyla çalıştırın. Uygulama, sistem tepsisine simge durumuna küçülecektir. Ayarları açmak ve sisteminizdeki uygulamaları taratmak için tepsi simgesine (kalkan ikonu) çift tıklayın. Panik modunu tetiklemek için istediğiniz zaman **F12** tuşuna basmanız yeterlidir!

<hr>

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## 📄 License
[MIT](https://choosealicense.com/licenses/mit/)
