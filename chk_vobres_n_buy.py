# data: [
#   {'9001': 'A006400', '302': '삼성SDI', '10': '000652000', '25': '2', '11': '000036000', '12': '000005840', '13': '000471854', '16': '000640000', '17': '000657000', '18': '000627000'}, 
#   {'9001': 'A009150', '302': '삼성전기', '10': '001311000', '25': '2', '11': '000107000', '12': '000008890', '13': '000855148', '16': '001240000', '17': '001327000', '18': '001204000'}
# ]

import time
from check_n_buy import chk_n_buy
from tel_send import tel_send

from get_setting import get_setting
VO_RATE = get_setting('vo_rate', default='')

from debug_log import start_debugging
# log = start_debugging()

def get_target_price(last_ohlc, data):
    vo = int(last_ohlc['고가']) - int(last_ohlc['저가'])    # 전일 고가 - 저가
    vo_rate = VO_RATE
    # print(vo_rate)
    open_prc = int(data['16'])      # 당일 시가
    target_price = open_prc + int(vo * vo_rate)

    return target_price



buy_list, block_list = [], []  # 장 시작 및 종료 시 초기화
log = start_debugging(console=False)
def chk_vobres_n_buy(data, token=None, last_ohlc=None):

    for i in range(len(data)):
        code_n_name = data[i]['9001']   # ['302] 종목명
        stk_cd = code_n_name[-6:]       # 'A' 제거 6자리 종목코드 추출(뒤에서 여섯번째 부터 끝까지)
        found = False

        for j in range(len(last_ohlc)):
            if stk_cd == last_ohlc[j]['종목코드']:
                found = True
                cur_prc = int(data[i]['10'])
                # 현재가가 5일 평균, 10일 평균 이상
                if cur_prc >= int(last_ohlc[j]['5MA']) and cur_prc >= int(last_ohlc[j]['10MA']):
                    t_prc = get_target_price(last_ohlc[j], data[i])     # 변동성 돌파 금액
                    # 변동성 돌파 and not 보유한 종목 and not 에러발생 종목
                    if cur_prc >= t_prc and stk_cd not in buy_list and stk_cd not in block_list:
                            if chk_n_buy(stk_cd, token, log):
                                time.sleep(1.0)
                                
                                print(f'매수 chk_n_buy: {stk_cd, data[i]['302']}, t_prc:{t_prc}, cur_prc:{cur_prc}')                            
                                                                
                                buy_list.append(stk_cd) # buy_list에 매수한 종목 추가
                                log.info(f'매수완료 {stk_cd} {data[i]['302']} {t_prc}')
                                log.info('매수 리스트:', buy_list)

                            else:   # 잔고부족 등 에러발생 시
                                block_list.append(stk_cd)
                                log.error(f'매수 Error 발생: {stk_cd, data[i]['302']}, cur_prc:{cur_prc}')
                                log.error(f'매수실패 리스트: {block_list}')
                else:   # 현재가 < 5MA, 10MA
                    log.info(f'하향추세 {stk_cd} {data[i]['302']} < 5MA 10MA')
    
        if not found:   # last_ohlc.txt에 없는 종목이면 
            log.warning(f' Not found in last_ohlc.txt {stk_cd} {data[i]['302']}')
        # get_daypole_data() -> last_ohlc.append -> target_price 조건에 맞으면 매수        


    log.debug(f'조건검색 종목 수{len(data)}')
    