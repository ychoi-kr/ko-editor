#!/usr/bin/python3
import os
import glob
import re
from datetime import datetime
from collections import defaultdict
import shutil
import argparse
import json
import filecmp

# 1. 도움말(Help) 텍스트 상세 구성
help_desc = "교정 작업 파일을 backups 폴더에 자동 백업하고, 파일명의 날짜 꼬리표를 당일 날짜로 덮어쓰거나 버전을 올리는 스크립트입니다."
help_epilog = """
[사용 예시]
  python3 today.py                 # 대화형 실행 (Y/N 확인)
  python3 today.py -d              # 변경/백업될 대상 확인만 하기 (Dry Run)
  python3 today.py -y              # 묻지 않고 백업 및 변경 즉시 실행 (자동화용)
  python3 today.py -y -j           # 결과를 JSON으로 출력 (에이전트 파싱용)
"""

parser = argparse.ArgumentParser(
    description=help_desc,
    epilog=help_epilog,
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument("-d", "--dry-run", action="store_true", 
                    help="실제로 파일을 변경/복사하지 않고 예정된 결과만 처리합니다.")
parser.add_argument("-y", "--yes", action="store_true", 
                    help="사용자 확인(Proceed?)을 생략하고 즉시 작업을 실행합니다.")
parser.add_argument("-j", "--json", action="store_true", 
                    help="일반 텍스트 출력을 숨기고 실행 결과를 JSON 형식으로 출력합니다.")
args = parser.parse_args()

# 에이전트 파싱용 JSON 결과 데이터 포맷
result_data = {
    "dry_run": args.dry_run,
    "backup": {"success": {}, "skipped": {}, "failed": {}},
    "rename": {"success": {}, "failed": {}},
    "backup_only": {"success": {}, "failed": {}},
    "skipped_no_target": False,
    "error_message": None
}

if not args.json:
    print(f"Current Directory: {os.getcwd()}")

d = {}
today_str = datetime.now().strftime("%Y%m%d")
date_pattern = r"(20\d{2}[01]\d[0-3]\d)(?:_(\d+))?"

# 변경 대상 파일 수집
for x in glob.glob("*.doc?"):
    match = re.search(date_pattern, x)

    if match:
        file_date = match.group(1)
        file_ver = match.group(2)

        if file_date == today_str:
            if file_ver:
                new_ver = int(file_ver) + 1
                new_date_str = f"{today_str}_{new_ver}"
            else:
                new_date_str = f"{today_str}_1"
        else:
            new_date_str = today_str

        y = re.sub(date_pattern, new_date_str, x, count=1)

        if x != y:
            d[x] = y

# 충돌 감지: 같은 대상 파일명으로 매핑되는 소스 파일 처리
backup_only = []  # 백업만 할 파일 (이전 버전)
targets = defaultdict(list)
for x, y in d.items():
    targets[y].append(x)

for y, sources in targets.items():
    if len(sources) > 1:
        def get_version(filename):
            m = re.search(date_pattern, filename)
            return int(m.group(2)) if m and m.group(2) else 0
        sources.sort(key=get_version)
        for older in sources[:-1]:
            backup_only.append(older)
            del d[older]

if not args.json:
    for x, y in d.items():
        print(f"Target: '{x}' -> will be backed up and renamed to '{y}'")
    for x in backup_only:
        print(f"Backup only: '{x}' -> will be moved to backups (older version)")

if not d and not backup_only:
    result_data["skipped_no_target"] = True
    if not args.json:
        print("백업 및 이름을 변경할 대상 파일이 없습니다.")
else:
    backup_dir = "backups"
    
    if args.dry_run:
        result_data["rename"]["success"] = d
        result_data["backup_only"]["success"] = {x: os.path.join(backup_dir, x) for x in backup_only}
        if not args.json:
            print("\n[Dry Run] 위 파일들이 backups 폴더에 백업된 후 이름이 변경될 예정입니다.")
            if backup_only:
                print("[Dry Run] 이전 버전 파일들은 backups 폴더로 이동될 예정입니다.")
    else:
        proceed = args.yes
        if not args.yes and not args.json:
            proceed = input("\nProceed with Backup & Rename? (Y/N) ").strip().lower() == 'y'
        elif not args.yes and args.json:
            result_data["error_message"] = "JSON 모드에서는 대화형 입력을 받을 수 없습니다. '-y' 옵션을 함께 사용하세요."

        if proceed:
            # backups 폴더가 없으면 생성
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
                
            for x, y in d.items():
                backup_path = os.path.join(backup_dir, x)
                needs_backup = True
                
                # --- [1] 백업 로직 ---
                if os.path.exists(backup_path):
                    # 파일 내용과 메타데이터가 완전히 동일한지 검사 (shallow=False로 확실하게 비교)
                    if filecmp.cmp(x, backup_path, shallow=False):
                        needs_backup = False
                
                if needs_backup:
                    try:
                        # 메타데이터(수정 시간 등)를 보존하며 복사
                        shutil.copy2(x, backup_path)
                        result_data["backup"]["success"][x] = backup_path
                        if not args.json:
                            print(f"[Backup] Copied: {x} -> {backup_path}")
                    except Exception as e:
                        result_data["backup"]["failed"][x] = str(e)
                        if not args.json:
                            print(f"[Backup] Failed: {x} (Error: {e})")
                        continue # 백업에 실패하면 원본 보호를 위해 파일명 변경도 건너뜀
                else:
                    result_data["backup"]["skipped"][x] = "No changes since last backup"
                    if not args.json:
                        print(f"[Backup] Skipped: {x} (동일한 파일이 이미 백업됨)")
                
                # --- [2] 이름 변경 로직 ---
                try:
                    shutil.move(x, y)
                    result_data["rename"]["success"][x] = y
                    if not args.json:
                        print(f"[Rename] Moved: {x} -> {y}")
                except Exception as e:
                    result_data["rename"]["failed"][x] = str(e)
                    if not args.json:
                        print(f"[Rename] Failed: {x} -> {y} (Error: {e})")

            # --- [3] 이전 버전 파일 backups 이동 ---
            for x in backup_only:
                backup_path = os.path.join(backup_dir, x)
                try:
                    shutil.move(x, backup_path)
                    result_data["backup_only"]["success"][x] = backup_path
                    if not args.json:
                        print(f"[Backup] Moved (older version): {x} -> {backup_path}")
                except Exception as e:
                    result_data["backup_only"]["failed"][x] = str(e)
                    if not args.json:
                        print(f"[Backup] Failed: {x} (Error: {e})")
        else:
            if not args.json and not result_data["error_message"]:
                print("작업이 취소되었습니다.")

# 3. JSON 출력 처리
if args.json:
    print(json.dumps(result_data, ensure_ascii=False, indent=2))
