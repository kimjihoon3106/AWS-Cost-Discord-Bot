import boto3
import requests
import calendar
from datetime import datetime, timedelta
from typing import Dict, Tuple
import os

# 환율 정보 가져오기
def get_usd_to_krw_rate() -> float:
    """
    현재 USD에서 KRW로의 환율을 가져옵니다.
    """
    try:
        # Open Exchange Rates API 또는 다른 무료 환율 API 사용
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        data = response.json()
        usd_to_krw = data['rates']['KRW']
        return usd_to_krw
    except Exception as e:
        print(f"환율 정보 조회 실패: {e}")
        # 기본값 반환 (실제 환율로 업데이트 필요)
        return 1300.0


# AWS Account ID 조회
def get_aws_account_id() -> str:
    """
    AWS Account ID를 조회합니다.
    """
    try:
        sts_client = boto3.client('sts', region_name='us-east-1')
        account_id = sts_client.get_caller_identity()['Account']
        return account_id
    except Exception as e:
        print(f"AWS Account ID 조회 실패: {e}")
        return "Unknown"


# AWS 비용 조회
def get_aws_cost() -> Tuple[float, Dict]:
    """
    AWS Cost Explorer를 사용하여 이번 달 총 비용을 조회합니다.
    """
    try:
        # AWS 자격증명은 환경변수 또는 ~/.aws/credentials에서 자동으로 로드됩니다
        ce_client = boto3.client('ce', region_name='us-east-1')
        
        # 이번 달의 시작 날짜와 마지막 날짜 설정
        now = datetime.utcnow()
        start = now.replace(day=1).strftime('%Y-%m-%d')
        last_day_of_month = calendar.monthrange(now.year, now.month)[1]
        end = now.replace(day=last_day_of_month).strftime('%Y-%m-%d')
        
        print(f"  조회 기간: {start} ~ {end}")
        
        # 비용 조회 요청
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start,
                'End': end
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )
        
        # 비용 계산
        total_cost = 0.0
        service_costs = {}
        
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                service_costs[service] = cost
                total_cost += cost
        
        return total_cost, service_costs
    
    except Exception as e:
        print(f"AWS 비용 조회 실패: {e}")
        return 0.0, {}


# Discord 메시지 전송
def send_discord_message(webhook_url: str, usd_cost: float, krw_rate: float, service_costs: Dict, account_id: str) -> bool:
    """
    Discord 웹훅을 사용하여 AWS 비용 정보를 전송합니다.
    """
    try:
        krw_cost = usd_cost * krw_rate
        
        # 서비스별 비용 상세 정보 생성
        services_detail = "\n".join([
            f"• {service}: ${cost:.2f} (₩{cost * krw_rate:,.0f})"
            for service, cost in sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:5]
        ])
        
        if not services_detail:
            services_detail = "비용 정보가 없습니다."
        
        # Discord Embed 메시지 생성
        embed = {
            "title": "📊 AWS 월간 비용 리포트",
            "color": 16776960,  # 노란색
            "fields": [
                {
                    "name": "🔐 AWS Account ID",
                    "value": f"{account_id}",
                    "inline": False
                },
                {
                    "name": "💵 총 비용 (USD)",
                    "value": f"${usd_cost:.2f}",
                    "inline": True
                },
                {
                    "name": "₩ 총 비용 (KRW)",
                    "value": f"₩{krw_cost:,.0f}",
                    "inline": True
                },
                {
                    "name": "📈 현재 환율",
                    "value": f"1 USD = ₩{krw_rate:,.2f}",
                    "inline": True
                },
                {
                    "name": "📋 상위 5개 서비스 비용",
                    "value": services_detail,
                    "inline": False
                }
            ],
            "footer": {
                "text": f"조회 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        }
        
        # Discord 웹훅으로 전송
        payload = {
            "embeds": [embed]
        }
        
        response = requests.post(webhook_url, json=payload)
        
        if response.status_code == 204:
            print("Discord 메시지 전송 성공")
            return True
        else:
            print(f"Discord 메시지 전송 실패: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"Discord 메시지 전송 중 오류: {e}")
        return False


# Main 함수
def main():
    """
    환율 조회, AWS 비용 조회, Discord 알림을 처리하는 메인 함수
    """
    print("=" * 50)
    print("AWS 비용 리포트 시작")
    print("=" * 50)
    
    # 1단계: 환율 조회
    print("\n1단계: 현재 환율 조회 중...")
    krw_rate = get_usd_to_krw_rate()
    print(f"✓ 환율 조회 완료: 1 USD = ₩{krw_rate:,.2f}")
    
    # 2단계: AWS Account ID 조회
    print("\n2단계: AWS Account ID 조회 중...")
    account_id = get_aws_account_id()
    print(f"✓ Account ID 조회 완료: {account_id}")
    
    # 3단계: AWS 비용 조회
    print("\n3단계: AWS 비용 조회 중...")
    usd_cost, service_costs = get_aws_cost()
    print(f"✓ AWS 비용 조회 완료: ${usd_cost:.2f}")
    
    # 4단계: Discord로 전송
    print("\n4단계: Discord로 알림 전송 중...")
    discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    
    if not discord_webhook_url:
        print("❌ 오류: DISCORD_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")
        return
    
    success = send_discord_message(discord_webhook_url, usd_cost, krw_rate, service_costs, account_id)
    
    if success:
        print("✓ 모든 작업 완료!")
    else:
        print("❌ 일부 작업 실패")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
