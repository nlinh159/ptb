import streamlit as st
import pandas as pd
import time

from distance import haversine, driving_distance, format_time

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="Photobooth Finder HN",
    page_icon="📸",
    layout="centered"
)

st.title("📸 Photobooth Finder – Hà Nội")

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_data():
    return pd.read_csv("photobooth_hn.csv")

df = load_data()

# ======================
# USER INPUT
# ======================
st.subheader("📍 Vị trí hiện tại")

USER_LAT = st.number_input(
    "Latitude",
    value=21.0334778,
    format="%.7f"
)

USER_LON = st.number_input(
    "Longitude",
    value=105.7707209,
    format="%.7f"
)

MODE = st.radio(
    "Chế độ chạy",
    ["Nhanh, không tốn API", "Kết hợp (chính xác hơn)"]
)

MAX_DISTANCE_KM = st.slider(
    "Giới hạn quãng đường (km)",
    min_value=1,
    max_value=20,
    value=5
)

HAVERSINE_BUFFER = st.slider(
    "Chim bay (km)",
    min_value=1.0,
    max_value=10.0,
    value=4.0,
    step=0.1
)

run = st.button("🔍 Tìm photobooth")

# ======================
# RUN LOGIC
# ======================
if run:
    start_time = time.time()
    results = []

    with st.spinner("Đang tính toán khoảng cách..."):
        for _, row in df.iterrows():
            name = row["Tên"]
            address = row["Quận / huyện"]
            booth_lat = float(row["lat"])
            booth_lon = float(row["lon"])

            # 1️⃣ Haversine filter
            air_km = haversine(
                USER_LAT, USER_LON,
                booth_lat, booth_lon
            )

            if air_km > HAVERSINE_BUFFER:
                continue

            map_link = (
                f"https://www.google.com/maps/dir/"
                f"{USER_LAT},{USER_LON}/{booth_lat},{booth_lon}"
            )

            # ===== MODE: HAVERSINE =====
            if MODE.startswith("Nhanh"):
                results.append({
                    "Tên": name,
                    "Quận / Huyện": address,
                    "Khoảng cách (chim bay, km)": round(air_km, 2),
                    "Google Maps": map_link
                })
                continue

            # ===== MODE: HYBRID =====
            try:
                km, seconds = driving_distance(
                    USER_LAT, USER_LON,
                    booth_lat, booth_lon
                )
                time.sleep(1)  # tránh rate limit

                if km <= MAX_DISTANCE_KM:
                    results.append({
                        "Tên": name,
                        "Quận / Huyện": address,
                        "Chim bay (km)": round(air_km, 2),
                        "Đường đi (km)": round(km, 2),
                        "Thời gian": format_time(seconds),
                        "Google Maps": map_link
                    })

            except Exception as e:
                st.warning(f"Lỗi API với {name}")
                continue
    end_time = time.time()
    run_time = end_time - start_time
    # ======================
    # OUTPUT
    # ======================
    if results:
        st.success(f"✅ Tìm thấy {len(results)} photobooth")
        st.caption(f"⏱️ Thời gian xử lý: {run_time:.1f} giây")
        
        df_result = pd.DataFrame(results)

        if MODE.startswith("Nhanh"):
            distance_col = "Khoảng cách (chim bay, km)"
        else:
            distance_col = "Chim bay (km)"

        df_result = df_result.sort_values(by=distance_col)
        
        df_result.insert(0, "STT", range(1, len(df_result) + 1))

        st.dataframe(
            df_result,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("❌ Không tìm thấy địa điểm phù hợp")
