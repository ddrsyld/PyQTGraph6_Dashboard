# ⚡ CellGuys BMS - Telemetry Monitor & Protection Dashboard (Python Edition)

> **Samsung Innovation Campus (SIC) Batch 8 Stage 2 - Final Project (IoT & Hardware Discovery)**  
> **Inovasi Proyek:** *CellGuys BMS (Smart 12.8V 4S LiFePO4 Battery Protection & Telemetry System)*

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![MQTT](https://img.shields.io/badge/Protocol-MQTT%20%2F%20Serial-orange?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue?style=for-the-badge)
![Design](https://img.shields.io/badge/Theme-Strict%20Monochrome-black?style=for-the-badge)

Aplikasi desktop telemetri industri dengan tema visual **Strict Monochrome (Hitam & Putih murni)** berstandar tinggi untuk sistem manajemen baterai **CellGuys BMS**. Mendukung konektivitas ganda: **MQTT** (kompatibel dengan simulasi ESP32 di Wokwi atau broker cloud) dan **Serial USB-UART / RS-232** untuk perangkat keras fisik langsung.

---

## ⚡ Cara Cepat Menjalankan (1-Click Run)

Bagi pengguna **Windows**, Anda **TIDAK PERLU** repot mengatur virtual environment atau menginstal library secara manual satu per satu:

1. Clone repositori ini atau download sebagai ZIP lalu ekstrak:
   ```bash
   git clone https://github.com/<username>/<repo-name>.git
   cd <repo-name>
   ```
2. **Cukup klik ganda (double-click) file:**
   ```cmd
   run.bat
   ```
3. ✨ **Selesai!** Script `run.bat` secara otomatis akan:
   - Memeriksa ketersediaan Python di komputer Anda.
   - Membuat Virtual Environment (`.venv`) terisolasi secara otomatis (tanpa mengotori Python global).
   - Mengunduh dan menginstal seluruh dependensi (`PyQt6`, `pyqtgraph`, `paho-mqtt`, `pyserial`).
   - Meluncurkan dashboard ke layar Anda.
   *(Saat dijalankan untuk kedua kalinya, aplikasi akan langsung terbuka secara instan tanpa proses unduh lagi).*

---

## 💻 Cara Menjalankan via Terminal (Manual / Multi-Platform)

Jika Anda menggunakan Linux, macOS, atau ingin menjalankannya lewat Command Prompt / PowerShell secara manual:

### 1. Prasyarat
- Pastikan **Python 3.10** atau lebih baru sudah terpasang.
- Cek instalasi:
  ```bash
  python --version
  ```

### 2. Setup Virtual Environment (Disarankan)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependensi
```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi
```bash
python main.py
```

### 5. Parameter Tambahan (CLI Flags Opsional)
```bash
# Langsung jalankan dalam mode simulasi (tanpa perlu ESP32/Hardware)
python main.py --simulate

# Tentukan Broker MQTT dan Topic khusus
python main.py --broker broker.emqx.io --topic sic/bms/telemetry

# Jalankan langsung dalam mode Serial USB-UART
python main.py --serial
```

---

## 🎮 Panduan Penggunaan Aplikasi (How to Use)

Dashboard menyediakan 3 mode operasi untuk kemudahan pengujian dan penggunaan di lapangan:

### 1. Mode Mock Simulation (Tanpa Alat / Tanpa Internet)
Ingin melihat tampilan dan grafik bekerja tanpa perangkat keras fisik?
- Buka dashboard, masuk ke tab **KONEKSI / SETTINGS**.
- Klik tombol **"START SIMULASI"** (atau jalankan `run.bat --simulate`).
- Dashboard akan memproduksi data telemetri dinamis (tegangan berfluktuasi wajar, arus charge/discharge, suhu, dan perhitungan State of Charge / SoC).

### 2. Mode MQTT (Wokwi Simulation & Cloud IoT)
Digunakan untuk pengujian simulasi ESP32 di [Wokwi.com](https://wokwi.com) atau perangkat IoT berbasis Wi-Fi:
- Default Broker: `broker.emqx.io` (Port `1883`).
- Topic Telemetri: `sic/bms/telemetry`
- Topic Kontrol: `sic/bms/control`
- Format JSON payload yang diterima:
  ```json
  {
    "v": 13.20,
    "i": 2.50,
    "t": 28.5,
    "soc": 80.0,
    "ah": 0.125,
    "relay": 1,
    "fault": 0,
    "cells": [3.30, 3.30, 3.30, 3.30]
  }
  ```

### 3. Mode Serial (Hardware Nyata via USB-UART)
Digunakan saat ESP32 terhubung langsung ke PC via kabel USB:
- Pada tab **KONEKSI**, pilih mode **Serial (USB/RS-232)**.
- Pilih port COM yang terdeteksi (contoh: `COM3`, `COM4`).
- Baudrate default: `115200`.
- Klik **CONNECT**.

### 4. Kontrol Proteksi & Reset Fault
- **Relay Disconnect / Connect:** Mengirimkan perintah darurat `RELAY_OFF` atau `RELAY_ON` untuk memutus/menyambung beban baterai.
- **Reset Fault:** Mengirimkan perintah `RESET_FAULT` untuk menghapus status alarm setelah kondisi abnormal (overvoltage, undervoltage, overtemperature) teratasi.
- **Export Data CSV:** Klik tombol **Export CSV** di tab Diagnostik untuk menyimpan seluruh riwayat data telemetri ke file spreadsheet.

---

## 📌 Fitur Unggulan

- 🖤 **Strict Industrial Monochrome:** Desain teknis presisi tinggi hitam-putih murni tanpa elemen warna-warni yang mengalihkan perhatian teknisi di lapangan.
- 🔄 **Adaptive Dark / Light Mode:** Dukungan penuh tema gelap dan terang dengan klik interaktif pada logo header aplikasi.
- 🐕 **Tri-State Connection Watchdog:**
  1. `OFFLINE`: Belum terhubung ke socket.
  2. `WAITING DATA`: Socket terhubung ke broker, namun ESP32 belum memancarkan data.
  3. `ONLINE STREAMING`: Data mengalir lancar secara real-time dengan pemantau frekuensi (Hz).
  4. `IDLE (Xs)`: Peringatan visual otomatis jika transmisi data terhenti lebih dari 3 detik.
- 📈 **Real-Time Oscilloscope Multi-Plot:** Menampilkan kurva gelombang Tegangan (V), Arus (A), dan Suhu (°C) dengan engine performa tinggi PyQtGraph.
- 🔋 **4S Battery Cell Visualizer:** Menampilkan keseimbangan tegangan tiap sel (Cell 1 – Cell 4) untuk paket LiFePO4 12.8V.
- 📋 **Live Diagnostic Console:** Log telemetri berkecepatan tinggi dengan filter kategori (`INFO`, `WARN`, `DATA`, `RAW`).

---

## 🛠️ Cara Build ke File Executable (.exe)

Jika Anda ingin membagikan aplikasi ini kepada orang lain tanpa mengharuskan mereka memiliki Python sama sekali, Anda dapat mengompilasinya menjadi file `.exe`:

1. Cukup klik ganda file:
   ```cmd
   build.bat
   ```
2. Hasil build akan berada di dalam folder:
   ```
   dist\CellGuys_BMS\CellGuys_BMS.exe
   ```

---

## 📂 Struktur Repositori

```
Python_Version/
├── models/
│   ├── __init__.py
│   └── telemetry.py          # Data model, LiFePO4 SoC LUT, Coulomb counting
├── services/
│   ├── __init__.py
│   ├── data_parser.py       # Parser universal (JSON, Key-Value, CSV)
│   ├── mqtt_service.py       # Worker thread koneksi MQTT Paho v2
│   └── serial_service.py     # Worker thread koneksi Serial PySerial
├── ui/
│   ├── __init__.py
│   ├── themes.py             # Palette QSS Dark & Light Monochrome
│   ├── main_window.py        # Logika GUI utama, watchdog, dan event handler
│   └── widgets/
│       ├── arc_gauge.py      # Arc gauge radial custom QPainter
│       ├── battery_widget.py # Widget visualisasi 4-sel baterai
│       ├── kpi_card.py       # Kartu metrik KPI teknis
│       └── waveform_chart.py # Plotting osiloskop PyQtGraph
├── resources/                # Aset logo resmi CellGuys (transparan, putih, hitam)
├── main.py                   # Titik masuk utama aplikasi
├── requirements.txt          # Daftar dependensi library Python
├── run.bat                   # Script otomatis 1-klik untuk menjalankan aplikasi
├── build.bat                 # Script 1-klik untuk kompilasi ke .exe
├── .gitignore                # Filter file cache & build untuk Git
└── README.md                 # Dokumentasi lengkap proyek
```

---

## 🚀 Panduan Push ke GitHub (Untuk Pengembang)

Jika Anda baru pertama kali membuat repository di GitHub untuk folder ini, jalankan perintah berikut di terminal:

```bash
# 1. Inisialisasi Git di dalam folder ini
git init

# 2. Tambahkan semua file (file cache dan folder build otomatis diabaikan berkat .gitignore)
git add .

# 3. Lakukan commit pertama
git commit -m "feat: initial commit CellGuys BMS Telemetry Dashboard with auto-launcher"

# 4. Buat branch utama 'main'
git branch -M main

# 5. Hubungkan ke repositori GitHub Anda (ganti URL di bawah dengan URL repo GitHub Anda)
git remote add origin https://github.com/<username-github>/<nama-repo>.git

# 6. Push kode ke GitHub
git push -u origin main
```

---

## 👨‍💻 Tim Pengembang & Lisensi

Proyek ini dikembangkan oleh tim inovasi **CellGuys** untuk **Samsung Innovation Campus (SIC) Batch 8 Stage 2**.  
Didistribusikan di bawah lisensi terbuka untuk tujuan edukasi dan pengembangan IoT.
