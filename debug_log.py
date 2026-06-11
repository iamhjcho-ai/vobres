# import logging.config

# logger_dict = {
#     'version': 1,
#     'formatters': {
#         'default': {
#             "format": "%(asctime)s | %(levelname)s - %(message)s"
#         },
#         'simple': {
#             'format': '[%(asctime)s] %(message)s'
#         }
#     },
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': 'debug.log',
#             'formatter': 'default',
#         },
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple',
#         },
#     },
#     'root': {
#         'level': 'DEBUG',
#         'handlers': ['file']
#     }
# }



import logging
from logging.handlers import RotatingFileHandler


def start_debugging(level='DEBUG', log_filename='Debug.log', console=True):
    try:
        # 로거 생성 / 로깅 레벨 설정
        logger = logging.getLogger("vobres_log")
        logger.setLevel(logging.DEBUG)      # DEBUG:root: 디버깅 메시지 
                                            # INFO:root: 일반 정보 메시지 
                                            # WARNING:root: 경고 메시지 
                                            # ERROR:root: 에러 발생! 
                                            # CRITICAL:root: 치명적인 오류 발생!

        # 파일 핸들러 생성
        # file_handler = logging.FileHandler("debug.log", encoding='utf-8')
        # 만약, 파일 최대 사이즈와 최대 갯수를 지정하고 싶다면 다음과 같이 하면 된다.
        # 1MB 크기의 파일을 최대 3개만 만들겠다. 초과하면 오래된것 부터 하나씩 삭제
        file_handler = RotatingFileHandler(log_filename, encoding='utf-8', maxBytes=1024*1024, backupCount=3)

        # 로그 메시지 포맷 설정
        formatter = logging.Formatter("[%(levelname)s] '%(filename)s' %(asctime)s : %(message)s")
        file_handler.setFormatter(formatter)

        # 로거에 파일 핸들러 추가
        logger.addHandler(file_handler)

        if console:     # 콘솔 핸들러도 추가
            console_handler = logging.StreamHandler()   # 콘솔 핸들러 생성
            formatter = logging.Formatter("[%(levelname)s] '%(filename)s': %(message)s")
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
    except Exception as e:
        print(f'start_debugging: {e}')
        
    return logger



if __name__ == '__main__':

    logger = start_debugging()
    # 로깅
    logger.debug("for debug 디버그")
    logger.info("for info")
    logger.warning("for warn")
    logger.error("for error")
    logger.critical("for critical")

