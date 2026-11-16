"""
dashboard.py - Dashboard Streamlit untuk dataset.csv
Jalankan (PowerShell, venv aktif):  streamlit run dashboard.py
"""
import os

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="IoT Multi-Protocol Traffic Analyzer", layout="wide")

LOKASI_DEFAULT = "dataset.csv"
if not os.path.exists(LOKASI_DEFAULT):
    LOKASI_DEFAULT = r"C:\Users\farel\Documents\capture\dataset.csv"

st.title("IoT Multi-Protocol Traffic Analyzer")
st.caption("Perbandingan traffic normal dan anomali pada MQTT, CoAP, dan HTTP "
           "berdasarkan behavioral indicators.")

# ---------- Sidebar ----------
st.sidebar.header("Dashboard Filter")
lokasi = st.sidebar.text_input("Lokasi dataset.csv", LOKASI_DEFAULT)
unggah = st.sidebar.file_uploader("Unggah dataset.csv", type="csv")

try:
    df = pd.read_csv(unggah if unggah is not None else lokasi, parse_dates=["timestamp"])
except Exception as e:
    st.error(f"Dataset tidak bisa dibuka: {e}")
    st.stop()

semua_proto = sorted(df["protocol"].unique())
semua_label = sorted(df["label"].unique())
semua_skenario = sorted(df["scenario"].unique())

proto = st.sidebar.multiselect("Protokol", semua_proto, default=semua_proto)
label = st.sidebar.multiselect("Tipe Traffic", semua_label, default=semua_label)
skenario = st.sidebar.multiselect("Skenario", semua_skenario, default=semua_skenario)

f = df[df["protocol"].isin(proto) & df["label"].isin(label) & df["scenario"].isin(skenario)]
if f.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

# ---------- Overview ----------
st.subheader("Traffic Overview")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Jendela Observasi (10 detik)", len(f))
k2.metric("Normal", int((f["label"] == "Normal").sum()))
k3.metric("Anomali", int((f["label"] == "Anomali").sum()))
k4.metric("Protokol", f["protocol"].nunique())

if "Anomali" not in set(f["label"]):
    st.info("Belum ada data anomali di dataset ini. Jalankan skenario anomali lalu buat ulang dataset.csv.")

per_proto = f.groupby(["protocol", "label"]).size().reset_index(name="jumlah")
st.plotly_chart(px.bar(per_proto, x="protocol", y="jumlah", color="label", barmode="group",
                       title="Jumlah Jendela Observasi per Protokol"), key="bar_proto")

# ---------- Skenario ----------
st.subheader("Skenario")
per_skenario = f.groupby(["scenario", "protocol"]).size().reset_index(name="jumlah")
st.plotly_chart(px.bar(per_skenario, x="scenario", y="jumlah", color="protocol",
                       title="Distribusi Data Berdasarkan Skenario"), key="bar_skenario")

# ---------- Timeline ----------
st.subheader("Traffic Timeline")
st.plotly_chart(px.scatter(f, x="timestamp", y="packet_rate", color="label", symbol="protocol",
                           title="Packet Rate Timeline"), key="timeline")

# ---------- Behavioral Indicators ----------
st.subheader("Behavioral Indicators")
st.caption("Perbandingan indikator perilaku antara traffic normal dan anomali.")
indikator = [
    ("packet_rate", "Packet Rate (paket/detik)"),
    ("byte_rate", "Byte Rate (byte/detik)"),
    ("connection_rate", "Connection Rate (koneksi/detik)"),
    ("session_duration", "Session Duration (detik)"),
]
kiri, kanan = st.columns(2)
for i, (kolom, judul) in enumerate(indikator):
    with (kiri if i % 2 == 0 else kanan):
        st.plotly_chart(px.box(f, x="label", y=kolom, color="protocol", title=judul),
                        key=f"box_{kolom}")

st.markdown("**Rata-rata per tipe traffic dan protokol**")
st.dataframe(
    f.groupby(["label", "protocol"])[[k for k, _ in indikator]].mean().round(3)
)

# ---------- Dataset Explorer ----------
st.subheader("Dataset Explorer")
st.dataframe(f.sort_values("timestamp"))
