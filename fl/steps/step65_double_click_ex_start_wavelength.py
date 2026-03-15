"""
第六十五步：双击EX起始波长输入框，输入起始波长200
记录操作到GUI数据集
"""
import os
import time
import random
import pyautogui
from pathlib import Path
import sys

# 添加父目录到路径，以便导入共享模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.gui_recorder import GUIRecorder
from core.trajectory_recorder import TrajectoryRecorder
from core.trajectory_helper import save_click_action, save_write_action, save_hotkey_action


def get_textbox_rectangle():
    """
    获取EX起始波长输入框的矩形区域
    双击范围: (985,537), (1021,535), (983,546), (1026,545)
    
    Returns:
        (x1, y1, x2, y2): 矩形区域坐标
    """
    # 定义矩形的四个顶点
    points = [
        (985, 537),   # 左上
        (1021, 535),  # 右上
        (983, 546),   # 左下
        (1026, 545)   # 右下
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


def double_click_ex_start_wavelength_and_input(textbox_x: int = None, 
                                               textbox_y: int = None,
                                               textbox_rect: tuple = None,
                                               recorder: GUIRecorder = None,
                                               trajectory_recorder: TrajectoryRecorder = None,
                                               use_default_rectangle: bool = True,
                                               input_value: str = "200"):
    """
    双击EX起始波长输入框，清空并输入起始波长200
    
    Args:
        textbox_x: 输入框X坐标（如果指定，将使用此坐标）
        textbox_y: 输入框Y坐标（如果指定，将使用此坐标）
        textbox_rect: 输入框矩形区域 (x1, y1, x2, y2)，如果提供，将在矩形内随机选择
        recorder: GUI记录器对象
        trajectory_recorder: 轨迹记录器对象
        use_default_rectangle: 是否使用默认矩形区域
        input_value: 双击后要输入的值（默认为"200"）
    """
    print("=" * 60)
    print("第六十五步：双击EX起始波长输入框，输入起始波长200")
    print("=" * 60)
    
    # 确保input_value是字符串
    if input_value is None:
        input_value = "200"
    else:
        input_value = str(input_value)
    
    # 获取输入框坐标或矩形区域
    if use_default_rectangle and textbox_rect is None and textbox_x is None:
        # 使用默认矩形区域
        textbox_rect = get_textbox_rectangle()
        textbox_x, textbox_y = get_random_point_in_rectangle(textbox_rect)
        print(f"\n使用默认EX起始波长输入框矩形区域")
        print(f"矩形范围: X[{textbox_rect[0]}-{textbox_rect[2]}], Y[{textbox_rect[1]}-{textbox_rect[3]}]")
        print(f"在矩形区域内随机选择坐标: ({textbox_x}, {textbox_y})")
    elif textbox_rect is not None:
        # 使用提供的矩形区域
        textbox_x, textbox_y = get_random_point_in_rectangle(textbox_rect)
        print(f"\n在矩形区域内随机选择坐标: ({textbox_x}, {textbox_y})")
        print(f"矩形范围: ({textbox_rect[0]}, {textbox_rect[1]}) 到 ({textbox_rect[2]}, {textbox_rect[3]})")
    
    print(f"\n双击坐标: ({textbox_x}, {textbox_y})")
    print(f"输入值: {input_value}")
    
    try:
        # 获取双击前的截图
        screenshot_before_double_click = None
        if trajectory_recorder:
            screenshot_before_double_click = trajectory_recorder.get_screenshot()
        
        # 移动鼠标到输入框位置
        print(f"\n移动鼠标到EX起始波长输入框位置 ({textbox_x}, {textbox_y})...")
        pyautogui.moveTo(textbox_x, textbox_y, duration=0.5)
        time.sleep(0.3)
        
        # 记录鼠标移动
        if recorder:
            recorder.add_custom_action("mouse_move", {
                "position": {"x": textbox_x, "y": textbox_y},
                "description": "移动到EX起始波长输入框位置"
            })
        
        # 双击输入框（选中输入框）
        print("双击EX起始波长输入框...")
        pyautogui.doubleClick(textbox_x, textbox_y)
        time.sleep(0.2)
        
        # 获取双击后的截图并保存轨迹（双击输入框）
        if trajectory_recorder and screenshot_before_double_click:
            screenshot_after_double_click = trajectory_recorder.get_screenshot()
            # 计算bbox
            if textbox_rect:
                bbox = [textbox_rect[0], textbox_rect[1], textbox_rect[2], textbox_rect[3]]
            elif use_default_rectangle:
                default_rect = get_textbox_rectangle()
                bbox = [default_rect[0], default_rect[1], default_rect[2], default_rect[3]]
            else:
                bbox = [textbox_x - 10, textbox_y - 10, textbox_x + 10, textbox_y + 10]
            
            screen_width, screen_height = pyautogui.size()
            x_norm = textbox_x / screen_width
            y_norm = textbox_y / screen_height
            
            element_info = trajectory_recorder.create_element_info(bbox, element_id=0)
            trajectory_recorder.save_step(
                action_name="doubleClick",
                action_parameters={"x": x_norm, "y": y_norm},
                element_info=element_info,
                screenshot_before=screenshot_before_double_click,
                screenshot_after=screenshot_after_double_click,
                step_instruction="双击EX起始波长输入框"
            )
        
        # 记录双击操作（向后兼容）
        if recorder:
            recorder.add_custom_action("double_click", {
                "position": {"x": textbox_x, "y": textbox_y},
                "target": "ex_start_wavelength_input_field",
                "description": "双击EX起始波长输入框"
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
            if textbox_rect:
                bbox = [textbox_rect[0], textbox_rect[1], textbox_rect[2], textbox_rect[3]]
            elif use_default_rectangle:
                default_rect = get_textbox_rectangle()
                bbox = [default_rect[0], default_rect[1], default_rect[2], default_rect[3]]
            else:
                bbox = [textbox_x - 10, textbox_y - 10, textbox_x + 10, textbox_y + 10]
            save_hotkey_action(
                trajectory_recorder,
                ['ctrl', 'a'],
                step_instruction="清空输入框"
            )
        
        # 记录清空操作（向后兼容）
        if recorder:
            recorder.add_custom_action("clear_input", {
                "keys": ["ctrl", "a", "delete"],
                "description": "清空EX起始波长输入框"
            })
        
        # 获取输入前的截图
        screenshot_before_input = None
        if trajectory_recorder:
            screenshot_before_input = trajectory_recorder.get_screenshot()
        
        # 输入数值
        print(f"输入EX起始波长值: {input_value}...")
        pyautogui.write(input_value, interval=0.05)
        time.sleep(0.3)
        
        # 获取输入后的截图并保存轨迹
        if trajectory_recorder and screenshot_before_input:
            screenshot_after_input = trajectory_recorder.get_screenshot()
            # 计算bbox
            if textbox_rect:
                bbox = [textbox_rect[0], textbox_rect[1], textbox_rect[2], textbox_rect[3]]
            elif use_default_rectangle:
                default_rect = get_textbox_rectangle()
                bbox = [default_rect[0], default_rect[1], default_rect[2], default_rect[3]]
            else:
                bbox = [textbox_x - 10, textbox_y - 10, textbox_x + 10, textbox_y + 10]
            
            save_write_action(
                trajectory_recorder,
                input_value,
                textbox_x,
                textbox_y,
                bbox,
                step_instruction=f"输入EX起始波长值: {input_value}"
            )
        
        # 记录输入操作（向后兼容）
        if recorder:
            input_data = {
                "position": {"x": textbox_x, "y": textbox_y},
                "text": input_value,
                "target": "ex_start_wavelength_input_field",
                "description": f"输入EX起始波长值: {input_value}"
            }
            if textbox_rect:
                input_data["rectangle"] = {
                    "points": [
                        (textbox_rect[0], textbox_rect[1]),
                        (textbox_rect[2], textbox_rect[1]),
                        (textbox_rect[0], textbox_rect[3]),
                        (textbox_rect[2], textbox_rect[3])
                    ],
                    "is_random": True
                }
            else:
                if use_default_rectangle:
                    default_rect = get_textbox_rectangle()
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
        print("✓ 第六十五步完成")
        return True
        
    except Exception as e:
        print(f"输入EX起始波长失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数 - 双击EX起始波长输入框并输入数值并记录操作"""
    # 初始化GUI记录器
    output_file = "FL_step65_double_click_ex_start_wavelength.json"
    recorder = GUIRecorder(output_file)
    
    print("\n" + "=" * 60)
    print("第六十五步：双击EX起始波长输入框，输入起始波长200（记录操作）")
    print("=" * 60)
    print(f"操作将记录到: {output_file}\n")
    
    # 开始记录（只初始化，不启动实时监听，因为我们手动记录操作）
    recorder.recording = True
    recorder.actions = []
    recorder.start_time = time.time()
    print("✓ 已开始记录操作\n")
    
    try:
        # 执行输入操作（使用默认输入框矩形区域，输入固定值200）
        success = double_click_ex_start_wavelength_and_input(
            recorder=recorder,
            use_default_rectangle=True,  # 使用默认矩形区域
            input_value="200"  # 输入固定值200
        )
        
        if success:
            print("\n" + "=" * 60)
            print("第六十五步完成！应该已经输入EX起始波长值200。")
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
                    print(f"  {i}. 输入EX起始波长值 '{text}' - 坐标: ({pos.get('x')}, {pos.get('y')})")
                elif action_type == 'double_click':
                    pos = action.get('data', {}).get('position', {})
                    print(f"  {i}. 双击EX起始波长输入框 - 坐标: ({pos.get('x')}, {pos.get('y')})")
                elif action_type == 'clear_input':
                    print(f"  {i}. 清空EX起始波长输入框")
                elif action_type == 'mouse_move':
                    pos = action.get('data', {}).get('position', {})
                    print(f"  {i}. 鼠标移动 - 坐标: ({pos.get('x')}, {pos.get('y')})")
                else:
                    print(f"  {i}. {action_type}")


if __name__ == "__main__":
    main()

