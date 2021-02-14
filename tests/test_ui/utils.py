from src.ui.focus import AbstractFocus


def reset_focus_instances():
    AbstractFocus._instances = []
