# Mage Rhythm

Mage Rhythm adalah game ritme interaktif berbasis Computer Vision yang memanfaatkan webcam sebagai alat kendali utama. Proyek ini menggabungkan deteksi tangan, logika rhythm game, dan audio playback secara real-time dalam satu pengalaman permainan yang sederhana namun menarik.

## Ringkasan proyek

- Tujuan: menciptakan game berbasis gestur tangan untuk menghancurkan target sesuai irama musik.
- Teknologi utama: Python, OpenCV, NumPy, Pygame.
- Mode interaksi: deteksi posisi tangan, pengenalan gesture kepalan tangan, dan pemutaran musik.
- Status repositori: siap dijalankan setelah instalasi dependensi dasar selesai.

## Fitur utama

- Deteksi kulit tangan secara real-time menggunakan ruang warna HSV.
- Penghitung skor, perfect/good/miss, serta overlay feedback visual.
- Sistem spawn target ritme berdasarkan BPM lagu utama.
- Kontrol pause, resume, restart, dan quit melalui keyboard.
- Struktur repositori yang sudah dipisahkan menjadi folder sumber, aset, dan dokumen demo.

## Struktur direktori

```text
PCV Game/
├── main.py                  # entry point utama game
├── assets/
│   ├── screenshots/         # folder tangkapan layar gameplay
│   └── demo/                # tautan dan catatan demonstrasi video
├── freedom_dive.mp3         # audio utama
└── weapon.png               # aset visual senjata
```
Jalankan game dengan perintah:

```bash
python main.py
```

## Kontrol permainan

- Q: keluar dari game
- P: pause / resume
- R: restart game

## Panduan teknis singkat

- `main.py` berfungsi sebagai titik masuk yang sudah disiapkan untuk pengujian dan demo.
- `src/main.py` menyimpan kode sumber utama yang dapat dipelihara secara terpisah.
- Folder `assets/screenshots/` dipersiapkan untuk menyimpan hasil tangkapan layar gameplay.
- Folder `assets/demo/README.md` dipersiapkan sebagai lokasi tautan video demonstrasi.

## Tangkapan layar dan demo

- Screenshot Game: [Gameplay](assets/screenshots/image.png)
- Screenshot Pause: [Pause](assets/screenshots/pause.png)
- Screenshot Quit: [Quit](assets/screenshots/quit.png)
- Demo video: [Video Demo](assets/video/Demo%20Game%20PCV.mp4)

## Catatan pengembangan

Proyek ini masih dapat ditingkatkan dengan:
- penambahan deteksi gesture yang lebih akurat,
- pengaturan threshold warna kulit yang lebih adaptif,
- integrasi level dan skema musik yang lebih variatif,
- penyimpanan skor dan replay.
