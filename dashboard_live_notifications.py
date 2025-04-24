import streamlit as st
import cv2
import time
import numpy as np
import pickle
import os

# 📂 ملفات البيانات
team_control_path = "stubs/team_control.npy"
player_speeds_path = "stubs/player_speeds.pkl"
video_path = "output_videos/output_video.avi"

# التحقق من وجود الملفات
if not all(os.path.exists(p) for p in [team_control_path, player_speeds_path, video_path]):
    st.error("❗ Please ensure the video and data files (team_control.npy, player_speeds.pkl) exist.")
    st.stop()

# تحميل البيانات
team_control = np.load(team_control_path)
with open(player_speeds_path, "rb") as f:
    player_speeds = pickle.load(f)

# إعداد الصفحة
st.set_page_config(layout="wide")

# ✅ تصميم CSS حديث
st.markdown("""
    <style>
    body {
        background-color: #0F1117;
        color: #E4E6EB;
        font-family: 'Segoe UI', sans-serif;
    }

    .video-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 20px;
        position: relative;
    }

    .video-container img {
        border-radius: 20px;
        border: 2px solid #00FFAA;
        box-shadow: 0 12px 24px rgba(0, 255, 170, 0.2);
    }

    /* إشعارات ثابتة في الجهة اليمنى */
    .notification-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 350px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .stAlert {
        background: rgba(0, 0, 0, 0.5);
        border-radius: 10px;
        padding: 12px;
        color: white;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
    }

    </style>
""", unsafe_allow_html=True)

# عنوان الصفحة
st.markdown(
    "<h1 style='text-align: center; font-size: 3em; color: #00FFAA;'>⚽️ Live Football Match Dashboard</h1>",
    unsafe_allow_html=True
)

# اختيار حجم الفيديو
video_size = st.selectbox("🎥 اختر حجم الفيديو:", ["Small", "Medium", "Large"], index=2)
video_width, video_height = {
    "Small": (640, 360),
    "Medium": (960, 540),
    "Large": (1280, 720)
}[video_size]

# عناصر واجهة المستخدم
frame_placeholder = st.empty()
info_placeholder = st.empty()

# فتح الفيديو
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
frame_delay = 1.0 / fps
frame_id = 0

# إشعارات وتحكمات
control_alert_window = int(fps * 10)
speed_alert_window = int(fps * 5)
slow_threshold = 6
slow_tracker = {}

alerts_list_speed = []
alerts_list_possession = []

last_alerts_speed = set()
last_alerts_possession = set()

# تحميل أولي
with st.spinner("⏳ تحميل الفيديو والبيانات..."):
    time.sleep(1)

# تشغيل الفيديو
st.markdown('<div class="video-container">', unsafe_allow_html=True)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret or frame_id >= len(team_control):
        break

    alerts_speed = []
    alerts_possession = []

    # تحليل الاستحواذ
    if frame_id >= control_alert_window:
        window = team_control[frame_id - control_alert_window:frame_id]
        if np.sum(window == 2) / len(window) > 0.6:
            alerts_possession.append("Team 2 has dominated possession for over 10 seconds!")

    # تحليل السرعة
    if frame_id < len(player_speeds):
        speed_data = player_speeds[frame_id]
        for pid, speed in speed_data.items():
            if speed < slow_threshold:
                slow_tracker.setdefault(pid, []).append(frame_id)
            else:
                slow_tracker[pid] = []
            if len(slow_tracker[pid]) >= speed_alert_window:
                alerts_speed.append(f"Player {pid} has been slow (< {slow_threshold} km/h) for too long!")

    # حفظ الإشعارات الحديثة فقط
    alerts_list_speed.extend(list(set(alerts_speed) - last_alerts_speed))
    alerts_list_possession.extend(list(set(alerts_possession) - last_alerts_possession))

    # عرض الفيديو
    frame_resized = cv2.resize(frame, (video_width, video_height))
    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
    frame_placeholder.image(frame_rgb, channels="RGB")

    # معلومات الاستحواذ
    if frame_id > 0:
        team1_pct = np.sum(team_control[:frame_id] == 1) / frame_id * 100
        team2_pct = np.sum(team_control[:frame_id] == 2) / frame_id * 100
        info_placeholder.markdown(f"""
        - Team 1 Ball Control: **{team1_pct:.2f}%**
        - Team 2 Ball Control: **{team2_pct:.2f}%**
        """)
    else:
        info_placeholder.markdown("Initializing...")

    # ✅ إشعارات السرعة الحديثة فقط في الشريط الجانبي
    with st.container():
        unique_speed_alerts = list(set(alerts_list_speed) - last_alerts_speed)
        if unique_speed_alerts:
            st.markdown("<h4 style='color:#00FFAA;'>🐢 تنبيهات السرعة</h4>", unsafe_allow_html=True)
            for alert in unique_speed_alerts:
                st.markdown(f"""
                    <div class="stAlert">
                        ⚠️ {alert}
                    </div>
                """, unsafe_allow_html=True)
            last_alerts_speed.update(unique_speed_alerts)

    # ✅ إشعارات الاستحواذ الحديثة فقط في الشريط الجانبي
    with st.container():
        unique_possession_alerts = list(set(alerts_list_possession) - last_alerts_possession)
        if unique_possession_alerts:
            st.markdown("<h4 style='color:#FFA500;'>🎯 تنبيهات الاستحواذ</h4>", unsafe_allow_html=True)
            for alert in unique_possession_alerts:
                st.markdown(f"""
                    <div class="stAlert">
                        ⚠️ {alert}
                    </div>
                """, unsafe_allow_html=True)
            last_alerts_possession.update(unique_possession_alerts)

    frame_id += 1
    time.sleep(frame_delay)

cap.release()
