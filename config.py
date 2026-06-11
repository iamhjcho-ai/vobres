# 실제 투자 시 False로 변경
is_paper_trading = True

# 따옴표 안에 작성할 것
real_app_key = ""
real_app_secret = ""

paper_app_key = "ui6AC3XtV4A64hcmUtmiR0KU4rolnqkPosHfkzhp1eE"
paper_app_secret = "0oAldMX-fmvqT7y48X6TtfHtN9cSfrmcM-QIjlYhK6s"

real_host_url = "https://api.kiwoom.com"
paper_host_url = "https://mockapi.kiwoom.com"

real_socket_url = "wss://api.kiwoom.com:10000"
paper_socket_url = "wss://mockapi.kiwoom.com:10000"

app_key = paper_app_key if is_paper_trading else real_app_key
app_secret = paper_app_secret if is_paper_trading else real_app_secret

host_url = paper_host_url if is_paper_trading else real_host_url
socket_url = paper_socket_url if is_paper_trading else real_socket_url

#telegram BotFather @js_sstock_bot
telegram_chat_id = "8708993110"   
telegram_token = "8725467832:AAEnbdvMrHATtummmJd_E6aWp4Do1QCXNMg"