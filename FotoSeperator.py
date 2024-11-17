import cv2
import tkinter as tk
from tkinter import filedialog
import os
import numpy as np

# Global değişkenler
secilen_bolgeler = []
bolge_donusturme = {}
cizim = False
baslangic_x, baslangic_y = -1, -1
goruntu = None
goruntu_kucuk = None
oran = 1.0
guncel_goruntu = None
dosyalar = []
mevcut_dosya_indeksi = 0

# Renkler
RENKLER = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

# Klasör ayarları
cikti_klasoru = "cikti_klasoru"
os.makedirs(cikti_klasoru, exist_ok=True)

# Görüntüyü yeniden boyutlandırma
def yeniden_boyutlandir(goruntu, hedef_genislik, hedef_yukseklik):
    yukseklik, genislik = goruntu.shape[:2]
    oran = min(hedef_genislik / genislik, hedef_yukseklik / yukseklik)
    yeni_boyut = (int(genislik * oran), int(yukseklik * oran))
    goruntu_kucuk = cv2.resize(goruntu, yeni_boyut)
    return goruntu_kucuk, oran

# Fare callback fonksiyonu
def fare_olayi(event, x, y, flags, param):
    global cizim, baslangic_x, baslangic_y, secilen_bolgeler, guncel_goruntu, bolge_donusturme

    # Koordinatları görüntü sınırları içinde tut
    x = max(0, min(x, guncel_goruntu.shape[1] - 1))
    y = max(0, min(y, guncel_goruntu.shape[0] - 1))

    if event == cv2.EVENT_LBUTTONDOWN:  # Sol tıkla seçim başlat
        cizim = True
        baslangic_x, baslangic_y = x, y

    elif event == cv2.EVENT_MOUSEMOVE:  # Fare hareket ederken seçim yap
        if cizim:
            kopya = guncel_goruntu.copy()
            cv2.rectangle(kopya, (baslangic_x, baslangic_y), (x, y), (0, 255, 0), 2)
            cv2.imshow("Görüntü", kopya)

    elif event == cv2.EVENT_LBUTTONUP:  # Sol tık bırakıldığında seçim tamamla
        cizim = False
        bitis_x, bitis_y = x, y
        secilen_bolgeler.append((baslangic_x, baslangic_y, bitis_x, bitis_y))
        bolge_donusturme[len(secilen_bolgeler) - 1] = None  # Döndürme işlemleri için boş bırakılır
        renk = RENKLER[(len(secilen_bolgeler) - 1) % len(RENKLER)]
        cv2.rectangle(guncel_goruntu, (baslangic_x, baslangic_y), (bitis_x, bitis_y), renk, 2)
        butonlari_guncelle()
        cv2.imshow("Görüntü", guncel_goruntu)

# Görüntüye tüm seçimleri renkleriyle çizen fonksiyon
def secim_renkleri_guncelle():
    global guncel_goruntu
    kopya = guncel_goruntu.copy()
    for idx, (x1, y1, x2, y2) in enumerate(secilen_bolgeler):
        renk = RENKLER[idx % len(RENKLER)]
        cv2.rectangle(kopya, (x1, y1), (x2, y2), renk, 2)
    cv2.imshow("Görüntü", kopya)

# Her seçim için döndürme butonları oluşturma
def butonlari_guncelle():
    for widget in bolge_butonu_frame.winfo_children():
        widget.destroy()

    for idx, (x1, y1, x2, y2) in enumerate(secilen_bolgeler):
        tk.Label(bolge_butonu_frame, text=f"Seçim {idx + 1}", fg="black").pack()
        tk.Button(bolge_butonu_frame, text="180° Döndür", command=lambda i=idx: don180(i)).pack()
        tk.Button(bolge_butonu_frame, text="90° Sola Döndür", command=lambda i=idx: don90sol(i)).pack()
        tk.Button(bolge_butonu_frame, text="90° Sağa Döndür", command=lambda i=idx: don90sag(i)).pack()

# Seçim için döndürme işlemleri
def don180(idx):
    bolge_donusturme[idx] = "180"
    print(f"Seçim {idx + 1} 180° döndürülecek.")

def don90sol(idx):
    bolge_donusturme[idx] = "90sol"
    print(f"Seçim {idx + 1} 90° sola döndürülecek.")

def don90sag(idx):
    bolge_donusturme[idx] = "90sag"
    print(f"Seçim {idx + 1} 90° sağa döndürülecek.")

# Görüntüleri seç ve sırayla göster
def goruntu_sec():
    global dosyalar, mevcut_dosya_indeksi
    dosyalar = filedialog.askopenfilenames(title="Görüntüleri Seç",
                                           filetypes=(("Resim Dosyaları", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff"),))
    if dosyalar:
        mevcut_dosya_indeksi = 0
        goruntu_goster()

# Görüntüyü göster
def goruntu_goster():
    global goruntu, goruntu_kucuk, oran, secilen_bolgeler, guncel_goruntu, bolge_donusturme

    if mevcut_dosya_indeksi >= len(dosyalar):
        print("Tüm görüntüler işlendi.")
        return

    dosya_yolu = dosyalar[mevcut_dosya_indeksi]
    goruntu = cv2.imread(dosya_yolu)
    goruntu_kucuk, oran = yeniden_boyutlandir(goruntu, 1200, 800)
    guncel_goruntu = goruntu_kucuk.copy()
    secilen_bolgeler = []
    bolge_donusturme = {}
    cv2.imshow("Görüntü", guncel_goruntu)
    cv2.setMouseCallback("Görüntü", fare_olayi)
    kaydet_butonu.config(state=tk.NORMAL)
    butonlari_guncelle()

# Seçimleri kaydet ve sıradaki görüntüye geç
def secimleri_kaydet():
    global mevcut_dosya_indeksi, goruntu, secilen_bolgeler, bolge_donusturme

    if not secilen_bolgeler:
        print("Seçim yapılmadı.")
        return

    for idx, (x1, y1, x2, y2) in enumerate(secilen_bolgeler):
        # Koordinatları orijinal boyutlara ölçekle
        x1 = int(x1 / oran)
        y1 = int(y1 / oran)
        x2 = int(x2 / oran)
        y2 = int(y2 / oran)

        # Koordinatların sırasını düzelt
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        # Seçilen bölgeyi kırp
        parca = goruntu[y1:y2, x1:x2]

        # Döndürme işlemi
        if bolge_donusturme[idx] == "180":
            parca = cv2.rotate(parca, cv2.ROTATE_180)
        elif bolge_donusturme[idx] == "90sol":
            parca = cv2.rotate(parca, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif bolge_donusturme[idx] == "90sag":
            parca = cv2.rotate(parca, cv2.ROTATE_90_CLOCKWISE)

        # Kaydet
        parca_dosya_adi = f"parca_jjj{mevcut_dosya_indeksi}_{idx + 1}.png"
        cv2.imwrite(os.path.join(cikti_klasoru, parca_dosya_adi), parca)

    mevcut_dosya_indeksi += 1
    print(f"{len(secilen_bolgeler)} parça kaydedildi. Sıradaki görüntüye geçiliyor.")
    goruntu_goster()

# Geri al (son seçimi kaldır)
def geri_al():
    if secilen_bolgeler:
        secilen_bolgeler.pop()
        butonlari_guncelle()
        secim_renkleri_guncelle()

# Tkinter arayüz
pencere = tk.Tk()
pencere.title("Görüntü Kırpma ve Kaydetme")
pencere.geometry("600x400")

goruntu_sec_butonu = tk.Button(pencere, text="Görüntüleri Seç", command=goruntu_sec)
goruntu_sec_butonu.pack(pady=10)

kaydet_butonu = tk.Button(pencere, text="Seçimleri Kaydet", command=secimleri_kaydet, state=tk.DISABLED)
kaydet_butonu.pack(pady=10)

geri_al_butonu = tk.Button(pencere, text="Geri Al", command=geri_al)
geri_al_butonu.pack(pady=10)

bolge_butonu_frame = tk.Frame(pencere)
bolge_butonu_frame.pack(pady=10)

pencere.mainloop()
