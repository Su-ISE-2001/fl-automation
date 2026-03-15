"""
轨迹记录器
参考desktop_gradio_frontend.py的结构，用于保存完整的轨迹数据（包括操作前后的截图）
"""
import os
import json
import time
import copy
import pyautogui
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image

# 轨迹模板
TRAJECTORY_TEMPLATE = {
    "query": None,
    "application": None,
    "platform_type": "windows",
    "url": None,
    "trajectory": []
}

# 步骤模板
STEP_TEMPLATE = {
    "observation": None,  # 截图路径（操作前的截图）
    "screenshot_caption": None,
    "rationale": None,
    "step_instruction": None,
    "action": [],  # 操作列表，格式为[{"name": "xxx", "parameters": {...}}]
    "width": None,
    "height": None,
    "elapsed_time": None,  # 当前步骤的相对运行时间（秒）
    "objects": None,  # 对象信息路径
    "reference_idx": None
}

# 对象模板
OBJECT_TEMPLATE = {
    "id": 0,
    "bbox": None,  # [left, top, right, bottom]
    "deperated": False,
    "active": True,
    "focusable": True,
    "clickable": True,
}


class TrajectoryRecorder:
    """轨迹记录器类，用于保存完整的轨迹数据"""
    
    def __init__(self, root_dir: str = "./trajectory_data", query: str = "UV Analyst自动化流程", 
                 application: str = "UV Analyst for UV2510"):
        """
        初始化轨迹记录器
        
        Args:
            root_dir: 数据保存根目录
            query: 查询/任务描述
            application: 应用程序名称
        """
        self.root_dir = Path(root_dir)
        self.query = query
        self.application = application
        
        # 创建轨迹文件夹
        now = datetime.now()
        year = now.year
        month = str(now.month).zfill(2)
        day = str(now.day).zfill(2)
        hour = str(now.hour).zfill(2)
        minute = str(now.minute).zfill(2)
        second = str(now.second).zfill(2)
        
        # 创建目录结构：root_dir/YYYYMMDD/HHMMSS/
        self.trajectory_dir = self.root_dir / f"{year}{month}{day}" / f"{hour}{minute}{second}"
        self.img_dir = self.trajectory_dir / "images"
        self.object_dir = self.trajectory_dir / "objects"
        
        # 创建目录
        self.trajectory_dir.mkdir(parents=True, exist_ok=True)
        self.img_dir.mkdir(parents=True, exist_ok=True)
        self.object_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化轨迹数据
        self.trajectory_data = copy.deepcopy(TRAJECTORY_TEMPLATE)
        self.trajectory_data['query'] = query
        self.trajectory_data['application'] = application
        self.trajectory_data['platform_type'] = "windows"
        
        # 步骤计数器和开始时间
        self.step_num = 0
        self.start_time = time.time()
        
        print(f"轨迹记录器已初始化")
        print(f"数据保存目录: {self.trajectory_dir}")
    
    def save_step(self, action_name: str, action_parameters: Dict[str, Any], 
                  element_info: Optional[Dict[str, Any]] = None,
                  screenshot_before: Optional[Image.Image] = None,
                  screenshot_after: Optional[Image.Image] = None,
                  step_instruction: Optional[str] = None,
                  rationale: Optional[str] = None,
                  screenshot_caption: Optional[str] = None):
        """
        保存一个步骤的轨迹信息
        
        Args:
            action_name: 操作名称（如 "click", "doubleClick", "write" 等）
            action_parameters: 操作参数（如 {"x": 0.5, "y": 0.3}）
            element_info: 元素信息（包含bbox等）
            screenshot_before: 操作前的截图（PIL Image）
            screenshot_after: 操作后的截图（PIL Image）
            step_instruction: 步骤指令（可选）
            rationale: 操作理由（可选）
            screenshot_caption: 截图标注（可选）
        """
        # 创建步骤数据
        step_data = copy.deepcopy(STEP_TEMPLATE)
        
        # 计算相对运行时间
        elapsed_time = time.time() - self.start_time
        step_data['elapsed_time'] = round(elapsed_time, 3)
        
        # 保存操作前的截图
        if screenshot_before is not None:
            img_path = self.img_dir / f"step_{self.step_num}.png"
            screenshot_before.save(str(img_path), format='PNG')
            step_data['observation'] = os.path.relpath(str(img_path), self.trajectory_dir)
            width, height = screenshot_before.size
            step_data['width'] = width
            step_data['height'] = height
        else:
            # 如果没有提供截图，获取当前屏幕截图
            screenshot = pyautogui.screenshot()
            img_path = self.img_dir / f"step_{self.step_num}.png"
            screenshot.save(str(img_path), format='PNG')
            step_data['observation'] = os.path.relpath(str(img_path), self.trajectory_dir)
            width, height = screenshot.size
            step_data['width'] = width
            step_data['height'] = height
        
        # 保存操作信息
        action_details = {
            "name": action_name,
            "parameters": action_parameters
        }
        step_data['action'] = [action_details]
        
        # 保存可选字段
        if step_instruction:
            step_data['step_instruction'] = step_instruction
        if rationale:
            step_data['rationale'] = rationale
        if screenshot_caption:
            step_data['screenshot_caption'] = screenshot_caption
        
        # 保存对象信息
        if element_info is None:
            element_info = copy.deepcopy(OBJECT_TEMPLATE)
            element_info["id"] = 0
            element_info["bbox"] = [0, 0, 0, 0]
        
        objects_path = self.object_dir / f"step_{self.step_num}.json"
        with open(objects_path, 'w', encoding='utf-8') as f:
            json.dump([element_info], f, ensure_ascii=False, indent=4)
        step_data['objects'] = os.path.relpath(str(objects_path), self.trajectory_dir)
        
        # 设置reference_idx
        if isinstance(element_info, dict) and 'id' in element_info:
            step_data['reference_idx'] = element_info.get('id', 0)
        else:
            step_data['reference_idx'] = 0
        
        # 添加到轨迹
        self.trajectory_data['trajectory'].append(step_data)
        
        # 如果提供了操作后的截图，也保存它（作为下一个步骤的观察）
        if screenshot_after is not None:
            self.step_num += 1
            after_img_path = self.img_dir / f"step_{self.step_num}.png"
            screenshot_after.save(str(after_img_path), format='PNG')
            # 注意：操作后的截图会在下一个步骤中使用
        
        self.step_num += 1
        print(f"已保存步骤 {self.step_num - 1}: {action_name}")
    
    def save_trajectory(self):
        """保存完整的轨迹数据到JSON文件"""
        trajectory_file = self.trajectory_dir / "trajectory.json"
        with open(trajectory_file, 'w', encoding='utf-8') as f:
            json.dump(self.trajectory_data, f, ensure_ascii=False, indent=4)
        
        print(f"\n轨迹数据已保存到: {trajectory_file}")
        print(f"共保存 {len(self.trajectory_data['trajectory'])} 个步骤")
        return str(trajectory_file)
    
    def get_screenshot(self) -> Image.Image:
        """获取当前屏幕截图"""
        return pyautogui.screenshot()
    
    def create_element_info(self, bbox: List[float], element_id: int = 0) -> Dict[str, Any]:
        """
        创建元素信息
        
        Args:
            bbox: 边界框 [left, top, right, bottom]
            element_id: 元素ID
        
        Returns:
            元素信息字典
        """
        element_info = copy.deepcopy(OBJECT_TEMPLATE)
        element_info["id"] = element_id
        element_info["bbox"] = bbox
        return element_info
