"""
第二十三步：点击文件名输入框，输入基于时间的文件名
记录操作到GUI数据集
"""
import os
import time
import random
import pyautogui
from pathlib import Path
from datetime import datetime
import sys

# 添加父目录到路径，以便导入共享模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.gui_recorder import GUIRecorder
from core.trajectory_recorder import TrajectoryRecorder
from core.trajectory_helper import save_click_action, save_write_action, save_hotkey_action


def get_input_field_rectangle():
    """
    获取文件名输入框的矩形区域
    输入框范围: (766,618), (890,620), (767,633), (838,633)
    
    Returns:
        (x1, y1, x2, y2): 矩形区域坐标
    """
    # 定义矩形的四个顶点
    points = [
        (766, 618),   # 左上
        (890, 620),   # 右上
        (767, 633),   # 左下
        (838, 633)    # 右下
    ]
    
    # 计算矩形的边界
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)
    
    return (x_min, y_min, x_max, y_max)


def get_random_point_in_rectangle(rect_coords):
    """
    在矩形区域内随机选择一个点
    
    Args:
        rect_coords: 矩形坐标 (x1, y1, x2, y2)
    
    Returns:
        (x, y): 随机点的坐标
    """
    x1, y1, x2, y2 = rect_coords
    
    # 确保x1 < x2, y1 < y2
    x_min = min(x1, x2)
    x_max = max(x1, x2)
    y_min = min(y1, y2)
    y_max = max(y1, y2)
    
    # 在矩形内随机选择一个点
    x = random.randint(x_min, x_max)
    y = random.randint(y_min, y_max)
    
    return (x, y)


def generate_filename_by_time():
    """
    根据保存时间生成文件名
    
    Returns:
        str: 基于时间的文件名（格式：YYYYMMDD_HHMMSS）
    """
    now = datetime.now()
    filename = now.strftime("%Y%m%d_%H%M%S")
    return filename


def input_filename(input_x: int = None, 
                   input_y: int = None,
                   input_rect: tuple = None,
                   filename: str = None,
                   recorder: GUIRecorder = None,
                   trajectory_recorder: TrajectoryRecorder = None,
                   use_default_rectangle: bool = True):
    """
    点击文件名输入框并输入基于时间的文件名
    
    Args:
        input_x: 输入框X坐标（如果指定，将使用此坐标）
        input_y: 输入框Y坐标（如果指定，将使用此坐标）
        input_rect: 输入框矩形区域 (x1, y1, x2, y2)，如果提供，将在矩形内随机选择
        filename: 文件名（如果为None，将自动生成基于时间的文件名）
        recorder: GUI记录器对象
        trajectory_recorder: 轨迹记录器对象
        use_default_rectangle: 是否使用默认矩形区域
    """
    print("=" * 60)
    print("第二十三步：点击文件名输入框，输入基于时间的文件名")
    print("=" * 60)
    
    # 生成文件名（如果未提供）
    if filename is None:
        filename = generate_filename_by_time()
    
    print(f"\n生成的文件名: {filename}")
    
    # 获取输入框坐标或矩形区域
    if use_default_rectangle and input_rect is None and input_x is None:
        # 使用默认矩形区域
        input_rect = get_input_field_rectangle()
        input_x, input_y = get_random_point_in_rectangle(input_rect)
        print(f"\n使用默认文件名输入框矩形区域")
        print(f"矩形范围: X[{input_rect[0]}-{input_rect[2]}], Y[{input_rect[1]}-{input_rect[3]}]")
        print(f"在矩形区域内随机选择坐标: ({input_x}, {input_y})")
    elif input_rect is not None:
        # 使用提供的矩形区域
        input_x, input_y = get_random_point_in_rectangle(input_rect)
        print(f"\n在矩形区域内随机选择坐标: ({input_x}, {input_y})")
        print(f"矩形范围: ({input_rect[0]}, {input_rect[1]}) 到 ({input_rect[2]}, {input_rect[3]})")
    
    print(f"\n输入框坐标: ({input_x}, {input_y})")
    
    try:
        # 获取点击输入框前的截图
        screenshot_before_click = None
        if trajectory_recorder:
            screenshot_before_click = trajectory_recorder.get_screenshot()
        
        # 移动鼠标到输入框位置
        print(f"\n移动鼠标到文件名输入框位置 ({input_x}, {input_y})...")
        pyautogui.moveTo(input_x, input_y, duration=0.5)
        time.sleep(0.3)
        
        # 记录鼠标移动
        if recorder:
            recorder.add_custom_action("mouse_move", {
                "position": {"x": input_x, "y": input_y},
                "description": "移动到文件名输入框位置"
            })
        
        # 点击输入框（选中输入框）
        print("点击文件名输入框...")
        pyautogui.click(input_x, input_y)
        time.sleep(0.2)
        
        # 获取点击后的截图并保存轨迹（点击输入框）
        if trajectory_recorder and screenshot_before_click:
            screenshot_after_click = trajectory_recorder.get_screenshot()
            # 计算bbox
            if input_rect:
                bbox = [input_rect[0], input_rect[1], input_rect[2], input_rect[3]]
            elif use_default_rectangle:
                default_rect = get_input_field_rectangle()
                bbox = [default_rect[0], default_rect[1], default_rect[2], default_rect[3]]
            else:
                bbox = [input_x - 10, input_y - 10, input_x + 10, input_y + 10]
            
            save_click_action(
                trajectory_recorder,
                "click",
                input_x,
                input_y,
                bbox,
                step_instruction="点击文件名输入框"
            )
        
        # 记录点击操作（向后兼容）
        if recorder:
            recorder.add_custom_action("click", {
                "position": {"x": input_x, "y": input_y},
                "target": "filename_input_field",
                "description": "点击文件名输入框"
            })
        
        # 获取清空前的截图
        screenshot_before_clear = None
        if trajectory_recorder:
            screenshot_before_clear = trajectory_recorder.get_screenshot()
        
        # 清空输入框（Ctrl+A然后Delete）
        print("清空输入框...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        # 保存清空操作的轨迹
        if trajectory_recorder and screenshot_before_clear:
            screenshot_after_clear = trajectory_recorder.get_screenshot()
            if input_rect:
                bbox = [input_rect[0], input_rect[1], input_rect[2], input_rect[3]]
            elif use_default_rectangle:
                default_rect = get_input_field_rectangle()
                bbox = [default_rect[0], default_rect[1], default_rect[2], default_rect[3]]
            else:
                bbox = [input_x - 10, input_y - 10, input_x + 10, input_y + 10]
            element_info = trajectory_recorder.create_element_info(bbox, element_id=0)
            save_hotkey_action(
                trajectory_recorder,
                ['ctrl', 'a'],
                step_instruction="清空输入框"
            )
        
        # 记录清空操作（向后兼容）
        if recorder:
            recorder.add_custom_action("clear_input", {
                "keys": ["ctrl", "a", "delete"],
                "description": "清空文件名输入框"
            })
        
        # 获取输入前的截图
        screenshot_before_input = None
        if trajectory_recorder:
            screenshot_before_input = trajectory_recorder.get_screenshot()
        
        # 输入文件名
        print(f"输入文件名: {filename}...")
        pyautogui.write(filename, interval=0.05)
        time.sleep(0.3)
        
        # 获取输入后的截图并保存轨迹
        if trajectory_recorder and screenshot_before_input:
            screenshot_after_input = trajectory_recorder.get_screenshot()
            # 计算bbox
            if input_rect:
                bbox = [input_rect[0], input_rect[1], input_rect[2], input_rect[3]]
            elif use_default_rectangle:
                default_rect = get_input_field_rectangle()
                bbox = [default_rect[0], default_rect[1], default_rect[2], default_rect[3]]
            else:
                bbox = [input_x - 10, input_y - 10, input_x + 10, input_y + 10]
            
            save_write_action(
                trajectory_recorder,
                filename,
                input_x,
                input_y,
                bbox,
                step_instruction=f"输入基于时间的文件名: {filename}"
            )
        
        # 记录输入操作（向后兼容）
        if recorder:
            input_data = {
                "position": {"x": input_x, "y": input_y},
                "text": filename,
                "filename_type": "time_based",
                "filename_format": "YYYYMMDD_HHMMSS",
                "target": "filename_input_field",
                "description": f"输入基于时间的文件名: {filename}"
            }
            if input_rect:
                input_data["rectangle"] = {
                    "points": [
                        (input_rect[0], input_rect[1]),
                        (input_rect[2], input_rect[1]),
                        (input_rect[0], input_rect[3]),
                        (input_rect[2], input_rect[3])
                    ],
                    "is_random": True
                }
            else:
                if use_default_rectangle:
                    default_rect = get_input_field_rectangle()
                    input_data["rectangle"] = {
                        "points": [
                            (default_rect[0], default_rect[1]),
                            (default_rect[2], default_rect[1]),
                            (default_rect[0], default_rect[3]),
                            (default_rect[2], default_rect[3])
                        ],
                        "is_random": True
                    }
            recorder.add_custom_action("input_text", input_data)
        
        print(f"✓ 输入操作完成")
        print("✓ 第二十三步完成")
        return True
        
    except Exception as e:
        print(f"输入文件名失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数 - 输入基于时间的文件名并记录操作"""
    # 初始化GUI记录器
    output_file = "FL_step23_input_filename.json"
    recorder = GUIRecorder(output_file)
    
    print("\n" + "=" * 60)
    print("第二十三步：点击文件名输入框，输入基于时间的文件名（记录操作）")
    print("=" * 60)
    print(f"操作将记录到: {output_file}\n")
    
    # 开始记录（只初始化，不启动实时监听，因为我们手动记录操作）
    recorder.recording = True
    recorder.actions = []
    recorder.start_time = time.time()
    print("✓ 已开始记录操作\n")
    
    try:
        # 执行输入操作（使用默认文件名输入框矩形区域，自动生成基于时间的文件名）
        success = input_filename(
            recorder=recorder,
            use_default_rectangle=True,  # 使用默认矩形区域
            filename=None  # None表示自动生成基于时间的文件名
        )
        
        if success:
            print("\n" + "=" * 60)
            print("第二十三步完成！应该已经输入基于时间的文件名。")
            print("=" * 60)
        else:
            print("\n操作失败，请检查错误信息")
            
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 停止记录并保存
        recorder.recording = False
        recorder.save_recording()
        
        print(f"\n✓ 操作已记录到: {output_file}")
        print(f"✓ 共记录 {len(recorder.actions)} 个操作")
        
        # 显示记录的操作摘要
        if recorder.actions:
            print("\n操作摘要:")
            for i, action in enumerate(recorder.actions, 1):
                action_type = action.get('type', 'unknown')
                if action_type == 'input_text':
                    text = action.get('data', {}).get('text', '')
                    pos = action.get('data', {}).get('position', {})
                    print(f"  {i}. 输入文件名 '{text}' - 坐标: ({pos.get('x')}, {pos.get('y')})")
                elif action_type == 'click':
                    pos = action.get('data', {}).get('position', {})
                    print(f"  {i}. 点击文件名输入框 - 坐标: ({pos.get('x')}, {pos.get('y')})")
                elif action_type == 'clear_input':
                    print(f"  {i}. 清空文件名输入框")
                elif action_type == 'mouse_move':
                    pos = action.get('data', {}).get('position', {})
                    print(f"  {i}. 鼠标移动 - 坐标: ({pos.get('x')}, {pos.get('y')})")
                else:
                    print(f"  {i}. {action_type}")


if __name__ == "__main__":
    main()

