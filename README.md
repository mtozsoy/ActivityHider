<div align="center">
  <h1>Activity Hider</h1>
  <p>
    <strong>An LLM-powered, context-aware workspace switcher for Windows.</strong><br>
    <em>Windows için LLM destekli, bağlama duyarlı çalışma alanı değiştirici.</em>
  </p>

  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
  [![PyQt6](https://img.shields.io/badge/PyQt-6-green.svg?style=flat-square&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/intro)
  [![LLM](https://img.shields.io/badge/LLM-GPT--4o--mini-black.svg?style=flat-square)](https://github.com/marketplace/models)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

  <p>
    <a href="#english">English</a> | <a href="#türkçe">Türkçe</a>
  </p>
</div>

<hr>

<h2 id="english">English</h2>

Activity Hider is a "boss key" tool with a twist: instead of just minimizing windows, it reads the titles of the windows that are currently open, asks an LLM to classify what the user is doing (e.g. gaming, coding, browsing), and switches to an application from a **different** category in one keystroke.

The project was built to practice desktop automation with the Win32 API, LLM integration with structured (JSON) output, and multithreaded GUI development in Python.

### How it works

1. **Context collection:** `system_monitor.py` lists the visible windows and the foreground window using `pygetwindow`.
2. **Pre-computed decision:** A background thread sends this context to GPT-4o-mini (via GitHub Models) every 10 seconds and keeps the next target app ready. This way the LLM call never sits on the critical path when the hotkey is pressed.
3. **Switch:** When **F12** is pressed, all visible windows are minimized through the Win32 API and the prepared target app is opened. If there is no AI decision yet, it falls back to `explorer.exe`.
4. **App pool:** `app_scanner.py` scans Start Menu and Desktop shortcuts, and the LLM groups the installed apps into categories to build the switch pool.

### Features

- **Context-aware selection:** The LLM picks a target from the opposite category of the current activity and avoids repeating the same app.
- **Low-latency switching:** Because the decision is prepared in advance, the switch happens almost instantly.
- **System tray app:** Runs quietly in the system tray, without a console window.
- **Optional start at login:** It can register itself in Windows Task Scheduler with elevated privileges so it starts at login, and this can be turned off from the settings.
- **Settings panel:** A dark-themed PyQt6 dashboard to manage the app pool, run an AI scan and set repeat limits.

### Project structure

| File | Role |
|------|------|
| `main.py` | Orchestrator: hotkey listener, background decision loop, window hiding and app launch |
| `system_monitor.py` | Collects the foreground window and visible window titles |
| `ai_engine.py` | Builds the prompt and parses the LLM's JSON decision |
| `app_scanner.py` | Scans installed shortcuts and categorizes them with the LLM |
| `gui_app.py` | PyQt6 settings panel and system tray icon |
| `config_manager.py` | Loads and saves settings |
| `startup_manager.py` | Adds or removes the Task Scheduler entry for start at login |

### Installation

```bash
git clone https://github.com/mtozsoy/ActivityHider.git
cd ActivityHider
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install PyQt6 qdarkstyle openai pywin32 pygetwindow keyboard python-dotenv
```

Create a `.env` file in the root directory and add a GitHub token that has access to GitHub Models:

```env
GITHUB_TOKEN=ghp_your_personal_access_token_here
```

### Usage

Run `python main.py`. The app minimizes to the system tray. Double-click the tray icon to open the settings and scan for apps. Press **F12** to switch.

### Privacy note

To make a decision, the titles of open windows are sent to the GitHub Models API. Window titles can contain personal information (file names, page titles), so keep this in mind before using the tool.

### Possible improvements

- Classifying locally with a rule-based or small local model, so no window titles leave the machine
- A configurable hotkey
- Unit tests for the decision and config logic

<hr>

<h2 id="türkçe">Türkçe</h2>

Activity Hider, "boss key" fikrine farklı bir yaklaşım getiren bir araçtır. Pencereleri yalnızca küçültmekle kalmaz: o an açık olan pencerelerin başlıklarını okur, kullanıcının ne yaptığını (oyun, kod yazma, gezinme vb.) bir LLM'e sınıflandırtır ve tek tuşla **farklı** kategoriden bir uygulamaya geçer.

Proje; Win32 API ile masaüstü otomasyonu, yapılandırılmış (JSON) çıktılı LLM entegrasyonu ve Python'da çok iş parçacıklı arayüz geliştirme pratiği yapmak için geliştirildi.

### Nasıl çalışır

1. **Bağlam toplama:** `system_monitor.py`, `pygetwindow` ile görünür pencereleri ve öndeki pencereyi listeler.
2. **Önceden hazırlanan karar:** Arka plandaki bir iş parçacığı bu bağlamı 10 saniyede bir GPT-4o-mini'ye (GitHub Models üzerinden) gönderir ve bir sonraki hedef uygulamayı hazırda tutar. Böylece kısayola basıldığında LLM çağrısı beklenmez.
3. **Geçiş:** **F12**'ye basıldığında görünür pencerelerin hepsi Win32 API ile küçültülür ve hazırlanan uygulama açılır. Henüz bir yapay zekâ kararı yoksa `explorer.exe` açılır.
4. **Uygulama havuzu:** `app_scanner.py`, Başlat menüsü ve masaüstü kısayollarını tarar; LLM, yüklü uygulamaları kategorilere ayırarak geçiş havuzunu oluşturur.

### Özellikler

- **Bağlama duyarlı seçim:** LLM, mevcut etkinliğin zıt kategorisinden bir hedef seçer ve aynı uygulamayı tekrar etmekten kaçınır.
- **Düşük gecikmeli geçiş:** Karar önceden hazırlandığı için geçiş neredeyse anında gerçekleşir.
- **Sistem tepsisinde çalışma:** Konsol penceresi olmadan sistem tepsisinde sessizce çalışır.
- **İsteğe bağlı otomatik başlatma:** Oturum açılışında başlaması için kendini yükseltilmiş yetkiyle Windows Görev Zamanlayıcısı'na kaydedebilir; bu özellik ayarlardan kapatılabilir.
- **Ayarlar paneli:** Uygulama havuzunu yönetmek, yapay zekâ taraması yapmak ve tekrar limitlerini ayarlamak için koyu temalı bir PyQt6 paneli.

### Proje yapısı

| Dosya | Görevi |
|-------|--------|
| `main.py` | Orkestratör: kısayol dinleme, arka plan karar döngüsü, pencere gizleme ve uygulama açma |
| `system_monitor.py` | Öndeki pencereyi ve görünür pencere başlıklarını toplar |
| `ai_engine.py` | Prompt'u oluşturur ve LLM'in JSON kararını ayrıştırır |
| `app_scanner.py` | Yüklü kısayolları tarar ve LLM ile kategorilere ayırır |
| `gui_app.py` | PyQt6 ayarlar paneli ve sistem tepsisi simgesi |
| `config_manager.py` | Ayarları yükler ve kaydeder |
| `startup_manager.py` | Otomatik başlatma için Görev Zamanlayıcısı kaydını ekler veya siler |

### Kurulum

```bash
git clone https://github.com/mtozsoy/ActivityHider.git
cd ActivityHider
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install PyQt6 qdarkstyle openai pywin32 pygetwindow keyboard python-dotenv
```

Ana dizinde bir `.env` dosyası oluşturun ve GitHub Models erişimi olan bir GitHub token'ı ekleyin:

```env
GITHUB_TOKEN=ghp_kisisel_erisim_anahtariniz_buraya
```

### Kullanım

`python main.py` komutuyla çalıştırın. Uygulama sistem tepsisine küçülür. Ayarları açmak ve uygulamaları taratmak için tepsi simgesine çift tıklayın. Geçiş yapmak için **F12**'ye basın.

### Gizlilik notu

Karar verebilmek için açık pencerelerin başlıkları GitHub Models API'sine gönderilir. Pencere başlıkları kişisel bilgi (dosya adları, sayfa başlıkları) içerebileceği için aracı kullanmadan önce bunu göz önünde bulundurun.

### Geliştirilebilecekler

- Pencere başlıklarının bilgisayardan çıkmaması için kural tabanlı ya da küçük bir yerel modelle sınıflandırma
- Değiştirilebilir kısayol tuşu
- Karar ve ayar mantığı için birim testleri

<hr>

## License

[MIT](https://choosealicense.com/licenses/mit/)
