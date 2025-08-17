```bash
my_face_auth_app/
│── app.py               # Entry point (Tkinter UI)
│── config.py            # DB config
│── requirements.txt     # Dependencies
│
├── db/
│   └── database.py      # MySQL connection + queries
│
├── face/
│   ├── detector.py      # Face detection logic (OpenCV Haar Cascade)
│   ├── trainer.py       # Train face recognizer (LBPH)
│   └── recognizer.py    # Recognition + authentication
│
├── ui/
│   ├── login.py         # Login window
│   ├── register.py      # Registration window
│   └── dashboard.py     # Dashboard after login
│
├── models/
│   └── haarcascade_frontalface_default.xml   # Haar Cascade file
│
└── data/
    └── faces/           # Captured face images per user
```