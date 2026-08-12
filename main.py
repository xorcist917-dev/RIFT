#!/usr/bin/env python3

import json
import os
import platform
import shlex
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote_plus



APP_NAME = "RIFT"
CONFIG_DIR = Path.home() / ".rift"
CONFIG_FILE = CONFIG_DIR / "config.json"



def hard_reset_config():
    try:
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
            print("✓ RIFT configuration deleted.")
        else:
            print("✓ No configuration file found.")
    except Exception as error:
        print(f"✗ Could not delete configuration: {error}")

        if "--hard-reset" in sys.argv:
            hard_reset_config()
            sys.exit(0)

DEFAULT_CONFIG = {
    "search_engine": "duckduckgo",
    "homepage": "https://duckduckgo.com/",
    "theme": "midnight",
    "tab_position": "top",
    "memory_limit": 1024,
    "downloads": str(Path.home() / "Downloads"),
    "new_tab": "homepage",
}

SEARCH_ENGINES = {
    "duckduckgo": "https://duckduckgo.com/?q={query}",
    "google": "https://www.google.com/search?q={query}",
    "bing": "https://www.bing.com/search?q={query}",
    "brave": "https://search.brave.com/search?q={query}",
    "startpage": "https://www.startpage.com/sp/search?query={query}",
}

THEMES = {
    "midnight": {
        "window": "#090c10",
        "panel": "#10151b",
        "panel2": "#171e27",
        "input": "#0b1015",
        "text": "#e8edf2",
        "muted": "#7f8b99",
        "accent": "#7ee787",
        "border": "#26313d",
    },

    "mono": {
        "window": "#101010",
        "panel": "#171717",
        "panel2": "#202020",
        "input": "#0c0c0c",
        "text": "#eeeeee",
        "muted": "#999999",
        "accent": "#ffffff",
        "border": "#383838",
    },

    "ocean": {
        "window": "#071218",
        "panel": "#0b1c26",
        "panel2": "#102b39",
        "input": "#081820",
        "text": "#e5f7ff",
        "muted": "#80a9b8",
        "accent": "#4ddcff",
        "border": "#214657",
    },
}




def load_config():
    if not CONFIG_FILE.exists():
        return None

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            saved = json.load(file)

        config = DEFAULT_CONFIG.copy()
        config.update(saved)

        return config

    except Exception as error:
        print(f"Could not load configuration: {error}")
        return None


def save_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4)


def reset_config():
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()




def validate_config(config):
    errors = []

    if config["search_engine"] not in SEARCH_ENGINES:
        errors.append(
            f"Unknown search engine: {config['search_engine']}"
        )

    if config["theme"] not in THEMES:
        errors.append(
            f"Unknown theme: {config['theme']}"
        )

    if config["tab_position"] not in ("top", "bottom"):
        errors.append(
            "tab_position must be 'top' or 'bottom'"
        )

    if config["new_tab"] not in ("homepage", "blank"):
        errors.append(
            "new_tab must be 'homepage' or 'blank'"
        )

    try:
        memory = int(config["memory_limit"])

        if memory < 128:
            errors.append(
                "memory_limit must be at least 128 MB"
            )

    except (ValueError, TypeError):
        errors.append(
            "memory_limit must be a number"
        )

    return errors




def print_banner():
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║                                              ║")
    print("║                    RIFT                      ║")
    print("║                  V1.0                        ║")
    print("║                                              ║")
    print("║       BUILD YOUR BROWSER MANUALLY            ║")
    print("║                                              ║")
    print("╚══════════════════════════════════════════════╝")
    print()


def cli_help(topic=None):
    print()

    if topic == "set":

        print("set <option> <value>")
        print()
        print("Available options:")
        print()
        print("  search_engine <engine>")
        print("  homepage <url>")
        print("  theme <theme>")
        print("  tab_position <top|bottom>")
        print("  memory_limit <mb>")
        print("  downloads <path>")
        print("  new_tab <homepage|blank>")

    else:

        print("RIFT COMMANDS")
        print("────────────────────────────────────────")
        print()
        print("  help")
        print("  help set")
        print()
        print("  set <option> <value>")
        print()
        print("  status")
        print("  search list")
        print("  theme list")
        print()
        print("  defaults")
        print("  reset")
        print()
        print("  finish")
        print("  exit")

    print()


def print_status(config):
    print()
    print("RIFT CONFIGURATION")
    print("────────────────────────────────────────")
    print()

    for key, value in config.items():
        label = key.replace("_", " ").title()
        print(f"{label:<20} {value}")

    print()
    print(f"Config: {CONFIG_FILE}")
    print()


def bootstrap():
    config = DEFAULT_CONFIG.copy()

    print_banner()

    print("No browser configuration was found.")
    print()
    print("RIFT starts as a command-line builder.")
    print("Configure your browser manually.")
    print()
    print("Type 'help' for commands.")
    print()

    while True:

        try:
            command_line = input("rift> ").strip()

        except KeyboardInterrupt:
            print()
            print("Exiting.")
            return

        except EOFError:
            print()
            return

        if not command_line:
            continue

        try:
            parts = shlex.split(command_line)

        except ValueError as error:
            print(f"Parse error: {error}")
            continue

        command = parts[0].lower()
        args = parts[1:]


        if command == "help":

            topic = args[0] if args else None
            cli_help(topic)


        elif command == "status":

            print_status(config)



        elif command == "set":

            if len(args) < 2:
                print("Usage: set <option> <value>")
                continue

            key = args[0]
            value = " ".join(args[1:])

            if key not in config:
                print(f"Unknown option: {key}")
                print("Use 'help set'.")
                continue

            if key == "memory_limit":

                try:
                    value = int(value)

                except ValueError:
                    print("memory_limit must be a number.")
                    continue

            old_value = config[key]

            config[key] = value

            errors = validate_config(config)

            if errors:

                config[key] = old_value

                print(f"✗ {errors[0]}")

            else:

                print(f"✓ {key} = {value}")



        elif command == "search":

            if args and args[0] == "list":

                print()
                print("SEARCH ENGINES")
                print("──────────────")

                for engine in SEARCH_ENGINES:
                    print(f"  • {engine}")

                print()

            else:

                print("Usage: search list")


        elif command == "theme":

            if args and args[0] == "list":

                print()
                print("THEMES")
                print("──────")

                for theme in THEMES:
                    print(f"  • {theme}")

                print()

            else:

                print("Usage: theme list")

 

        elif command == "defaults":

            config = DEFAULT_CONFIG.copy()

            print("✓ Restored defaults.")



        elif command == "reset":

            reset_config()

            config = DEFAULT_CONFIG.copy()

            print("✓ Configuration reset.")



        elif command == "finish":

            errors = validate_config(config)

            if errors:

                print()
                print("Cannot finish:")
                print()

                for error in errors:
                    print(f"  ✗ {error}")

                print()

                continue

            print()
            print("VALIDATING")
            print("───────────")

            checks = [
                "Search engine",
                "Homepage",
                "Theme",
                "Tabs",
                "Memory monitor",
                "Downloads",
            ]

            for check in checks:

                time.sleep(0.08)

                print(f"✓ {check}")

            save_config(config)

            print()
            print("Configuration complete.")
            print()
            print("Restarting RIFT...")
            print()

            restart_to_gui()

    

        elif command in ("exit", "quit"):

            print("Configuration not saved.")
            return

     

        else:

            print(
                f"Unknown command: {command}. "
                "Type 'help'."
            )




def restart_to_gui():

    environment = os.environ.copy()

    environment["RIFT_GUI"] = "1"

    subprocess.Popen(
        [
            sys.executable,
            str(Path(__file__).resolve()),
        ],
        env=environment,
    )

    raise SystemExit(0)



try:

    from PySide6.QtCore import (
        Qt,
        QUrl,
        QTimer,
    )

    from PySide6.QtGui import (
        QKeySequence,
        QAction,
    )

    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLineEdit,
        QPushButton,
        QToolButton,
        QLabel,
        QTabWidget,
        QMenu,
        QMessageBox,
    )

    from PySide6.QtWebEngineWidgets import (
        QWebEngineView,
    )

    PYSIDE_AVAILABLE = True

except ImportError:

    PYSIDE_AVAILABLE = False



if PYSIDE_AVAILABLE:

    class WebTab(QWidget):

        def __init__(self, browser, url):

            super().__init__()

            self.browser = browser

            layout = QVBoxLayout(self)

            layout.setContentsMargins(
                0,
                0,
                0,
                0,
            )

            self.view = QWebEngineView()

            layout.addWidget(self.view)

            self.view.urlChanged.connect(
                self.url_changed
            )

            self.view.titleChanged.connect(
                self.title_changed
            )

            self.view.loadStarted.connect(
                self.load_started
            )

            self.view.loadFinished.connect(
                self.load_finished
            )

            self.load(url)

        def load(self, url):

            self.view.setUrl(
                QUrl(url)
            )

        def url_changed(self, url):

            if self.browser.current_tab() is self:

                self.browser.address.setText(
                    url.toString()
                )

        def title_changed(self, title):

            index = self.browser.tabs.indexOf(self)

            if index == -1:
                return

            if not title:
                title = "New Tab"

            if len(title) > 24:
                title = title[:24] + "…"

            self.browser.tabs.setTabText(
                index,
                title,
            )

        def load_started(self):

            if self.browser.current_tab() is self:
                self.browser.status_text.setText(
                    "Loading..."
                )

        def load_finished(self, success):

            if self.browser.current_tab() is self:

                if success:
                    self.browser.status_text.setText(
                        "Ready"
                    )

                else:
                    self.browser.status_text.setText(
                        "Failed to load"
                    )



    class Browser(QMainWindow):

        def __init__(self, config):

            super().__init__()

            self.config = config

            self.theme = THEMES[
                config["theme"]
            ]

            self.setWindowTitle("RIFT")

            self.resize(
                1280,
                800,
            )

            self.setMinimumSize(
                800,
                500,
            )

            self.last_cpu_time = time.process_time()
            self.last_wall_time = time.monotonic()

            self.build_ui()

            self.apply_theme()

            self.setup_shortcuts()

            self.setup_monitor()

            self.add_tab()



        def build_ui(self):

            root = QWidget()

            root_layout = QVBoxLayout(root)

            root_layout.setContentsMargins(
                6,
                6,
                6,
                4,
            )

            root_layout.setSpacing(5)

            navigation = QHBoxLayout()

            navigation.setSpacing(4)

            self.back_button = QToolButton()
            self.back_button.setText("←")
            self.back_button.setToolTip("Back")

            self.forward_button = QToolButton()
            self.forward_button.setText("→")
            self.forward_button.setToolTip("Forward")

            self.reload_button = QToolButton()
            self.reload_button.setText("⟳")
            self.reload_button.setToolTip("Reload")

            self.back_button.clicked.connect(
                self.go_back
            )

            self.forward_button.clicked.connect(
                self.go_forward
            )

            self.reload_button.clicked.connect(
                self.reload
            )

            self.address = QLineEdit()

            self.address.setPlaceholderText(
                "Search or enter address"
            )

            self.address.returnPressed.connect(
                self.navigate
            )

            self.ram_label = QLabel(
                "RAM --"
            )

            self.cpu_label = QLabel(
                "CPU --"
            )

            self.menu_button = QToolButton()

            self.menu_button.setText("⋮")

            self.menu_button.clicked.connect(
                self.open_menu
            )

            navigation.addWidget(
                self.back_button
            )

            navigation.addWidget(
                self.forward_button
            )

            navigation.addWidget(
                self.reload_button
            )

            navigation.addWidget(
                self.address,
                1,
            )

            navigation.addWidget(
                self.ram_label
            )

            navigation.addWidget(
                self.cpu_label
            )

            navigation.addWidget(
                self.menu_button
            )

            root_layout.addLayout(
                navigation
            )

            # Tabs
            self.tabs = QTabWidget()

            self.tabs.setTabsClosable(True)

            self.tabs.tabCloseRequested.connect(
                self.close_tab
            )

            self.tabs.currentChanged.connect(
                self.tab_changed
            )

            if self.config["tab_position"] == "bottom":

                self.tabs.setTabPosition(
                    QTabWidget.TabPosition.South
                )

            else:

                self.tabs.setTabPosition(
                    QTabWidget.TabPosition.North
                )

            root_layout.addWidget(
                self.tabs,
                1,
            )

            # Status bar
            status = QHBoxLayout()

            self.status_text = QLabel(
                "RIFT V1"
            )

            status.addWidget(
                self.status_text
            )

            status.addStretch()

            self.version_label = QLabel(
                "V1"
            )

            status.addWidget(
                self.version_label
            )

            root_layout.addLayout(
                status
            )

            self.setCentralWidget(
                root
            )



        def apply_theme(self):

            t = self.theme

            self.setStyleSheet(
                f"""
                QMainWindow, QWidget {{
                    background: {t["window"]};
                    color: {t["text"]};
                    font-family:
                        "Inter",
                        "Segoe UI",
                        sans-serif;
                }}

                QToolButton {{
                    background: {t["panel2"]};
                    color: {t["text"]};
                    border: 1px solid {t["border"]};
                    border-radius: 6px;
                    padding: 5px 9px;
                }}

                QToolButton:hover {{
                    background: {t["border"]};
                }}

                QLineEdit {{
                    background: {t["input"]};
                    color: {t["text"]};
                    border: 1px solid {t["border"]};
                    border-radius: 7px;
                    padding: 7px 10px;
                }}

                QLineEdit:focus {{
                    border: 1px solid {t["accent"]};
                }}

                QTabWidget::pane {{
                    border: none;
                }}

                QTabBar::tab {{
                    background: {t["panel"]};
                    color: {t["muted"]};
                    border: 1px solid {t["border"]};
                    padding: 8px 14px;
                }}

                QTabBar::tab:selected {{
                    background: {t["panel2"]};
                    color: {t["text"]};
                }}

                QMenu {{
                    background: {t["panel"]};
                    color: {t["text"]};
                    border: 1px solid {t["border"]};
                }}

                QMenu::item:selected {{
                    background: {t["panel2"]};
                }}
                """
            )


        def setup_shortcuts(self):

            self.new_tab_action = QAction(
                "New Tab",
                self,
            )

            self.new_tab_action.setShortcut(
                QKeySequence("Ctrl+T")
            )

            self.new_tab_action.triggered.connect(
                self.new_tab
            )

            self.addAction(
                self.new_tab_action
            )

            self.close_tab_action = QAction(
                "Close Tab",
                self,
            )

            self.close_tab_action.setShortcut(
                QKeySequence("Ctrl+W")
            )

            self.close_tab_action.triggered.connect(
                self.close_current_tab
            )

            self.addAction(
                self.close_tab_action
            )

            self.focus_address_action = QAction(
                "Focus Address",
                self,
            )

            self.focus_address_action.setShortcut(
                QKeySequence("Ctrl+L")
            )

            self.focus_address_action.triggered.connect(
                self.focus_address
            )

            self.addAction(
                self.focus_address_action
            )

            self.reload_action = QAction(
                "Reload",
                self,
            )

            self.reload_action.setShortcut(
                QKeySequence("Ctrl+R")
            )

            self.reload_action.triggered.connect(
                self.reload
            )

            self.addAction(
                self.reload_action
            )



        def setup_monitor(self):

            self.monitor_timer = QTimer(
                self
            )

            self.monitor_timer.timeout.connect(
                self.update_stats
            )

            self.monitor_timer.start(
                1000
            )

        def update_stats(self):

            memory = self.memory_usage()

            cpu = self.cpu_usage()

            self.ram_label.setText(
                f"RAM {memory:.0f} MB"
            )

            self.cpu_label.setText(
                f"CPU {cpu:.1f}%"
            )

            limit = int(
                self.config["memory_limit"]
            )

            if memory >= limit:

                self.ram_label.setStyleSheet(
                    "color:#ff5555;"
                )

            elif memory >= limit * 0.85:

                self.ram_label.setStyleSheet(
                    "color:#ffb86c;"
                )

            else:

                self.ram_label.setStyleSheet(
                    ""
                )

        def memory_usage(self):

            proc_status = Path(
                "/proc/self/status"
            )

            if proc_status.exists():

                try:

                    for line in proc_status.read_text().splitlines():

                        if line.startswith("VmRSS:"):

                            kb = float(
                                line.split()[1]
                            )

                            return kb / 1024

                except Exception:
                    pass

            try:

                import resource

                value = resource.getrusage(
                    resource.RUSAGE_SELF
                ).ru_maxrss

                if platform.system() == "Darwin":

                    return value / (
                        1024 * 1024
                    )

                return value / 1024

            except Exception:

                return 0

        def cpu_usage(self):

            current_cpu = time.process_time()

            current_wall = time.monotonic()

            cpu_delta = (
                current_cpu -
                self.last_cpu_time
            )

            wall_delta = (
                current_wall -
                self.last_wall_time
            )

            self.last_cpu_time = current_cpu
            self.last_wall_time = current_wall

            if wall_delta <= 0:
                return 0

            return (
                cpu_delta /
                wall_delta
            ) * 100

 

        def current_tab(self):

            widget = self.tabs.currentWidget()

            if isinstance(widget, WebTab):
                return widget

            return None

        def current_view(self):

            tab = self.current_tab()

            if tab:
                return tab.view

            return None

        def add_tab(self, url=None):

            if url is None:

                if self.config["new_tab"] == "blank":

                    url = "about:blank"

                else:

                    url = self.config["homepage"]

            tab = WebTab(
                self,
                url,
            )

            index = self.tabs.addTab(
                tab,
                "New Tab",
            )

            self.tabs.setCurrentIndex(
                index
            )

            self.focus_address()

        def new_tab(self):

            self.add_tab()

        def close_tab(self, index):

            widget = self.tabs.widget(
                index
            )

            if widget:

                widget.deleteLater()

            self.tabs.removeTab(
                index
            )

            if self.tabs.count() == 0:

                self.add_tab()

        def close_current_tab(self):

            index = self.tabs.currentIndex()

            if index >= 0:

                self.close_tab(index)

        def tab_changed(self, index):

            if index < 0:
                return

            tab = self.current_tab()

            if tab:

                self.address.setText(
                    tab.view.url().toString()
                )



        def go_back(self):

            view = self.current_view()

            if view:
                view.back()

        def go_forward(self):

            view = self.current_view()

            if view:
                view.forward()

        def reload(self):

            view = self.current_view()

            if view:
                view.reload()

        def focus_address(self):

            self.address.setFocus()

            self.address.selectAll()

        def navigate(self):

            text = self.address.text().strip()

            if not text:
                return

            if (
                text.startswith("http://")
                or text.startswith("https://")
                or text.startswith("file://")
            ):

                url = text

            elif (
                "." in text
                and " " not in text
            ):

                url = "https://" + text

            else:

                engine = self.config[
                    "search_engine"
                ]

                template = SEARCH_ENGINES[
                    engine
                ]

                url = template.format(
                    query=quote_plus(text)
                )

            view = self.current_view()

            if view:

                view.setUrl(
                    QUrl(url)
                )


        def open_menu(self):

            menu = QMenu(
                self
            )

            new_tab = menu.addAction(
                "New Tab"
            )

            new_tab.triggered.connect(
                self.new_tab
            )

            reload_action = menu.addAction(
                "Reload"
            )

            reload_action.triggered.connect(
                self.reload
            )

            menu.addSeparator()

            configure = menu.addAction(
                "Configure RIFT"
            )

            configure.triggered.connect(
                self.show_configuration
            )

            about = menu.addAction(
                "About"
            )

            about.triggered.connect(
                self.show_about
            )

            menu.exec(
                self.menu_button.mapToGlobal(
                    self.menu_button.rect().bottomLeft()
                )
            )

        def show_configuration(self):

            QMessageBox.information(
                self,
                "RIFT Configuration",
                "Close RIFT and run:\n\n"
                "python rift.py --configure\n\n"
                "Configure manually, then use:\n\n"
                "finish\n\n"
                "RIFT will restart with the new configuration.",
            )

        def show_about(self):

            QMessageBox.about(
                self,
                "RIFT",
                "RIFT V1\n\n"
                "Build your browser manually.\n\n"
                "Single-file prototype.",
            )



def start_gui(config):

    if not PYSIDE_AVAILABLE:

        print()
        print("PySide6 is required for the GUI.")
        print()
        print("Install it with:")
        print()
        print("    pip install PySide6")
        print()

        raise SystemExit(1)

    Path(
        config["downloads"]
    ).expanduser().mkdir(
        parents=True,
        exist_ok=True,
    )

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        APP_NAME
    )

    app.setApplicationDisplayName(
        APP_NAME
    )

    window = Browser(
        config
    )

    window.show()

    return app.exec()



def main():

    if "--reset" in sys.argv:

        reset_config()

        print(
            f"RIFT configuration removed: "
            f"{CONFIG_FILE}"
        )

        return

    if (
        "--configure" in sys.argv
        or "--setup" in sys.argv
    ):

        bootstrap()

        return

    config = load_config()


    if config is None:

        bootstrap()

        return

 
    start_gui(
        config
    )

if __name__ == "__main__":
    pass



if PYSIDE_AVAILABLE:

    from pathlib import Path
    from PySide6.QtWebEngineCore import QWebEngineProfile


    class V3DownloadBrowser(Browser):

        def __init__(self, config):

            super().__init__(config)

            self.download_dir = Path(
                config["downloads"]
            ).expanduser()

            self.download_dir.mkdir(
                parents=True,
                exist_ok=True,
            )


            QWebEngineProfile.defaultProfile().downloadRequested.connect(
                self.handle_download
            )

            self.active_downloads = []

 

        def handle_download(self, download):

            try:

                directory = self.download_dir

                directory.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                filename = download.downloadFileName()

                if not filename:

                    filename = "download"

                filename = Path(
                    filename
                ).name

                target = directory / filename


                if target.exists():

                    stem = target.stem
                    suffix = target.suffix

                    number = 1

                    while True:

                        candidate = (
                            directory /
                            f"{stem} ({number}){suffix}"
                        )

                        if not candidate.exists():

                            target = candidate

                            break

                        number += 1

                download.setDownloadDirectory(
                    str(directory)
                )

                download.setDownloadFileName(
                    target.name
                )

                self.active_downloads.append(
                    download
                )

                download.receivedBytesChanged.connect(
                    lambda: self.download_progress(
                        download
                    )
                )

                download.isFinishedChanged.connect(
                    lambda: self.download_finished(
                        download
                    )
                )

                download.accept()

                self.status_text.setText(
                    f"Downloading: {target.name}"
                )

            except Exception as error:

                print(
                    "RIFT download error:",
                    error,
                )

                try:
                    download.cancel()
                except Exception:
                    pass


        def download_progress(self, download):

            try:

                received = download.receivedBytes()
                total = download.totalBytes()

                filename = (
                    download.downloadFileName()
                    or "download"
                )

                if total > 0:

                    percent = (
                        received /
                        total
                    ) * 100

                    self.status_text.setText(
                        f"Downloading "
                        f"{filename} "
                        f"({percent:.0f}%)"
                    )

                else:

                    self.status_text.setText(
                        f"Downloading "
                        f"{filename} "
                        f"({received / 1024 / 1024:.1f} MB)"
                    )

            except Exception:
                pass


        def download_finished(self, download):

            try:

                filename = (
                    download.downloadFileName()
                    or "download"
                )

                state = download.state()

                self.status_text.setText(
                    f"Download finished: {filename}"
                )

                if download in self.active_downloads:

                    self.active_downloads.remove(
                        download
                    )

            except Exception:
                pass

 

        def open_menu(self):

            menu = QMenu(
                self
            )

            new_tab = menu.addAction(
                "New Tab"
            )

            new_tab.triggered.connect(
                self.new_tab
            )

            reload_action = menu.addAction(
                "Reload"
            )

            reload_action.triggered.connect(
                self.reload
            )

            menu.addSeparator()

            suspend = menu.addAction(
                "Suspend Current Tab"
            )

            suspend.triggered.connect(
                self.suspend_current_tab
            )

            restore = menu.addAction(
                "Restore Current Tab"
            )

            restore.triggered.connect(
                self.restore_current_tab
            )

            menu.addSeparator()

            downloads = menu.addAction(
                "Open Downloads Folder"
            )

            downloads.triggered.connect(
                self.open_download_folder
            )

            performance = menu.addAction(
                "Performance Status"
            )

            performance.triggered.connect(
                self.show_v2_performance
            )

            configure = menu.addAction(
                "Configure RIFT"
            )

            configure.triggered.connect(
                self.show_configuration
            )

            menu.addSeparator()

            about = menu.addAction(
                "About"
            )

            about.triggered.connect(
                self.show_about
            )

            menu.exec(
                self.menu_button.mapToGlobal(
                    self.menu_button.rect().bottomLeft()
                )
            )


        def open_download_folder(self):

            path = self.download_dir.resolve()

            try:

                if sys.platform.startswith("win"):

                    os.startfile(
                        str(path)
                    )

                elif sys.platform == "darwin":

                    subprocess.Popen(
                        [
                            "open",
                            str(path),
                        ]
                    )

                else:

                    subprocess.Popen(
                        [
                            "xdg-open",
                            str(path),
                        ]
                    )

            except Exception as error:

                QMessageBox.warning(
                    self,
                    "RIFT Downloads",
                    f"Could not open downloads folder:\n\n{error}",
                )



def v3_main():

    if "--reset" in sys.argv:

        reset_config()

        print(
            f"Deleted {CONFIG_FILE}"
        )

        return

    if (
        "--configure" in sys.argv
        or "--setup" in sys.argv
    ):

        v2_bootstrap()

        return

    config = load_config()

    if config is None:

        v2_bootstrap()

        return

    config = apply_v2_defaults(
        config
    )

    if not PYSIDE_AVAILABLE:

        print()
        print(
            "PySide6 is required."
        )
        print()
        print(
            "Install it with:"
        )
        print()
        print(
            "pip install PySide6"
        )
        print()

        return

    download_dir = Path(
        config["downloads"]
    ).expanduser()

    download_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "RIFT"
    )

    app.setApplicationDisplayName(
        "RIFT"
    )

    window = V3DownloadBrowser(
        config
    )

    window.show()

    sys.exit(
        app.exec()
    )




if __name__ == "__main__":
    pass






V31_DEFAULTS = {
    "performance_cache": "disk",
    "performance_cache_size": 64,
    "performance_disk_cache": True,
    "performance_preload": False,
    "performance_animations": False,
    "performance_background": False,
    "performance_memory_manager": True,
    "performance_tab_suspend": 300,
}


for _v31_key, _v31_value in V31_DEFAULTS.items():

    if _v31_key not in DEFAULT_CONFIG:

        DEFAULT_CONFIG[
            _v31_key
        ] = _v31_value




def v31_process_memory_mb():
   

    if sys.platform == "win32":

        try:
            import ctypes
            from ctypes import wintypes

            class PROCESS_MEMORY_COUNTERS(
                ctypes.Structure
            ):
                _fields_ = [
                    (
                        "cb",
                        wintypes.DWORD,
                    ),
                    (
                        "PageFaultCount",
                        wintypes.DWORD,
                    ),
                    (
                        "PeakWorkingSetSize",
                        ctypes.c_size_t,
                    ),
                    (
                        "WorkingSetSize",
                        ctypes.c_size_t,
                    ),
                    (
                        "QuotaPeakPagedPoolUsage",
                        ctypes.c_size_t,
                    ),
                    (
                        "QuotaPagedPoolUsage",
                        ctypes.c_size_t,
                    ),
                    (
                        "QuotaPeakNonPagedPoolUsage",
                        ctypes.c_size_t,
                    ),
                    (
                        "QuotaNonPagedPoolUsage",
                        ctypes.c_size_t,
                    ),
                    (
                        "PagefileUsage",
                        ctypes.c_size_t,
                    ),
                    (
                        "PeakPagefileUsage",
                        ctypes.c_size_t,
                    ),
                ]

            kernel32 = ctypes.WinDLL(
                "kernel32",
                use_last_error=True,
            )

            psapi = ctypes.WinDLL(
                "psapi",
                use_last_error=True,
            )

            GetCurrentProcess = (
                kernel32.GetCurrentProcess
            )

            GetCurrentProcess.restype = (
                wintypes.HANDLE
            )

            process = GetCurrentProcess()

            counters = (
                PROCESS_MEMORY_COUNTERS()
            )

            counters.cb = ctypes.sizeof(
                counters
            )

            GetProcessMemoryInfo = (
                psapi.GetProcessMemoryInfo
            )

            GetProcessMemoryInfo.argtypes = [
                wintypes.HANDLE,
                ctypes.POINTER(
                    PROCESS_MEMORY_COUNTERS
                ),
                wintypes.DWORD,
            ]

            GetProcessMemoryInfo.restype = (
                wintypes.BOOL
            )

            success = GetProcessMemoryInfo(
                process,
                ctypes.byref(counters),
                counters.cb,
            )

            if success:

                return (
                    counters.WorkingSetSize
                    / (1024 * 1024)
                )

        except Exception:
            pass



    status_file = Path(
        "/proc/self/status"
    )

    if status_file.exists():

        try:

            for line in status_file.read_text().splitlines():

                if line.startswith(
                    "VmRSS:"
                ):

                    parts = line.split()

                    if len(parts) >= 2:

                        return (
                            int(parts[1])
                            / 1024
                        )

        except Exception:
            pass

    return None




if PYSIDE_AVAILABLE:

    def v31_apply_webengine_settings(browser):



        try:

            profile = (
                QWebEngineProfile.defaultProfile()
            )

            settings = profile.settings()


            settings.setAttribute(
                QWebEngineSettings.JavascriptEnabled,
                True,
            )

 

            settings.setAttribute(
                QWebEngineSettings.PluginsEnabled,
                False,
            )



            settings.setAttribute(
                QWebEngineSettings.LocalStorageEnabled,
                True,
            )



            settings.setAttribute(
                QWebEngineSettings.WebGLEnabled,
                True,
            )


            settings.setAttribute(
                QWebEngineSettings.FullScreenSupportEnabled,
                True,
            )


            settings.setAttribute(
                QWebEngineSettings.PdfViewerEnabled,
                True,
            )

    

            settings.setAttribute(
                QWebEngineSettings.AutoLoadImages,
                True,
            )


            settings.setAttribute(
                QWebEngineSettings.JavascriptCanAccessClipboard,
                False,
            )


            cache_mode = browser.config.get(
                "performance_cache",
                "disk",
            )

            disk_cache_enabled = browser.config.get(
                "performance_disk_cache",
                True,
            )

            if not disk_cache_enabled:

                profile.setHttpCacheType(
                    QWebEngineProfile.NoCache
                )

            elif cache_mode == "memory":

                profile.setHttpCacheType(
                    QWebEngineProfile.MemoryHttpCache
                )

            else:

                profile.setHttpCacheType(
                    QWebEngineProfile.DiskHttpCache
                )


            try:

                cache_mb = int(
                    browser.config.get(
                        "performance_cache_size",
                        64,
                    )
                )

                cache_mb = max(
                    8,
                    min(
                        cache_mb,
                        2048,
                    )
                )

                profile.setHttpCacheMaximumSize(
                    cache_mb * 1024 * 1024
                )

            except Exception:
                pass

        except Exception as error:

            print(
                "RIFT WebEngine tuning warning:",
                error,
            )



if PYSIDE_AVAILABLE:

    class V31Browser(V3DownloadBrowser):

        def __init__(self, config):

            for key, value in V31_DEFAULTS.items():

                if key not in config:

                    config[key] = value

            super().__init__(
                config
            )

            v31_apply_webengine_settings(
                self
            )

          
            self.v31_perf_timer = QTimer(
                self
            )

            self.v31_perf_timer.timeout.connect(
                self.v31_update_status
            )

            self.v31_perf_timer.start(
                5000
            )


        def v31_update_status(self):

            try:

                memory = (
                    v31_process_memory_mb()
                )

                if memory is None:
                    return

                total, available, used = (
                    v2_system_memory()
                )

                if total:

                    pressure = (
                        used / total
                    ) * 100

                    self.status_text.setText(
                        f"RIFT "
                        f"{memory:.0f} MB"
                        f"  •  "
                        f"System "
                        f"{pressure:.0f}%"
                    )

                else:

                    self.status_text.setText(
                        f"RIFT "
                        f"{memory:.0f} MB"
                    )

            except Exception:
                pass


        def show_v31_performance(self):

            process_memory = (
                v31_process_memory_mb()
            )

            total, available, used = (
                v2_system_memory()
            )

            if process_memory is None:

                process_text = (
                    "Unavailable"
                )

            else:

                process_text = (
                    f"{process_memory:.1f} MB"
                )

            if total is not None:

                system_text = (
                    f"{used:.0f} MB / "
                    f"{total:.0f} MB"
                )

                available_text = (
                    f"{available:.0f} MB"
                )

                pressure_text = (
                    f"{(used / total) * 100:.1f}%"
                )

            else:

                system_text = "Unavailable"
                available_text = "Unavailable"
                pressure_text = "Unavailable"

            active = 0
            idle = 0
            suspended = 0

            for index in range(
                self.tabs.count()
            ):

                tab = self.tabs.widget(
                    index
                )

                if not isinstance(
                    tab,
                    V2WebTab,
                ):
                    continue

                if tab.v2_state == TAB_ACTIVE:

                    active += 1

                elif tab.v2_state == TAB_IDLE:

                    idle += 1

                elif tab.v2_state == TAB_SUSPENDED:

                    suspended += 1

            cache_type = self.config.get(
                "performance_cache",
                "disk",
            )

            cache_size = self.config.get(
                "performance_cache_size",
                64,
            )

            text = f"""
RIFT PERFORMANCE
════════════════════════════════

PROCESS

    RIFT RSS             {process_text}

SYSTEM

    Used                 {system_text}
    Available            {available_text}
    Pressure             {pressure_text}

TABS

    Active               {active}
    Idle                 {idle}
    Suspended            {suspended}

WEBENGINE

    Disk cache           {"ON" if self.config.get("performance_disk_cache", True) else "OFF"}
    Cache mode           {cache_type}
    Cache limit          {cache_size} MB
    Preload              {"ON" if self.config.get("performance_preload", False) else "OFF"}
    Background work     {"ON" if self.config.get("performance_background", False) else "OFF"}

MEMORY MANAGER

    Enabled              {"YES" if self.config.get("performance_memory_manager", True) else "NO"}
    Suspend after        {self.config.get("performance_tab_suspend", 300)} sec

════════════════════════════════
"""

            QMessageBox.information(
                self,
                "RIFT Performance",
                text.strip(),
            )


        def open_menu(self):

            menu = QMenu(
                self
            )

            new_tab = menu.addAction(
                "New Tab"
            )

            new_tab.triggered.connect(
                self.new_tab
            )

            reload_action = menu.addAction(
                "Reload"
            )

            reload_action.triggered.connect(
                self.reload
            )

            menu.addSeparator()

            suspend = menu.addAction(
                "Suspend Current Tab"
            )

            suspend.triggered.connect(
                self.suspend_current_tab
            )

            restore = menu.addAction(
                "Restore Current Tab"
            )

            restore.triggered.connect(
                self.restore_current_tab
            )

            menu.addSeparator()

            downloads = menu.addAction(
                "Open Downloads Folder"
            )

            downloads.triggered.connect(
                self.open_download_folder
            )

            performance = menu.addAction(
                "Performance Monitor"
            )

            performance.triggered.connect(
                self.show_v31_performance
            )

            configure = menu.addAction(
                "Configure RIFT"
            )

            configure.triggered.connect(
                self.show_configuration
            )

            menu.addSeparator()

            about = menu.addAction(
                "About"
            )

            about.triggered.connect(
                self.show_about
            )

            menu.exec(
                self.menu_button.mapToGlobal(
                    self.menu_button.rect().bottomLeft()
                )
            )



def v31_cli_help(topic=None):

    if topic == "performance":

        print()
        print(
            "RIFT PERFORMANCE OPTIONS"
        )
        print(
            "────────────────────────────────────────"
        )
        print()
        print(
            "  set memory_limit <MB>"
        )
        print(
            "  set performance_tab_suspend <seconds>"
        )
        print(
            "  set performance_cache disk"
        )
        print(
            "  set performance_cache memory"
        )
        print(
            "  set performance_cache_size <MB>"
        )
        print(
            "  set performance_disk_cache true|false"
        )
        print(
            "  set performance_preload true|false"
        )
        print(
            "  set performance_animations true|false"
        )
        print(
            "  set performance_background true|false"
        )
        print(
            "  set performance_memory_manager true|false"
        )
        print()

        return

    v2_cli_help(
        topic
    )


def v31_set_value(
    config,
    key,
    value,
):

    boolean_keys = {
        "performance_disk_cache",
        "performance_preload",
        "performance_animations",
        "performance_background",
        "performance_memory_manager",
    }

    if key in boolean_keys:

        lowered = value.lower()

        if lowered in (
            "true",
            "yes",
            "on",
            "1",
        ):

            config[key] = True

            return True

        if lowered in (
            "false",
            "no",
            "off",
            "0",
        ):

            config[key] = False

            return True

        print(
            f"{key} must be true or false."
        )

        return False

    if key in (
        "performance_cache_size",
        "performance_tab_suspend",
    ):

        try:

            number = int(
                value
            )

        except ValueError:

            print(
                f"{key} must be a number."
            )

            return False

        if key == "performance_cache_size":

            if number < 8 or number > 2048:

                print(
                    "Cache size must be between 8 and 2048 MB."
                )

                return False

        if key == "performance_tab_suspend":

            if number < 10:

                print(
                    "Tab suspension must be at least 10 seconds."
                )

                return False

        config[key] = number

        return True

    if key == "performance_cache":

        value = value.lower()

        if value not in (
            "disk",
            "memory",
        ):

            print(
                "performance_cache must be 'disk' or 'memory'."
            )

            return False

        config[key] = value

        return True

    return False



def v31_bootstrap():

    config = DEFAULT_CONFIG.copy()

    apply_v2_defaults(
        config
    )

    for key, value in V31_DEFAULTS.items():

        if key not in config:

            config[key] = value

    print_banner()

    print(
        "RIFT V3.1 PERFORMANCE BUILDER"
    )

    print()
    print(
        "Type 'help performance' for performance options."
    )
    print()

    while True:

        try:

            command_line = input(
                "rift> "
            ).strip()

        except (
            KeyboardInterrupt,
            EOFError,
        ):

            print()

            return

        if not command_line:
            continue

        try:

            parts = shlex.split(
                command_line
            )

        except ValueError as error:

            print(
                f"Parse error: {error}"
            )

            continue

        command = parts[0].lower()
        args = parts[1:]

        if command == "help":

            v31_cli_help(
                args[0]
                if args
                else None
            )

        elif command == "status":

            print_status(
                config
            )

            print(
                "Performance:"
            )

            for key in V31_DEFAULTS:

                print(
                    f"  {key}: "
                    f"{config.get(key)}"
                )

            print()

        elif command == "set":

            if len(args) < 2:

                print(
                    "Usage: set <option> <value>"
                )

                continue

            key = args[0]

            value = " ".join(
                args[1:]
            )

            if key in V31_DEFAULTS:

                if v31_set_value(
                    config,
                    key,
                    value,
                ):

                    print(
                        f"✓ {key} = "
                        f"{config[key]}"
                    )

                continue
                
            if key not in config:

                print(
                    f"Unknown option: {key}"
                )

                continue

            old = config[key]

            if key == "memory_limit":

                try:

                    value = int(
                        value
                    )

                except ValueError:

                    print(
                        "memory_limit must be a number."
                    )

                    continue

            else:

                value = value

            config[key] = value

            errors = validate_config(
                config
            )

            if errors:

                config[key] = old

                print(
                    f"✗ {errors[0]}"
                )

            else:

                print(
                    f"✓ {key} = "
                    f"{value}"
                )

        elif command == "finish":

            errors = validate_config(
                config
            )

            if errors:

                for error in errors:

                    print(
                        f"✗ {error}"
                    )

                continue

            save_config(
                config
            )

            print()
            print(
                "✓ Configuration saved."
            )
            print(
                "✓ Starting RIFT V3.1..."
            )
            print()

            v31_launch_gui(
                config
            )

            return

        elif command in (
            "exit",
            "quit",
        ):

            return

        else:

            print(
                f"Unknown command: {command}"
            )



def v31_launch_gui(config):

    if not PYSIDE_AVAILABLE:

        print(
            "PySide6 is required."
        )

        return

    download_dir = Path(
        config["downloads"]
    ).expanduser()

    download_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "RIFT"
    )

    app.setApplicationDisplayName(
        "RIFT"
    )

    window = V31Browser(
        config
    )

    window.show()

    sys.exit(
        app.exec()
    )



def v31_main():

    if "--reset" in sys.argv:

        reset_config()

        print(
            f"Deleted {CONFIG_FILE}"
        )

        return

    if (
        "--configure" in sys.argv
        or "--setup" in sys.argv
    ):

        v31_bootstrap()

        return

    config = load_config()

    if config is None:

        v31_bootstrap()

        return

    config = apply_v2_defaults(
        config
    )

    for key, value in V31_DEFAULTS.items():

        if key not in config:

            config[key] = value

    v31_launch_gui(
        config
    )

if __name__ == "__main__":
    pass



def rift_v31_memory_mb():
   
 

    if sys.platform != "win32":
        return None

    try:
        import ctypes
        from ctypes import wintypes

        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        kernel32 = ctypes.WinDLL("kernel32")
        psapi = ctypes.WinDLL("psapi")

        handle = kernel32.GetCurrentProcess()

        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(counters)

        result = psapi.GetProcessMemoryInfo(
            handle,
            ctypes.byref(counters),
            counters.cb,
        )

        if result:
            return counters.WorkingSetSize / (1024 * 1024)

    except Exception:
        pass

    return None


def rift_v31_windows_memory():

  

    if sys.platform != "win32":
        return None, None, None

    try:
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(status)

        ctypes.windll.kernel32.GlobalMemoryStatusEx(
            ctypes.byref(status)
        )

        total = (
            status.ullTotalPhys
            / (1024 * 1024)
        )

        available = (
            status.ullAvailPhys
            / (1024 * 1024)
        )

        used = total - available

        return total, available, used

    except Exception:
        return None, None, None


def rift_v31_show_memory():

    process = rift_v31_memory_mb()

    total, available, used = (
        rift_v31_windows_memory()
    )

    print()
    print("RIFT MEMORY")
    print("────────────────────────────")

    if process is not None:
        print(
            f"RIFT process:  {process:.0f} MB"
        )
    else:
        print(
            "RIFT process:  unavailable"
        )

    if total is not None:

        print(
            f"System used:   {used / 1024:.2f} GB"
        )

        print(
            f"System free:   {available / 1024:.2f} GB"
        )

        print(
            f"System total:  {total / 1024:.2f} GB"
        )

        print(
            f"System load:   {(used / total) * 100:.1f}%"
        )

    else:

        print(
            "System memory: unavailable"
        )

    print()


def rift_v31_run():

    
    config = None

    if "load_config" in globals():

        try:
            config = load_config()
        except Exception:
            config = None

    if config is None:

        if "DEFAULT_CONFIG" in globals():

            config = DEFAULT_CONFIG.copy()

        else:

            config = {}


    if not globals().get(
        "PYSIDE_AVAILABLE",
        False,
    ):

        print()
        print(
            "PySide6 is required."
        )
        print(
            "Install it with:"
        )
        print(
            "python -m pip install PySide6"
        )
        print()

        return



    browser_class = globals().get(
        "Browser"
    )

    if browser_class is None:

        print(
            "RIFT could not find the existing Browser class."
        )

        return


    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "RIFT"
    )

    app.setApplicationDisplayName(
        "RIFT"
    )

    
    if "downloads" in config:

        try:

            Path(
                config["downloads"]
            ).expanduser().mkdir(
                parents=True,
                exist_ok=True,
            )

        except Exception:
            pass

  

    try:

        window = browser_class(
            config
        )

    except TypeError:

        window = browser_class()

    window.show()

    

    if PYSIDE_AVAILABLE:

        timer = QTimer()

        timer.setInterval(
            5000
        )

        def update_memory():

            process = rift_v31_memory_mb()

            if process is None:
                return

         

            status = getattr(
                window,
                "status_text",
                None,
            )

            if status is not None:

                try:

                    status.setText(
                        f"RIFT • {process:.0f} MB"
                    )

                except Exception:
                    pass

        timer.timeout.connect(
            update_memory
        )

        timer.start()

       
        window._rift_memory_timer = timer

    sys.exit(
        app.exec()
    )



if __name__ == "__main__":

  
    if "--memory" in sys.argv:

        rift_v31_show_memory()

    else:

        rift_v31_run()