import requests
import pandas as pd
import json
import time
from datetime import date, timedelta
import os
import shutil


from config import host_url
from login import  fn_au10001 as get_token
from tel_send import tel_send



# REST 시세 - 주식일봉차트조회요청 ka10081
def fn_ka10081(data, cont_yn='N', next_key='', token=None):
    # 1. 요청할 API URL
    endpoint = '/api/dostk/chart'
    url =  host_url + endpoint

    # 2. header 데이터
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',   # 컨텐츠타입
        'authorization': f'Bearer {token}',          # 접근토큰
        'cont-yn': cont_yn,                                 # 연속조회여부
        'next-key': next_key,                               # 연속조회키
        'api-id': 'ka10081',                                # TR명
    }

    # 3. http POST 요청
    response = requests.post(url, headers=headers, json=data)

    return response


def read_excelfile(excel_filename, sh_name):
    dataframe = pd.read_excel(excel_filename, sheet_name=sh_name, engine='openpyxl')
    print('read excelfile')

    return dataframe


def mk_daypole_txt(filename, option, base_dt=None, token=None):
    script_dir = os.path.dirname(__file__)  # 현재 스크립트 파일이 있는 폴더
    # excel_fname = script_dir + '\\' + filename # "주식종목및코드 260510.xlsx"
    excel_fname = script_dir + '/' + filename # 리눅스
    
    folder_name = 'daypole_data'    # 존재 여부 확인 후 생성(권장)
    # data_folder = script_dir + '\\' + folder_name + '\\' 
    data_folder = script_dir + '/' + folder_name + '/' 

    # 폴더가 존재하면 폴더 및 하위 파일 전체 삭제
    if os.path.exists(data_folder):
        shutil.rmtree(data_folder)

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    sh_name = option    # "코스피100" 또는 "코스닥20"
        
    df = read_excelfile(excel_fname, sh_name)
    names = df['종목']      # 종목열만 추출 
    #print(type(names))    # names의 type() <class 'pandas.Series'>

    if base_dt == None:
        today = date.today()
        yesterday = today - timedelta(days=1)   # 260602
        base_dt = yesterday
        base_dt = base_dt.strftime("%Y%m%d")    # YYYYMMDD

    for i in range(len(names)):
        code_n_name = names[i]
        code = code_n_name[-6:]     # 종목코드 추출
        name = code_n_name[:-6]     # 종목명 추출
        print(f'{i+1} 종목코드: {code} 종목명: {name}')

        params = {
            'stk_cd': code,     # 종목코드 거래소별 종목코드 (KRX:039490,NXT:039490_NX,SOR:039490_AL)
            'base_dt': base_dt, # 기준일자 YYYYMMDD
            'upd_stkpc_tp': '1',# 수정주가구분 0 or 1
        }

        # REST 시세 - 주식일봉차트조회요청 ka10081
        response = fn_ka10081(data=params, token=token)

        fp = open(f'{data_folder}{name}.txt', 'w', encoding='utf-8')
        fp.write(json.dumps(response.json(), indent=4, ensure_ascii=False))
        fp.close
        
        time.sleep(1.0)

    msg = f'\n{base_dt} 기준 총 {i+1} 종목의 일봉 데이터가 txt 파일로 생성되었습니다.'
    print(msg)
    tel_send(msg)


if __name__ == "__main__":
    ACCESS_TOKEN = get_token()
    mk_daypole_txt("주식종목및코드 260510.xlsx", "코스피100", token=ACCESS_TOKEN)