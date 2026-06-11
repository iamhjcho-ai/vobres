import json
import pandas as pd
import os

inv_days = 20   # 투자일수 
vo_rate = 0.5   # 변동성 돌파 적용 비율

# 주식번호로 일봉차트 데이터 파일 읽기
def datafile_read(filename):
    resp = ""
    fpath = ""

    script_dir = os.path.dirname(__file__)  # 현재 스크립트 파일이 있는 폴더
    fpath = script_dir + '\\daypole_data\\'
        
    filename = fpath + filename 
    try:
        fp = open(f'{filename}.txt', 'r')
        resp = fp.read()
        fp.close
        # print(f'\n종목코드: {filename}')
    except Exception as e:
        print(f'파일 {filename}.txt 입출력 에러: {e}')

    return resp     # str 반환


# N일 이동평균 구하기
def moving_average(start, days):
    ma_sum = 0
    for i in range(0, days):
        if (i < days):
            ma_sum += int(rows[start]['cur_prc']) 
            start += 1   
    ma = int(ma_sum/days)
    # print(f'{days}일 이동평균: {ma:,}원')
    return ma


def cal_roi(days):
    vo_lastday, o_p, l_p, h_p, c_p, roi_sum = 0, 0, 0, 0, 0, 0

    for j in range(1, days+1):
        # 전일 변동성 = 전일 최고가 - 전일 최저가
        vo_lastday = int(rows[j]['high_pric']) - int(rows[j]['low_pric'])           
        # 당일 시가 + (전일 고가 - 전일 저가) * rate(0.5)
        target_price = int(rows[j-1]['open_pric']) + (vo_lastday * vo_rate)

        o_p = int(rows[j-1]['open_pric'])   # 당일 시가
        l_p = int(rows[j-1]['low_pric'])    # 당일 최저가
        h_p = int(rows[j-1]['high_pric'])   # 당일 최고가    
        c_p = int(rows[j-1]['cur_prc'])     # 당일 현재가(종가)
        print(f'일자 {int(rows[j-1]['dt'])} 시가 {o_p} 최고 {h_p} 저가 {l_p} 종가 {c_p} 매수 {target_price}', end=' ')
        # 엑셀 파일 저장
        ma5 = moving_average(j-1, 5)
        ma10 = moving_average(j-1, 10)

        # 당일 시가가 매수가보다 높고(변동성 돌파), 5일 이평 및 10일 이평 이상일 때 매수
        if h_p > target_price and ma5 < target_price and ma10 < target_price:
            today_roi = c_p - target_price      # 당일 종가 - 매수가
            print(f'당일익: {today_roi}')
            # 엑셀 파일 저장
            if j > 1 and today_roi > 0:         # 수익 중이면 익일 시가로 매도
                today_roi = int(rows[j-2]['open_pric']) - target_price
                print(f'익일익: {today_roi}')
                # 엑셀 파일 저장
                roi_sum += today_roi
            else:
                roi_sum += today_roi
        else:
            print('매수불가')
            # 엑셀 파일 저장

    lastday_prc = int(rows[0]['cur_prc'])
    roi_percent = round(((roi_sum / lastday_prc) * 100), 2)
    print(f'ROI: {roi_sum} Percent: {roi_percent} 현재가: {int(rows[0]['cur_prc'])}')
    # 엑셀 파일 저장

    sum_list = [roi_sum, roi_percent, int(rows[0]['cur_prc'])]

    return sum_list # roi_sum



# 실행 구간

if __name__ == '__main__':

    # 에코프로, 현대차, 삼성SDI, LG화학, 현대로템, 삼성전자, 포스코홀딩스, 네이버
    # stk_cd_list = [86520, 5380, 6400, 51910, 64350, 5930, 5490, 35420] 
    total_sum = []
    r, p, c = 0,0,0
    excel_fname = "주식종목및코드 260510.xlsx"
    # sh_name = "코스닥20"
    sh_name = "코스피100"

    df = pd.read_excel(excel_fname, sheet_name=sh_name, engine='openpyxl')

    names = df['종목']      # 종목열만 추출 
    #print(type(names))    # names의 type() <class 'pandas.Series'>

    for i in range(len(names)):
        code_n_name = names[i]
        code = code_n_name[-6:]     # 종목코드 추출
        name = code_n_name[:-6]     # 종목명 추출
        print(f'\n{i+1} 종목코드: {code} 종목명: {name}')
    

        # response type <class 'str'> 내용은 dict(json) 문자열
        response = datafile_read(name)
        # json_data type <class 'dict'>
        json_data = json.loads(response)    # 파이썬 객체 str response를 dict json_data로 변환 (파이썬에서 json type은 따로 없으므로 dict 객체로 변환)         

        rows = json_data.get('stk_dt_pole_chart_qry', [])   # rows = json_data['stk_dt_pole_chart_qry']	동일함
        #print(f'테이터 type()  response: {type(response)}, json_data: {type(json_data)}, rows: {type(rows)}')

        total_sum.append(cal_roi(inv_days)) 

    for i in range(0, len(total_sum)):
        r += total_sum[i][0]
        p += total_sum[i][1]
        c += total_sum[i][2]

    print(r, p, c)
    # 총투자금액 수익률 (r / c) * 0.01
    print(f'총투자금액 대비 수익률: {(r / c)*100:.2f}%')
    # 엑셀 파일 저장