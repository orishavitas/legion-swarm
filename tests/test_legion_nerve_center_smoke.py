import importlib


def test_module_imports():
    mod = importlib.import_module("legion.nerve_center")
    assert hasattr(mod, "main")
    assert hasattr(mod, "build_layout")


def test_build_layout_returns_layout():
    from rich.layout import Layout
    from legion.nerve_center import build_layout
    layout = build_layout()
    assert isinstance(layout, Layout)
