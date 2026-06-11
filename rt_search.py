import asyncio 
import websockets
import json
import random
from config import socket_url
# from check_n_buy import chk_n_buy
from get_setting import get_setting
from login import fn_au10001 as get_token

from util import read_datafile
from chk_vobres_n_buy import chk_vobres_n_buy

class RealTimeSearch:
	def __init__(self, on_connection_closed=None):
		self.socket_url = socket_url + '/api/dostk/websocket'
		self.websocket = None
		self.connected = False
		self.keep_running = True
		self.receive_task = None
		self.on_connection_closed = on_connection_closed  # 연결 종료 시 호출될 콜백 함수
		self.token = None  # 토큰 저장

	async def connect(self, token):
		"""WebSocket 서버에 연결합니다."""
		try:
			self.token = token  # 토큰 저장
			self.websocket = await websockets.connect(self.socket_url)
			self.connected = True
			print("서버와 연결을 시도 중입니다.")

			# 로그인 패킷
			param = {
				'trnm': 'LOGIN',
				'token': token
			}

			print('실시간 시세 서버로 로그인 패킷을 전송합니다.')
			# 웹소켓 연결 시 로그인 정보 전달
			await self.send_message(message=param)

		except Exception as e:
			print(f'Connection error: {e}')
			self.connected = False
			self.websocket = None

	async def send_message(self, message, token=None):
		"""서버에 메시지를 보냅니다. 연결이 없다면 자동으로 연결합니다."""
		if not self.connected:
			if token:
				await self.connect(token)  # 연결이 끊어졌다면 재연결
		if self.connected and self.websocket:
			# message가 문자열이 아니면 JSON으로 직렬화
			if not isinstance(message, str):
				message = json.dumps(message)

			await self.websocket.send(message)
			print(f'Message sent: {message}')

	async def receive_messages(self):
		# 260522 추가
		ohlc_data = read_datafile(filename='last_ohlc.txt') # str
		json_data = json.loads(ohlc_data)           # dict
		last_ohlc = json_data.get('stk', [])        # json_data['stk']
		# 260522

		"""서버에서 오는 메시지를 수신하여 출력합니다."""
		while self.keep_running and self.connected and self.websocket:
			try:
				# 서버로부터 수신한 메시지를 받음
				raw_message = await self.websocket.recv()
				# JSON 형식으로 파싱
				response = json.loads(raw_message)
				
				
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

							# 비동기 함수를 태스크로 실행하여 이벤트 루프 블로킹 방지
							# 이렇게 하면 WebSocket 메시지 수신이 계속 가능하고 PING 응답도 정상 처리됨
							# asyncio.create_task(chk_vobres_n_buy(data=response['data'], token=self.token, last_ohlc=last_ohlc))

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
				if self.websocket:
					try:
						await self.websocket.close()
					except:
						pass
				
				# 연결 종료 콜백 호출
				if self.on_connection_closed:
					try:
						await self.on_connection_closed()
					except Exception as e:
						print(f'콜백 실행 중 오류: {e}')
				break  # 루프 종료

			except json.JSONDecodeError as e:
				print(f'JSON 파싱 오류: {e}')
				print(f'수신한 원본 메시지: {raw_message if raw_message else "수신 실패"}')
				continue  # 다음 메시지 수신 계속

			except Exception as e:
				print(f'receive_messages에서 예외 발생: {type(e).__name__}: {e}')
				print(f'연결 상태: connected={self.connected}, websocket={self.websocket is not None}')
				
				# 연결이 끊어진 것으로 보이면 연결 상태 확인
				if self.websocket:
					try:
						# 연결이 살아있는지 확인
						await asyncio.wait_for(self.websocket.ping(), timeout=2)
						print('연결은 유지되고 있습니다. 메시지 수신 계속...')
						continue
					except Exception as ping_e:
						print(f'연결 확인 실패: {ping_e}')
						self.connected = False
						if self.on_connection_closed:
							try:
								await self.on_connection_closed()
							except Exception as callback_e:
								print(f'콜백 실행 중 오류: {callback_e}')
						break  # 루프 종료
				else:
					print('websocket이 None입니다. 루프 종료')
					break  # 루프 종료


	async def disconnect(self):
		"""WebSocket 연결 종료"""
		self.keep_running = False
		if self.connected and self.websocket:
			try:
				await self.websocket.close()
			except Exception as e:
				print(f'WebSocket close error: {e}')
			finally:
				self.connected = False
				self.websocket = None
				print('Disconnected from WebSocket server')

	async def start(self, token):
		"""
		실시간 검색을 시작합니다.
		Returns:
			bool: 성공 여부
		"""
		try:
			# keep_running 플래그를 True로 리셋
			self.keep_running = True
			
			# 이미 웹소켓이 돌고 있다면 종료
			if self.receive_task and not self.receive_task.done():
				self.receive_task.cancel()
				try:
					await self.receive_task
				except asyncio.CancelledError:
					pass
				self.receive_task = None
				await self.disconnect()

			# WebSocket 연결
			await self.connect(token)
			
			# 연결이 성공했는지 확인
			if not self.connected:
				print('WebSocket 연결에 실패했습니다.')
				return False

			# WebSocket 메시지 수신을 백그라운드에서 실행합니다.
			self.receive_task = asyncio.create_task(self.receive_messages())

			# seq = get_setting('search_seq', '0')
			seq = get_setting('search_seq', '1')	# 260520

			# 실시간 항목 등록
			await asyncio.sleep(1)
			await self.send_message({ 
				'trnm': 'CNSRREQ', # 서비스명
				'seq': seq, # 조건검색식 일련번호
				'search_type': '1', # 조회타입
				'stex_tp': 'K', # 거래소구분
			}, token)
			
			print(f'실시간 검색이 시작되었습니다. seq: {seq}')
			return True
			
		except Exception as e:
			print(f'실시간 검색 시작 실패: {e}')
			return False

	async def stop(self):
		"""
		웹소켓 연결을 종료합니다.
		
		Returns:
			bool: 성공 여부
		"""
		try:
			# 이미 웹소켓이 돌고 있다면 종료
			if self.receive_task and not self.receive_task.done():
				self.receive_task.cancel()
				try:
					await self.receive_task
				except asyncio.CancelledError:
					pass
				self.receive_task = None
				await self.disconnect()
			
			print('실시간 검색이 중지되었습니다.')
			return True
			
		except Exception as e:
			print(f'실시간 검색 중지 실패: {e}')
			return False

# 사용 예시
async def main():
	rt_search = RealTimeSearch()
	
	# 실시간 검색 시작
	success = await rt_search.start(get_token())
	if success:
		print("실시간 검색이 성공적으로 시작되었습니다.")
		
		# 10초 후 중지
		await asyncio.sleep(30)
		await rt_search.stop()

if __name__ == '__main__':
	asyncio.run(main())
