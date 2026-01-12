# 🐞 SimpleBugSim

A simple yet dynamic bug evolution simulator built with Python, Pygame, and PyQtGraph.
Each "bug" is represented by a moving ball with unique life attributes such as size, speed, attack, defense, and reproduction rate.
The simulation evolves over time — populations rise and fall as energy fluctuates, bugs compete, and immortals emerge.

---

## 🚀 Features

- 🎮 Pygame Simulation Window — visually displays all bugs moving and interacting in real time.
- 📊 Live Statistics Graph — powered by PyQtGraph, showing:
  - Universe Energy
  - Bug Population
  - Average Radius
  - Immortal Count
- 🧬 Individualized Traits — each bug has randomized life stats affecting how they survive and reproduce.
- 🔄 Dynamic Evolution — populations naturally change over time based on energy balance and interactions.

---

## 🧩 Technologies Used

- Python 3.x
- Pygame
- PyQtGraph
- threading
- random

---

## ⚙️ Installation

1. Clone the repository:
   ```
   git clone https://github.com/Nocivofrank/SimpleBugSim.git
   cd SimpleBugSim
   ```

2. (Recommended) Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # on Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
If you don’t have a requirements.txt yet, here’s what it should include:
pygame
pyqtgraph
PyQt5

---

## ▶️ Usage

Run the simulation:
python main.py

Once launched:
- The Pygame window shows your bugs in action.
- The PyQtGraph window tracks key simulation stats in real time.

---

## 🔬 How It Works

- Each bug is initialized with randomized attributes:
  - size, speed, attack, defense, reproduction_rate, etc.
- Energy is shared globally and individually; bugs consume energy and reproduce if possible.
- The PyQtGraph window continuously updates live metrics for easy observation of population trends.

---

## 🧠 Future Plans

- Add mutation mechanics between generations
- Implement predator/prey behaviors
- Add configurable settings (bug count, energy rate, mutation strength)
- Save and replay simulation sessions
- Export data for analysis (CSV/JSON)

---

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome!
Feel free to open an issue or submit a pull request.

---

## 💬 Author

Created by Nocivofrank
If you like this project, give it a ⭐ on GitHub!



