from imports import *
from constants import *

from splash import SplashScreen
from rbc_community_map import RBCCommunityMap


# -----------------------
# Main Entry Point
# -----------------------

def _self_check(output_path: str | None = None) -> int:
    """Validate frozen resources and keyring packaging without starting Qt."""
    backend = keyring.get_keyring()
    backend_name = f"{type(backend).__module__}.{type(backend).__name__}"
    try:
        entry_points = importlib_metadata.entry_points(group="keyring.backends")
    except TypeError:  # Python versions with the older entry-points API
        entry_points = importlib_metadata.entry_points().get("keyring.backends", ())
    entry_point_names = sorted(entry_point.name for entry_point in entry_points)

    expected_backends = {
        "win32": ("Windows", "keyring.backends.Windows"),
        "darwin": ("macOS", "keyring.backends.macOS"),
    }.get(sys.platform, ("SecretService", "libsecret", "chainer"))
    import_errors = []
    for module_name in expected_backends[1:] if sys.platform in {"win32", "darwin"} else (
        "keyring.backends.SecretService",
        "keyring.backends.libsecret",
        "keyring.backends.chainer",
    ):
        try:
            __import__(module_name)
        except Exception as exc:  # pragma: no cover - platform-specific imports
            import_errors.append(f"{module_name}: {exc}")

    resources = {
        "images": IMAGES_DIR,
        "css": APP_DIR / "css",
        "help": APP_DIR / "docs" / "help",
    }
    lines = [
        f"version={VERSION_NUMBER}",
        f"keyring_backend={backend_name}",
        f"keyring_entry_points={','.join(entry_point_names)}",
        f"app_dir={APP_DIR}",
        *(f"resource_{name}={path.exists()}:{path}" for name, path in resources.items()),
        f"backend_import_errors={';'.join(import_errors)}",
    ]
    output = "\n".join(lines) + "\n"
    if output_path:
        Path(output_path).write_text(output, encoding="utf-8")
    elif getattr(sys, "stdout", None) is not None:
        print(output, end="")

    required_entry_point = set(expected_backends[:1])
    valid = (
        all(path.exists() for path in resources.values())
        and required_entry_point.intersection(entry_point_names)
        and not import_errors
    )
    # A frozen package must never silently fall back to fail.Keyring. Linux
    # package jobs verify backend availability through their installed smoke test;
    # live unlocked-collection behavior remains covered on the Mint VM.
    valid = valid and not backend_name.endswith("fail.Keyring")
    return 0 if valid else 1



def _frame_shows_test_page(image) -> bool:
    """True if a grabbed frame shows the #3366cc test-page background.

    Requires a substantial fraction of samples to match the known test
    color, so blank white/black frames cannot pass.
    """
    if image.isNull():
        return False
    target = (0x33, 0x66, 0xCC)
    matching = total = 0
    for y in range(0, image.height(), 8):
        for x in range(0, image.width(), 8):
            color = image.pixelColor(x, y)
            total += 1
            if color.alpha() > 0 and all(
                abs(channel - want) <= 32
                for channel, want in zip(
                    (color.red(), color.green(), color.blue()), target
                )
            ):
                matching += 1
    return total > 0 and matching / total > 0.5



def _gui_self_check_negative() -> int:
    """Feed a synthetic blank frame through the render predicate; it must fail."""
    image = PySide6.QtGui.QImage(64, 64, PySide6.QtGui.QImage.Format.Format_ARGB32)
    image.fill(PySide6.QtGui.QColor(255, 255, 255, 255))
    return 0 if not _frame_shows_test_page(image) else 1



def _gui_self_check(render_check: bool = True) -> int:
    """Load a page through Qt WebEngine and exit when it is ready.

    With *render_check* the window is shown and, after the page finishes
    loading, a grabbed frame must contain painted (non-black, non-transparent)
    pixels — proving WebEngine actually renders, not just initializes.
    """
    app = QApplication(sys.argv)
    webview = QWebEngineView()
    webview.resize(320, 240)
    result = {"ok": False, "rendered": False}

    def has_painted_pixels() -> bool:
        handle = webview.windowHandle()
        if handle is None or not handle.isExposed():
            return False
        return _frame_shows_test_page(webview.grab().toImage())

    def verify() -> None:
        result["rendered"] = webview.isVisible() and has_painted_pixels()
        app.quit()

    def finish(ok: bool) -> None:
        result["ok"] = ok
        if not ok:
            app.quit()
        elif render_check:
            QTimer.singleShot(1000, verify)
        else:
            app.quit()

    webview.loadFinished.connect(finish)
    webview.setHtml(
        "<html><body style='margin:0;background:#3366cc'>"
        "<p style='color:#fff;font-size:40px'>RBC Map</p></body></html>"
    )
    webview.show()
    QTimer.singleShot(20_000, app.quit)
    app.exec()
    webview.deleteLater()
    return 0 if result["ok"] and (not render_check or result["rendered"]) else 1



def main() -> None:
    self_check_path = next(
        (arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--self-check=")),
        None,
    )
    if "--self-check" in sys.argv or self_check_path:
        raise SystemExit(_self_check(self_check_path))
    if "--self-check-gui" in sys.argv:
        raise SystemExit(_gui_self_check(render_check=True))
    if "--self-check-gui=load" in sys.argv:
        raise SystemExit(_gui_self_check(render_check=False))
    if "--self-check-gui=negative" in sys.argv:
        raise SystemExit(_gui_self_check_negative())

    app = QApplication(sys.argv)

    images_dir = APP_DIR / "images"

    app_icon = PySide6.QtGui.QIcon(str(images_dir / "favicon.ico"))
    app.setWindowIcon(app_icon)

    splash = SplashScreen(str(images_dir / "loading.png"))
    splash.show()
    splash.show_message("Starting up...")

    try:
        main_window = RBCCommunityMap(splash=splash)
        main_window.show()
        splash.finish(main_window)
    except Exception as exc:
        logging.critical("Fatal startup error", exc_info=exc)
        splash.close()
        QMessageBox.critical(
            None,
            "Startup Error",
            "The application failed to start.\n\n"
            "Please check the log files for details.",
        )
        sys.exit(1)

    sys.exit(app.exec())



if __name__ == "__main__":
    main()
