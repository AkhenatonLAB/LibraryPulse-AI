🚀 How to Run

After installing all required packages:

python main.py

(Replace main.py with your actual file name if it differs.)
🛠️ Current Features

    Real-time person tracking using YOLOv8 and MediaPipe.

    Counter for the number of people entering and leaving a specified area.

    Debug arrows showing movement direction (currently enabled for testing purposes).

🐞 Known Issues

    Debug arrows may show reversed directions due to mirrored camera frames.
    This will be fixed when we transition to a proper, non-mirrored test environment.

📁 Project Structure
File/Folder	Description
main.py	Main Python file that handles camera input, tracking, and counting logic.
yolo11n.pt	Custom YOLO model file used for tracking.
requirements.txt	Python packages required to run the project.
README.md	You are here! Project documentation.
📌 Notes

    Debug features (like direction arrows) will either be removed or optimized (added to a debug mode) for production use.

    Project is still in active development; feedback and testing results are highly appreciated.

✨ Developed with care by Atılım University Students ✨