from apscheduler.schedulers.blocking import BlockingScheduler
from cost import main
import logging

# 로깅 설정 (INFO 레벨로 설정)
logging.basicConfig(level=logging.INFO)

# 스케줄러 작업을 설정하는 함수
def schedule_job():
    # BlockingScheduler 객체 생성
    scheduler = BlockingScheduler()
    
    # 스케줄러에 작업 추가: 매일 00시 00분에 main 함수 실행 (KST)
    scheduler.add_job(main, 'cron', hour=0, minute=00)
    
    # 스케줄러 시작 정보 로그 출력
    logging.info("스케줄러가 시작되었습니다. 매일 00시(KST)에 예약된 작업입니다.")
    
    # 스케줄러 시작
    scheduler.start()

# 스크립트가 직접 실행될 때만 schedule_job 함수 호출
if __name__ == '__main__':
    schedule_job()
