"""
UV Analyst for UV2510 自动化脚本
使用pywinauto和pyautogui实现GUI自动化
"""
import time
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import pywinauto
from pywinauto import Application
import pyautogui
from .gui_recorder import GUIRecorder


class UVAnalystAutomation:
    """UV Analyst自动化类"""
    
    def __init__(self, shortcut_path: str = r"C:\Users\Public\Desktop\ UV Analyst for UV2510 4.1.lnk"):
        """
        初始化自动化对象
        
        Args:
            shortcut_path: 软件快捷方式路径
        """
        self.shortcut_path = shortcut_path
        self.app: Optional[Application] = None
        self.main_window = None
        self.recorder = GUIRecorder("uv_analyst_actions.json")
        
    def launch_application(self, wait_time: int = 5):
        """
        启动应用程序
        
        Args:
            wait_time: 等待应用启动的时间（秒）
        """
        print(f"正在启动应用程序: {self.shortcut_path}")
        
        if not os.path.exists(self.shortcut_path):
            raise FileNotFoundError(f"找不到快捷方式: {self.shortcut_path}")
        
        # 使用subprocess启动快捷方式
        subprocess.Popen([self.shortcut_path], shell=True)
        time.sleep(wait_time)
        
        # 尝试连接到应用程序
        try:
            # 方法1: 通过窗口标题连接
            self.app = Application(backend="uia").connect(title_re=".*UV.*Analyst.*", timeout=10)
            print("已连接到应用程序（通过窗口标题）")
        except:
            try:
                # 方法2: 通过进程名连接
                self.app = Application(backend="uia").connect(path="UV2510.exe", timeout=10)
                print("已连接到应用程序（通过进程名）")
            except:
                # 方法3: 使用pyautogui作为备选
                print("使用pyautogui作为备选方案")
                self.app = None
        
        if self.app:
            self.main_window = self.app.top_window()
            print(f"主窗口: {self.main_window.window_text()}")
        else:
            print("警告: 无法连接到应用程序，将使用屏幕坐标方式")
            
    def find_element(self, element_name: str, control_type: str = "Button"):
        """
        查找界面元素
        
        Args:
            element_name: 元素名称或文本
            control_type: 控件类型（Button, Edit, Menu等）
        """
        if not self.app:
            return None
            
        try:
            if control_type == "Button":
                return self.main_window.child_window(control_type="Button", found_index=0)
            elif control_type == "Edit":
                return self.main_window.child_window(control_type="Edit", found_index=0)
            else:
                return self.main_window.child_window(control_type=control_type, found_index=0)
        except Exception as e:
            print(f"查找元素失败: {e}")
            return None
    
    def click_button(self, button_text: str = None, button_index: int = None, 
                    use_coordinates: tuple = None, record: bool = True):
        """
        点击按钮
        
        Args:
            button_text: 按钮文本
            button_index: 按钮索引
            use_coordinates: 使用坐标点击 (x, y)
            record: 是否记录操作
        """
        if use_coordinates:
            x, y = use_coordinates
            pyautogui.click(x, y)
            if record:
                self.recorder.add_custom_action("click", {
                    "method": "coordinates",
                    "position": {"x": x, "y": y},
                    "target": "button"
                })
            print(f"点击坐标: ({x}, {y})")
            return
            
        if self.app and self.main_window:
            try:
                if button_text:
                    button = self.main_window.child_window(title=button_text, control_type="Button")
                elif button_index is not None:
                    buttons = self.main_window.descendants(control_type="Button")
                    button = buttons[button_index] if button_index < len(buttons) else None
                else:
                    raise ValueError("必须提供button_text或button_index")
                    
                if button:
                    button.click_input()
                    if record:
                        self.recorder.add_custom_action("click", {
                            "method": "element",
                            "target": button_text or f"button_{button_index}"
                        })
                    print(f"点击按钮: {button_text or f'索引{button_index}'}")
                    time.sleep(0.5)
            except Exception as e:
                print(f"点击按钮失败: {e}")
        else:
            print("应用程序未连接，无法点击按钮")
    
    def input_text(self, text: str, control_name: str = None, 
                  use_coordinates: tuple = None, record: bool = True):
        """
        输入文本
        
        Args:
            text: 要输入的文本
            control_name: 控件名称
            use_coordinates: 使用坐标点击输入框 (x, y)
            record: 是否记录操作
        """
        if use_coordinates:
            x, y = use_coordinates
            pyautogui.click(x, y)
            time.sleep(0.3)
            pyautogui.write(text)
            if record:
                self.recorder.add_custom_action("input_text", {
                    "method": "coordinates",
                    "position": {"x": x, "y": y},
                    "text": text
                })
            print(f"在坐标 ({x}, {y}) 输入文本: {text}")
            return
            
        if self.app and self.main_window:
            try:
                if control_name:
                    edit = self.main_window.child_window(control_type="Edit", title_re=control_name)
                else:
                    edit = self.main_window.child_window(control_type="Edit", found_index=0)
                    
                if edit:
                    edit.set_text(text)
                    if record:
                        self.recorder.add_custom_action("input_text", {
                            "method": "element",
                            "target": control_name or "first_edit",
                            "text": text
                        })
                    print(f"输入文本: {text}")
                    time.sleep(0.3)
            except Exception as e:
                print(f"输入文本失败: {e}")
        else:
            print("应用程序未连接，无法输入文本")
    
    def select_menu(self, menu_path: list, record: bool = True):
        """
        选择菜单项
        
        Args:
            menu_path: 菜单路径列表，如 ["File", "Open"]
            record: 是否记录操作
        """
        if self.app and self.main_window:
            try:
                menu = self.main_window.menu_item(menu_path)
                menu.click_input()
                if record:
                    self.recorder.add_custom_action("menu_select", {
                        "menu_path": menu_path
                    })
                print(f"选择菜单: {' > '.join(menu_path)}")
                time.sleep(0.5)
            except Exception as e:
                print(f"选择菜单失败: {e}")
        else:
            print("应用程序未连接，无法选择菜单")
    
    def wait_for_window(self, window_title: str, timeout: int = 10):
        """
        等待窗口出现
        
        Args:
            window_title: 窗口标题（支持正则表达式）
            timeout: 超时时间（秒）
        """
        if self.app:
            try:
                window = self.app.window(title_re=window_title, timeout=timeout)
                print(f"窗口已出现: {window_title}")
                return window
            except Exception as e:
                print(f"等待窗口超时: {e}")
                return None
        return None
    
    def take_screenshot(self, filename: str = None):
        """
        截取屏幕截图
        
        Args:
            filename: 保存的文件名
        """
        if filename is None:
            filename = f"screenshot_{int(time.time())}.png"
        
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"截图已保存: {filename}")
        return filename
    
    def run_automation_script(self, script_file: str):
        """
        运行自动化脚本
        
        Args:
            script_file: 脚本文件路径（JSON格式）
        """
        import json
        with open(script_file, 'r', encoding='utf-8') as f:
            script = json.load(f)
        
        print(f"开始执行自动化脚本: {script_file}")
        for action in script.get('actions', []):
            action_type = action.get('type')
            if action_type == 'click':
                self.click_button(use_coordinates=(action['x'], action['y']))
            elif action_type == 'input':
                self.input_text(action['text'], use_coordinates=(action['x'], action['y']))
            elif action_type == 'wait':
                time.sleep(action['duration'])
            elif action_type == 'screenshot':
                self.take_screenshot(action.get('filename'))
        
        print("自动化脚本执行完成")
    
    def close_application(self):
        """关闭应用程序"""
        if self.app:
            try:
                self.main_window.close()
                print("应用程序已关闭")
            except Exception as e:
                print(f"关闭应用程序失败: {e}")
        else:
            # 使用任务管理器关闭
            os.system("taskkill /F /IM UV2510.exe")


def example_usage():
    """示例用法"""
    automation = UVAnalystAutomation()
    
    # 启动记录
    automation.recorder.start_recording()
    
    try:
        # 启动应用程序
        automation.launch_application()
        time.sleep(2)
        
        # 这里添加你的自动化操作
        # 例如：
        # automation.click_button(use_coordinates=(100, 200))
        # automation.input_text("test", use_coordinates=(150, 250))
        
        print("按 Ctrl+C 停止记录")
        input("按回车键停止记录...")
        
    except KeyboardInterrupt:
        print("\n停止记录...")
    finally:
        # 停止记录并保存
        automation.recorder.stop_recording()
        automation.recorder.save_recording()
        automation.close_application()


if __name__ == "__main__":
    example_usage()
