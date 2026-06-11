import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def run():
     # 세션 설정으로 성능 향상 및 안정성 확보
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    # 웹 크롤링 차단 방지를 위한 헤더 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = f"https://finance.naver.com/sise/sise_index.naver?code=KPI100"
    # url = f"https://finance.naver.com/sise/entryJongmok.naver?type=KPI100"
    
    # 효율적인 URL 구성 및 요청    
    response = session.get(
        url,
        headers=headers,
        timeout=10
    )
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    # print(soup)
    trs = soup.select_one(".box_type_m")# > table.type_1 > tbody > tr")
   
    table = soup.find_all('table', class_='type_1')
    # trs = soup.select("table.type_1")# > tbody > tr")
    print(table)
    # print(trs.text)

    # for tr in trs:
    #     tr.select_one('td:nth-child(2)').text

run()


# [<div class="box_type_m">
# <h4 class="top_tlt" style="text-align:left;"><em>편입종목</em>상위</h4>
# <table cellpadding="0" cellspacing="0" class="type_1" style="”table-layout:fixed;”">
# <col width="119"/><col width="69"/><col width="79"/><col width="67"/><col width="71"/><col width="100"/><col width="89"/>
# <tr>
# <th class="tl" style="padding-left:15"><a class="sort_down" href="/sise/entryJongmok.naver?order=itemname&amp;isRightDirection=true">종목별</a></th>
# <th class="tl" style="padding-left:10"><a class="sort_down" href="/sise/entryJongmok.naver?order=now_val&amp;isRightDirection=true">현재가</a></th>
# <th class="tr" style="padding-right:10"><a class="sort_down" href="/sise/entryJongmok.naver?order=change_val&amp;isRightDirection=true">전일비</a></th>
# <th class="tr" style="padding-right:10"><a class="sort_down" href="/sise/entryJongmok.naver?order=change_rate&amp;isRightDirection=true">등락률</a></th>
# <th class="ls tr" style="padding-right:8"><a class="sort_down" href="/sise/entryJongmok.naver?order=acc_quant&amp;isRightDirection=true">거래량</a></th>
# <th class="ls tr" style="padding-right:13"><a class="sort_down" href="/sise/entryJongmok.naver?order=acc_amount&amp;isRightDirection=true">거래대금<span class="add_txt">(백만)</span></a></th>
# <th class="ls tr" style="padding-right:14"><a class="sort_up" href="/sise/entryJongmok.naver?order=market_sum&amp;isRightDirection=false">시가총액<span class="add_txt">(억)</span></a></th>
# </tr>
# <tr><td class="blank_07" colspan="7"></td></tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=005930" target="_parent">삼성전자</a></td>
# <td class="number_2">310,250</td>
# <td class="rate_down2">
# <em class="bu_p bu_pup"><span class="blind">상승</span></em><span class="tah p11 red02">
#                                 10,750
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 red01">
#                                 +3.59%
#                                 </span>

# </td>
# <td class="number">14,726,966</td>
# <td class="number_2">4,597,900</td>
# <td class="number_2">18,138,079</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=000660" target="_parent">SK하이닉스</a></td>
# <td class="number_2">2,304,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pup"><span class="blind">상승</span></em><span class="tah p11 red02">
#                                 15,000
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 red01">
#                                 +0.66%
#                                 </span>

# </td>
# <td class="number">2,763,094</td>
# <td class="number_2">6,469,118</td>
# <td class="number_2">16,420,662</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=402340" target="_parent">SK스퀘어</a></td>
# <td class="number_2">1,226,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pdn"><span class="blind">하락</span></em><span class="tah p11 nv01">
#                                 11,000
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 nv01">
#                                 -0.89%
#                                 </span>

# </td>
# <td class="number">470,139</td>
# <td class="number_2">584,830</td>
# <td class="number_2">1,617,810</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=009150" target="_parent">삼성전기</a></td>
# <td class="number_2">2,111,500</td>
# <td class="rate_down2">
# <em class="bu_p bu_pup"><span class="blind">상승</span></em><span class="tah p11 red02">
#                                 262,500
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 red01">
#                                 +14.20%
#                                 </span>

# </td>
# <td class="number">1,418,936</td>
# <td class="number_2">2,911,768</td>
# <td class="number_2">1,577,157</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=005380" target="_parent">현대차</a></td>
# <td class="number_2">709,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pup"><span class="blind">상승</span></em><span class="tah p11 red02">
#                                 32,000
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 red01">
#                                 +4.73%
#                                 </span>

# </td>
# <td class="number">1,627,816</td>
# <td class="number_2">1,166,535</td>
# <td class="number_2">1,451,733</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=373220" target="_parent">LG에너지솔루션</a></td>
# <td class="number_2">460,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pup"><span class="blind">상승</span></em><span class="tah p11 red02">
#                                 18,000
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 red01">
#                                 +4.07%
#                                 </span>

# </td>
# <td class="number">708,458</td>
# <td class="number_2">318,811</td>
# <td class="number_2">1,076,400</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=032830" target="_parent">삼성생명</a></td>
# <td class="number_2">374,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pup"><span class="blind">상승</span></em><span class="tah p11 red02">
#                                 16,500
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 red01">
#                                 +4.62%
#                                 </span>

# </td>
# <td class="number">221,189</td>
# <td class="number_2">80,403</td>
# <td class="number_2">748,000</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=329180" target="_parent">HD현대중공업</a></td>
# <td class="number_2">695,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pdn"><span class="blind">하락</span></em><span class="tah p11 nv01">
#                                 9,000
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 nv01">
#                                 -1.28%
#                                 </span>

# </td>
# <td class="number">187,458</td>
# <td class="number_2">131,783</td>
# <td class="number_2">729,481</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=028260" target="_parent">삼성물산</a></td>
# <td class="number_2">421,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pup"><span class="blind">상승</span></em><span class="tah p11 red02">
#                                 21,500
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 red01">
#                                 +5.38%
#                                 </span>

# </td>
# <td class="number">246,866</td>
# <td class="number_2">103,102</td>
# <td class="number_2">682,726</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=034020" target="_parent">두산에너빌리티</a></td>
# <td class="number_2">104,100</td>
# <td class="rate_down2">
# <em class="bu_p bu_pdn"><span class="blind">하락</span></em><span class="tah p11 nv01">
#                                 1,800
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 nv01">
#                                 -1.70%
#                                 </span>

# </td>
# <td class="number">1,717,467</td>
# <td class="number_2">178,293</td>
# <td class="number_2">666,824</td>
# </tr>
# <tr><td class="blank_09" colspan="7"></td></tr>
# <tr><td class="division_line" colspan="7"></td></tr>
# </table>
# <!--- 페이지 네비게이션 시작--->
# <table align="center" class="Nnavi" summary="페이지 네비게이션 리스트">
# <caption>페이지 네비게이션</caption>
# <tr>
# <td class="on">
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=1">1</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=2">2</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=3">3</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=4">4</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=5">5</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=6">6</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=7">7</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=8">8</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=9">9</a>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=10">10</a>
# <td class="pgRR">
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=10">맨뒤
#                                 <img alt="" border="0" height="5" src="https://ssl.pstatic.net/static/n/cmn/bu_pgarRR.gif" width="8"/>
# </a>
# </td>
# </tr>
# </table>
# <!--- 페이지 네비게이션 끝--->
# </div>]
# PS C:\Users\aaa\Desktop\기타\code\yalco260527\vobres> & C:/Users/aaa/AppData/Local/Programs/Python/Python314/python.exe c:/Users/aaa/Desktop/기타/code/yalco260527/vobres/crawling/naver_stock.py
# []
# PS C:\Users\aaa\Desktop\기타\code\yalco260527\vobres> & C:/Users/aaa/AppData/Local/Programs/Python/Python314/python.exe c:/Users/aaa/Desktop/기타/code/yalco260527/vobres/crawling/naver_stock.py
# [<div class="box_type_m">
# <h4 class="top_tlt" style="text-align:left;"><em>편입종목</em>상위</h4>
# <table cellpadding="0" cellspacing="0" class="type_1" style="”table-layout:fixed;”">
# <col width="119"/><col width="69"/><col width="79"/><col width="67"/><col width="71"/><col width="100"/><col width="89"/>
# <tr>
# <th class="tl" style="padding-left:15"><a class="sort_down" href="/sise/entryJongmok.naver?order=itemname&amp;isRightDirection=true">종목별</a></th>
# <th class="tl" style="padding-left:10"><a class="sort_down" href="/sise/entryJongmok.naver?order=now_val&amp;isRightDirection=true">현재가</a></th>
# <th class="tr" style="padding-right:10"><a class="sort_down" href="/sise/entryJongmok.naver?order=change_val&amp;isRightDirection=true">전일비</a></th>
# <th class="tr" style="padding-right:10"><a class="sort_down" href="/sise/entryJongmok.naver?order=change_rate&amp;isRightDirection=true">등락률</a></th>
# <th class="ls tr" style="padding-right:8"><a class="sort_down" href="/sise/entryJongmok.naver?order=acc_quant&amp;isRightDirection=true">거래량</a></th>
# <th class="ls tr" style="padding-right:13"><a class="sort_down" href="/sise/entryJongmok.naver?order=acc_amount&amp;isRightDirection=true">거래대금<span class="add_txt">(백만)</span></a></th>
# <th class="ls tr" style="padding-right:14"><a class="sort_up" href="/sise/entryJongmok.naver?order=market_sum&amp;isRightDirection=false">시가총액<span class="add_txt">(억)</span></a></th>
# </tr>
# <tr><td class="blank_07" colspan="7"></td></tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=005930" target="_parent">삼성전자</a></td>
# <td class="number_2">311,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pup"><span class="blind">상승</span></em><span class="tah p11 red02">
#                                 11,500
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 red01">
#                                 +3.84%
#                                 </span>

# </td>
# <td class="number">14,872,065</td>
# <td class="number_2">4,642,974</td>
# <td class="number_2">18,181,926</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=000660" target="_parent">SK하이닉스</a></td>
# <td class="number_2">2,303,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pup"><span class="blind">상승</span></em><span class="tah p11 red02">
#                                 14,000
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 red01">
#                                 +0.61%
#                                 </span>

# </td>
# <td class="number">2,785,213</td>
# <td class="number_2">6,520,046</td>
# <td class="number_2">16,413,535</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=402340" target="_parent">SK스퀘어</a></td>
# <td class="number_2">1,226,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pdn"><span class="blind">하락</span></em><span class="tah p11 nv01">
#                                 11,000
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 nv01">
#                                 -0.89%
#                                 </span>

# </td>
# <td class="number">473,756</td>
# <td class="number_2">589,264</td>
# <td class="number_2">1,617,810</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=009150" target="_parent">삼성전기</a></td>
# <td class="number_2">2,077,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pup"><span class="blind">상승</span></em><span class="tah p11 red02">
#                                 228,000
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 red01">
#                                 +12.33%
#                                 </span>

# </td>
# <td class="number">1,447,073</td>
# <td class="number_2">2,970,720</td>
# <td class="number_2">1,551,388</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=005380" target="_parent">현대차</a></td>
# <td class="number_2">709,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pup"><span class="blind">상승</span></em><span class="tah p11 red02">
#                                 32,000
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 red01">
#                                 +4.73%
#                                 </span>

# </td>
# <td class="number">1,640,818</td>
# <td class="number_2">1,175,752</td>
# <td class="number_2">1,451,733</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=373220" target="_parent">LG에너지솔루션</a></td>
# <td class="number_2">462,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pup"><span class="blind">상승</span></em><span class="tah p11 red02">
#                                 20,000
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 red01">
#                                 +4.52%
#                                 </span>

# </td>
# <td class="number">717,710</td>
# <td class="number_2">323,067</td>
# <td class="number_2">1,081,080</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=032830" target="_parent">삼성생명</a></td>
# <td class="number_2">373,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pup"><span class="blind">상승</span></em><span class="tah p11 red02">
#                                 15,500
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 red01">
#                                 +4.34%
#                                 </span>

# </td>
# <td class="number">224,789</td>
# <td class="number_2">81,742</td>
# <td class="number_2">746,000</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=329180" target="_parent">HD현대중공업</a></td>
# <td class="number_2">695,000</td>
# <td class="rate_down2">
# <em class="bu_p bu_pdn"><span class="blind">하락</span></em><span class="tah p11 nv01">
#                                 9,000
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 nv01">
#                                 -1.28%
#                                 </span>

# </td>
# <td class="number">189,118</td>
# <td class="number_2">132,935</td>
# <td class="number_2">729,481</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=028260" target="_parent">삼성물산</a></td>
# <td class="number_2">421,500</td>
# <td class="rate_down2">
# <em class="bu_p bu_pup"><span class="blind">상승</span></em><span class="tah p11 red02">
#                                 22,000
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 red01">
#                                 +5.51%
#                                 </span>

# </td>
# <td class="number">251,353</td>
# <td class="number_2">104,990</td>
# <td class="number_2">683,536</td>
# </tr>
# <tr>
# <td class="ctg"><a href="/item/main.naver?code=034020" target="_parent">두산에너빌리티</a></td>
# <td class="number_2">104,500</td>
# <td class="rate_down2">
# <em class="bu_p bu_pdn"><span class="blind">하락</span></em><span class="tah p11 nv01">
#                                 1,400
#                                 </span>

# </td>
# <td class="number_2">
# <span class="tah p11 nv01">
#                                 -1.32%
#                                 </span>

# </td>
# <td class="number">1,740,339</td>
# <td class="number_2">180,680</td>
# <td class="number_2">669,386</td>
# </tr>
# <tr><td class="blank_09" colspan="7"></td></tr>
# <tr><td class="division_line" colspan="7"></td></tr>
# </table>
# <!--- 페이지 네비게이션 시작--->
# <table align="center" class="Nnavi" summary="페이지 네비게이션 리스트">
# <caption>페이지 네비게이션</caption>
# <tr>
# <td class="on">
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=1">1</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=2">2</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=3">3</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=4">4</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=5">5</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=6">6</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=7">7</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=8">8</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=9">9</a>
# </td>
# <td>
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=10">10</a>
# </td>
# <td class="pgRR">
# <a href="/sise/entryJongmok.naver?type=KPI100&amp;page=10">맨뒤
#                                 <img alt="" border="0" height="5" src="https://ssl.pstatic.net/static/n/cmn/bu_pgarRR.gif" width="8"/>
# </a>
# </td>
# </tr>
# </table>
# <!--- 페이지 네비게이션 끝--->
# </div>]
