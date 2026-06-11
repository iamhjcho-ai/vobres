"""
네이버 증권 접속하여 
    코스피 100 종목 정보 crawling 후 주식종목및코드.xlsx 코스피100 시트에 저장
    코스닥 100 종목 정보 crawling 후 주식종목및코드.xlsx 코스닥100 시트에 저장
"""

import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                              QProgressBar, QTableWidget, QTableWidgetItem, 
                              QHeaderView, QMessageBox, QFileDialog, QSpinBox)
from PySide6.QtCore import Qt, QThread, Signal

# 웹 크롤링 작업을 위한 스레드 클래스
class CrawlerThread(QThread):
    """
    백그라운드에서 웹 크롤링을 수행하는 스레드 클래스
    GUI가 멈추지 않도록 별도 스레드로 실행
    """
    # 시그널 정의
    progress_signal = Signal(int)  # 진행 상황 업데이트
    data_signal = Signal(list)     # 수집된 데이터 전달
    error_signal = Signal(str)     # 오류 메시지 전달
    finished_signal = Signal(int, float)  # 완료 시그널 (데이터 수, 소요 시간)

    def __init__(self, pages):
        super().__init__()
        self.pages = pages

    def run(self):
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

        for page in range(1, self.pages+1):
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

                        # 데이터 전처리 - 'N/A' 값이 아닌 경우만 처리 260604 수정
                        if  cur_prc != 'N/A' and prc_updown != 'N/A' and rate_updown != 'N/A' and t_amount != 'N/A' and t_sum != 'N/A' and market_sum != 'N/A':
                            cur_prc = float(cur_prc.replace(',', ''))
                            prc_updown = float(prc_updown.replace(',', ''))
                            rate_updown = rate_updown[1:-1]  # 부호와 % 제거
                            rate_updown = float(rate_updown.replace(',', ''))
                            t_amount = float(t_amount.replace(',', ''))
                            t_sum = float(t_sum.replace(',', ''))
                            market_sum = float(market_sum.replace(',', ''))
                        # 데이터 추가 260604 수정
                        data.append([name, cur_prc, prc_updown, rate_updown, t_amount, t_sum, market_sum])
                        print(data,'\n')
                        
                print(data)    
                # sys.exit()

                # 진행 상황 업데이트
                progress = int((page / self.pages) * 100)
                self.progress_signal.emit(progress)
                
                # 요청 간격 추가로 서버 부하 방지
                time.sleep(1.0)

            except Exception as e:
                print(f"페이지 {page} 처리 중 오류 발생: {str(e)}")
                self.error_signal.emit(f"페이지 {page} 처리 중 오류 발생: {str(e)}")
                continue

        # 수집 완료 후 데이터 전송
        self.data_signal.emit(data)
        self.finished_signal.emit(len(data), time.time() - start_time)


class StockCrawlerApp(QMainWindow):
    """
    주식 데이터 크롤링 및 분석을 위한 메인 GUI 애플리케이션
    """
    def __init__(self):
        super().__init__()
        self.df = None  # 데이터프레임 저장 변수
        self.initUI()
        
    def initUI(self):
        # 메인 윈도우 설정
        self.setWindowTitle('주식 데이터 수집기')
        self.setGeometry(100, 100, 1000, 600)
        
        # 중앙 위젯 및 레이아웃 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 입력 영역 레이아웃
        input_layout = QHBoxLayout()
        
        # 페이지 수 입력
        input_layout.addWidget(QLabel('수집할 페이지 수:'))
        # self.page_input = QLineEdit('1')
        # self.page_input.setFixedWidth(100)
        # input_layout.addWidget(self.page_input)

        # 260527
        self.page_input = QSpinBox()
        self.page_input.setRange(1, 50)          # 최소 0 \~ 최대 100
        self.page_input.setSingleStep(1)          # 1씩 증가/감소
        self.page_input.setValue(1)              # 초기값 1
        self.page_input.setFixedWidth(100)
        # self.spinbox.valueChanged.connect(self.on_value_changed)
        input_layout.addWidget(self.page_input)
        
        # 수집 버튼
        self.crawl_button = QPushButton('데이터 수집 시작')
        self.crawl_button.clicked.connect(self.start_crawling)
        input_layout.addWidget(self.crawl_button)
        
        # 저장 버튼
        self.save_button = QPushButton('엑셀로 저장')
        self.save_button.clicked.connect(self.save_to_excel)
        self.save_button.setEnabled(False)  # 초기에는 비활성화
        input_layout.addWidget(self.save_button)
        
        input_layout.addStretch()
        main_layout.addLayout(input_layout)
        
        # 진행 상황 표시
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel('진행 상황:'))
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        main_layout.addLayout(progress_layout)
        
        # 상태 메시지
        self.status_label = QLabel('준비됨')
        main_layout.addWidget(self.status_label)
        
        # 데이터 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        # 260604 항목 수정
        self.table.setHorizontalHeaderLabels(["종목명", "현재가", "전일비", 
                                             "등락률(%)", "거래량", "거래대금(백만)", "시가총액(억)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) # 첫번째 컬럼 크기 조절 가능
        main_layout.addWidget(self.table)
        
    def start_crawling(self):
        """크롤링 작업 시작"""
        try:
            pages = int(self.page_input.text())
            if pages <= 0:
                QMessageBox.warning(self, '입력 오류', '페이지 수는 1 이상이어야 합니다.')
                return
                
            # UI 상태 업데이트
            self.crawl_button.setEnabled(False)
            self.save_button.setEnabled(False)
            self.progress_bar.setValue(0)
            self.status_label.setText('데이터 수집 중...')
            self.table.setRowCount(0)
            
            # 크롤링 스레드 시작
            self.crawler_thread = CrawlerThread(pages)
            self.crawler_thread.progress_signal.connect(self.update_progress)
            self.crawler_thread.data_signal.connect(self.display_data)
            self.crawler_thread.error_signal.connect(self.show_error)
            self.crawler_thread.finished_signal.connect(self.crawling_finished)
            self.crawler_thread.start()
            
        except ValueError:
            QMessageBox.warning(self, '입력 오류', '유효한 페이지 수를 입력하세요.')
    
    def update_progress(self, value):
        """진행 상황 업데이트"""
        self.progress_bar.setValue(value)
    
    def display_data(self, data):
        """수집된 데이터 테이블에 표시"""
        # 데이터프레임 생성
        self.df = pd.DataFrame(data, columns=["종목명", "현재가", "전일비", 
                                             "등락률(%)", "거래량", "거래대금(백만)", "시가총액(억)"])
        
        # 테이블에 데이터 표시
        self.table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem()
                # 숫자 데이터는 오른쪽 정렬, 문자열은 왼쪽 정렬
                if col_idx == 0:  # 종목명
                    item.setText(str(cell_data))
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:  # 숫자 데이터
                    if col_idx == 3:    # 등락률
                        item.setText(f"{cell_data:,.2f}")    
                    else:
                        item.setText(f"{cell_data:,.0f}")   # 260604 수정 .2f -> .0f
                    # item.setText(str(cell_data))
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)
    
    def show_error(self, error_msg):
        """오류 메시지 표시"""
        self.status_label.setText(f"오류: {error_msg}")
    
    def crawling_finished(self, data_count, elapsed_time):
        """크롤링 작업 완료 처리"""
        self.crawl_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.status_label.setText(f"총 {data_count}개 데이터 수집 완료 | 소요 시간: {elapsed_time:.2f}초")
    
    def save_to_excel(self):
        """데이터를 엑셀 파일로 저장"""
        if self.df is None or self.df.empty:
            QMessageBox.warning(self, '저장 오류', '저장할 데이터가 없습니다.')
            return
            
        # 파일 저장 다이얼로그
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        default_filename = f'stock_data_{timestamp}.xlsx'
        file_path, _ = QFileDialog.getSaveFileName(
            self, '엑셀 파일 저장', default_filename, 'Excel Files (*.xlsx)')
            
        if file_path:
            try:
                # 엑셀 파일 저장
                with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                    self.df.to_excel(writer, index=False)
                    # 엑셀 서식 자동 적용
                    workbook = writer.book
                    worksheet = writer.sheets['Sheet1']
                    number_format = workbook.add_format({'num_format': '#,##0.00'})
                    worksheet.set_column('B:G', 15, number_format)
                
                QMessageBox.information(self, '저장 완료', f'데이터가 성공적으로 저장되었습니다.\n{file_path}')
            except Exception as e:
                QMessageBox.critical(self, '저장 오류', f'파일 저장 중 오류가 발생했습니다: {str(e)}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StockCrawlerApp()
    window.show()
    sys.exit(app.exec())