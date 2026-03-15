# FL 软件自动化（单软件）

本目录为 **FL 荧光软件** 单软件自动化，可单独运行、单独仓库发布。

## 依赖说明

FL 流程中部分步骤（如 EX 固定波长、EM 起止波长）会从 **UV 流程的结果** 读取 `peak_nm`。  
若先跑过 UV 流程，会生成 `step22_result_*.json`，FL 会自动查找最新一份使用。  
若单独只跑 FL，请先手动准备一份 `step22_result.json`（含 `peak_nm` 或 `nm` 字段），或在本目录/项目根目录下存在该文件。

## 运行方式

在**项目根目录**下执行：

```bash
python fl/run_fl_automation.py
```

可选参数：
- `--label <标签>`：输出文件名与轨迹目录会带该标签
- `--no-confirm`：跳过开始确认

## 流程说明

约 45 步（对应原流程 31–75），包括：
- 启动 FL → 联机 → 波长扫描/设置/仪器/狭缝/PMT → EM 扫描（使用 UV 的 peak_nm）→ 保存 xls → 读 A31 → 保存曲线 → EX 扫描（使用 A31）→ 保存 → 退出

## 单独发布到 GitHub

若只发布 FL 部分，可复制以下内容到新仓库：

- 本目录 `fl/`
- 根目录的 `core/`
- 根目录的 `requirements.txt`、`config.yaml`

运行前请确保有 UV 结果文件 `step22_result.json`（或 `step22_result_*.json`），或手动创建符合格式的 JSON。

```bash
pip install -r requirements.txt
python fl/run_fl_automation.py
```
