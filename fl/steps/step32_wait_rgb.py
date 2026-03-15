"""
第二步：等待指定区域RGB变为目标值
记录等待操作到GUI数据集
"""
import os
import time
import pyautogui
from pathlib import Path
import sys

# 添加父目录到路径，以便导入共享模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.gui_recorder import GUIRecorder
from core.trajectory_recorder import TrajectoryRecorder
from core.trajectory_helper import save_wait_action


def get_detection_rectangle():
    """
    获取检测区域的矩形
    检测区域: (333,678), (397,687), (332,754), (403,757)
    
    Returns:
        (x1, y1, x2, y2): 矩形区域坐标
    """
    # 定义矩形的四个顶点
    points = [
        (333, 678),   # 左上
        (397, 687),   # 右上
        (332, 754),   # 左下
        (403, 757)    # 右下
    ]
    
    # 计算矩形的边界
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)
    
    return (x_min, y_min, x_max, y_max)


def wait_for_rgb_change(detection_rect: tuple, target_rgb: tuple, max_wait_seconds: int = 120, 
                       check_interval: float = 1.0, trajectory_recorder: TrajectoryRecorder = None,
                       step_instruction: str = "等待软件开启成功"):
    """
    智能等待检测区域变成目标RGB值
    每一步等待1秒并写入轨迹JSON文件
    如果等待了5.8秒，就记录5个1秒的等待动作和1个0.8秒的等待动作
    
    Args:
        detection_rect: 检测矩形区域 (x1, y1, x2, y2)
        target_rgb: 目标RGB值 (r, g, b)
        max_wait_seconds: 最大等待时间（秒），默认120秒
        check_interval: 检查间隔（秒），默认1.0秒
        trajectory_recorder: 轨迹记录器对象，用于记录每次等待操作
        step_instruction: 步骤指令描述
    
    Returns:
        bool: 检测区域是否已变成目标RGB值
    """
    x1, y1, x2, y2 = detection_rect
    x_min = min(x1, x2)
    x_max = max(x1, x2)
    y_min = min(y1, y2)
    y_max = max(y1, y2)
    
    # RGB容差（允许一定的误差）
    rgb_tolerance = 5
    
    print(f"\n正在检测区域是否变成目标RGB（检测区域: ({x_min}, {y_min}) 到 ({x_max}, {y_max})）...")
    print(f"目标RGB: rgb{target_rgb}")
    print(f"最大等待时间: {max_wait_seconds} 秒")
    print(f"检测间隔: {check_interval} 秒")
    
    start_time = time.time()
    check_count = 0
    last_wait_end_time = start_time  # 记录上次等待结束的时间
    
    while time.time() - start_time < max_wait_seconds:
        try:
            check_count += 1
            elapsed = time.time() - start_time
            remaining_time = max_wait_seconds - elapsed
            
            # 计算本次等待时间：如果剩余时间>=1秒，等待1秒；否则等待剩余时间
            wait_duration = min(check_interval, remaining_time)
            
            # 如果等待时间>0.01秒，才进行等待并记录
            if wait_duration > 0.01:
                # 每次等待并记录等待操作到轨迹JSON
                if trajectory_recorder:
                    # 调用save_wait_action，它会自动获取截图、等待、再获取截图并保存
                    save_wait_action(
                        trajectory_recorder,
                        wait_duration,  # 等待时间（1秒或剩余时间）
                        step_instruction=step_instruction
                    )
                else:
                    # 如果没有轨迹记录器，只等待
                    time.sleep(wait_duration)
                
                last_wait_end_time = time.time()
            
            # 获取当前屏幕截图用于RGB检测
            screenshot = pyautogui.screenshot()
            
            # 提取检测区域
            detection_region = screenshot.crop((x_min, y_min, x_max, y_max))
            
            # 计算检测区域的平均RGB值
            pixels = list(detection_region.getdata())
            if pixels:
                # 计算平均RGB
                total_r, total_g, total_b = 0, 0, 0
                for pixel in pixels:
                    if len(pixel) == 3:  # RGB
                        r, g, b = pixel
                    elif len(pixel) == 4:  # RGBA
                        r, g, b, _ = pixel
                    else:
                        continue
                    total_r += r
                    total_g += g
                    total_b += b
                
                pixel_count = len(pixels)
                avg_r = total_r // pixel_count
                avg_g = total_g // pixel_count
                avg_b = total_b // pixel_count
                avg_rgb = (avg_r, avg_g, avg_b)
                
                # 检查RGB是否匹配（允许容差）
                r_match = abs(avg_r - target_rgb[0]) <= rgb_tolerance
                g_match = abs(avg_g - target_rgb[1]) <= rgb_tolerance
                b_match = abs(avg_b - target_rgb[2]) <= rgb_tolerance
                rgb_matched = r_match and g_match and b_match
                
                # 显示检测信息
                status = "✓ 匹配" if rgb_matched else "✗ 不匹配"
                print(f"\r检测 #{check_count} | 已等待 {elapsed:.1f}秒 | 平均RGB: rgb{avg_rgb} | {status}", end="", flush=True)
                
                # 如果RGB匹配，认为检测区域已变成目标RGB值
                if rgb_matched:
                    # 计算从上次等待结束到现在的剩余时间
                    current_time = time.time()
                    remaining_after_detection = current_time - last_wait_end_time
                    
                    # 如果有剩余时间（>0.01秒），记录一个剩余时间的等待动作
                    if remaining_after_detection > 0.01 and trajectory_recorder:
                        save_wait_action(
                            trajectory_recorder,
                            remaining_after_detection,
                            step_instruction=step_instruction
                        )
                    
                    total_elapsed = current_time - start_time
                    print(f"\n✓ 检测到区域已变成目标RGB（等待了 {total_elapsed:.1f} 秒，共检测 {check_count} 次）")
                    return True
            
            # 如果剩余时间不足，退出循环
            if remaining_time <= 0.01:
                break
            
        except Exception as e:
            print(f"\n检测过程中出错: {e}")
            time.sleep(check_interval)
            continue
    
    # 超时：计算从上次等待结束到现在的剩余时间
    current_time = time.time()
    remaining_after_timeout = current_time - last_wait_end_time
    
    # 如果有剩余时间（>0.01秒），记录一个剩余时间的等待动作
    if remaining_after_timeout > 0.01 and trajectory_recorder:
        save_wait_action(
            trajectory_recorder,
            remaining_after_timeout,
            step_instruction=step_instruction
        )
    
    elapsed = current_time - start_time
    print(f"\n⚠ 等待超时（已等待 {elapsed:.1f} 秒，共检测 {check_count} 次），将继续执行")
    return False


def wait_for_rgb(recorder: GUIRecorder = None, trajectory_recorder: TrajectoryRecorder = None):
    """
    等待指定区域RGB变为目标值
    
    Args:
        recorder: GUI记录器对象
        trajectory_recorder: 轨迹记录器对象
    """
    print("=" * 60)
    print("第二步：等待指定区域RGB变为目标值")
    print("=" * 60)
    
    try:
        # 获取检测区域
        detection_rect = get_detection_rectangle()
        
        # 目标RGB值
        target_rgb = (38, 38, 38)
        
        # 记录等待开始
        wait_start_time = time.time()
        if recorder:
            recorder.add_custom_action("wait_start", {
                "description": "开始智能检测屏幕变化",
                "target_rgb": target_rgb,
                "detection_rect": detection_rect
            })
        
        # 智能等待检测区域变成目标RGB值
        rgb_matched = wait_for_rgb_change(
            detection_rect,
            target_rgb,
            max_wait_seconds=120,
            check_interval=1.0,  # 每步等待1秒
            trajectory_recorder=trajectory_recorder,
            step_instruction="等待软件开启成功"
        )
        
        wait_duration = time.time() - wait_start_time
        
        # 记录等待结束
        if recorder:
            recorder.add_custom_action("wait_end", {
                "duration_seconds": wait_duration,
                "rgb_matched": rgb_matched,
                "description": f"等待完成（耗时 {wait_duration:.1f} 秒）"
            })
        
        if rgb_matched:
            print("✓ 检测完成，区域已变成目标RGB值")
        else:
            print("⚠ 检测超时，但将继续执行")
        
        print("✓ 第二步完成")
        return True
        
    except Exception as e:
        print(f"等待操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数 - 等待RGB变化并记录操作"""
    # 初始化GUI记录器
    output_file = "FL_step2_wait_rgb.json"
    recorder = GUIRecorder(output_file)
    
    print("\n" + "=" * 60)
    print("第二步：等待指定区域RGB变为目标值（记录操作）")
    print("=" * 60)
    print(f"操作将记录到: {output_file}\n")
    
    # 开始记录（只初始化，不启动实时监听，因为我们手动记录操作）
    recorder.recording = True
    recorder.actions = []
    recorder.start_time = time.time()
    print("✓ 已开始记录操作\n")
    
    try:
        # 执行等待操作
        success = wait_for_rgb(recorder=recorder)
        
        if success:
            print("\n" + "=" * 60)
            print("第二步完成！")
            print("=" * 60)
        else:
            print("\n操作失败或被中断，请检查错误信息")
            
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
                if action_type == 'wait_start':
                    desc = action.get('data', {}).get('description', '')
                    print(f"  {i}. {desc}")
                elif action_type == 'wait_end':
                    duration = action.get('data', {}).get('duration_seconds', 0)
                    print(f"  {i}. 等待完成 - {duration:.2f} 秒")
                else:
                    print(f"  {i}. {action_type}")


if __name__ == "__main__":
    main()

