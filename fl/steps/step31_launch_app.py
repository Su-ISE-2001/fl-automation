"""
第一步：双击桌面图标打开软件
记录双击操作到GUI数据集
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


def get_random_point_in_rectangle():
    """
    在指定的矩形区域内随机选择一个点
    矩形由四个点围成: (17,711), (53,713), (18,745), (55,747)
    
    Returns:
        (x, y): 随机点的坐标
    """
    # 定义矩形的四个顶点
    points = [
        (17, 711),  # 左上
        (53, 713),  # 右上
        (18, 745),  # 左下
        (55, 747)   # 右下
    ]
    
    # 计算矩形的边界
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)
    
    # 在矩形内随机选择一个点
    x = random.randint(x_min, x_max)
    y = random.randint(y_min, y_max)
    
    return (x, y)


def launch_by_double_click(shortcut_path: str = None, 
                          icon_x: int = None, icon_y: int = None,
                          recorder: GUIRecorder = None,
                          trajectory_recorder: TrajectoryRecorder = None,
                          use_random_rectangle: bool = True):
    """
    使用pyautogui模拟双击桌面图标，并记录操作
    
    Args:
        shortcut_path: 快捷方式路径（可选，用于验证）
        icon_x: 图标X坐标（如果指定，将使用此坐标；否则在矩形内随机）
        icon_y: 图标Y坐标（如果指定，将使用此坐标；否则在矩形内随机）
        recorder: GUI记录器对象
        trajectory_recorder: 轨迹记录器对象
        use_random_rectangle: 是否在矩形区域内随机选择点击位置
    """
    print("=" * 60)
    print("第一步：双击桌面图标打开软件")
    print("=" * 60)
    
    # 检查快捷方式是否存在（如果提供了路径）
    if shortcut_path and not os.path.exists(shortcut_path):
        print(f"警告：找不到快捷方式文件: {shortcut_path}")
        print("将继续执行双击操作...")
    
    if shortcut_path:
        print(f"快捷方式路径: {shortcut_path}")
    
    # 获取图标坐标
    if icon_x is None or icon_y is None:
        if use_random_rectangle:
            # 在矩形区域内随机选择
            icon_x, icon_y = get_random_point_in_rectangle()
            print(f"\n在矩形区域内随机选择坐标: ({icon_x}, {icon_y})")
            print("矩形范围: X[17-55], Y[711-747]")
        else:
            print("\n需要获取图标在桌面上的坐标...")
            print("请将鼠标移动到桌面图标上，然后按空格键获取坐标")
            import keyboard
            coordinates = None
            
            def on_key(event):
                nonlocal coordinates
                if event.name == 'space' and event.event_type == 'down':
                    x, y = pyautogui.position()
                    coordinates = (x, y)
                    print(f"\n✓ 获取到坐标: ({x}, {y})")
                    keyboard.unhook_all()
            
            keyboard.on_press(on_key)
            
            try:
                while coordinates is None:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                keyboard.unhook_all()
                return False
            
            keyboard.unhook_all()
            
            if coordinates is None:
                print("未获取到坐标，操作取消")
                return False
            icon_x, icon_y = coordinates
    
    print(f"\n点击坐标: ({icon_x}, {icon_y})")
    
    try:
        # 显示桌面（Win+D）
        print("\n显示桌面...")
        pyautogui.hotkey('win', 'd')
        time.sleep(0.8)
        
        # 记录显示桌面的操作（如果recorder存在）
        if recorder:
            recorder.add_custom_action("hotkey", {
                "keys": ["win", "d"],
                "description": "显示桌面"
            })
        
        # 移动鼠标到图标位置
        print(f"移动鼠标到图标位置 ({icon_x}, {icon_y})...")
        pyautogui.moveTo(icon_x, icon_y, duration=0.5)
        time.sleep(0.3)
        
        # 记录鼠标移动
        if recorder:
            recorder.add_custom_action("mouse_move", {
                "position": {"x": icon_x, "y": icon_y},
                "description": "移动到图标位置"
            })
        
        # 获取双击前的截图（用于轨迹记录）
        if trajectory_recorder:
            screenshot_before = trajectory_recorder.get_screenshot()
        
        # 双击图标
        print("双击图标...")
        pyautogui.doubleClick(icon_x, icon_y)
        time.sleep(0.5)
        
        # 记录双击操作
        if recorder:
            recorder.add_custom_action("double_click", {
                "position": {"x": icon_x, "y": icon_y},
                "target": "desktop_icon",
                "description": "双击桌面图标打开软件",
                "rectangle": {
                    "points": [(18, 711), (54, 713), (20, 745), (55, 747)],
                    "is_random": use_random_rectangle
                }
            })
        
        # 保存轨迹信息（使用save_click_action记录双击操作）
        if trajectory_recorder:
            # 计算边界框
            bbox = [18, 711, 54, 747]  # [left, top, right, bottom]
            
            # 使用save_click_action记录双击操作
            # 注意：save_click_action会在内部获取截图，但我们已经获取了操作前的截图
            # 所以我们需要手动保存步骤，而不是使用save_click_action
            screenshot_after = trajectory_recorder.get_screenshot()
            time.sleep(1.0)  # 等待应用启动
            screenshot_after = trajectory_recorder.get_screenshot()  # 再次获取，确保应用已启动
            
            # 计算归一化坐标
            screen_width, screen_height = pyautogui.size()
            x_norm = icon_x / screen_width
            y_norm = icon_y / screen_height
            
            # 创建元素信息
            element_info = trajectory_recorder.create_element_info(bbox, element_id=0)
            
            # 保存步骤
            trajectory_recorder.save_step(
                action_name="doubleClick",
                action_parameters={
                    "x": x_norm,
                    "y": y_norm
                },
                element_info=element_info,
                screenshot_before=screenshot_before,
                screenshot_after=screenshot_after,
                step_instruction="双击桌面图标打开软件"
            )
        
        print("✓ 双击操作完成")
        print("等待应用程序启动...")
        time.sleep(2)
        
        print("✓ 第一步完成：软件应该已经打开")
        return True
        
    except Exception as e:
        print(f"双击操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False



def main():
    """主函数 - 双击桌面图标并记录操作"""
    shortcut_path = None  # 可以根据实际情况设置路径
    
    # 初始化GUI记录器
    output_file = "FL_step1_double_click.json"
    recorder = GUIRecorder(output_file)
    
    print("\n" + "=" * 60)
    print("第一步：双击桌面图标打开软件（记录操作）")
    print("=" * 60)
    print(f"操作将记录到: {output_file}\n")
    
    # 开始记录（只初始化，不启动实时监听，因为我们手动记录操作）
    recorder.recording = True
    recorder.actions = []
    recorder.start_time = time.time()
    print("✓ 已开始记录操作\n")
    
    try:
        # 执行双击操作（在矩形区域内随机选择点击位置）
        success = launch_by_double_click(
            shortcut_path=shortcut_path,
            recorder=recorder,
            use_random_rectangle=True  # 在矩形区域内随机选择
        )
        
        if success:
            print("\n" + "=" * 60)
            print("第一步完成！软件应该已经打开。")
            print("=" * 60)
        else:
            print("\n启动失败，请检查错误信息")
            
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
                    print(f"  {i}. 双击图标 - 坐标: ({pos.get('x')}, {pos.get('y')})")
                elif action_type == 'hotkey':
                    keys = action.get('data', {}).get('keys', [])
                    print(f"  {i}. 快捷键 - {'+'.join(keys)}")
                elif action_type == 'mouse_move':
                    pos = action.get('data', {}).get('position', {})
                    print(f"  {i}. 鼠标移动 - 坐标: ({pos.get('x')}, {pos.get('y')})")
                else:
                    print(f"  {i}. {action_type}")


if __name__ == "__main__":
    main()

