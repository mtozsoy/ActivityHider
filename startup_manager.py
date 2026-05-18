import os
import subprocess
import sys

TASK_NAME = "ActivityHider"

def get_python_exe():
    """Mevcut sanal ortamın (venv) pythonw.exe yolunu döndürür (arkaplanda çalışması için)."""
    venv_python = sys.executable
    if "python.exe" in venv_python.lower():
        venv_python = venv_python.replace("python.exe", "pythonw.exe")
    return venv_python

def get_main_script():
    """Çalıştırılacak ana scriptin tam yolunu döndürür."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))

def is_startup_enabled():
    """Görev zamanlayıcıda ActivityHider görevinin olup olmadığını kontrol eder."""
    try:
        result = subprocess.run(["schtasks", "/query", "/tn", TASK_NAME], capture_output=True, text=True)
        return "ERROR:" not in result.stderr
    except Exception:
        return False

def enable_startup():
    """Windows Görev Zamanlayıcıya giriş yapıldığında yönetici izniyle açılacak şekilde ekler."""
    python_path = get_python_exe()
    script_path = get_main_script()
    
    # Task scheduler komutu
    # /sc onlogon: Kullanıcı giriş yaptığında çalışır
    # /rl highest: UAC atlayıp doğrudan yönetici yetkisiyle çalışır
    # /f: Zaten varsa üzerine yazar
    command = f'schtasks /create /tn "{TASK_NAME}" /tr "\\"{python_path}\\" \\"{script_path}\\"" /sc onlogon /rl highest /f'
    
    try:
        # Komutu çalıştır
        subprocess.run(command, shell=True, check=True)
        return True, "Başlangıçta çalıştırma başarıyla aktifleştirildi."
    except subprocess.CalledProcessError as e:
        return False, f"Hata oluştu (Uygulamanın yönetici olarak çalıştığından emin olun): {e}"

def disable_startup():
    """Görev zamanlayıcıdan başlangıç görevini siler."""
    command = f'schtasks /delete /tn "{TASK_NAME}" /f'
    try:
        subprocess.run(command, shell=True, check=True)
        return True, "Başlangıçta çalıştırma iptal edildi."
    except subprocess.CalledProcessError as e:
        return False, f"Silinirken hata oluştu: {e}"
