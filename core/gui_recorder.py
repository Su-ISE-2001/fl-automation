"""
GUI操作记录器
用于记录鼠标和键盘操作，生成GUI数据集
"""
import json
import time
import keyboard
import mouse
from datetime import datetime
from typing import List, Dict, Any
import pyautogui


class GUIRecorder:
    """GUI操作记录器类"""
    
    def __init__(self, output_file: str = "gui_recording.json"):
        """
        初始化记录器
        
        Args:
            output_file: 输出文件路径
        """
        self.output_file = output_file
        self.actions: List[Dict[str, Any]] = []
        self.recording = False
        self.start_time = None
        
    def start_recording(self):
        """开始记录操作"""
        self.recording = True
        self.actions = []
        self.start_time = time.time()
        print("开始记录GUI操作...")
        
        # 注册鼠标事件
        try:
            # mouse库的API可能因版本而异
            if hasattr(mouse, 'on_click'):
                mouse.on_click(self._on_mouse_click)
            if hasattr(mouse, 'on_scroll'):
                mouse.on_scroll(self._on_mouse_scroll)
            # on_move可能不存在，跳过
            # mouse.on_move(self._on_mouse_move)
        except Exception as e:
            print(f"警告: 鼠标事件注册失败: {e}")
        
        # 注册键盘事件
        try:
            keyboard.on_press(self._on_key_press)
        except Exception as e:
            print(f"警告: 键盘事件注册失败: {e}")
        
    def stop_recording(self):
        """停止记录操作"""
        self.recording = False
        try:
            if hasattr(mouse, 'unhook_all'):
                mouse.unhook_all()
        except:
            pass
        try:
            keyboard.unhook_all()
        except:
            pass
        print("停止记录GUI操作")
        
    def save_recording(self):
        """保存记录到文件"""
        if not self.actions:
            print("没有记录到任何操作")
            return
            
        recording_data = {
            "timestamp": datetime.now().isoformat(),
            "total_actions": len(self.actions),
            "duration": time.time() - self.start_time if self.start_time else 0,
            "actions": self.actions
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(recording_data, f, indent=2, ensure_ascii=False)
        
        print(f"已保存 {len(self.actions)} 个操作到 {self.output_file}")
        
    def _on_mouse_click(self, event):
        """处理鼠标点击事件"""
        if not self.recording:
            return
        
        try:
            # 处理不同版本的mouse库API
            if hasattr(event, 'button'):
                button = event.button.name if hasattr(event.button, 'name') else str(event.button)
            else:
                button = 'left'  # 默认
            
            if hasattr(event, 'pos'):
                pos = event.pos
            elif hasattr(event, 'x') and hasattr(event, 'y'):
                pos = (event.x, event.y)
            else:
                pos = pyautogui.position()
            
            action = {
                "type": "mouse_click",
                "button": button,
                "position": {"x": pos[0], "y": pos[1]},
                "timestamp": time.time() - self.start_time,
                "screen_size": {"width": pyautogui.size().width, "height": pyautogui.size().height}
            }
            self.actions.append(action)
        except Exception as e:
            print(f"记录鼠标点击时出错: {e}")
        
    def _on_mouse_move(self, event):
        """处理鼠标移动事件（可选，可能产生大量数据）"""
        # 为了减少数据量，可以只记录重要的移动
        pass
        
    def _on_mouse_scroll(self, event):
        """处理鼠标滚动事件"""
        if not self.recording:
            return
        
        try:
            # 处理不同版本的mouse库API
            if hasattr(event, 'delta'):
                delta = event.delta
            else:
                delta = 0
            
            if hasattr(event, 'pos'):
                pos = event.pos
            elif hasattr(event, 'x') and hasattr(event, 'y'):
                pos = (event.x, event.y)
            else:
                pos = pyautogui.position()
            
            action = {
                "type": "mouse_scroll",
                "delta": delta,
                "position": {"x": pos[0], "y": pos[1]},
                "timestamp": time.time() - self.start_time
            }
            self.actions.append(action)
        except Exception as e:
            print(f"记录鼠标滚动时出错: {e}")
        
    def _on_key_press(self, event):
        """处理键盘按键事件"""
        if not self.recording:
            return
            
        action = {
            "type": "key_press",
            "key": event.name,
            "scan_code": event.scan_code,
            "timestamp": time.time() - self.start_time
        }
        self.actions.append(action)
        
    def add_custom_action(self, action_type: str, data: Dict[str, Any]):
        """添加自定义操作记录"""
        if not self.recording:
            return
            
        action = {
            "type": action_type,
            "data": data,
            "timestamp": time.time() - self.start_time if self.start_time else 0
        }
        self.actions.append(action)
