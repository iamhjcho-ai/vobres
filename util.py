import os
import pandas as pd


# 260522 추가
def read_datafile(filename, foldername=None):
    str_data = ""   

    script_dir = os.path.dirname(os.path.abspath(__file__))
    if foldername:
        script_dir = os.path.join(script_dir, foldername)
    f_path = os.path.join(script_dir, filename)
 
    try:
        fp = open(f_path, 'r', encoding='utf-8')
        str_data = fp.read()
        fp.close
    except Exception as e:
        print(f'{filename}: {e}')

    return str_data     # string type 반환

def read_excelfile(excel_filename, sh_name):
    dataframe = pd.read_excel(excel_filename, sheet_name=sh_name, engine='openpyxl')
    print('read excelfile')

    return dataframe