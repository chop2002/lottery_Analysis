from __future__ import annotations
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
VERIFY_ALL = BASE_DIR / "verify_all.py"
MAKE_REPORT = BASE_DIR / "make_report.py"


def run_script(script_path: Path) -> int:
    print(f"\n===== 執行：{script_path.name} =====")
    result = subprocess.run([sys.executable, str(script_path)], check=False)
    if result.returncode == 0:
        print(f"✅ {script_path.name} 完成")
    else:
        print(f"❌ {script_path.name} 失敗，return code = {result.returncode}")
    return result.returncode


def main() -> None:
    print("===== 開始驗證 + 報表 =====")
    rc1 = run_script(VERIFY_ALL)
    rc2 = run_script(MAKE_REPORT)

    if rc1 == 0 and rc2 == 0:
        print("\n🎯 全部流程完成")
    else:
        print("\n⚠️ 流程完成，但有部分模組失敗")


if __name__ == "__main__":
    main()