# KiWoom 주식자동매매 프로그램 실행용 shell script
# chmod 755 run_linux.sh
echo "KiWoom 주식자동매매 프로그램 실행용 shell script"
echo "현재 시간: $(date)"

set -x  # 명령어 출력 o  set +x  명령어 출력 x
sudo apt update
sudo apt install python3.11-venv
python3.11 -m venv venv
source venv/bin/activate
pip install httpx
pip install requests
pip install websockets
pip install pandas
pip install openpyxl
# python3 main.py

# 백그라운드 실행 1  
# > output.log: 프로그램 출력 결과를 해당 파일에 저장합니다.
# 2>&1: 에러 메시지도 일반 출력과 같은 곳(output.log)으로 보냅니다.
# & 백그라운드로 실행
# 프로그램 확인: ps -ef | grep python3 명령어로 프로세스가 잘 돌고 있는지 PID(프로세스 번호)를 확인합니다.
# 종료 명령어: kill -9 [PID번호] (예: kill -9 12345)

nohup python3 main.py > output.log 2>&1 &
ps -ef | grep python3

# 백그라운드 실행 2 : screen 명령어 사용 (프로세스 화면 모니터링 가능)
# 설치: 
# sudo apt install screen     # (Ubuntu/Debian 기준)
# screen -S mystock
# python3 main.py
# screen 백그라운드 프로세스로 부터 터미널 창으로 전환 (Detach): 키보드에서 Ctrl + A를 누른 뒤 D를 누릅니다. (세션은 유지되며 터미널 창으로 빠져나옵니다)
# screen 세션 목록 확인: screen -ls
# screen 백그라운드 세션으로 복귀 (Reattach): screen -r mystock
# Remove dead screens:  screen -wipe