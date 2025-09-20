
# 🛡️ Windows Alarm

**Windows Alarm** adalah sistem keamanan berbasis **Python** dan **Node.js** yang dirancang untuk mendeteksi aktivitas mencurigakan pada perangkat (gerakan mouse, pencabutan charger, aktivitas keyboard, pengambilan screenshot, hingga tangkapan kamera) dan mengirimkan notifikasi secara otomatis ke **WhatsApp** melalui koneksi WebSocket.

---

## 📂 Struktur Proyek

```bash
windows-alarm/
├── security.py          # Script utama sistem keamanan (Python)
├── waconnect.js         # Koneksi WhatsApp (Node.js, Baileys)
├── requirements.txt     # Dependensi Python
├── package.json         # Dependensi Node.js
└── README.md            # Dokumentasi proyek
````

---

## ⚙️ Fitur Utama

* 🔊 **Alarm suara** (beep) melalui perintah `alert`.
* 🖱️ **Deteksi gerakan mouse** → notifikasi otomatis ke WhatsApp.
* 🔌 **Monitoring charger** → peringatan jika charger dilepas.
* ⌨️ **Keylogger sederhana** → pencatatan tombol yang ditekan.
* 📸 **Pengambilan screenshot berkala** → hasil dikirim ke WhatsApp.
* 🎥 **Tangkapan kamera** → foto webcam terkirim ke WhatsApp.
* 💬 **Command Listener** → menerima perintah dari WhatsApp:

  * `.alert` → mengaktifkan alarm.
  * `.unalert` → menonaktifkan alarm.
  * `.logoff` → mengunci layar Windows.

---

## 🛠️ Persiapan Lingkungan

### 1. Instalasi Python & Dependensi

1. Pastikan Python **3.x** sudah terpasang.
2. Instal dependensi Python:

```bash
pip install -r requirements.txt
```

Isi `requirements.txt`:

```text
wmi
pyautogui
keyboard
opencv-python
pillow
websocket-client
```

### 2. Instalasi Node.js & Dependensi

1. Pastikan Node.js (disarankan versi LTS) sudah terpasang.
2. Instal dependensi Node.js:

```bash
npm install
```

Contoh `package.json`:

```json
{
  "name": "windows-alarm",
  "version": "1.0.0",
  "description": "Windows Alarm with WhatsApp integration (Baileys + WebSocket)",
  "main": "waconnect.js",
  "scripts": {
    "start": "node waconnect.js"
  },
  "dependencies": {
    "@whiskeysockets/baileys": "^6.7.6",
    "ws": "^8.18.0",
    "pino": "^9.0.0",
    "qrcode": "^1.5.3"
  }
}
```

---

## 🚀 Cara Menjalankan

1. Jalankan server WhatsApp (`waconnect.js`):

```bash
node waconnect.js
```

* Pada eksekusi pertama, QR Code akan muncul.
* Scan menggunakan aplikasi WhatsApp untuk menghubungkan bot.

2. Jalankan sistem keamanan (`security.py`):

```bash
python security.py
```

3. Sistem aktif. Semua aktivitas (mouse, charger, keyboard, screenshot, kamera) akan dipantau dan dikirim ke nomor WhatsApp tujuan.

---

## 📌 Konfigurasi

Nomor WhatsApp tujuan dapat dikonfigurasi pada variabel global di `security.py`:

```python
# ===== KONFIGURASI =====
sensi_mouse = 50
TARGET_NUMBER = "628xxxxxxxxxx"  # Ganti dengan nomor WhatsApp tujuan
alarm = False
log_file = "security_log.txt"
tempat_ss = "screenshots"
tempat_foto = "camera_shots"
# =======================
```

**Format nomor**: gunakan kode negara tanpa tanda `+` → contoh: `62881xxxxxxx`.

---

## 🔄 Diagram Alur Sistem

```text
                ┌──────────────┐
                │  security.py │
                │   (Python)   │
                └───────┬──────┘
                        │  JSON (event: mouse, charger, keyboard, ss, cam)
                        ▼
                ┌──────────────┐
                │ waconnect.js │
                │   (Node.js)  │
                └───────┬──────┘
                        │ Baileys API
                        ▼
                ┌────────────────┐
                │   WhatsApp     │
                │ (Nomor User)   │
                └────────────────┘

<=== Command balik ===
User kirim WA: ".alert" / ".unalert" / ".logoff"
     ▼
Node.js menerima → broadcast perintah ke Python
     ▼
Python mengeksekusi (alarm aktif/nonaktif, lock workstation)
```

---

## 📄 Log Aktivitas

Semua event terekam pada file log:

```text
security_log.txt
```

Contoh isi:

```text
2025-09-19 14:30:12 - ⚠️ Mouse bergerak mencurigakan!
2025-09-19 14:30:45 - ⚠️ Charger dicabut!
2025-09-19 14:31:10 - 🛑 Tombol ditekan: a
```

---

## 🧩 Kontribusi

1. Fork repository ini.
2. Buat branch baru (`feature/fitur-baru`).
3. Lakukan commit atas perubahan.
4. Push branch ke repository.
5. Buat Pull Request.

---

## ⚠️ Disclaimer

* Proyek ini ditujukan untuk **tujuan pembelajaran dan eksperimen pribadi**.
* Dilarang menggunakan script ini untuk tindakan ilegal, spionase, atau tanpa izin dari pemilik perangkat.
* Penulis tidak bertanggung jawab atas segala bentuk penyalahgunaan.

```
```
