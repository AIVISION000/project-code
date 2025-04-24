from utils.video_utils import read_video, save_video
from trackers.tracker import Tracker
import cv2
import numpy as np
import pickle
import os

from team_assigner.team_assigner import TeamAssigner
from player_ball_assigner.player_ball_assigner import PlayerBallAssigner
from camera_movement_estimator.camera_movement_estimator import CameraMovementEstimator
from view_transformer.view_transformer import ViewTransformer
from speed_and_distance_estimator.speed_and_distance_estimator import SpeedAndDistance_Estimator

def main():
    # 📥 تحميل الفيديو
    video_frames = read_video('input_videos/08fd33_4.mp4')

    # 🧠 تتبع العناصر
    tracker = Tracker('best.pt')
    tracks = tracker.get_object_tracks(video_frames, read_from_stub=False)
    tracker.add_position_to_tracks(tracks)

    # 📷 تقدير حركة الكاميرا
    camera_estimator = CameraMovementEstimator(video_frames[0])
    camera_movement = camera_estimator.get_camera_movement(video_frames)
    camera_estimator.add_adjust_positions_to_tracks(tracks, camera_movement)

    # 🗺️ تحويل الإحداثيات
    transformer = ViewTransformer()
    transformer.add_transformed_position_to_tracks(tracks)

    # ⚽ إكمال تتبع الكرة
    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])

    # 🏃‍♂️ حساب السرعة والمسافة
    speed_estimator = SpeedAndDistance_Estimator()
    speed_estimator.add_speed_and_distance_to_tracks(tracks)

    # 🏳️ تعيين الفريق لكل لاعب
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(video_frames[0], tracks["players"][0])

    for frame_num, players in enumerate(tracks["players"]):
        for pid, player in players.items():
            team = team_assigner.get_player_team(video_frames[frame_num], player["bbox"], pid)
            player["team"] = team
            player["team_color"] = team_assigner.team_colors[team]

    # 🧠 حساب الاستحواذ
    team_control = []
    player_assigner = PlayerBallAssigner()

    for frame_num, players in enumerate(tracks["players"]):
        ball_bbox = tracks["ball"][frame_num][1]["bbox"]
        assigned_player = player_assigner.assign_ball_to_player(players, ball_bbox)
        if assigned_player != -1:
            players[assigned_player]["has_ball"] = True
            team_control.append(players[assigned_player]["team"])
        else:
            team_control.append(team_control[-1] if team_control else 1)

    team_control = np.array(team_control)

    # 🧪 حفظ سرعات اللاعبين لكل فريم
    player_speeds = []
    for frame in tracks["players"]:
        speeds = {}
        for pid, info in frame.items():
            if "speed" in info:
                speeds[pid] = info["speed"]
        player_speeds.append(speeds)

    # 🖼️ رسم الفيديو المعالج
    output_frames = tracker.draw_annotations(video_frames, tracks, team_control)
    output_frames = camera_estimator.draw_camera_movement(output_frames, camera_movement)
    speed_estimator.draw_speed_and_distance(output_frames, tracks)

    # 💾 إنشاء مجلدات وتخزين الملفات
    os.makedirs("output_videos", exist_ok=True)
    os.makedirs("stubs", exist_ok=True)

    save_video(output_frames, "output_videos/output_video.avi")
    np.save("stubs/team_control.npy", team_control)

    with open("stubs/player_speeds.pkl", "wb") as f:
        pickle.dump(player_speeds, f)

    print("✅ Processing complete. Video and data saved.")

if __name__ == '__main__':
    main()
