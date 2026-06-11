import json
import pandas as pd
import openpyxl
from openpyxl.styles import Font
import os
from get_setting import get_setting
from util import read_datafile
from tel_send import tel_send
import csv

inv_days = get_setting('inv_days', default='')  # 투자일수 
vo_rate = get_setting('vo_rate', default='')    # vo_rate = 0.5   # 변동성 돌파 적용 비율


# N일 이동평균 구하기
def moving_average(start, days, rows):
    ma_sum = 0
    for i in range(0, days):
        if (i < days):
            ma_sum += int(rows[start]['cur_prc']) 
            start += 1   
    ma = int(ma_sum/days)
    # print(f'{days}일 이동평균: {ma:,}원')
    return ma




def cal_roi(days, rows, writer):
    vo_lastday, o_p, l_p, h_p, c_p = 0, 0, 0, 0, 0
    roi_sum, buy_sum, today_roi, today_roi_sum, buy_count = 0, 0, 0, 0, 0
    abc, arr = 0, 0
    title = ['No.','날짜','시가','고가','저가','현재가','5MA','10MA','매수가','당일수익','익일수익','수익률','MA미적용']
    
    csv_data = [['' for _ in range(0)] for _ in range(21)]

    for j in range(1, days+1):
        # 전일 변동성 = 전일 최고가 - 전일 최저가
        vo_lastday = int(rows[j]['high_pric']) - int(rows[j]['low_pric'])           
        # 당일 시가 + (전일 고가 - 전일 저가) * rate(0.5)
        target_price = int(rows[j-1]['open_pric']) + int(vo_lastday * vo_rate)

        o_p = int(rows[j-1]['open_pric'])   # 당일 시가
        l_p = int(rows[j-1]['low_pric'])    # 당일 최저가
        h_p = int(rows[j-1]['high_pric'])   # 당일 최고가    
        c_p = int(rows[j-1]['cur_prc'])     # 당일 현재가(종가)
        print(f'일자 {int(rows[j-1]['dt'])} 시가 {o_p:,} 최고 {h_p:,} 저가 {l_p:,} 종가 {c_p:,} 매수 {target_price:,}', end=' ')

        ma5 = moving_average(j-1, 5, rows)
        ma10 = moving_average(j-1, 10, rows)
        
                              
        csv_data[j-1].append(j)                 # 번호                
        csv_data[j-1].append(rows[j-1]['dt'])   # 일자                          
        csv_data[j-1].append(o_p)               # 시가                          
        csv_data[j-1].append(h_p)               # 최고가                           
        csv_data[j-1].append(l_p)               # 최저가                         
        csv_data[j-1].append(c_p)               # 종가(현재가)                         
        csv_data[j-1].append(ma5)               # MA5                         
        csv_data[j-1].append(ma10)              # MA10                  
        csv_data[j-1].append(target_price)      # 매수가


        # 당일 시가가 매수가보다 높고(변동성 돌파), 5일 이평 및 10일 이평 이상일 때 매수
        if h_p > target_price and ma5 < target_price and ma10 < target_price:
            today_roi = c_p - target_price      # 당일 종가 - 매수가
            buy_sum += target_price             # 총 매수금액
            buy_count += 1                      # 총 매입일수
            today_roi_sum += today_roi          # 총 당일수익금액
                    

            print(f'당일익: {today_roi}')
            csv_data[j-1].append(today_roi)                  
            csv_data[j-1].append(today_roi) 

            if j > 1 and today_roi > 0:                     # 수익 중이면 익일 시가로 매도
                today_roi = int(rows[j-2]['open_pric']) - target_price
                print(f'익일익: {today_roi}')
                del csv_data[j-1][10:]   
                csv_data[j-1].append(today_roi)             # 익일수익 update
                roi_sum += today_roi                        # 총 수익금액
            else:
                roi_sum += today_roi                        # 총 수익금액
        else:
            print('매수불가')
            csv_data[j-1].append('False')
            csv_data[j-1].append('False')
            today_roi = 0
        
        csv_data[j-1].append(round((today_roi / target_price) * 100, 2))    # 수익률


    if buy_count:
        abc = int(buy_sum / buy_count)               # 평균 매수가
        arr = round((roi_sum/ abc) * 100, 2)         # 평균 수익률
    else:
        abc, arr = 0, 0

    print('---------------------------------------------------------------------------------------')
    print(f'매수일수: {buy_count}일 평균수익률: {arr}% 평균매수가: {abc:,}원 수익금액: {roi_sum:,}원')
    

    csv_data[j].append('총 매수금액')
    csv_data[j].append(buy_sum)
    csv_data[j].append('총 당일수익')
    csv_data[j].append(today_roi_sum)
    csv_data[j].append('총 익일수익')
    csv_data[j].append(today_roi_sum)

    j = 0
    csv_data.insert(j, title)

    csv_data.insert(j, ['적용일수'])
    csv_data[j].append(inv_days)
    csv_data[j].append('변동률')
    csv_data[j].append(vo_rate)
    csv_data[j].append('매수일수')
    csv_data[j].append(buy_count)
    csv_data[j].append('평균 매수가')
    csv_data[j].append(abc)
    csv_data[j].append('평균 수익률')
    csv_data[j].append(arr)
    

    writer.writerows(csv_data)

    sum_list = [abc, arr, roi_sum]

    return sum_list # roi_sum


def vobres_sim_csv(filename, option):
    total_sum = []
    abc, arr, roi = 0,0,0

    script_dir = os.path.dirname(os.path.abspath(__file__))
    f_path = os.path.join(script_dir, filename)

    df = pd.read_excel(f_path, sheet_name=option, engine='openpyxl')

    names = df['종목']      # 종목열만 추출 
    #print(type(names))    # names의 type() <class 'pandas.Series'>

    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = os.path.join(script_dir, 'daypole_data')

    for i in range(0,len(names)):
        code_n_name = names[i]
        code = code_n_name[-6:]     # 종목코드 추출
        name = code_n_name[:-6]     # 종목명 추출
        print(f'\n{i+1} 종목코드: {code} 종목명: {name}')
    
        
        # 주식번호로 일봉차트 데이터 파일 읽기
        response = read_datafile(name + '.txt', 'daypole_data') # response type <class 'str'> 내용은 dict(json) 문자열
        # json_data type <class 'dict'>
        json_data = json.loads(response)    # 파이썬 객체 str response를 dict json_data로 변환 (파이썬에서 json type은 따로 없으므로 dict 객체로 변환)         

        rows = json_data.get('stk_dt_pole_chart_qry', [])   # rows = json_data['stk_dt_pole_chart_qry']	동일함
        #print(f'테이터 type()  response: {type(response)}, json_data: {type(json_data)}, rows: {type(rows)}')

        
        # CSV 파일 생성
        csv_data = []
        f_path = os.path.join(script_dir, name + '.csv')
        with open(f_path, 'w', newline='', encoding='utf-8') as file:
        # with open(f_path, 'w', newline='') as file:
            writer = csv.writer(file)
            csv_data.append('종목코드')
            csv_data.append(code)
            csv_data.append('종목명')
            csv_data.append(name)
            # csv_data = f'종목코드, {code}, 종목명, {name}'
            writer.writerow(csv_data)

            total_sum.append(cal_roi(inv_days, rows, writer))


    for i in range(0, len(total_sum)):
        abc += total_sum[i][0]    # 평균 매수가
        # arr += total_sum[i][1]    # 평균 수익률
        roi += total_sum[i][2]    # 수익 금액

    msg = f'\nTotal ABC: {abc:,}원  ARR: {round((roi/abc)*100,2)}%  ROI: {roi:,}원'
    print(msg)
    tel_send(msg + '\n종목별 CSV 파일 업데이트 완료')
    return



import asyncio
# 실행 구간

async def main():
    vobres_sim_csv("주식종목및코드 260510.xlsx", "코스피100")

if __name__ == '__main__':  
      asyncio.run(main())