<p align="center">
  <img width="220" src="https://neximagen.mysterysd.in/view/AgACAgUAAyEGAASYZ-7zAAMwaBUMbSvqR69hW2saLELmE8GLSIcAAvnGMRtQGKhUwoEvEB6833ABAAMCAAN4AAM2BA" alt="Downloader Zone Logo">
</p>

<p align="center">
  <b>Telegram Auto Delete Bot</b><br>
  <i>Auto Delete Bot is a lightweight and efficient Telegram bot built using python-telegram-bot v22.0 and Flask, designed to help keep your groups or channels clean by automatically deleting messages after a certain time or based on specific rules.</i>
</p>

<p align="center">
  <a href="https://github.com/DOWNLOADER-ZONE/Telegram-Auto-Delete-Bot"><img src="https://img.shields.io/github/stars/DOWNLOADER-ZONE/Telegram-Auto-Delete-Bot?style=flat-square&color=yellow&logo=github"/></a>
  <a href="https://github.com/DOWNLOADER-ZONE/Telegram-Auto-Delete-Bot"><img src="https://img.shields.io/github/forks/DOWNLOADER-ZONE/Telegram-Auto-Delete-Bot?style=flat-square&color=blue&logo=github"/></a>
  <a href="https://t.me/DOWNLOADERZONEUPDATES"><img src="https://img.shields.io/badge/Telegram-Channel-blue?style=flat-square&logo=telegram"/></a>
  <a href="https://t.me/DZONEDISCUSSION"><img src="https://img.shields.io/badge/Support-Group-blueviolet?style=flat-square&logo=telegram"/></a>
  <a href="https://github.com/DOWNLOADER-ZONE/Telegram-Auto-Delete-Bot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/DOWNLOADER-ZONE/Telegram-Auto-Delete-Bot?style=flat-square&color=success"/></a>
</p>


<h2>💡 Features</h2>
<ul>
  <li>✅ Built with <code>python-telegram-bot 22.0</code> and <code>Flask</code></li>
  <li>✅ Automatically deletes messages based on time</li>
  <li>✅ Supports custom delay globally</li>
  <li>✅ Runs 24/7 with <code>keep_alive()</code> Flask server</li>
  <li>✅ Fully async and CLI-friendly</li>
  <li>✅ Easy deployment on Replit / Render / PythonAnywhere etc</li>
</ul>

<h2>🛠 Requirements</h2>
<ul>
  <li>📦 <code>python-telegram-bot==22.0</code></li>
  <li>📦 <code>httpx==0.28.1</code></li>
  <li>📦 <code>flask</code></li>
  <li>📦 <code>PyMongo</code></li>
</ul>

<h2>📁 Project Structure</h2>
<pre><code>Telegram-Auto-Delete-Bot/
├── autodelete.py       # Main script (Bot Token , Admin to be added here)
├── keep_alive.py       # Helps keep project up using uptimer robot or similar services
└── requirements.txt    # This file contains all the requirements to be installed       
└── README.md           # About
</pre></code>

<h2>🚀 Usage</h2>
<p>Clone this repository:</p>
<pre><code>git clone https://github.com/DOWNLOADER-ZONE/Telegram-Auto-Delete-Bot.git</pre></code>
<pre><code>cd Telegram-Auto-Delete-Bot</pre></code>
<pre><code>pip install -r requirements.txt</code></pre>
<pre><code>python autodelete.py</code></pre>
<p>Add ur credentials in autodelete.py and run the script.</p>

<h2>🧠 How It Works</h2>
<p>Bot receives a message → Waits 30 seconds → Deletes it.</p>

<h2>❗ Common Errors</h2>
<p><strong>Keep-alive not working?</strong> Make sure Flask server is running and you are using a <code>threaded=True</code> or similar config in production.</p>
    
<h2>📃 License</h2>
<p>This project is licensed under the MIT License. See the LICENSE file for details.</p>

<p align="center">
  <b>Made with ❤️ by Downloader Zone</b>
</p>

