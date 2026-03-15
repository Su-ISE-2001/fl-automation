"""
第二十五步：关闭弹出的Excel窗口
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
from core.trajectory_helper import save_click_action


def get_button_rectangle():
    """
    获取关闭Excel窗口按钮的矩形区域
    点击范围: (1368,259), (1375,259), (1369,267), (1374,267)
    
    Returns:
        (x1, y1, x2, y2): 矩形区域坐标
    """
    # 定义矩形的四个顶点
    points = [
        (1368, 259),   # 左上
        (1375, 259),   # 右上
        (1369, 267),   # 左下
        (1374, 267)    # 右下
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


def close_excel_window(button_x: int = None, 
                       button_y: int = None,
                       button_rect: tuple = None,
                       recorder: GUIRecorder = None,
                       trajectory_recorder: TrajectoryRecorder = None,
                       use_default_rectangle: bool = True):
    """
    关闭弹出的Excel窗口
    
    Args:
        button_x: 关闭按钮X坐标（如果指定，将使用此坐标）
        button_y: 关闭按钮Y坐标（如果指定，将使用此坐标）
        button_rect: 关闭按钮矩形区域 (x1, y1, x2, y2)，如果提供，将在矩形内随机选择
        recorder: GUI记录器对象
        trajectory_recorder: 轨迹记录器对象
        use_default_rectangle: 是否使用默认矩形区域
    """
    print("=" * 60)
    print("第二十五步：关闭弹出的Excel窗口")
    print("=" * 60)
    
    # 获取按钮坐标或矩形区域
    if use_default_rectangle and button_rect is None and button_x is None:
        # 使用默认矩形区域
        button_rect = get_button_rectangle()
        button_x, button_y = get_random_point_in_rectangle(button_rect)
        print(f"\n使用默认关闭按钮矩形区域")
        print(f"矩形范围: X[{button_rect[0]}-{button_rect[2]}], Y[{button_rect[1]}-{button_rect[3]}]")
        print(f"在矩形区域内随机选择坐标: ({button_x}, {button_y})")
    elif button_rect is not None:
        # 使用提供的矩形区域
        button_x, button_y = get_random_point_in_rectangle(button_rect)
        print(f"\n在矩形区域内随机选择坐标: ({button_x}, {button_y})")
        print(f"矩形范围: ({button_rect[0]}, {button_rect[1]}) 到 ({button_rect[2]}, {button_rect[3]})")
    
    print(f"\n点击坐标: ({button_x}, {button_y})")
    
    try:
        # 获取点击前的截图
        screenshot_before = None
        if trajectory_recorder:
            screenshot_before = trajectory_recorder.get_screenshot()
        
        # 移动鼠标到关闭按钮位置
        print(f"\n移动鼠标到关闭按钮位置 ({button_x}, {button_y})...")
        pyautogui.moveTo(button_x, button_y, duration=0.5)
        time.sleep(0.3)
        
        # 记录鼠标移动
        if recorder:
            recorder.add_custom_action("mouse_move", {
                "position": {"x": button_x, "y": button_y},
                "description": "移动到Excel关闭按钮位置"
            })
        
        # 点击关闭按钮
        print("点击关闭Excel窗口...")
        pyautogui.click(button_x, button_y)
        time.sleep(0.5)
        
        # 获取点击后的截图并保存轨迹
        if trajectory_recorder and screenshot_before:
            screenshot_after = trajectory_recorder.get_screenshot()
            # 计算bbox
            if button_rect:
                bbox = [button_rect[0], button_rect[1], button_rect[2], button_rect[3]]
            elif use_default_rectangle:
                default_rect = get_button_rectangle()
                bbox = [default_rect[0], default_rect[1], default_rect[2], default_rect[3]]
            else:
                bbox = [button_x - 10, button_y - 10, button_x + 10, button_y + 10]
            
            save_click_action(
                trajectory_recorder,
                "click",
                button_x,
                button_y,
                bbox,
                step_instruction="关闭弹出的Excel窗口"
            )
        
        # 记录点击操作（向后兼容）
        if recorder:
            click_data = {
                "position": {"x": button_x, "y": button_y},
                "target": "excel_close_button",
                "button_name": "Excel关闭按钮",
                "description": "关闭弹出的Excel窗口"
            }
            if button_rect:
                click_data["rectangle"] = {
                    "points": [
                        (button_rect[0], button_rect[1]),
                        (button_rect[2], button_rect[1]),
                        (button_rect[0], button_rect[3]),
                        (button_rect[2], button_rect[3])
                    ],
                    "is_random": True
                }
            else:
                # 即使没有显式提供button_rect，如果使用了默认矩形，也记录
                if use_default_rectangle:
                    default_rect = get_button_rectangle()
                    click_data["rectangle"] = {
                        "points": [
                            (default_rect[0], default_rect[1]),
                            (default_rect[2], default_rect[1]),
                            (default_rect[0], default_rect[3]),
                            (default_rect[2], default_rect[3])
                        ],
                        "is_random": True
                    }
            recorder.add_custom_action("click", click_data)
        
        print("✓ 点击操作完成")
        print("✓ 第二十五步完成")
        return True
        
    except Exception as e:
        print(f"关闭Excel窗口失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数 - 关闭Excel窗口并记录操作"""
    # 初始化GUI记录器
    output_file = "FL_step25_close_excel.json"
    recorder = GUIRecorder(output_file)
    
    print("\n" + "=" * 60)
    print("第二十五步：关闭弹出的Excel窗口（记录操作）")
    print("=" * 60)
    print(f"操作将记录到: {output_file}\n")
    
    # 开始记录（只初始化，不启动实时监听，因为我们手动记录操作）
    recorder.recording = True
    recorder.actions = []
    recorder.start_time = time.time()
    print("✓ 已开始记录操作\n")
    
    try:
        # 执行关闭操作（使用默认关闭按钮矩形区域）
        success = close_excel_window(
            recorder=recorder,
            use_default_rectangle=True  # 使用默认矩形区域
        )
        
        if success:
            print("\n" + "=" * 60)
            print("第二十五步完成！Excel窗口应该已经被关闭。")
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
                if action_type == 'click':
                    pos = action.get('data', {}).get('position', {})
                    print(f"  {i}. 关闭Excel窗口 - 坐标: ({pos.get('x')}, {pos.get('y')})")
                elif action_type == 'mouse_move':
                    pos = action.get('data', {}).get('position', {})
                    print(f"  {i}. 鼠标移动 - 坐标: ({pos.get('x')}, {pos.get('y')})")
                else:
                    print(f"  {i}. {action_type}")


if __name__ == "__main__":
    main()

