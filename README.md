
# 🎯 AI-Powered Football Match Analyzer

A real-time system that uses deep learning and computer vision to analyze football matches, track players and the ball, and provide instant insights to support coaches in decision-making.

---

## 📂 Project Structure

```
players_detect_project/
│
├── camera_movement_estimator/         # Estimate camera movement
├── development_and_analysis/          # Data cleaning and visual analysis
├── player_ball_assigner/              # Assign ball possession to player
├── speed_and_distance_estimator/      # Calculate player speed and distance
├── stubs/                             # Preprocessed files (Pickle)
├── team_assigner/                     # Detect team for each player
├── trackers/                          # Object tracking logic
├── view_transformer/                  # Convert camera view to top-down
├── best.pt                            # Trained YOLOv8 model weights
├── main.py                            # Main entry to run the full pipeline
└── yolo_inference.py                  # Inference script using YOLOv8
```

---

## 🧠 How It Works

- **Video Input**: The system accepts football match videos.
- **YOLOv8 Inference**: Detects players, referees, ball, and goalkeeper.
- **Tracking & Assignment**:
  - Tracks players and ball movement over time.
  - Assigns ball possession to the nearest player.
  - Assigns team labels and colors.
- **Analytics Modules**:
  - Calculates player speed, distance, and performance drops.
  - Detects camera movement to adjust accuracy.
  - Sends **real-time alerts** to the coach when tactics shift or performance declines.

---

## ✅ Key Features

- Real-time AI-based decision support for coaches.
- Precision tracking of players, ball, and game flow.
- Insights like ball possession %, sprint speed, tactical shifts.
- Modular design, easily extendable for future improvements.

---

## 🧪 Model Performance

| Class       | Accuracy |
|-------------|----------|
| Player      | 99.4%    |
| Goalkeeper  | 94.8%    |
| Referee     | 97.7%    |
| Ball        | 59.9% ⚠️  |

> Tested on 50 real match clips. Ball detection will be improved with more data.

---

## 🚧 Future Plans

- Improve ball detection accuracy with more diverse data.
- Add user interface for live visualization.
- API integration for live camera input.
- Full match testing in real-world environments.

---

## 🤝 Contributors & Support

Built as part of the **SDAIA AI League Hackathon**, with the goal of empowering sports strategy using AI.
