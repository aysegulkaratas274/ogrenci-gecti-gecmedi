# 🎓 Öğrenci Geçer mi? — Proje Rehberi

Bu dosya, proje klasöründe hangi dosyanın ne işe yaradığını ve içinde neler olduğunu sade bir dille anlatır.

---

## Proje ne yapıyor?

Bir öğrencinin **sınavı geçip geçmeyeceğini** tahmin eden bir model kurduk.

- **Veri seti:** Kaggle'daki *Students Performance in Exams* (1000 öğrenci)
- **"Geçti" ne demek?** Veri setinde hazır bir geçti/kaldı bilgisi yok. Öğrencinin matematik, okuma ve yazma notlarının **ortalaması 60 veya üzerindeyse "geçti"**, altındaysa "kaldı" kabul ettik. (Neden 60 seçildiği aşağıda anlatılıyor.)
- **Model neye bakarak tahmin ediyor?** Sınav notlarına değil, öğrencinin şu 5 bilgisine bakıyor:

| Bilgi | Ne anlama geliyor? |
|---|---|
| Cinsiyet | Kız / Erkek |
| Etnik grup | Grup A, B, C, D, E (gerçek isimleri gizlenmiş) |
| Ebeveynin eğitim düzeyi | Öğrencinin **anne/babasının** okul durumu (öğrencinin kendisinin değil) |
| Öğle yemeği | Standart (ücretli) veya ücretsiz/indirimli. ABD'de ücretsiz yemek düşük gelirli ailelere verilir, yani bu bilgi aslında **ailenin gelir durumunu** gösterir |
| Hazırlık kursu | Öğrenci sınava hazırlık kursunu tamamladı mı, almadı mı |

> **Neden sınav notlarını kullanmadık?** Çünkü "geçti/kaldı" bilgisini zaten bu notlardan hesapladık. Notları modele verseydik model cevabı önceden görmüş olurdu. Buna **veri sızıntısı** denir.

### Geçme notu neden 60?

Veri setinde resmi bir geçme notu yok; bu eşiği biz seçtik. Veri **ABD okul sistemine** göre hazırlanmış ve ABD'de yaygın not sisteminde 60'ın altı **F**, yani "kaldı" demektir. Bu yüzden verinin geldiği sistemdeki geçme sınırını, yani 60'ı kullandık:

| Not | Harf | Anlamı |
|---|---|---|
| 90–100 | A | Geçti |
| 80–89 | B | Geçti |
| 70–79 | C | Geçti |
| 60–69 | D | Geçti (en düşük geçer not) |
| **0–59** | **F** | **Kaldı** |

> **Hoca sorarsa kısa cevap:** *"Veri ABD sistemine göre hazırlanmış, orada 60'ın altı F yani kaldı."*

---

## 📁 Klasörde neler var?

```
yztproje1/
├── ogrenci_gecme_tahmini.ipynb   → Ödevin kendisi (rapor)
├── app.py                        → Streamlit uygulaması (bonus)
├── data/
│   └── StudentsPerformance.csv   → Veri seti
├── requirements.txt              → Gerekli kütüphanelerin listesi
└── README.md                     → Bu dosya
```

---

## 📓 `ogrenci_gecme_tahmini.ipynb` — Ödevin kendisi

**Hocanın okuyacağı dosya bu.** İçinde kod, çıktılar (tablolar, grafikler) ve Türkçe açıklamalar adım adım yer alıyor. Çıktılar dosyaya kayıtlı, yani açar açmaz her şey görünür; yeniden çalıştırmaya gerek yok.

**Nasıl açılır?** VS Code ile açabilirsin.

### İçindeki bölümler

**1. Veriyi Tanıma**
- Verinin ilk birkaç satırı
- Her sütunun ne anlama geldiğini anlatan tablo
- Geçme notunun neden 60 seçildiği (ABD not sistemi)
- Kaç öğrenci geçmiş, kaç öğrenci kalmış: **715 geçti (%71.5), 285 kaldı (%28.5)**
- Sınıflar dengeli mi? **Tam dengeli değil**; geçenler yaklaşık 2.5 kat fazla.

**2. Veri Temizleme**
- Eksik veri var mı? **Yok.** Tekrar eden satır var mı? **Yok.**
- Sınav notu sütunları modelden çıkarıldı (veri sızıntısını önlemek için).
- Yazıyla tutulan bilgiler (ör. "female", "male") modelin anlayacağı 0/1 sayılarına çevrildi (*one-hot encoding*).

**3. Görselleştirme — 6 grafik, her birinin altında yorum**

| # | Grafik | Ne gösteriyor? |
|---|---|---|
| 1 | Geçen / kalan sayısı | 715 geçti, 285 kaldı |
| 2 | Cinsiyete göre geçme oranı | Kızlar %76, erkekler %67 |
| 3 | Öğle yemeğine göre geçme oranı | Standart yemek %80, ücretsiz/indirimli %56 (**en büyük fark**) |
| 4 | Hazırlık kursuna göre geçme oranı | Kursu tamamlayan %83, almayan %65 |
| 5 | Ebeveyn eğitimine göre geçme oranı | Anne/babanın eğitimi arttıkça geçme oranı artıyor |
| 6 | Etnik gruba göre geçme oranı | Grup A %55, Grup E %83 |

**4. Model**
- Verinin **%80'i** modeli eğitmek (train), **%20'si** modeli test etmek için ayrıldı.
- İki model kuruldu: **Logistic Regression** ve **Decision Tree**.

**5. Sonuç**
- Accuracy, precision ve recall tabloları
- Confusion matrix (hangi öğrenciler doğru, hangileri yanlış tahmin edildi)
- Hangi bilginin geçme şansını ne kadar etkilediği ("kaç kat artırır/azaltır" tablosu)
- **"Yanlış evet mi daha kötü, yanlış hayır mı?"** sorusunun cevabı

**6. Bonus**
- **6.1:** Üçüncü model olarak Random Forest eklendi; üç model karşılaştırıldı.
- **6.2:** Modelin yanıldığı birkaç öğrenci incelendi ve neden yanıldığı yorumlandı.

**Genel Sonuç** ve **Verinin sınırları** notu (veri seti yapay olarak üretilmiştir)

---

## 🖥️ `app.py` — Streamlit uygulaması (bonus)

Bu dosya bir rapor değil, **tarayıcıda açılan bir uygulama**. Projeyi sunarken canlı göstermek için ideal.

### Nasıl çalıştırılır?

Proje klasöründe bir terminal açıp şunu yaz:

```
streamlit run app.py
```

Tarayıcıda uygulama açılır. Kapatmak için terminalde **Ctrl + C**'ye bas.

> Hata alırsan şunu dene: `python -m streamlit run app.py`
> Uygulama veriyi `data` klasöründen okuduğu için komutu **proje klasöründeyken** çalıştırmalısın.

### Uygulamanın sekmeleri

| Sekme | İçinde ne var? |
|---|---|
| 📊 **Grafikler** | Notebook'taki 6 grafik ve kısa yorumları |
| 📈 **Model Sonuçları** | Üç modelin karşılaştırma tablosu (en iyi değerler yeşil). Seçtiğin modelin confusion matrix'i |
| 🎓 **Tahmin Et** | Bir öğrencinin bilgilerini seçip **Tahmin et**'e basıyorsun. Uygulama **GEÇER / KALIR** sonucunu, geçme olasılığını ve sonucu hangi bilgilerin olumlu ya da olumsuz etkilediğini gösteriyor |

---

## 📌 Notebook ile uygulama arasındaki fark

| | Notebook (`.ipynb`) | Uygulama (`app.py`) |
|---|---|---|
| Ne işe yarar? | Okunan, değerlendirilen **rapor** | Kullanılan, denenen **uygulama** |
| Veri temizleme adımları | ✅ Var | ❌ Yok |
| 6 grafik ve yorumları | ✅ Var (detaylı yorum) | ✅ Var (kısa yorum) |
| Model sonuçları ve confusion matrix | ✅ Var | ✅ Var |
| "Kaç kat" katsayı analizi | ✅ Var | ❌ Yok |
| Yanlış tahmin incelemesi | ✅ Var | ❌ Yok |
| Kendi seçtiğin öğrenci için tahmin | ❌ Yok | ✅ Var |

İkisi de modeli **aynı veri ve aynı ayarlarla** eğitiyor; bu yüzden sonuçları birebir aynı.

---

## 🏆 Ana sonuçlar (kısaca)

| Model | Accuracy | Kalacak öğrencileri yakalama |
|---|---|---|
| **Logistic Regression (en iyi)** | **%63** | **57 öğrenciden 33'ü (%58)** |
| Decision Tree | %58 | 57 öğrenciden 33'ü (%58) |
| Random Forest | %61.5 | 57 öğrenciden 27'si (%47) |

- **Geçmeyi en çok etkileyen iki şey:** öğle yemeği türü (ailenin gelir durumu) ve hazırlık kursu.
- **Yanlış "evet" daha kötü:** Kalacak bir öğrenciye "geçer" denirse o öğrenci gözden kaçar ve yardım alamaz. Yanlış "hayır"da ise geçecek bir öğrenci gereksiz yere ek desteğe yönlendirilir; bu da ona zarar vermez. Bu yüzden model, kalacak öğrencileri yakalamaya öncelik verecek şekilde ayarlandı.

---

## ❓ Hocanın sorabileceği sorular

**"Geçme notunu neden 60 aldınız?"**
→ Veri ABD sistemine göre hazırlanmış; orada 60'ın altı F, yani kaldı. (Notebook Bölüm 1)

**"Herkese 'geçer' diyen bir model bile %71.5 accuracy alır. Sizinki neden %63?"**
→ O model kalacak öğrencilerin **hiçbirini** bulamaz. Bizim model 57 riskli öğrencinin 33'ünü buluyor. Bu problemde amaç riskli öğrenciyi bulmak olduğu için accuracy'den biraz feda ettik. (Notebook Bölüm 5.1 ve 5.4)

**"Neden sınav notlarını kullanmadınız?"**
→ "Geçti/kaldı" bilgisi zaten bu notlardan hesaplandı. Notları kullansaydık model cevabı önceden görmüş olurdu (veri sızıntısı). (Notebook Bölüm 2.2)

**"Accuracy neden daha yüksek değil?"**
→ Model öğrencinin ne kadar çalıştığını, devamsızlığını, önceki notlarını bilmiyor; sadece arka plan bilgilerine bakıyor. Aynı arka plana sahip iki öğrenciden biri geçip diğeri kalabiliyor. (Notebook Bölüm 6.2)

**"Bu sonuçlar gerçek öğrenciler için geçerli mi?"**
→ Hayır. Veri seti eğitim amaçlı **yapay olarak üretilmiş**. Bu çalışma, bir sınıflandırma probleminin baştan sona nasıl kurulduğunu göstermek için yapıldı. (Notebook, Genel Sonuç)

---

## 🛠️ Kullanılan kütüphaneler

| Kütüphane | Ne için kullanıldı? |
|---|---|
| **pandas** | Veriyi okumak, tablo işlemleri |
| **numpy** | Sayısal hesaplamalar |
| **matplotlib / seaborn** | Grafikler |
| **scikit-learn** | Modeller (Logistic Regression, Decision Tree, Random Forest) ve başarı ölçümleri |
| **streamlit** | Tarayıcıda çalışan uygulama |
