"""
第十一步：双击PMT文本框，清空并输入600
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
    获取PMT文本框的矩形区域
    文本框范围: (952,522), (1006,521), (954,536), (1013,538)
    
    Returns:
        (x1, y1, x2, y2): 矩形区域坐标
    """
    # 定义矩形的四个顶点
    points = [
        (952, 522),   # 左上
        (1006, 521),  # 右上
        (954, 536),   # 左下
        (1013, 538)   # 右下
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


def double_click_pmt_and_input(textbox_x: int = None, 
                                textbox_y: int = None,
                                textbox_rect: tuple = None,
                                recorder: GUIRecorder = None,
                                trajectory_recorder: TrajectoryRecorder = None,
                                use_default_rectangle: bool = True,
                                input_value: str = "600"):
    """
    双击PMT文本框，清空并输入数值
    
    Args:
        textbox_x: 文本框X坐标（如果指定，将使用此坐标）
        textbox_y: 文本框Y坐标（如果指定，将使用此坐标）
        textbox_rect: 文本框矩形区域 (x1, y1, x2, y2)，如果提供，将在矩形内随机选择
        recorder: GUI记录器对象
        trajectory_recorder: 轨迹记录器对象
        use_default_rectangle: 是否使用默认矩形区域
        input_value: 双击后要输入的值（默认"600"）
    """
    print("=" * 60)
    print("第十一步：双击PMT文本框，清空并输入600")
    print("=" * 60)
    
    # 获取文本框坐标或矩形区域
    if use_default_rectangle and textbox_rect is None and textbox_x is None:
        # 使用默认矩形区域
        textbox_rect = get_textbox_rectangle()
        textbox_x, textbox_y = get_random_point_in_rectangle(textbox_rect)
        print(f"\n使用默认PMT文本框矩形区域")
        print(f"矩形范围: X[{textbox_rect[0]}-{textbox_rect[2]}], Y[{textbox_rect[1]}-{textbox_rect[3]}]")
        print(f"在矩形区域内随机选择坐标: ({textbox_x}, {textbox_y})")
    elif textbox_rect is not None:
        # 使用提供的矩形区域
        textbox_x, textbox_y = get_random_point_in_rectangle(textbox_rect)
        print(f"\n在矩形区域内随机选择坐标: ({textbox_x}, {textbox_y})")
        print(f"矩形范围: ({textbox_rect[0]}, {textbox_rect[1]}) 到 ({textbox_rect[2]}, {textbox_rect[3]})")
    
    print(f"\n双击坐标: ({textbox_x}, {textbox_y})")
    
    try:
        # 获取双击前的截图
        screenshot_before_double_click = None
        if trajectory_recorder:
            screenshot_before_double_click = trajectory_recorder.get_screenshot()
        
        # 移动鼠标到文本框位置
        print(f"\n移动鼠标到PMT文本框位置 ({textbox_x}, {textbox_y})...")
        pyautogui.moveTo(textbox_x, textbox_y, duration=0.5)
        time.sleep(0.3)
        
        # 记录鼠标移动
        if recorder:
            recorder.add_custom_action("mouse_move", {
                "position": {"x": textbox_x, "y": textbox_y},
                "description": "移动到PMT文本框位置"
            })
        
        # 双击文本框
        print("双击PMT文本框...")
        pyautogui.doubleClick(textbox_x, textbox_y)
        time.sleep(0.3)
        
        # 获取双击后的截图并保存轨迹
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
                step_instruction="双击PMT文本框"
            )
        
        # 记录双击操作（向后兼容）
        if recorder:
            click_data = {
                "position": {"x": textbox_x, "y": textbox_y},
                "target": "pmt_textbox",
                "action_type": "double_click",
                "description": "双击PMT文本框"
            }
            if textbox_rect:
                click_data["rectangle"] = {
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
                    click_data["rectangle"] = {
                        "points": [
                            (default_rect[0], default_rect[1]),
                            (default_rect[2], default_rect[1]),
                            (default_rect[0], default_rect[3]),
                            (default_rect[2], default_rect[3])
                        ],
                        "is_random": True
                    }
            recorder.add_custom_action("double_click", click_data)
        
        print("✓ 双击操作完成")
        
        # 双击后清空文本框并输入数值
        print(f"清空文本框并输入数值: {input_value}...")
        time.sleep(0.2)  # 短暂等待，确保输入框已激活
        
        # 获取清空前的截图
        screenshot_before_clear = None
        if trajectory_recorder:
            screenshot_before_clear = trajectory_recorder.get_screenshot()
        
        # 清空输入框（Ctrl+A）
        pyautogui.hotkey('ctrl', 'a')
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
            
            element_info = trajectory_recorder.create_element_info(bbox, element_id=0)
            screen_width, screen_height = pyautogui.size()
            x_norm = textbox_x / screen_width
            y_norm = textbox_y / screen_height
            trajectory_recorder.save_step(
                action_name="hotkey",
                action_parameters={"args": ["ctrl", "a"]},
                element_info=element_info,
                screenshot_before=screenshot_before_clear,
                screenshot_after=screenshot_after_clear,
                step_instruction="清空文本框"
            )
        
        # 记录清空操作（向后兼容）
        if recorder:
            recorder.add_custom_action("clear_input", {
                "keys": ["ctrl", "a"],
                "description": "清空输入框"
            })
        
        print("✓ 清空操作完成")
        
        # 输入数值
        print(f"输入数值: {input_value}...")
        pyautogui.write(input_value, interval=0.1)
        time.sleep(0.3)
        
        # 获取输入后的截图并保存轨迹
        if trajectory_recorder:
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
                step_instruction=f"输入数值 {input_value}"
            )
        
        # 记录输入操作（向后兼容）
        if recorder:
            input_data = {
                "position": {"x": textbox_x, "y": textbox_y},
                "text": input_value,
                "target": "pmt_input_field",
                "description": f"输入数值 {input_value}"
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
        print("✓ 第十一步完成")
        return True
        
    except Exception as e:
        print(f"双击PMT文本框并输入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数 - 双击PMT文本框，清空并输入600并记录操作"""
    # 初始化GUI记录器
    output_file = "FL_step11_double_click_pmt.json"
    recorder = GUIRecorder(output_file)
    
    print("\n" + "=" * 60)
    print("第十一步：双击PMT文本框，清空并输入600（记录操作）")
    print("=" * 60)
    print(f"操作将记录到: {output_file}\n")
    
    # 开始记录（只初始化，不启动实时监听，因为我们手动记录操作）
    recorder.recording = True
    recorder.actions = []
    recorder.start_time = time.time()
    print("✓ 已开始记录操作\n")
    
    try:
        # 执行双击操作并输入600（使用默认PMT文本框矩形区域）
        success = double_click_pmt_and_input(
            recorder=recorder,
            use_default_rectangle=True,  # 使用默认矩形区域
            input_value="600"  # 输入600
        )
        
        if success:
            print("\n" + "=" * 60)
            print("第十一步完成！PMT文本框应该已经被双击，并已输入600。")
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
                if action_type == 'double_click':
                    pos = action.get('data', {}).get('position', {})
                    print(f"  {i}. 双击PMT文本框 - 坐标: ({pos.get('x')}, {pos.get('y')})")
                elif action_type == 'clear_input':
                    print(f"  {i}. 清空输入框")
                elif action_type == 'input_text':
                    text = action.get('data', {}).get('text', '')
                    pos = action.get('data', {}).get('position', {})
                    print(f"  {i}. 输入文本 '{text}' - 坐标: ({pos.get('x')}, {pos.get('y')})")
                elif action_type == 'mouse_move':
                    pos = action.get('data', {}).get('position', {})
                    print(f"  {i}. 鼠标移动 - 坐标: ({pos.get('x')}, {pos.get('y')})")
                else:
                    print(f"  {i}. {action_type}")


if __name__ == "__main__":
    main()

