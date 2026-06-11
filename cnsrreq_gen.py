import asyncio 
import websockets
import json
import os
import time
from config import socket_url       # 260522 추가
# from check_n_buy import chk_n_buy
# from get_setting import get_setting
from login import fn_au10001 as get_token
from chk_vobres_n_buy import chk_vobres_n_buy
from util import read_datafile
from mk_daypole_txt import mk_daypole_txt
from vobres_sim_excel import vobres_sim_excel
from vobres_sim_csv import vobres_sim_csv
from mk_last_ohlc_txt import mk_last_ohlc_excel_to_txt
from mk_last_ohlc_txt import mk_last_ohlc_csv_to_txt
from market_hour import MarketHour
from tel_send import tel_send

# socket 정보
# SOCKET_URL = 'wss://mockapi.kiwoom.com:10000/api/dostk/websocket'  # 모의투자 접속 URL
# SOCKET_URL = 'wss://api.kiwoom.com:10000/api/dostk/websocket'  # 접속 URL
# ACCESS_TOKEN = get_token()  # '사용자 AccessToken'  # 고객 Access Token


class WebSocketClient:
    def __init__(self, token):        
        self.socket_url = socket_url + '/api/dostk/websocket'
        self.websocket = None
        self.connected = False
        self.keep_running = True
        self.token = token#get_token()        # 260522 추가

    # WebSocket 서버에 연결합니다.
    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.socket_url)
            self.connected = True
            print("서버와 연결을 시도 중입니다.")

            # 로그인 패킷
            param = {
                'trnm': 'LOGIN',
                'token': self.token,#ACCESS_TOKEN,
            }

            print('실시간 시세 서버로 로그인 패킷을 전송합니다.')
            # 웹소켓 연결 시 로그인 정보 전달
            await self.send_message(message=param)

        except Exception as e:
            print(f'Connection error: {e}')
            self.connected = False

    # 서버에 메시지를 보냅니다. 연결이 없다면 자동으로 연결합니다.
    async def send_message(self, message):
        if not self.connected:
            await self.connect()  # 연결이 끊어졌다면 재연결
        if self.connected:
            # message가 문자열이 아니면 JSON으로 직렬화
            if not isinstance(message, str):
                message = json.dumps(message)

        await self.websocket.send(message)
        print(f'Message sent: {message}')


    # 서버에서 오는 메시지를 수신하여 출력합니다.
    async def receive_messages(self):

        test = 0
        # 260522 추가
        ohlc_data = read_datafile(filename='last_ohlc.txt') # str
        json_data = json.loads(ohlc_data)           # dict
        last_ohlc = json_data.get('stk', [])        # json_data['stk']
        # 260522

        while self.keep_running:
            try:
                # 서버로부터 수신한 메시지를 JSON 형식으로 파싱
                response = json.loads(await self.websocket.recv())
             
                # 메시지 유형이 LOGIN일 경우 로그인 시도 결과 체크
                if response.get('trnm') == 'LOGIN':
                    if response.get('return_code') != 0:
                        print('LOGIN 실패하였습니다. : ', response.get('return_msg'))
                        await self.disconnect()
                    else:
                        print('LOGIN 성공하였습니다.')
                        print('CNSRLST 조건검색 목록조회 패킷을 전송합니다.')
                        # 로그인 패킷
                        param = {
                            'trnm': 'CNSRLST'
                        }
                        await self.send_message(message=param)

                # 메시지 유형이 PING일 경우 수신값 그대로 송신
                elif response.get('trnm') == 'PING':
                    await self.send_message(response)

                if response.get('trnm') != 'PING':
                    # print(f'실시간 시세 서버 응답 수신: {response}')
                
                    # 260522 수정
                    if  response.get('trnm') == 'CNSRLST':
                        if response.get('data') == None:
                            print('조회할 조건식이 없습니다.')
                        else:    
                            param = { 
                                'trnm': 'CNSRREQ',  # 서비스명
                                'seq': '1',         # 조건검색식 일련번호
                                'search_type': '0', # 조회타입
                                'stex_tp': 'K',     # 거래소구분
                                'cont_yn': 'N',     # 연속조회여부
                                'next_key': '',     # 연속조회키
                            }
                            print('\n조건검색 요청 일반 CNSRLST -> CNSRREQ\n') 
                            await self.send_message(message=param)  
                            await asyncio.sleep(1.0)
                        
                    elif response.get('trnm') == 'CNSRREQ':
                        if response.get('data'):
                            chk_vobres_n_buy(data=response['data'], token=self.token, last_ohlc=last_ohlc)  # token, ohlc_list
                            # test += 1
                            # if test >= 2:
                            #     break
                        
                        # param = { 
                        #     'trnm': 'CNSRREQ',  # 서비스명
                        #     'seq': '1',         # 조건검색식 일련번호
                        #     'search_type': '0', # 조회타입
                        #     'stex_tp': 'K',     # 거래소구분
                        #     'cont_yn': 'N',     # 연속조회여부
                        #     'next_key': '',     # 연속조회키
                        # }

                        print('\n조건검색 요청 일반 CNSRREQ\n')
                        await self.send_message(message=param) 
                        await asyncio.sleep(1.0)                
                        
                        if param['seq'] == '1':     # 260527 조건검색 2개를 번갈아 요청
                            param['seq'] = '2'
                        else:
                            param['seq'] = '1'
                        # 260522

            except websockets.ConnectionClosed:
                print('Connection closed by the server')
                self.connected = False
                await self.websocket.close()

    # WebSocket 실행
    async def run(self):
        await self.connect()
        await self.receive_messages()

    # WebSocket 연결 종료
    async def disconnect(self):
        self.keep_running = False
        if self.connected and self.websocket:
            await self.websocket.close()
            self.connected = False
            print('Disconnected from WebSocket server')


    async def is_market_end(self):
        while True:
            if MarketHour.is_market_end_time() and market_open:
                print(f"장 마감 시간({MarketHour.get_end_hour():02d}:{MarketHour.get_end_minute():02d})입니다. 자동으로 stop 명령을 실행합니다.")                
                self.keep_running = False
                await self.disconnect()
                break

            await asyncio.sleep(1.0) # for debugging
        


async def main():
    token = get_token()
    
    # WebSocketClient 전역 변수 선언
    websocket_client = WebSocketClient(token=token)


    # # WebSocket 클라이언트를 백그라운드에서 실행합니다.
    # receive_task = asyncio.create_task(websocket_client.run())
    # # 수신 작업이 종료될 때까지 대기
    # await receive_task


    receive_task = asyncio.create_task(websocket_client.run())
    market_task = asyncio.create_task(websocket_client.is_market_end())
    results = await asyncio.gather(receive_task, market_task)  

    print('await asyncio.gather(receive_task, market_task) return value: ', results)  


    




# asyncio로 프로그램을 실행합니다.
if __name__ == '__main__':
    
    market_open = False
    keep_running = False
    ohlc_updated = False

    
    if not ohlc_updated:     # and last_ohlc.txt 저장일자 비교하여 update 결정
            # last_ohlc.txt 생성 루틴
            # mk_daypole_txt() -> vobres_sim_excel() -> mk_ohlc_data()
            # get_setting() ohlc_base_dt 직전일이 아니면 update 
            mk_daypole_txt("주식종목및코드 260510.xlsx", "코스피100", token=get_token())            
            vobres_sim_csv("주식종목및코드 260510.xlsx", "코스피100")            
            mk_last_ohlc_csv_to_txt('주식종목및코드 260510.xlsx', '코스피100')
            # setting('ohlc_base_dt', today)

            ohlc_updated = True        
    
    print('Waiting for Market Open......')
    
    while not market_open and not keep_running:

        if MarketHour.is_market_open_time():
            market_open = True
            keep_running = True
            ohlc_updated = True
            break

        if MarketHour.is_market_start_time():
            # 이미 실행 중인 기능이 있는지 확인 (재로그인 후 자동 복구와의 중복 실행 방지)        
            print(f"장 시작 시간({MarketHour.get_start_hour():02d}:{MarketHour.get_start_minute():02d})입니다. 자동으로 실행합니다.")
            tel_send(print(f"장 시작 시간({MarketHour.get_start_hour():02d}:{MarketHour.get_start_minute():02d})입니다. 자동으로 실행합니다."))
            market_open = True
            keep_running = True

        # asyncio.sleep(1.0)
        time.sleep(1.0)


    if market_open and keep_running:        
        asyncio.run(main())

