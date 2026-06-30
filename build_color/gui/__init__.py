"""
Build Color - GUI Package

Launch the application with build_color.gui.launch()
"""


def launch():
    import sys

    from PyQt6.QtWidgets import QApplication

    from build_color.gui.app import BuildColorWindow

    # Windows taskbar icon fix
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("build.buildcolor.1")
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName("Build Color")
    app.setOrganizationName("Build Universe")

    window = BuildColorWindow()
    window.show()
    return app.exec()
