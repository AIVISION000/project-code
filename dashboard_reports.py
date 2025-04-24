import streamlit as st
import numpy as np
import pandas as pd
import pickle
import os

# تحميل البيانات
team_control_path = "stubs/team_control.npy"
player_speeds_path = "stubs/player_speeds.pkl"

if not all(os.path.exists(p) for p in [team_control_path, player_speeds_path]):
    st.error("❗ Missing required data files: team_control.npy, player_speeds.pkl")
    st.stop()

team_control = np.load(team_control_path)
with open(player_speeds_path, "rb") as f:
    player_speeds = pickle.load(f)

# ⚙️ إعداد
st.set_page_config(layout="wide")
st.title("📈 Player & Team Performance Reports")

# إعداد بيانات اللاعبين
players_data = {}

for frame_id, speed_dict in enumerate(player_speeds):
    for pid, speed in speed_dict.items():
        players_data.setdefault(pid, {"speeds": [], "slow_frames": [], "distance": 0.0})
        players_data[pid]["speeds"].append(speed)
        if speed < 6:
            players_data[pid]["slow_frames"].append(frame_id)

# حساب المسافة التقديرية (نفترض 1 فريم ≈ 1 متر لحساب تقريبي)
for pid, data in players_data.items():
    speeds = np.array(data["speeds"])
    distance = np.sum(speeds) / 3.6 / 24  # تحويل من كم/س إلى متر/فريم بمعدل 24fps
    data["distance"] = distance

# واجهة اختيار لاعب
selected_pid = st.selectbox("👤 Select a Player ID", sorted(players_data.keys()))

# عرض تقرير اللاعب المحدد
player = players_data[selected_pid]
avg_speed = np.mean(player["speeds"])
slow_count = len(player["slow_frames"])
distance = player["distance"]

st.subheader(f"👤 Player {selected_pid} Report")
st.markdown(f"""
- **Average Speed:** {avg_speed:.2f} km/h  
- **Times Slow (< 6 km/h):** {slow_count}  
- **Estimated Distance Covered:** {distance:.2f} m
""")

# رسم بياني للسرعة
st.line_chart(player["speeds"])

# جدول ملخص لكل اللاعبين
st.subheader("📊 All Players Summary")
player_summary = pd.DataFrame([
    {
        "Player ID": pid,
        "Avg Speed (km/h)": np.mean(data["speeds"]),
        "Slow Count": len(data["slow_frames"]),
        "Distance (m)": data["distance"]
    }
    for pid, data in players_data.items()
])
st.dataframe(player_summary)

# تحليل الفريق
st.subheader("📈 Team Performance Analysis")
team1_ratio = np.sum(team_control == 1) / len(team_control) * 100
team2_ratio = np.sum(team_control == 2) / len(team_control) * 100

top_player = player_summary.sort_values(by="Distance (m)", ascending=False).iloc[0]

st.markdown(f"""
- **Team 1 Ball Control:** {team1_ratio:.2f}%
- **Team 2 Ball Control:** {team2_ratio:.2f}%
- **Top Performer:** Player {top_player['Player ID']} — {top_player['Distance (m)']:.2f} m
""")
