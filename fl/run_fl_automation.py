"""
FL 软件单软件自动化流程（步骤 31–75）
可单独运行、单独发布。需先有 UV 的 step22 结果（peak_nm）或手动提供 step22_result.json。
"""
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.gui_recorder import GUIRecorder
from core.trajectory_recorder import TrajectoryRecorder
from core.xls_utils import find_latest_xls_file, read_cell_a31, save_result

from fl.steps.step31_launch_app import launch_by_double_click as launch_fl_app
from fl.steps.step32_wait_rgb import wait_for_rgb as wait_for_fl_rgb_32
from fl.steps.step33_click_button import click_button as click_fl_button
from fl.steps.step34_click_wavelength_scan import click_wavelength_scan_button as click_fl_wavelength_scan
from fl.steps.step35_click_settings import click_settings_button as click_fl_settings
from fl.steps.step36_click_instrument import click_instrument_button as click_fl_instrument
from fl.steps.step37_click_em_slit import click_em_slit_button as click_fl_em_slit
from fl.steps.step38_click_5nm import click_5nm_option as click_fl_5nm
from fl.steps.step39_click_ex_slit import click_ex_slit_button as click_fl_ex_slit
from fl.steps.step40_click_5nm import click_5nm_option as click_fl_5nm_ex
from fl.steps.step41_double_click_pmt import double_click_pmt_and_input as double_click_fl_pmt
from fl.steps.step42_click_wavelength_scan import click_wavelength_scan_button as click_fl_wavelength_scan_2
from fl.steps.step43_click_scan_mode import click_scan_mode_button as click_fl_scan_mode
from fl.steps.step44_click_em_scan import click_em_scan_button as click_fl_em_scan
from fl.steps.step45_double_click_ex_wavelength import double_click_ex_wavelength_and_input as double_click_fl_ex_wavelength
from fl.steps.step46_double_click_em_start_wavelength import double_click_em_start_wavelength_and_input as double_click_fl_em_start_wavelength
from fl.steps.step47_double_click_em_end_wavelength import double_click_em_end_wavelength_and_input as double_click_fl_em_end_wavelength
from fl.steps.step48_click_confirm import click_confirm_button as click_fl_confirm_button
from fl.steps.step49_wait_rgb import wait_for_rgb as wait_for_fl_rgb
from fl.steps.step50_click_start_scan import click_start_scan_button as click_fl_start_scan
from fl.steps.step52_click_xls_save import click_xls_save_button as click_fl_xls_save
from fl.steps.step53_input_filename import input_filename as input_fl_filename
from fl.steps.step54_click_save import click_save_button as click_fl_final_save
from fl.steps.step55_close_excel import close_excel_window as close_fl_excel
from fl.steps.step57_click_save_curve import click_save_curve_button as click_fl_save_curve
from fl.steps.step58_input_filename import double_click_and_input_filename as double_click_fl_input_filename
from fl.steps.step59_click_save import click_save_button as click_fl_save_final
from fl.steps.step60_click_settings import click_settings_button_fl as click_fl_settings_2
from fl.steps.step61_click_wavelength_scan import click_wavelength_scan_button as click_fl_wavelength_scan_3
from fl.steps.step62_click_scan_mode import click_scan_mode_button as click_fl_scan_mode_2
from fl.steps.step63_click_ex_scan import click_ex_scan_button as click_fl_ex_scan
from fl.steps.step64_double_click_em_fixed_wavelength import double_click_em_fixed_wavelength_and_input as double_click_fl_em_fixed_wavelength
from fl.steps.step65_double_click_ex_start_wavelength import double_click_ex_start_wavelength_and_input as double_click_fl_ex_start_wavelength
from fl.steps.step66_double_click_ex_end_wavelength import double_click_ex_end_wavelength_and_input as double_click_fl_ex_end_wavelength
from fl.steps.step67_click_confirm import click_confirm_button as click_fl_confirm_button_2
from fl.steps.step69_click_start_scan import click_start_scan_button as click_fl_start_scan_2
from fl.steps.step71_click_save import click_save_button as click_fl_save_2
from fl.steps.step72_input_filename import double_click_and_input_filename as double_click_fl_input_filename_2
from fl.steps.step73_click_save import click_save_button as click_fl_save_3
from fl.steps.step74_click_exit import click_exit_button as click_fl_exit
from fl.steps.step75_click_yes import click_yes_button as click_fl_yes

# 步骤49/51/68/70 共用同一 wait_for_rgb
def _wait_rgb(r, t): return wait_for_fl_rgb(recorder=r, trajectory_recorder=t)


def run_fl_automation(run_label: str = ""):
    """执行 FL 完整流程（约 45 步）。"""
    run_suffix = f"_{run_label}" if run_label else ""
    output_file = f"fl_automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}{run_suffix}.json"
    recorder = GUIRecorder(output_file)
    recorder.recording = True
    recorder.actions = []
    recorder.start_time = time.time()
    trajectory_recorder = TrajectoryRecorder(
        root_dir="./trajectory_data",
        query=f"FL自动化{run_suffix}",
        application="FL",
    )
    print("=" * 80)
    print("FL 软件自动化（单软件）")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"操作记录: {output_file}")
    print(f"轨迹目录: {trajectory_recorder.trajectory_dir}\n")
    step_count = 0
    failed_steps = []

    def step(cond, errmsg):
        nonlocal step_count
        step_count += 1
        print(f"\n{'='*80}\n步骤 {step_count}: {errmsg.split('：')[0]}\n{'='*80}")
        if not cond():
            raise Exception(errmsg)

    try:
        step(lambda: launch_fl_app(recorder=recorder, trajectory_recorder=trajectory_recorder, use_random_rectangle=True), "步骤31失败")
        step(lambda: wait_for_fl_rgb_32(recorder=recorder, trajectory_recorder=trajectory_recorder), "步骤32失败")
        step(lambda: click_fl_button(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤33失败")
        step(lambda: click_fl_wavelength_scan(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤34失败")
        step(lambda: click_fl_settings(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤35失败")
        step(lambda: click_fl_instrument(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤36失败")
        step(lambda: click_fl_em_slit(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤37失败")
        step(lambda: click_fl_5nm(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤38失败")
        step(lambda: click_fl_ex_slit(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤39失败")
        step(lambda: click_fl_5nm_ex(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤40失败")
        step(lambda: double_click_fl_pmt(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True, input_value="600"), "步骤41失败")
        step(lambda: click_fl_wavelength_scan_2(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤42失败")
        step(lambda: click_fl_scan_mode(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤43失败")
        step(lambda: click_fl_em_scan(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤44失败")
        step(lambda: double_click_fl_ex_wavelength(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True, input_value=None), "步骤45失败")
        step(lambda: double_click_fl_em_start_wavelength(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True, previous_value=None, offset=20), "步骤46失败")
        step(lambda: double_click_fl_em_end_wavelength(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True, step15_value=None), "步骤47失败")
        step(lambda: click_fl_confirm_button(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤48失败")
        step(lambda: _wait_rgb(recorder, trajectory_recorder), "步骤49失败")
        step(lambda: click_fl_start_scan(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤50失败")
        step(lambda: _wait_rgb(recorder, trajectory_recorder), "步骤51失败")
        step(lambda: click_fl_xls_save(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤52失败")
        step(lambda: input_fl_filename(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True, filename=None), "步骤53失败")
        step(lambda: click_fl_final_save(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤54失败")
        step(lambda: close_fl_excel(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤55失败")

        step_count += 1
        print(f"\n{'='*80}\n步骤 {step_count}: 处理FL xls 读取A31（数据处理）\n{'='*80}")
        fl_data_dir = r"E:\code\data-fl"
        xls_file_fl = find_latest_xls_file(fl_data_dir)
        if xls_file_fl:
            a31_result = read_cell_a31(xls_file_fl)
            if a31_result:
                a31_result_path = f"step56_fl_A31_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}{run_suffix}.json"
                save_result(a31_result, a31_result_path)
                print(f"✓ A31={a31_result['value']}，已保存: {a31_result_path}")
            else:
                print("警告：未能读取 A31")
        else:
            print("警告：未找到 data-fl 下 xls 文件")

        step(lambda: click_fl_save_curve(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤57失败")
        step(lambda: double_click_fl_input_filename(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True, filename=None), "步骤58失败")
        step(lambda: click_fl_save_final(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤59失败")
        step(lambda: click_fl_settings_2(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤60失败")
        step(lambda: click_fl_wavelength_scan_3(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤61失败")
        step(lambda: click_fl_scan_mode_2(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤62失败")
        step(lambda: click_fl_ex_scan(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤63失败")
        step(lambda: double_click_fl_em_fixed_wavelength(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True, input_value=None), "步骤64失败")
        step(lambda: double_click_fl_ex_start_wavelength(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True, input_value="200"), "步骤65失败")
        step(lambda: double_click_fl_ex_end_wavelength(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True, input_value=None), "步骤66失败")
        step(lambda: click_fl_confirm_button_2(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤67失败")
        step(lambda: _wait_rgb(recorder, trajectory_recorder), "步骤68失败")
        step(lambda: click_fl_start_scan_2(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤69失败")
        step(lambda: _wait_rgb(recorder, trajectory_recorder), "步骤70失败")
        step(lambda: click_fl_save_2(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤71失败")
        step(lambda: double_click_fl_input_filename_2(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True, filename=None), "步骤72失败")
        step(lambda: click_fl_save_3(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤73失败")
        step(lambda: click_fl_exit(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤74失败")
        step(lambda: click_fl_yes(recorder=recorder, trajectory_recorder=trajectory_recorder, use_default_rectangle=True), "步骤75失败")

        print(f"\n{'='*80}\n✓ FL 流程完成（共 {step_count} 步）\n{'='*80}")
    except KeyboardInterrupt:
        print(f"\n用户中断（步骤 {step_count}）")
        failed_steps.append(step_count)
    except Exception as e:
        print(f"\n执行失败（步骤 {step_count}）: {e}")
        failed_steps.append(step_count)
        import traceback
        traceback.print_exc()
    finally:
        recorder.recording = False
        recorder.save_recording()
        trajectory_recorder.save_trajectory()
        total = time.time() - recorder.start_time
        print(f"\n完成步骤: {step_count} | 耗时: {total/60:.2f} 分钟 | 记录: {output_file}")
        if failed_steps:
            print(f"失败步骤: {failed_steps}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="FL 单软件自动化")
    p.add_argument("--label", default="", help="运行标签")
    p.add_argument("--no-confirm", action="store_true", help="跳过开始确认")
    args = p.parse_args()
    if not args.no_confirm:
        if input("是否开始执行 FL 流程？(y/n): ").strip().lower() != 'y':
            sys.exit(0)
    run_fl_automation(run_label=args.label)
