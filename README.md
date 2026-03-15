# FL 软件自动化

本仓库仅包含 **FL 荧光软件** 自动化部分，从 AutoAIE 项目拆出。

## 依赖说明

部分步骤会读取 UV 流程生成的 `step22_result.json`（peak_nm）。单独运行前请准备该文件或先跑 UV 流程。

## 安装与运行

```bash
pip install -r requirements.txt
python fl/run_fl_automation.py
```

可选：`--label <标签>`、`--no-confirm`

详见 `fl/README.md`。
