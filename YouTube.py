import sys
import os
import threading
import yt_dlp
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFileDialog, QTableWidget, QTableWidgetItem, QComboBox,
    QStackedWidget, QListWidget, QListWidgetItem, QMessageBox, QHeaderView
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import QSplashScreen, QLabel
from PyQt6.QtCore import Qt, QTimer

class SplashScreen(QSplashScreen):
    """A beautifully designed splash screen with red & black theme."""

    def __init__(self):
        super().__init__()

        # Set the splash screen size
        self.setFixedSize(600, 400)

        # Set background color (Black)
        self.setStyleSheet("background-color: #141414; color: white;")

        # Remove window borders
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Center the splash screen
        self.center_splash()

        # App Name Label (Golden Yellow)
        self.app_name = QLabel("YouTube Playlist Downloader", self)
        self.app_name.setStyleSheet("font-size: 28px; font-weight: bold; color: #ffcc00;")  # Golden Yellow
        self.app_name.move(130, 100)  # Adjust position

        # Developer Name Label (White)
        self.developer_name = QLabel("Developed by Ali Abdikhaliq (Ayatiin Projects)\nVisit: https:ayatiin.com/tools", self)
        # self.developer_name = QLabel("visit: https:ayatiin.com/tools", self)
        self.developer_name.setStyleSheet("font-size: 18px; color: #dddddd;")  # Light Grey
        self.developer_name.move(170, 160)

        # Version Label (Grey)
        self.version_label = QLabel("Version 1.0", self)
        self.version_label.setStyleSheet("font-size: 16px; color: #888888;")  # Dark Grey
        self.version_label.move(250, 220)

        # Bottom Bar (Red)
        self.bottom_bar = QLabel(self)
        self.bottom_bar.setStyleSheet("background-color: #c70039;")  # Red Bar
        self.bottom_bar.setGeometry(0, 370, 600, 30)  # Position at the bottom

        # Loading Text
        self.loading_text = QLabel("Loading...", self)
        self.loading_text.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        self.loading_text.move(260, 375)

    def center_splash(self):
        """Centers the splash screen on the screen."""
        screen = QApplication.primaryScreen().geometry()
        splash_size = self.geometry()
        x = (screen.width() - splash_size.width()) // 2
        y = (screen.height() - splash_size.height()) // 2
        self.move(x, y)


# Global Variables
download_path = os.path.expanduser("~")
playlist_name = ""
download_threads = {}
paused_downloads = {}

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()

        # Window Settings
        self.setWindowTitle("YouTube Playlist Downloader - Ultimate Version 🚀")
        self.setGeometry(100, 100, 950, 650)
        self.center_window()  # ✅ Call function to center the window
        self.setStyleSheet("background-color: #1E1E1E; color: white; font-size: 14px;")

        # Main Layout
        layout = QHBoxLayout(self)

        # Sidebar Navigation
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #252525; color: white; border: none; font-weight: bold;")
        self.sidebar.addItem(QListWidgetItem("🏠 Home"))
        # self.sidebar.addItem(QListWidgetItem("📜 Download History"))
        self.sidebar.addItem(QListWidgetItem("⚙️ Settings"))
        self.sidebar.addItem(QListWidgetItem("📖 About Us"))
        self.sidebar.addItem(QListWidgetItem("💰 Donate"))
        layout.addWidget(self.sidebar)

        # Page Manager (Stacked Widget)
        self.pages = QStackedWidget()
        layout.addWidget(self.pages)

        # Add Pages
        self.home_page = self.create_home_page()
        # self.history_page = self.create_history_page()
        self.settings_page = self.create_settings_page()
        self.about_page = self.create_about_page()
        self.donation_page = self.create_donation_page()

        self.pages.addWidget(self.home_page)
        # self.pages.addWidget(self.history_page)
        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(self.about_page)
        self.pages.addWidget(self.donation_page)

        self.sidebar.currentRowChanged.connect(self.switch_page)

        self.setLayout(layout)
    def center_window(self):
        """Centers the application window on the screen."""
        screen = QApplication.primaryScreen().geometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def switch_page(self, index):
        """Switch between pages when sidebar is clicked."""
        self.pages.setCurrentIndex(index)

    def create_home_page(self):
        """Creates the main home page for downloads."""
        page = QWidget()
        layout = QVBoxLayout()

        # URL Input & Fetch Button
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube Playlist URL")
        url_layout.addWidget(self.url_input)

        self.fetch_button = QPushButton("Fetch")
        self.fetch_button.setStyleSheet("background-color: #3498db; color: white; padding: 8px; border-radius: 5px;")
        self.fetch_button.clicked.connect(self.fetch_playlist_thread)
        url_layout.addWidget(self.fetch_button)

        layout.addLayout(url_layout)

        # Save Path & Browse Button
        path_layout = QHBoxLayout()
        self.path_label = QLabel(f"📁 Save To: {download_path}")
        path_layout.addWidget(self.path_label)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setStyleSheet("background-color: #f39c12; color: white; padding: 8px; border-radius: 5px;")
        self.browse_button.clicked.connect(self.browse_folder)
        path_layout.addWidget(self.browse_button)

        layout.addLayout(path_layout)

        # Format & Quality Selection
        format_quality_layout = QHBoxLayout()
        self.format_dropdown = QComboBox()
        self.format_dropdown.addItems(["mp4", "mp3"])
        self.quality_dropdown = QComboBox()
        self.quality_dropdown.addItems(["best", "1080", "720", "480"])
        format_quality_layout.addWidget(QLabel("🎞 Format:"))
        format_quality_layout.addWidget(self.format_dropdown)
        format_quality_layout.addWidget(QLabel("🔽 Quality:"))
        format_quality_layout.addWidget(self.quality_dropdown)
        layout.addLayout(format_quality_layout)

        # Playlist Table
        self.video_table = QTableWidget(0, 3)
        self.video_table.setHorizontalHeaderLabels(["Title", "Status", "URL"])
        self.video_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.video_table.setStyleSheet("QHeaderView::section { background-color: #444; color: white; padding: 5px; font-weight: bold; }")
        layout.addWidget(self.video_table)

        # Download Button
        button_layout = QHBoxLayout()
        self.download_button = QPushButton("Download Selected")
        self.download_button.clicked.connect(self.start_download_thread)
        self.download_button.setStyleSheet("background-color: #2ecc71; color: white; padding: 8px; border-radius: 5px;")
        button_layout.addWidget(self.download_button)

        self.clear_button = QPushButton("Clear List")
        self.clear_button.clicked.connect(self.clear_list)
        self.clear_button.setStyleSheet("background-color: #e67e22; color: white; padding: 8px; border-radius: 5px;")
        button_layout.addWidget(self.clear_button)

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        self.exit_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px; border-radius: 5px;")
        button_layout.addWidget(self.exit_button)

        layout.addLayout(button_layout)
        # layout.addLayout(layout)
        # self.setLayout(layout)
        page.setLayout(layout)
        return page
    def create_history_page(self):
        """Creates the Download History Page."""
        page = QWidget()
        layout = QVBoxLayout()

        self.history_table = QTableWidget(0, 3)
        self.history_table.setHorizontalHeaderLabels(["Title", "Status", "File Path"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setStyleSheet("QHeaderView::section { background-color: #444; color: white; padding: 5px; font-weight: bold; }")

        layout.addWidget(self.history_table)

        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px; border-radius: 5px;")
        self.clear_history_button.clicked.connect(self.clear_history)
        layout.addWidget(self.clear_history_button)
        
        page.setLayout(layout)
        return page
    def clear_history(self):
        """Clears the download history."""
        self.history_table.setRowCount(0)
    def clear_list(self):
        self.video_table.setRowCount(0)
    def browse_folder(self):
        """Allows user to select a save folder."""
        global download_path
        download_path = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        self.path_label.setText(f"📁 Save To: {download_path}")

    def fetch_playlist_thread(self):
        threading.Thread(target=self.fetch_playlist, daemon=True).start()

    def fetch_playlist(self):
        """Fetch playlist information."""
        global playlist_name
        url = self.url_input.text().strip()
        if not url:
            return

        try:
            ydl_opts = {"quiet": True, "extract_flat": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)

            playlist_name = info_dict.get("title", "Unknown Playlist").replace(" ", "_")
            self.video_table.setRowCount(0)

            for entry in info_dict["entries"]:
                row_position = self.video_table.rowCount()
                self.video_table.insertRow(row_position)
                self.video_table.setItem(row_position, 0, QTableWidgetItem(entry.get("title", "Unknown Title")))
                self.video_table.setItem(row_position, 1, QTableWidgetItem("Pending"))
                # self.video_table.setItem(row_position, 2, QTableWidgetItem("0%"))
                self.video_table.setItem(row_position, 2, QTableWidgetItem(entry["url"]))

        except Exception as e:
            print(f"Failed to fetch playlist: {e}")

    def start_download_thread(self):
        threading.Thread(target=self.start_download, daemon=True).start()

    def start_download(self):
        selected_rows = set(index.row() for index in self.video_table.selectionModel().selectedRows())

        if not selected_rows:
            for row in range(self.video_table.rowCount()):
                self.update_status(row, "⚠ No Selection")
            return


        for row in selected_rows:
            video_url = self.video_table.item(row, 2).text()
            self.update_status(row, "Downloading...")

            thread = threading.Thread(target=self.download_video, args=(video_url, row), daemon=True)
            thread.start()

    def download_video(self, video_url, row):
        """Handles the actual downloading of the selected video."""
        global playlist_name
        try:
            file_format = self.format_dropdown.currentText()
            quality = self.quality_dropdown.currentText()
        except Exception as e:
            print(f"An error occurred: {e}")

        playlist_folder = os.path.join(download_path, playlist_name)
        os.makedirs(playlist_folder, exist_ok=True)

        output_folder = os.path.join(playlist_folder, "Videos" if file_format == "mp4" else "Audio")
        os.makedirs(output_folder, exist_ok=True)

        ydl_opts = {
            "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
            "format": f"bestvideo[height<={quality}]+bestaudio/best" if quality != "best" else "best",
            "noplaylist": True,
            "quiet": True,
        }

        if file_format == "mp3":
            ydl_opts.update({
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
                "format": "bestaudio/best",
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

            self.update_status(row, "Completed ✅")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            self.update_status(row, "Completed ✅")

        except Exception as e:
            print(f"Download failed for {video_url}: {e}")
            self.update_status(row, "Failed ❌")


    def create_about_page(self):
        """Creates the About Us Page."""
        page = QWidget()
        layout = QVBoxLayout()

        # Title
        about_label = QLabel("📖 About Ayatiin Projects")
        about_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #f1c40f;")
        layout.addWidget(about_label)

        # Description
        about_text = QLabel(
        "At Ayatiin Projects, we believe that knowledge and creativity should be accessible to everyone. "
        "Our YouTube Playlist Downloader is completely free and allows users to download entire YouTube playlists effortlessly. "
        "We are passionate about building free software for the community and making high-quality tools available without barriers. 🚀🎥"
        )
        about_text.setWordWrap(True)
        layout.addWidget(about_text)

        # Why Free?
        why_free_label = QLabel("🌟 Why We Made This Tool Free?")
        why_free_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2ecc71;")
        layout.addWidget(why_free_label)

        why_free_text = QLabel(
        "Many tools charge users for features that should be free. At Ayatiin Projects, we believe in breaking these barriers "
        "and providing everyone with free access to download YouTube content easily. No subscriptions, no hidden fees—just pure accessibility."
        )
        why_free_text.setWordWrap(True)
        layout.addWidget(why_free_text)

        # Support Us
        support_label = QLabel("💰 Support Ayatiin Projects")
        support_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
        layout.addWidget(support_label)

        support_text = QLabel(
        "If you love this tool and want to see more free software in the future, consider making a donation to help us:"
        )
        support_text.setWordWrap(True)
        layout.addWidget(support_text)

        # Donation Methods
        donation_methods = QLabel(
        "✔ **Maintain & Update the Tool**\n"
        "✔ **Add New Features & Improvements**\n"
        "✔ **Support More Platforms & Video Formats**\n\n"
        "### 🎁 Ways to Donate:\n"
        
        "💎 **Crypto Donations:**\n"
        "- **BTC (Bitcoin)**: `15iD33oNHtdhHZ7Thsycp4mUK56E4rPooe`\n"
        "- **ETH (Ethereum)**: `0x6b2f05666daa137f809923f2e9339d8f00827413`\n"
        "- **USDT (Tron TRC20)**: `TNMdCGo62AQsY7VX1kT6S1p1tD3ky85MMR`\n"
        "- **SOL (Solana)**: `4mYwB22DxTrU5kxoUMWJpCwPY2RdJwdYDxL2vJb5Aecn`\n"
        )
        donation_methods.setWordWrap(True)
        layout.addWidget(donation_methods)

        # Contact
        contact_label = QLabel("📢 Stay Connected")
        contact_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")
        layout.addWidget(contact_label)

        contact_text = QLabel(
        "📧 **Email:** support@ayatiin.com\n"
        "🌍 **Website:** ayatiin.com/tools\n"
        "🐦 **Twitter:** [@AyatiinProjects](https://twitter.com/Ayatiinacademy)\n"
        "📢 **GitHub:** [GitHub](https://github.com/Ali56arif)\n"
        )
        developer_label = QLabel("👨‍💻 Developed by Ali Abdikhaliq")
        developer_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffffff;")
        

        contact_text.setWordWrap(True)
        layout.addWidget(contact_text)
        layout.addWidget(developer_label)
        
        page.setLayout(layout)
        return page


    def create_donation_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        donation_label = QLabel("💰 Support Us\nIf you like this project, consider making other donation methods!\n" 'Contact Us Email: support@ayatiin.com')
         # Support Us
        support_label = QLabel("💰 Support Ayatiin Projects")
        support_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
        layout.addWidget(support_label)

        support_text = QLabel(
        "If you love this tool and want to see more free software in the future, consider making a donation to help us:"
        )
        support_text.setWordWrap(True)
        layout.addWidget(support_text)

        # Donation Methods
        donation_methods = QLabel(
        "✔ **Maintain & Update the Tool**\n"
        "✔ **Add New Features & Improvements**\n"
        "✔ **Support More Platforms & Video Formats**\n\n"
        "### 🎁 Ways to Donate:\n"
        
        "💎 **Crypto Donations:**\n"
        "- **BTC (Bitcoin)**: `15iD33oNHtdhHZ7Thsycp4mUK56E4rPooe`\n"
        "- **ETH (Ethereum)**: `0x6b2f05666daa137f809923f2e9339d8f00827413`\n"
        "- **USDT (Tron TRC20)**: `TNMdCGo62AQsY7VX1kT6S1p1tD3ky85MMR`\n"
        "- **SOL (Solana)**: `4mYwB22DxTrU5kxoUMWJpCwPY2RdJwdYDxL2vJb5Aecn`\n"
        )
        donation_methods.setWordWrap(True)
        layout.addWidget(donation_methods)
        layout.addWidget(donation_label)
        page.setLayout(layout)
        return page
    def create_settings_page(self):
        """Creates the Settings Page."""
        page = QWidget()
        layout = QVBoxLayout()

    # Light/Dark Mode Toggle
        self.theme_toggle = QPushButton("🌗 Toggle Light/Dark Mode")
        self.theme_toggle.setStyleSheet("background-color: #f1c40f; color: black; padding: 8px; border-radius: 5px;")
        self.theme_toggle.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_toggle)

        page.setLayout(layout)
        return page

    def toggle_theme(self):
        """Switch between light and dark mode."""
        current_style = self.styleSheet()
        if "background-color: #1E1E1E" in current_style:
            self.setStyleSheet("background-color: #FFFFFF; color: black; font-size: 14px;")
        else:
            self.setStyleSheet("background-color: #1E1E1E; color: white; font-size: 14px;")
    def update_status(self, row, status):
        self.video_table.setItem(row, 1, QTableWidgetItem(status))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Show Splash Screen Before Main Window Opens
    splash = SplashScreen()
    splash.show()

    # Delay splash for 3 seconds before opening main window
    QTimer.singleShot(3000, splash.close)

    window = YouTubeDownloader()
    QTimer.singleShot(3000, window.show)  # Show main window after splash closes

    sys.exit(app.exec())
