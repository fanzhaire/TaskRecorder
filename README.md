# TaskRecorder – Personal Task Management System 🗂️

> **Built with ChatGPT** – This project was created with help from OpenAI’s ChatGPT to demonstrate that even without a formal IT background, anyone can build a fully functional personal task-tracking tool.

**TaskRecorder** combines a modern Tkinter GUI with a minimal Flask backend for LAN-based task transfer. Everything runs locally — no cloud, no subscriptions, no database.

---

## ✨ Key Features

- 📝 Add, edit, delete tasks with notes, priority, and due date  
- 📌 Automatically sorted by priority and due date  
- 🔔 Popup reminders for overdue or soon-due tasks (≤ 5 days)  
- 📂 Completed tasks view with edit/restore options  
- 🔐 Password protection at startup  
- 🔄 LAN task transfer to another PC on the same Wi-Fi  

---

## 💻 Quick Start & Customization

> ⚙️ Requires **Python 3.7+**

```bash
# Step 1 — Install required packages
pip install -r requirements.txt

# Step 2 — Start the backend server (receives tasks from others)
cd backend
python receive_tasks.py   # default port is 6789

# Step 3 — Launch the GUI application
cd ../frontend
python task_recorder.py

# Optional: Change the login password
# Open frontend/task_recorder.py and find:
#     if password_entry.get() == "123456":
# Replace "123456" with your own password, e.g. "abcd1234"

# Optional: Make the password secure using an environment variable:
#     import os
#     if password_entry.get() == os.getenv("TASKRECORDER_PWD", "990708"):
# Then set it:
#     Linux/macOS: export TASKRECORDER_PWD="your-secret"
#     Windows:     setx TASKRECORDER_PWD "your-secret"

# Optional: Configure LAN IPs for task transfer
# In the same file, locate the `colleagues` dictionary:
#     colleagues = {
#         "Josh": "192.168.1.12",
#         "Alen": "192.168.1.13"
#     }
# Replace with your own teammate names and IP addresses.

