"""
UV Analyst 自动化核心模块
"""
from .gui_recorder import GUIRecorder
from .trajectory_recorder import TrajectoryRecorder

__all__ = [
    "GUIRecorder",
    "TrajectoryRecorder",
]
