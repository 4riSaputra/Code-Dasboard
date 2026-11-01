import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# =========================================================
# KONFIGURASI HALAMAN
# =========================================================

st.set_page_config(
    page_title="IoT Traffic Analyzer",
    page_icon="📡",
    layout="wide"
)


# =========================================================
# JUDUL
# =========================================================

st.title("📡 IoT Multi-Protocol Traffic Analyzer")

st.write(
    "Dashboard analisis traffic IoT untuk membandingkan "
    "traffic normal dan traffic anomali pada MQTT, CoAP, dan HTTP."
)

st.divider()


# =========================================================
# MEMBUAT DATA CONTOH
# =========================================================
# Data ini hanya digunakan sementara.
# Nanti akan kita ganti dengan CSV hasil penelitian.


np.random.seed(42)

jumlah_data = 500


protocol = np.random.choice(
    ["MQTT", "CoAP", "HTTP"],
    jumlah_data
)


label = np.random.choice(
    ["Normal", "Anomaly"],
    jumlah_data,
    p=[0.75, 0.25]
)


scenario = []

for x in label:

    if x == "Normal":

        scenario.append("Normal Traffic")

    else:

        scenario.append(
            np.random.choice(
                [
                    "Connection Burst",
                    "Abnormal Publishing/Request",
                    "Abnormal Subscription/Observe/Polling",
                    "Abnormal Topic/Resource/Endpoint",
                    "Mixed Traffic"
                ]
            )
        )


# =========================================================
# MEMBUAT DATAFRAME
# =========================================================

df = pd.DataFrame({

    "timestamp": pd.date_range(
        start="2026-01-01",
        periods=jumlah_data,
        freq="min"
    ),

    "protocol": protocol,

    "source_ip": np.random.choice(
        [
            "192.168.1.10",
            "192.168.1.11",
            "192.168.1.12",
            "192.168.1.13"
        ],
        jumlah_data
    ),

    "packet_rate": np.random.normal(
        100,
        25,
        jumlah_data
    ).clip(1),

    "byte_rate": np.random.normal(
        20000,
        4000,
        jumlah_data
    ).clip(100),

    "connection_rate": np.random.normal(
        5,
        1.5,
        jumlah_data
    ).clip(0.1),

    "session_duration": np.random.normal(
        30,
        8,
        jumlah_data
    ).clip(1),

    "label": label,

    "scenario": scenario
})


# =========================================================
# MEMBUAT ANOMALY LEBIH TINGGI
# =========================================================

df.loc[
    df["label"] == "Anomaly",
    "packet_rate"
] *= 4


df.loc[
    df["label"] == "Anomaly",
    "byte_rate"
] *= 3


df.loc[
    df["label"] == "Anomaly",
    "connection_rate"
] *= 5


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📊 Dashboard Filter")

st.sidebar.write("Gunakan filter untuk melihat traffic tertentu.")


# ---------------------------------------------------------
# FILTER PROTOCOL
# ---------------------------------------------------------

protocol_filter = st.sidebar.selectbox(
    "Protocol",
    [
        "All",
        "MQTT",
        "CoAP",
        "HTTP"
    ]
)


# ---------------------------------------------------------
# FILTER LABEL
# ---------------------------------------------------------

label_filter = st.sidebar.selectbox(
    "Traffic Type",
    [
        "All",
        "Normal",
        "Anomaly"
    ]
)


# ---------------------------------------------------------
# FILTER SCENARIO
# ---------------------------------------------------------

scenario_filter = st.sidebar.selectbox(
    "Scenario",
    [
        "All"
    ]
    + sorted(df["scenario"].unique().tolist())
)


# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df.copy()


if protocol_filter != "All":

    filtered_df = filtered_df[
        filtered_df["protocol"] == protocol_filter
    ]


if label_filter != "All":

    filtered_df = filtered_df[
        filtered_df["label"] == label_filter
    ]


if scenario_filter != "All":

    filtered_df = filtered_df[
        filtered_df["scenario"] == scenario_filter
    ]


# =========================================================
# KPI
# =========================================================

st.header("📌 Traffic Overview")


total_traffic = len(filtered_df)


normal_traffic = len(
    filtered_df[
        filtered_df["label"] == "Normal"
    ]
)


anomaly_traffic = len(
    filtered_df[
        filtered_df["label"] == "Anomaly"
    ]
)


total_protocol = filtered_df["protocol"].nunique()


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Traffic",
        f"{total_traffic:,}"
    )


with col2:

    st.metric(
        "Normal Traffic",
        f"{normal_traffic:,}"
    )


with col3:

    st.metric(
        "Anomaly Traffic",
        f"{anomaly_traffic:,}"
    )


with col4:

    st.metric(
        "Protocol",
        total_protocol
    )


st.divider()


# =========================================================
# TRAFFIC BERDASARKAN PROTOCOL
# =========================================================

st.header("📡 Traffic by Protocol")


protocol_data = (
    filtered_df["protocol"]
    .value_counts()
    .reset_index()
)


protocol_data.columns = [
    "protocol",
    "count"
]


fig_protocol = px.bar(
    protocol_data,
    x="protocol",
    y="count",
    title="Jumlah Traffic Berdasarkan Protocol",
    labels={
        "protocol": "Protocol",
        "count": "Jumlah Traffic"
    }
)


st.plotly_chart(
    fig_protocol,
    use_container_width=True
)


# =========================================================
# NORMAL VS ANOMALY
# =========================================================

st.header("🚨 Normal vs Anomaly")


label_data = (
    filtered_df["label"]
    .value_counts()
    .reset_index()
)


label_data.columns = [
    "label",
    "count"
]


fig_label = px.pie(
    label_data,
    names="label",
    values="count",
    title="Perbandingan Traffic Normal dan Anomaly",
    hole=0.4
)


st.plotly_chart(
    fig_label,
    use_container_width=True
)


# =========================================================
# BEHAVIORAL INDICATORS
# =========================================================

st.header("📈 Behavioral Indicators")

st.write(
    "Perbandingan indikator behavioral antara "
    "traffic normal dan traffic anomaly."
)


# ---------------------------------------------------------
# PACKET RATE
# ---------------------------------------------------------

col1, col2 = st.columns(2)


with col1:

    fig_packet = px.box(
        filtered_df,
        x="label",
        y="packet_rate",
        title="Packet Rate",
        labels={
            "label": "Traffic Type",
            "packet_rate": "Packet Rate"
        }
    )

    st.plotly_chart(
        fig_packet,
        use_container_width=True
    )


# ---------------------------------------------------------
# BYTE RATE
# ---------------------------------------------------------

with col2:

    fig_byte = px.box(
        filtered_df,
        x="label",
        y="byte_rate",
        title="Byte Rate",
        labels={
            "label": "Traffic Type",
            "byte_rate": "Byte Rate"
        }
    )

    st.plotly_chart(
        fig_byte,
        use_container_width=True
    )


# ---------------------------------------------------------
# CONNECTION RATE
# ---------------------------------------------------------

col1, col2 = st.columns(2)


with col1:

    fig_connection = px.box(
        filtered_df,
        x="label",
        y="connection_rate",
        title="Connection Rate",
        labels={
            "label": "Traffic Type",
            "connection_rate": "Connection Rate"
        }
    )

    st.plotly_chart(
        fig_connection,
        use_container_width=True
    )


# ---------------------------------------------------------
# SESSION DURATION
# ---------------------------------------------------------

with col2:

    fig_session = px.box(
        filtered_df,
        x="label",
        y="session_duration",
        title="Session Duration",
        labels={
            "label": "Traffic Type",
            "session_duration": "Duration"
        }
    )

    st.plotly_chart(
        fig_session,
        use_container_width=True
    )


# =========================================================
# ANOMALY SCENARIO
# =========================================================

st.header("⚠️ Anomaly Scenario")


anomaly_data = filtered_df[
    filtered_df["label"] == "Anomaly"
]


if len(anomaly_data) > 0:

    scenario_data = (
        anomaly_data["scenario"]
        .value_counts()
        .reset_index()
    )

    scenario_data.columns = [
        "scenario",
        "count"
    ]


    fig_scenario = px.bar(
        scenario_data,
        x="scenario",
        y="count",
        title="Distribusi Anomaly Berdasarkan Scenario",
        labels={
            "scenario": "Scenario",
            "count": "Jumlah"
        }
    )


    fig_scenario.update_layout(
        xaxis_tickangle=-25
    )


    st.plotly_chart(
        fig_scenario,
        use_container_width=True
    )

else:

    st.info(
        "Tidak ada traffic anomaly berdasarkan filter saat ini."
    )


# =========================================================
# TIMELINE
# =========================================================

st.header("⏱️ Traffic Timeline")


timeline_df = filtered_df.copy()


timeline_df["timestamp"] = pd.to_datetime(
    timeline_df["timestamp"]
)


timeline_df = timeline_df.sort_values(
    "timestamp"
)


fig_timeline = px.scatter(
    timeline_df,
    x="timestamp",
    y="packet_rate",
    color="label",
    hover_data=[
        "protocol",
        "source_ip",
        "scenario"
    ],
    title="Packet Rate Timeline"
)


st.plotly_chart(
    fig_timeline,
    use_container_width=True
)


# =========================================================
# DATASET
# =========================================================

st.header("🔎 Dataset Explorer")


st.dataframe(
    filtered_df,
    use_container_width=True,
    height=400
)


# =========================================================
# FOOTER
# =========================================================

st.divider()


st.caption(
    "IoT Multi-Protocol Traffic Analysis Dashboard | "
    "Prototype menggunakan data simulasi"
)
