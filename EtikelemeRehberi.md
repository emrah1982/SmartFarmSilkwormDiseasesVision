Süper 👍
Aşağıda sana **doğrudan PDF’e dönüştürülebilecek**, sahada ve akademik projelerde rahatça kullanılabilecek **“Çilek Görüntüleri Etiketleme Rehberi”**ni veriyorum.
(Bunu Word / Google Docs / LaTeX’e yapıştırıp **PDF olarak kaydedebilirsin**.)

---

# 🍓 ÇİLEK GÖRÜNTÜLERİ ETİKETLEME REHBERİ

**(YOLO Tabanlı Olgunluk ve Çiçek Tespiti İçin)**

## 1. Amaç ve Kapsam

Bu rehber, çilek bitkisine ait görüntülerde:

* **Çiçek**
* **Olgun meyve**
* **Olgun olmayan meyve**

nesnelerinin **tutarlı, doğru ve makine öğrenmesine uygun** şekilde etiketlenmesini sağlamak amacıyla hazırlanmıştır.

> ❗ Tutarsız etiketleme, model performansını düşüren **en kritik faktördür**.

---

## 2. Sınıf Tanımları (KESİN TANIMLAR)

### 🌼 Class 0 — `flower`

**Tanım:**
Sadece çiçek yapısı (taç yapraklar + polen merkezi) bulunan, **meyve oluşumu başlamamış** çiçek.

✅ Etiketlenir:

* Beyaz taç yapraklar belirgin
* Ortada sarı polen dokusu
* Meyve çekirdeği **yok**

❌ Etiketlenmez:

* Çiçek içinde meyve çekirdeği belirginleşmişse

📌 **Altın Kural:**

> Çiçek + meyve birlikteyse → `flower` etiketi VERME

---

### 🍓 Class 1 — `ripe` (Olgun Meyve)

**Tanım:**
Hasada yakın veya hasat edilebilir seviyede kızarmış çilek.

✅ Etiketlenir:

* Kırmızı / koyu kırmızı
* Meyve formu net
* Çekirdekler belirgin

⚠️ Dikkat:

* %70+ kırmızıysa → **ripe**
* Hafif yeşil alanlar sorun değil

---

### 🍏 Class 2 — `unripe` (Olgun Olmayan Meyve)

**Tanım:**
Henüz hasada uygun olmayan, yeşil veya açık renkli meyve.

✅ Etiketlenir:

* Yeşil / açık yeşil
* Sarı-yeşil geçiş
* Küçük veya tam gelişmemiş meyve

⚠️ Kritik Nokta:

* Yarı kızarmış ama baskın yeşilse → **unripe**
* Kararsız görüntüler mutlaka bu sınıfa eklenmeli

---

## 3. ÇİÇEK + MEYVE BİRLİKTELİĞİ (EN KRİTİK KURAL)

### 🚨 Eğer bir görüntüde:

* Çiçek yaprakları VAR
* Ama meyve çekirdeği OLUŞMUŞSA

✅ **SADECE MEYVE ETİKETLENİR**
❌ Çiçek etiketi verilmez

📌 Sebep:

* Model aynı nesneye iki sınıf atamaya zorlanır
* Bu durum özellikle **unripe** sınıfını bozar

---

## 4. Bounding Box (Kutu) Kuralları

### ✅ Yapılması Gerekenler

* Nesneyi **tam kapsa**
* Çok boşluk bırakma
* Nesne dışına taşma

### ❌ Yapılmaması Gerekenler

* Yaprakları dahil etme
* Arka planı genişçe alma
* Aynı nesneye iki kutu çizme

📌 **Kutu = nesnenin gerçek sınırı**

---

## 5. ZOR SAHNE ETİKETLEME TALİMATI

Aşağıdaki görüntüler **özellikle etiketlenmeli**:

* Gölge altındaki meyveler
* Yaprak arkasında kalan meyveler
* Çiçek içinde yeni oluşan meyveler
* Çok küçük (uzakta) meyveler
* Renk geçişi olan meyveler

📌 Bu görüntüler modele **en çok katkıyı sağlar**.

---

## 6. ETİKET TUTARLILIĞI KURALLARI

* Aynı tip meyve → her zaman aynı sınıf
* Kararsız kaldığında:

  * **unripe tercih edilir**
* Emin olunmayan görüntü:

  * Ayrı klasöre alın
  * Tekrar gözden geçirilir

---

## 7. KALİTE KONTROL CHECKLIST (✔)

Etiketleme bittikten sonra:

* [ ] Aynı nesne iki sınıfla etiketlenmiş mi?
* [ ] Çiçek + meyve çakışması var mı?
* [ ] `unripe` sayısı yeterli mi?
* [ ] Çok küçük nesneler atlanmış mı?
* [ ] Gölge görüntüler var mı?

---

## 8. MODEL PERFORMANSI İÇİN ALTIN KURALLAR

🔥 10 tane zor etiket
➡️ 100 tane kolay etiketten daha değerlidir

🔥 Tutarlılık
➡️ Veri sayısından daha önemlidir

🔥 `unripe` sınıfı
➡️ En çok dikkat edilmesi gereken sınıftır

---

## 9. ÖNERİLEN ETİKETLEME ARAÇLARI

* LabelImg (YOLO format)
* Roboflow Annotate
* CVAT

---

## 10. Sonuç

Bu rehber doğrultusunda yapılan etiketleme:

* `unripe` sınıfını güçlendirir
* Çiçek–meyve karışıklığını azaltır
* Modelin **zor sahnelerdeki başarısını artırır**

---
