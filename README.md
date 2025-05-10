# Factorionline (not a server)  
### Video Demo: https://www.youtube.com/watch?v=pL-efrb2YwU
Keep your Factorio multiplayer games in sync—without a dedicated server!

### Description:
**Factorionline** is a simple tool that automatically pushes your Factorio game saves to a GitHub repository and pulls the latest version before each session. This makes it easy to play with friends asynchronously, allowing each player to contribute to the same game without needing to be online at the same time.

### 🔧 Features  
- 📂 Sync save files to/from GitHub  
- 🤝 Share your game with friends effortlessly  
- 🕒 Play asynchronously—no server required  

### 🚀 How It Works  
- Each player installs the tool—everything else is automatic.  
- Then, when opening the game, you’ll be notified if the save has been successfully retrieved.  
  ![Screenshot 2025-05-08 104441](https://github.com/user-attachments/assets/8543eced-3d82-40e2-8f42-0981d5452bab)

- The tool pulls the latest save file from GitHub and places it in a folder with the save(s), if you're online.  
 ![Screenshot 2025-05-08 104527](https://github.com/user-attachments/assets/bf215426-63d8-42a2-9095-e33811e5b650)

- After playing, it commits and pushes the updates when saving, and notifies you about the process.
  ![image](https://github.com/user-attachments/assets/3057fea8-da00-4fb7-b663-40cef89da435)

- In case of internet disconnection or if another user is online, Factorionline handles it for you.  
![image](https://github.com/user-attachments/assets/3ee41cdd-71c5-49ae-b426-f83fede868ce)

Perfect for casual co-op games or long-running factory builds with friends!

### ⚠️ Warnings
- For now, only available on Windows.
- The tool requires an SSH key to be configured on your system.
- You must configure the path to your local Factorio save files manually.
- It does not support simultaneous play by multiple users (It would be desirable to support merging changes in the future to allow multiple players simultaneously).

### 🛠️ Project Status  
- This project is still in early development and has many features yet to be implemented.  
- If you find it useful or interesting, feel free to ⭐️ the repo—your support will motivate me to keep improving it!
