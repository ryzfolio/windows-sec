import wmi
import pyautogui
import keyboard
import winsound
import time
import threading
import pythoncom
import cv2
from PIL import ImageGrab
import os
import json
import websocket
import queue

sensi_mouse = 50
alarm = False
log_file = "security_log.txt"
tempat_ss = "screenshots"
tempat_foto = "camera_shots"

os.makedirs(tempat_ss, exist_ok=True)
os.makedirs(tempat_foto, exist_ok=True)

antrian_gmbr = queue.Queue()

ws = None  # Koneksi WebSocket

def play_alarm():
    global alarm
    while alarm:
        print("🔊 Alarm playing...")
        winsound.Beep(1000, 500)
        time.sleep(0.5)

def connect_ws():
    global ws
    while True:
        try:
            ws = websocket.create_connection("ws://localhost:3000")
            print("✅ WebSocket Connected!")
            return
        except Exception as e:
            print(f"⚠️ Gagal connect ke WebSocket, coba lagi dalam 3 detik... ({e})")
            time.sleep(3)


def send_whatsapp(nomor, tipe, pesan, caption=""):
    """Kirim pesan ke WhatsApp (teks langsung, gambar masuk antrian)"""
    if ws is None or not ws.connected:
        connect_ws()

    try:
        data = {"nomor": nomor, "tipe": tipe, "pesan": pesan, "caption": caption}

        if tipe == "TEXT":
            ws.send(json.dumps(data))
            print("📩 Teks terkirim:", pesan)
        else:
            antrian_gmbr.put(data)

    except Exception as e:
        print(f"❌ Gagal kirim WA (send_whatsapp): {e}")


def image_sender():
    global ws
    global alarm
    while True:
        try:
            if ws is None or not ws.connected:
                connect_ws()

            data = antrian_gmbr.get() 
            ws.send(json.dumps(data))
            response = ws.recv()
            print("📷 Gambar terkirim:", data["pesan"])

            reply = json.loads(response)
            print("💬 Pesan Diterima : ", reply)

        except Exception as e:
            print(f"❌ Error image_sender: {e}")

def command_listener():
    global ws
    global alarm

    while True:
        try:
            if ws is None or not ws.connected:
                connect_ws()

            response = ws.recv()
            reply = json.loads(response)
            print("💬 Perintah Diterima:", reply)

            command = reply.get("perintah")

            if command == "alert":
                print("----- 💀 Menerima Perintah : Alert On! 🔛 -----")
                if not alarm:
                    alarm = True
                    threading.Thread(target=play_alarm, daemon=True).start()

            elif command == "unalert":
                print("----- 💀 Menerima Perintah : Alert Off! 📴 -----")
                alarm = False

            elif command == "logoff":
                print("----- 💀 Menerima Perintah : LogOff! 🚪 -----")
                os.system("rundll32.exe user32.dll,LockWorkStation")

        except Exception as e:
            print(f"❌ Error command_listener: {e}")


def log_event(event):
    global log_file
    log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {event}"
    print(log_entry)
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(log_entry + "\n")


def check_charger():
    pythoncom.CoInitialize()
    c = wmi.WMI()
    for battery in c.Win32_Battery():
        return battery.BatteryStatus != 1
    return False


def monitor_security():
    mouse_terakhir = pyautogui.position()

    while True:
        try:
            mouse_sekarang = pyautogui.position()
            jauh_x = abs(mouse_sekarang[0] - mouse_terakhir[0])
            jauh_y = abs(mouse_sekarang[1] - mouse_terakhir[1])
            jauh = max(jauh_x, jauh_y)
            if abs(mouse_sekarang[0] - mouse_terakhir[0]) > sensi_mouse or abs(
                mouse_sekarang[1] - mouse_terakhir[1]
            ) > sensi_mouse:
                send_whatsapp("628818837894", "TEXT", f"🖱️ Mouse Laptop Digerakkan! bergerak sejauh {jauh}px")
                log_event("⚠️ Mouse bergerak mencurigakan!")

            mouse_terakhir = mouse_sekarang
            time.sleep(0.5)
        except Exception as e:
            log_event(f"❌ Error monitor_security: {e}")
            send_whatsapp("628818837894", "TEXT", f"⚠️ Gagal Monitoring! \nmonitor_security (mouse) : {e}")


def charger_monitor():
    status_casan = check_charger()

    while True:
        try:
            casan_terbaru = check_charger()
            if casan_terbaru != status_casan:
                if not casan_terbaru:
                    send_whatsapp("628818837894", "TEXT", "🔋 Charger Dicabut!")
                    log_event("⚠️ Charger dicabut!")
            status_casan = casan_terbaru
            time.sleep(1)
        except Exception as e:
            log_event(f"❌ Error charger_monitor: {e}")
            send_whatsapp("628818837894", "TEXT", f"⚠️ Gagal Monitoring! \ncharger_monitor (charger) : {e}")


def keyboard_logger():
    def on_key(event):
        log_event(f"🛑 Tombol ditekan: {event.name}")
        send_whatsapp("628818837894", "TEXT", f"👤 Keyboard Diketik: {event.name}")

    keyboard.on_press(on_key)
    keyboard.wait()


def capture_screenshot():
    try:
        waktu = str(int(time.time()))
        ss_path = os.path.join(tempat_ss, f"screenshot_{waktu}.png")

        screenshot = ImageGrab.grab()
        screenshot.save(ss_path)

        send_whatsapp("628818837894", "FOTO", ss_path, "Screenshot!")
        return ss_path
    except Exception as e:
        log_event(f"❌ Error capture_screenshot: {e}")
        return None


def capture_camera():
    """Ambil gambar dari kamera"""
    try:
        waktu = str(int(time.time()))
        cam_path = os.path.join(tempat_foto, f"camera_{waktu}.png")

        cap = cv2.VideoCapture(4)
        ret, frame = cap.read()
        cap.release()

        if ret:
            cv2.imwrite(cam_path, frame)
            send_whatsapp("628818837894", "FOTO", cam_path, "WebCam!")
            return cam_path
        else:
            log_event("❌ Kamera gagal menangkap gambar!")
            return None
    except Exception as e:
        log_event(f"❌ Error capture_camera: {e}")
        return None


def try_screenshot():
    while True:
        capture_screenshot()
        time.sleep(20)


def try_camera():
    while True:
        capture_camera()
        time.sleep(15)


if __name__ == "__main__":
    log_event("🔥 Sistem keamanan AKTIF!")
    threading.Thread(target=monitor_security, daemon=True).start()
    threading.Thread(target=charger_monitor, daemon=True).start()
    threading.Thread(target=keyboard_logger, daemon=True).start()
    threading.Thread(target=image_sender, daemon=True).start()
    threading.Thread(target=try_screenshot, daemon=True).start()
    threading.Thread(target=try_camera, daemon=True).start()
    threading.Thread(target=command_listener, daemon=True).start()
    
    while True:
        time.sleep(1)
