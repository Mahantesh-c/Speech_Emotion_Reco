# 🎙️ Speech Emotion Recognition Web App

> 🎧 Detect emotions from your voice using AI!  
> Built with **Django**, **Tailwind CSS**, and **JavaScript** – featuring a modern, responsive UI with real-time feedback and emoji visualization.

![Speech Emotion Recognition](https://img.shields.io/badge/Emotion-Detection-blueviolet?style=for-the-badge)
![Made with Django](https://img.shields.io/badge/Backend-Django-green?style=for-the-badge)
![Frontend](https://img.shields.io/badge/Frontend-TailwindCSS-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

---

## 🖼️ UI Preview

> ⚠️ _Replace the image link below with actual screenshots once available._

![UI Preview](https://via.placeholder.com/1000x500.png?text=Speech+Emotion+Recognition+UI+Preview)


---

## 🎯 Features

- 🔐 **User Authentication** – Register, Login, Logout, Forgot Password
- 🎤 **Voice Input** – Record voice or upload `.wav`/`.mp3` files
- 🧠 **Emotion Detection** – AI model detects real emotions from speech
- 😄 **Real-Time Emoji Feedback** – Dynamic UI updates with detected emotion
- 📊 **Visualizations** – Chart view of results and emotion analytics
- 🌗 **Dark Mode** – Beautiful toggleable dark/light theme
- 📱 **Fully Responsive** – Optimized for mobile, tablet, and desktop

---

## ⚙️ Installation Guide

Follow these steps to set up the project locally:

### 📦 Prerequisites

- Python 3.8+
- pip
- Git

### 🧰 Step-by-step Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/speech-emotion-recognition.git
cd speech-emotion-recognition

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install required packages
pip install -r requirements.txt

# 4. Apply Django migrations
python manage.py migrate

# 5. Run the development server
python manage.py runserver

# 6. Visit the app in your browser
# Open http://127.0.0.1:8000
