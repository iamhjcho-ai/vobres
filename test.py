import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
# from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
#                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
#                               QProgressBar, QTableWidget, QTableWidgetItem, 
#                               QHeaderView, QMessageBox, QFileDialog, QSpinBox)
# from PySide6.QtCore import Qt, QThread, Signal

def run(pages):
 
        # 세션 설정으로 성능 향상 및 안정성 확보
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))

        # 웹 크롤링 차단 방지를 위한 헤더 설정
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        data = []
        start_time = time.time()

        for page in range(1, pages+1):
            try:
                # 코스피100
                url = f"https://finance.naver.com/sise/entryJongmok.naver?type=KPI100&page={page}"
                        
                # 효율적인 URL 구성 및 요청
                response = session.get(
                    url,
                    headers=headers,
                    timeout=10
                )
                
                soup = BeautifulSoup(response.content, 'html.parser')

                trs = soup.select("table.type_1 > tr")
                response.raise_for_status()
                # print(trs)
                i = 0
                for tr in trs:
                    i += 1
                    if i >=3 and i <= 12:
                        name = tr.select_one('td.ctg').text    # 종목명                        
                        link_tag = tr.select_one('td.ctg > a') # a 태그가 'cfg' 안에 있는 경우
                        if link_tag:
                            link = link_tag['href']         # href 속성 값(링크) 추출
                            # link = link[-6:]
                            name = name + ' ' + link[-6:]   # 종목코드
                        tds = tr.select('td.number_2')
                        # print(tds)

# 1:  삼성전자 005930       name
# 34,290,059               t_sum 
# 하락  9,000               prc_updown
#  [<td class="number_2">351,500</td>,  list_num_2[0] cur_prc
# <td class="number_2"> <span class="tah p11 nv01"> -2.50% </span>  list_num_2[1] rate_updown
# </td>, <td class="number_2">12,172,611</td>, list_num_2[2] t_sum
# <td class="number_2">20,549,669</td>] list_num_2[3] market_sum
                        td_list = []
                        for td in tds:
                            text = td.get_text()
                            td_list.append(text.strip())
                            # print('td: ', td.get_text())
                        # print('td_list: ', td_list)

                        cur_prc = td_list[0]
                        rate_updown = td_list[1]
                        t_sum = td_list[2]
                        market_sum = td_list[3]
                        td_list.clear()
                        
                        temp = []
                        temp = (tr.select_one('td.rate_down2').text).split()
                        # temp = prc_updown.split()
                        ud = temp[0].strip()
                        if len(temp) <= 1:  # 보합0
                            ud = ''
                            p = '0'
                        else:
                            p = temp[1].strip()
                            if ud == '하락':
                                ud = '-'
                            else:
                                ud = ''
                        prc_updown = ud + p

                        t_amount = tr.select_one('td.number').text

                        # print('종목명 종목코드   현재가   전일비   등락률  거래량 거래대금(백만) 시가총액(억)')
                        # print(f'{i-2}: ', name, cur_prc, prc_updown, rate_updown, t_amount, t_sum, market_sum)

                        # 데이터 전처리 - 'N/A' 값이 아닌 경우만 처리
                        # if market_sum != 'N/A' and debt_total != 'N/A' and sales_increasing_rate != 'N/A' and frgn_rate != 'N/A' and per != 'N/A' and roe != 'N/A':
                        #     market_sum = float(market_sum.replace(',', ''))
                        #     debt_total = float(debt_total.replace(',', ''))
                        #     sales_increasing_rate = float(sales_increasing_rate.replace(',', ''))
                        #     frgn_rate = float(frgn_rate.replace(',', ''))
                        #     per = float(per.replace(',', ''))
                        #     roe = float(roe.replace(',', ''))
                        # 데이터 추가 260604 수정
                        data.append([name, cur_prc, prc_updown, rate_updown, t_amount, t_sum, market_sum])
                        print(data,'\n')
                        
                print(data)    
                # sys.exit()

                # 요청 간격 추가로 서버 부하 방지
                time.sleep(1.5)

            except Exception as e:
                print(f"페이지 {page} 처리 중 오류 발생: {str(e)}")
                continue


run(2)
