from __future__ import annotations
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
VERIFY_539 = BASE_DIR / "verify_539.py"
VERIFY_POWER = BASE_DIR / "verify_power.py"
VERIFY_649 = BASE_DIR / "verify_649.py"


def run_script(script_path: Path) -> int:
    print(f"\n===== 執行：{script_path.name} =====")
    result = subprocess.run([sys.executable, str(script_path)], check=False)
    if result.returncode == 0:
        print(f"✅ {script_path.name} 完成")
    else:
        print(f"❌ {script_path.name} 失敗，return code = {result.returncode}")
    return result.returncode


def main() -> None:
    print("===== 開始一鍵驗證全部彩票 =====")

    rc1 = run_script(VERIFY_539)
    rc2 = run_script(VERIFY_POWER)
    rc3 = run_script(VERIFY_649)

    if rc1 == 0 and rc2 == 0 and rc3 == 0:
        print("\n🎯 全部驗證完成")
    else:
        print("\n⚠️ 驗證完成，但有部分模組失敗")


if __name__ == "__main__":
    main()