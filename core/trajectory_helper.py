"""
轨迹记录辅助函数
提供通用的函数来帮助步骤脚本保存轨迹信息
"""
import pyautogui
from typing import Dict, Any, Optional, List, Tuple
from .trajectory_recorder import TrajectoryRecorder


def save_click_action(trajectory_recorder: TrajectoryRecorder,
                     action_name: str,
                     click_x: int, click_y: int,
                     bbox: List[float],
                     step_instruction: Optional[str] = None,
                     wait_after: float = 0.5) -> bool:
    """
    保存点击操作的轨迹信息
    
    Args:
        trajectory_recorder: 轨迹记录器
        action_name: 操作名称（如 "click", "doubleClick"）
        click_x: 点击X坐标
        click_y: 点击Y坐标
        bbox: 边界框 [left, top, right, bottom]
        step_instruction: 步骤指令（可选）
        wait_after: 操作后等待时间（秒）
    
    Returns:
        bool: 是否成功
    """
    if not trajectory_recorder:
        return False
    
    try:
        # 获取操作前的截图
        screenshot_before = trajectory_recorder.get_screenshot()
        
        # 执行点击操作（由调用者执行，这里只记录）
        # 注意：实际点击操作应该在调用此函数之前执行
        
        # 等待操作完成
        import time
        time.sleep(wait_after)
        
        # 获取操作后的截图
        screenshot_after = trajectory_recorder.get_screenshot()
        
        # 计算归一化坐标
        screen_width, screen_height = pyautogui.size()
        x_norm = click_x / screen_width
        y_norm = click_y / screen_height
        
        # 创建元素信息
        element_info = trajectory_recorder.create_element_info(bbox, element_id=0)
        
        # 保存步骤
        trajectory_recorder.save_step(
            action_name=action_name,
            action_parameters={
                "x": x_norm,
                "y": y_norm
            },
            element_info=element_info,
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after,
            step_instruction=step_instruction
        )
        
        return True
    except Exception as e:
        print(f"保存点击操作轨迹失败: {e}")
        return False


def save_write_action(trajectory_recorder: TrajectoryRecorder,
                     text: str,
                     click_x: int, click_y: int,
                     bbox: List[float],
                     step_instruction: Optional[str] = None,
                     wait_after: float = 0.5) -> bool:
    """
    保存输入文本操作的轨迹信息
    
    Args:
        trajectory_recorder: 轨迹记录器
        text: 输入的文本
        click_x: 点击输入框的X坐标
        click_y: 点击输入框的Y坐标
        bbox: 输入框边界框 [left, top, right, bottom]
        step_instruction: 步骤指令（可选）
        wait_after: 操作后等待时间（秒）
    
    Returns:
        bool: 是否成功
    """
    if not trajectory_recorder:
        return False
    
    try:
        # 获取操作前的截图
        screenshot_before = trajectory_recorder.get_screenshot()
        
        # 等待操作完成
        import time
        time.sleep(wait_after)
        
        # 获取操作后的截图
        screenshot_after = trajectory_recorder.get_screenshot()
        
        # 计算归一化坐标
        screen_width, screen_height = pyautogui.size()
        x_norm = click_x / screen_width
        y_norm = click_y / screen_height
        
        # 创建元素信息
        element_info = trajectory_recorder.create_element_info(bbox, element_id=0)
        
        # 保存步骤
        trajectory_recorder.save_step(
            action_name="write",
            action_parameters={
                "message": text,
                "x": x_norm,
                "y": y_norm
            },
            element_info=element_info,
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after,
            step_instruction=step_instruction
        )
        
        return True
    except Exception as e:
        print(f"保存输入操作轨迹失败: {e}")
        return False


def save_wait_action(trajectory_recorder: TrajectoryRecorder,
                    wait_seconds: float,
                    step_instruction: Optional[str] = None) -> bool:
    """
    保存等待操作的轨迹信息
    
    Args:
        trajectory_recorder: 轨迹记录器
        wait_seconds: 等待的秒数
        step_instruction: 步骤指令（可选）
    
    Returns:
        bool: 是否成功
    """
    if not trajectory_recorder:
        return False
    
    try:
        # 获取等待前的截图
        screenshot_before = trajectory_recorder.get_screenshot()
        
        # 等待
        import time
        time.sleep(wait_seconds)
        
        # 获取等待后的截图
        screenshot_after = trajectory_recorder.get_screenshot()
        
        # 创建默认元素信息
        element_info = trajectory_recorder.create_element_info([0, 0, 0, 0], element_id=0)
        
        # 保存步骤
        trajectory_recorder.save_step(
            action_name="wait",
            action_parameters={
                "seconds": wait_seconds
            },
            element_info=element_info,
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after,
            step_instruction=step_instruction
        )
        
        return True
    except Exception as e:
        print(f"保存等待操作轨迹失败: {e}")
        return False


def save_hotkey_action(trajectory_recorder: TrajectoryRecorder,
                      keys: List[str],
                      step_instruction: Optional[str] = None,
                      wait_after: float = 0.5) -> bool:
    """
    保存快捷键操作的轨迹信息
    
    Args:
        trajectory_recorder: 轨迹记录器
        keys: 按键列表（如 ["ctrl", "a"]）
        step_instruction: 步骤指令（可选）
        wait_after: 操作后等待时间（秒）
    
    Returns:
        bool: 是否成功
    """
    if not trajectory_recorder:
        return False
    
    try:
        # 获取操作前的截图
        screenshot_before = trajectory_recorder.get_screenshot()
        
        # 等待操作完成
        import time
        time.sleep(wait_after)
        
        # 获取操作后的截图
        screenshot_after = trajectory_recorder.get_screenshot()
        
        # 创建默认元素信息
        element_info = trajectory_recorder.create_element_info([0, 0, 0, 0], element_id=0)
        
        # 保存步骤
        trajectory_recorder.save_step(
            action_name="hotkey",
            action_parameters={
                "args": keys
            },
            element_info=element_info,
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after,
            step_instruction=step_instruction
        )
        
        return True
    except Exception as e:
        print(f"保存快捷键操作轨迹失败: {e}")
        return False
