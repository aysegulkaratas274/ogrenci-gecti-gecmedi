"""Öğrenci Geçer mi? — Streamlit arayüzü.

Çalıştırmak için:  streamlit run app.py
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, confusion_matrix,
                             precision_score, recall_score)
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

sns.set_theme(style="whitegrid")

OZELLIKLER = ["gender", "race/ethnicity", "parental level of education", "lunch", "test preparation course"]

# Arayüzde Türkçe gösterilen seçenekler → veri setindeki asıl değerler
SECENEKLER = {
    "gender": ("Cinsiyet", {"Kız": "female", "Erkek": "male"}),
    "race/ethnicity": ("Etnik grup", {f"Grup {h}": f"group {h}" for h in "ABCDE"}),
    "parental level of education": ("Öğrencinin anne/babasının eğitim düzeyi", {
        "Anne/baba liseyi bitirmemiş": "some high school",
        "Anne/baba lise mezunu": "high school",
        "Anne/baba üniversiteyi bitirmemiş": "some college",
        "Anne/baba önlisans mezunu": "associate's degree",
        "Anne/baba lisans (üniversite) mezunu": "bachelor's degree",
        "Anne/baba yüksek lisans mezunu": "master's degree",
    }),
    "lunch": ("Öğle yemeği (ailenin gelir göstergesi)", {
        "Standart (ücretli)": "standard",
        "Ücretsiz / indirimli (düşük gelir)": "free/reduced",
    }),
    "test preparation course": ("Sınava hazırlık kursu", {"Tamamladı": "completed", "Almadı": "none"}),
}


@st.cache_data
def veriyi_yukle():
    df = pd.read_csv("data/StudentsPerformance.csv")
    df["ortalama"] = df[["math score", "reading score", "writing score"]].mean(axis=1)
    df["gecti"] = (df["ortalama"] >= 60).astype(int)
    return df


@st.cache_resource
def modelleri_egit():
    """Notebook'taki üç modeli aynı ayarlarla eğitir."""
    df = veriyi_yukle()
    X = pd.get_dummies(df[OZELLIKLER], drop_first=True).astype(int)
    y = df["gecti"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    modeller = {
        "Logistic Regression": LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=4, class_weight="balanced", random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=300, max_depth=6,
                                                class_weight="balanced", random_state=42),
    }
    tahminler = {ad: m.fit(X_train, y_train).predict(X_test) for ad, m in modeller.items()}
    return modeller, X.columns, y_test, tahminler


def gecme_orani_grafigi(df, sutun, baslik, sira=None, etiketler=None, x_etiketi=None):
    oranlar = df.groupby(sutun)["gecti"].mean()
    if sira is not None:
        oranlar = oranlar.reindex(sira)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=etiketler or list(oranlar.index), y=oranlar.values * 100, ax=ax, color="#4C72B0")
    genel = df["gecti"].mean() * 100
    ax.axhline(genel, ls="--", color="gray", label=f"Genel oran (%{genel:.1f})")
    for i, v in enumerate(oranlar.values):
        ax.text(i, v * 100 + 1, f"%{v*100:.1f}", ha="center")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Geçme oranı (%)")
    ax.set_xlabel(x_etiketi or "")
    ax.set_title(baslik)
    ax.legend(loc="lower right")
    return fig


def grafikler_sekmesi(df):
    st.write("Her grafik bir özelliğin **geçme oranına** etkisini gösterir. "
             "Kesikli çizgi tüm öğrencilerin genel geçme oranıdır.")

    st.subheader("1. Geçen ve kalan öğrenci sayısı")
    fig, ax = plt.subplots(figsize=(8, 4))
    sayilar = df["gecti"].map({1: "Evet (geçti)", 0: "Hayır (kaldı)"}).value_counts()
    sayilar = sayilar.reindex(["Evet (geçti)", "Hayır (kaldı)"])
    sns.barplot(x=sayilar.index, y=sayilar.values, hue=sayilar.index,
                palette=["#55A868", "#C44E52"], legend=False, ax=ax)
    for i, v in enumerate(sayilar.values):
        ax.text(i, v + 10, str(v), ha="center")
    ax.set_xlabel("")
    ax.set_ylabel("Öğrenci sayısı")
    st.pyplot(fig)
    st.info("715 öğrenci geçti (%71.5), 285 öğrenci kaldı (%28.5). Sınıflar tam dengeli değil; "
            "bu yüzden modelde kalan öğrencilere daha fazla önem verildi.")

    st.subheader("2. Cinsiyete göre geçme oranı")
    st.pyplot(gecme_orani_grafigi(df, "gender", "Cinsiyete göre geçme oranı", etiketler=["Kız", "Erkek"]))
    st.info("Kızların geçme oranı (%76.1) erkeklerden (%66.6) yaklaşık 10 puan yüksek.")

    st.subheader("3. Öğle yemeği türüne göre geçme oranı")
    st.pyplot(gecme_orani_grafigi(df, "lunch", "Öğle yemeği türüne göre geçme oranı",
                                  sira=["free/reduced", "standard"],
                                  etiketler=["Ücretsiz/indirimli (düşük gelir)", "Standart (ücretli)"]))
    st.info("En büyük farkı yaratan özellik. Ücretsiz/indirimli yemek düşük gelirli ailelere verilir; "
            "bu öğrencilerde geçme oranı %56.3, diğerlerinde %79.8.")

    st.subheader("4. Hazırlık kursuna göre geçme oranı")
    st.pyplot(gecme_orani_grafigi(df, "test preparation course", "Hazırlık kursuna göre geçme oranı",
                                  sira=["none", "completed"], etiketler=["Almadı", "Tamamladı"]))
    st.info("Kursu tamamlayanların geçme oranı %83.2, almayanların %65.0 (~18 puan fark).")

    st.subheader("5. Ebeveynin (anne/baba) eğitim düzeyine göre geçme oranı")
    egitim = SECENEKLER["parental level of education"][1]
    st.pyplot(gecme_orani_grafigi(df, "parental level of education",
                                  "Ebeveynin eğitim düzeyine göre öğrencinin geçme oranı",
                                  sira=list(egitim.values()),
                                  etiketler=["Lise terk", "Lise", "Üniversite terk", "Önlisans", "Lisans", "Yüksek lisans"],
                                  x_etiketi="Ebeveynin (anne/baba) en yüksek eğitim düzeyi"))
    st.info("Bu sütun **öğrencinin değil, ebeveyninin** eğitim düzeyini gösterir (veri setindeki adı: "
            "*parental level of education*). Ebeveynin eğitimi arttıkça öğrencinin geçme oranı artıyor: "
            "ebeveyni lise ve altı olanlarda %61–64, lisans ve yüksek lisans olanlarda %82–83.")

    st.subheader("6. Etnik gruba göre geçme oranı")
    st.pyplot(gecme_orani_grafigi(df, "race/ethnicity", "Etnik gruba göre geçme oranı",
                                  sira=[f"group {h}" for h in "ABCDE"],
                                  etiketler=[f"Grup {h}" for h in "ABCDE"]))
    st.info("Grup A'da geçme oranı %55.1, grup E'de %82.9.")


def model_sekmesi(y_test, tahminler):
    st.write("Model, verinin %80'i ile eğitildi (train), kalan %20 ile test edildi. "
             "Aşağıdaki sonuçlar modelin daha önce görmediği 200 öğrencilik **test kümesine** aittir.")

    tablo = pd.DataFrame({
        ad: {
            "Accuracy": accuracy_score(y_test, p),
            "Precision (geçti)": precision_score(y_test, p),
            "Recall (geçti)": recall_score(y_test, p),
            "Recall (kaldı)": recall_score(y_test, p, pos_label=0),
        }
        for ad, p in tahminler.items()
    }).T
    st.dataframe(tablo.style.format("{:.3f}").highlight_max(axis=0, color="#c6e9c6"), width="stretch")
    st.success("**En iyi model: Logistic Regression.** Accuracy'si en yüksek ve kalacak öğrencileri en iyi yakalayan model.")

    secili = st.radio("Confusion matrix'ini görmek istediğin model:", list(tahminler), horizontal=True)
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay(confusion_matrix(y_test, tahminler[secili]),
                           display_labels=["Hayır (kaldı)", "Evet (geçti)"]).plot(ax=ax, cmap="Blues", colorbar=False)
    ax.grid(False)
    ax.set_xlabel("Modelin tahmini")
    ax.set_ylabel("Gerçek durum")
    st.pyplot(fig)
    st.info("**Nasıl okunur?** Sol üst: kalan ve doğru tahmin edilen öğrenciler. Sağ üst: kaldığı halde model "
            "\"geçer\" dedi (**yanlış evet**, en tehlikeli hata: yardım gereken öğrenci gözden kaçar). "
            "Sol alt: geçtiği halde model \"kalır\" dedi (yanlış hayır). Sağ alt: geçen ve doğru tahmin edilenler.")


def tahmin_sekmesi(model, sutunlar):
    st.write("Öğrencinin bilgilerini seç ve **Tahmin et**'e bas.")

    secimler, etiketli = {}, {}
    for sutun, (etiket, secenekler) in SECENEKLER.items():
        secim = st.selectbox(etiket, list(secenekler.keys()))
        secimler[sutun] = secenekler[secim]
        etiketli[f"{sutun}_{secenekler[secim]}"] = f"{etiket}: {secim}"

    if not st.button("Tahmin et", type="primary", width="stretch"):
        return

    kodlu = pd.get_dummies(pd.DataFrame([secimler])).astype(int).reindex(columns=sutunlar, fill_value=0)
    olasilik = model.predict_proba(kodlu)[0, 1]

    if olasilik >= 0.5:
        st.success(f"## ✅ GEÇER\nGeçme olasılığı: **%{olasilik * 100:.0f}**")
    else:
        st.error(f"## ❌ KALIR\nGeçme olasılığı: **%{olasilik * 100:.0f}**. "
                 "Bu öğrenci ek destek (etüt, hazırlık kursu) için önceliklendirilebilir.")

    # Her seçimin etkisi, aynı özelliğin diğer seçeneklerinin ortalamasına göre ölçülür.
    # (Referans kategorinin katsayısı 0 olduğu için, doğrudan katsayıya bakınca "Kız" gibi seçimler etkisiz görünürdü.)
    katsayilar = pd.Series(model.coef_[0], index=sutunlar)
    katki = {}
    for sutun, (_, secenekler) in SECENEKLER.items():
        tum = {v: katsayilar.get(f"{sutun}_{v}", 0.0) for v in secenekler.values()}
        katki[f"{sutun}_{secimler[sutun]}"] = tum[secimler[sutun]] - np.mean(list(tum.values()))
    katki = pd.Series(katki)
    olumlu = [etiketli[k] for k, v in katki.sort_values(ascending=False).items() if v > 0]
    olumsuz = [etiketli[k] for k, v in katki.sort_values().items() if v < 0]
    sol, sag = st.columns(2)
    with sol:
        st.markdown("**👍 Geçme şansını artıranlar**")
        st.markdown("\n".join(f"- {m}" for m in olumlu) or "_Yok_")
    with sag:
        st.markdown("**👎 Geçme şansını azaltanlar**")
        st.markdown("\n".join(f"- {m}" for m in olumsuz) or "_Yok_")


st.set_page_config(page_title="Öğrenci Geçer mi?", page_icon="🎓", layout="centered")
st.title("🎓 Öğrenci Geçer mi?")
st.caption("Students Performance in Exams veri seti · Ortalaması 60 ve üzeri olan öğrenci **geçti** sayılır. "
           "Veri seti eğitim amaçlı yapay olarak üretilmiştir.")

df = veriyi_yukle()
modeller, sutunlar, y_test, tahminler = modelleri_egit()

sekme1, sekme2, sekme3 = st.tabs(["📊 Grafikler", "📈 Model Sonuçları", "🎓 Tahmin Et"])
with sekme1:
    grafikler_sekmesi(df)
with sekme2:
    model_sekmesi(y_test, tahminler)
with sekme3:
    tahmin_sekmesi(modeller["Logistic Regression"], sutunlar)
