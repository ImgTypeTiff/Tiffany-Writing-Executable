import os
import sys
import markdown
from markdown.extensions import extra, fenced_code
from mdx_partial_gfm import PartialGithubFlavoredMarkdownExtension
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QSplitter,
    QFileDialog, QStatusBar, QTabWidget, QWidget, QVBoxLayout, QTextBrowser
)
from PySide6.QtGui import QAction, QFontDatabase, QTextCursor, QTextDocument
from PySide6.QtCore import Qt
from PySide6.QtPrintSupport import QPrinter
import importlib.util


class TiffWriter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tiffany Writing Executable")
        self.resize(800, 600)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.tabBar().setExpanding(False)  # Tabs stick left
        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.create_menus()

        self.new_tab()

    def create_menus(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        new_tab_action = QAction("New Tab", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_tab_action)

        export_pdf_action = QAction("Export PDF", self)
        export_pdf_action.setShortcut("Ctrl+E")
        export_pdf_action.triggered.connect(self.export_pdf)
        file_menu.addAction(export_pdf_action)

        view_menu = menu.addMenu("View")
        toggle_preview = QAction("Toggle Preview", self)
        toggle_preview.setShortcut("Ctrl+P")
        toggle_preview.triggered.connect(self.toggle_preview)
        view_menu.addAction(toggle_preview)

        toggle_html_preview = QAction("Toggle HTML Preview", self)
        toggle_html_preview.setShortcut("Ctrl+Shift+P")
        toggle_html_preview.triggered.connect(self.toggle_html_preview)
        view_menu.addAction(toggle_html_preview)

        edit_menu = menu.addMenu("Edit")
        toggle_dir_action = QAction("Toggle LTR/RTL", self)
        toggle_dir_action.setShortcut("Ctrl+R")
        toggle_dir_action.triggered.connect(self.toggle_text_direction)
        edit_menu.addAction(toggle_dir_action)

    # --- Tab management ---
    def new_tab(self, filename=None, content=""):
        tab = QWidget()
        layout = QVBoxLayout()
        splitter = QSplitter(Qt.Orientation.Horizontal)

        editor = QTextEdit()
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        editor.setFont(font)
        editor.setAcceptRichText(False)
        editor.setPlainText(content)

        preview = QTextBrowser()
        preview.setFont(font)
        preview.setHtml(self.render_markdown(content))

        html_preview = QTextBrowser()
        html_preview.setFont(font)
        html_preview.setHtml(self.render_markdown(content))

        splitter.addWidget(editor)
        splitter.addWidget(preview)
        splitter.addWidget(html_preview)
        html_preview.hide()  # HTML preview hidden by default
        preview.hide()  # preview hidden initially

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter)
        tab.setLayout(layout)

        tab_data = {
            "widget": tab,
            "editor": editor,
            "preview": preview,
            "html_preview": html_preview,
            "splitter": splitter,
            "file": filename,
            "direction": Qt.LeftToRight
        }

        editor.textChanged.connect(lambda ed=editor, pv=preview, hp=html_preview: self.update_preview(ed, pv, hp))
        tab.tab_data = tab_data

        tab_name = os.path.basename(filename) if filename else "Untitled"
        self.tabs.addTab(tab, tab_name)
        self.tabs.setCurrentWidget(tab)
        self.update_word_count(editor)

    def current_tab_data(self):
        idx = self.tabs.currentIndex()
        if idx == -1:
            return None
        widget = self.tabs.widget(idx)
        return getattr(widget, "tab_data", None)

    def close_tab(self, index):
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.new_tab()

    # --- Editor actions ---
    def render_markdown(self,text):
        # Basic Markdown with strike-through, code, and tables

        md_html = markdown.markdown(
            text,
            extensions=[extra.ExtraExtension(), fenced_code.FencedCodeExtension(), PartialGithubFlavoredMarkdownExtension(), 'nl2br']
        )
        styled_html = f"""
        <html>
        <head>
        <style>
            code {{ background-color: #555555; padding: 2px 4px; border-radius: 4px; }}
            pre {{ background-color: #555555; padding: 6px; border-radius: 4px; }}
            del {{ text-decoration: line-through; color: #ffffff; }}
        </style>
        </head>
        <body>{md_html}</body>
        </html>
        """
        return styled_html
    def update_preview(self, editor, preview, html_preview):
        text = editor.toPlainText()
        preview.setHtml(self.render_markdown(text))
        html_preview.setPlainText(self.render_markdown(text))
        self.update_word_count(editor)

    def update_word_count(self, editor):
        text = editor.toPlainText()
        count = len(text.split())
        self.status.showMessage(f"Word count: {count}")

    def toggle_preview(self):
        tab_data = self.current_tab_data()
        if not tab_data:
            return
        if tab_data["preview"].isVisible():
            tab_data["preview"].hide()
        else:
            tab_data["preview"].show()

    def toggle_html_preview(self):
        tab_data = self.current_tab_data()
        if not tab_data:
            return
        if tab_data["html_preview"].isVisible():
            tab_data["html_preview"].hide()
        else:
            tab_data["html_preview"].show()


    def toggle_text_direction(self):
        tab_data = self.current_tab_data()
        if not tab_data:
            return
        # Switch direction
        new_dir = Qt.RightToLeft if tab_data["direction"] == Qt.LeftToRight else Qt.LeftToRight
        tab_data["direction"] = new_dir
        tab_data["editor"].setLayoutDirection(new_dir)
        tab_data["preview"].setLayoutDirection(new_dir)

    # --- File actions ---
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Markdown File", "", "Markdown Files (*.md);;Text Files (*.txt)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.new_tab(path, content)

    def save_file(self):
        tab_data = self.current_tab_data()
        if not tab_data:
            return
        if tab_data["file"]:
            with open(tab_data["file"], "w", encoding="utf-8") as f:
                f.write(tab_data["editor"].toPlainText())
        else:
            self.save_file_as()

    def save_file_as(self):
        tab_data = self.current_tab_data()
        if not tab_data:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Markdown File", "", "Markdown Files (*.md);;Text Files (*.txt)")
        if path:
            tab_data["file"] = path
            self.save_file()
            self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(path))

    def export_pdf(self):
        tab_data = self.current_tab_data()
        if not tab_data:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export PDF", "", "PDF Files (*.pdf)")
        if not path:
            return
        html_content = tab_data["preview"].toHtml()
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        doc = QTextDocument()
        doc.setHtml(html_content)
        doc.print_(printer)

    def load_plugins(self):
        plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")

        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
            return

        for file in os.listdir(plugin_dir):
            if not file.endswith(".py") or file.startswith("_"):
                continue

            path = os.path.join(plugin_dir, file)
            name = file[:-3]

            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)

            try:
                spec.loader.exec_module(module)

                # 🔥 Call plugin init hook
                if hasattr(module, "__init_extension__"):
                    module.__init_extension__(self)
                    print(f"Initialized plugin: {name}")
                else:
                    print(f"Loaded plugin (no init): {name}")

                self.plugins.append(module)

            except Exception as e:
                print(f"Error loading plugin {name}: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TiffWriter()
    window.show()
    sys.exit(app.exec())