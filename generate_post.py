import os
import requests
import json
from datetime import datetime
import random
import time
import urllib.parse

# ============================================================
# 1. 설정
# ============================================================
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    exit(1)

# Fallback 모델 체인 — 첫 번째 모델이 Quota 초과 시 다음 모델로 자동 전환
MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-preview-05-20",
    "gemini-1.5-flash",
]

# 모델별 최대 재시도 횟수
MAX_RETRIES_PER_MODEL = 5

# 지수 백오프 대기 시간 (초) — 재시도할 때마다 대기 시간이 2배로 증가
BACKOFF_BASE = 30  # 30s → 60s → 120s → 240s → 480s

# ============================================================
# 2. 블로그 주제 리스트 (무작위 선택)
# ============================================================
themes = [
    "부자들의 독서 습관과 마인드셋의 비밀",
    "아침 5시 미라클 모닝 기상과 자기계발의 기적",
    "초보자를 위한 실전 가계부 작성법과 지출 통제",
    "100만원으로 시작하는 소액 투자 원칙",
    "돈을 끌어당기는 무의식 프로그래밍 체질 개선",
    "가장 확실한 자기계발: 체력 관리와 번아웃 예방",
    "2030 직장인 파이프라인 구축 및 부수입 창출 전략",
    "복리의 마법: 시간이 돈을 벌어주는 원리",
    "성공하는 사람들의 시간 관리 비밀 5가지",
    "월급 외 수입을 만드는 현실적인 방법들",
    "부자 마인드셋: 돈에 대한 생각을 바꾸는 법",
    "자기계발 독서법: 읽은 것을 실천으로 바꾸는 기술",
    "ETF 투자 입문: 직장인을 위한 실전 가이드",
    "습관의 힘: 작은 변화가 인생을 바꾸는 이유",
    "경제적 자유를 위한 돈 관리 시스템 구축법",
    "디지털 노마드 시대의 원격 부업 전략",
    "주식 초보를 위한 분산 투자 포트폴리오 만들기",
    "재테크 실패를 피하는 심리적 함정 5가지",
    "하루 30분 자기계발 루틴의 복리 효과",
    "부동산 없이 자산을 불리는 현실적인 방법",
]

selected_theme = random.choice(themes)
today_date = datetime.now().strftime('%Y-%m-%d')

# ============================================================
# 3. 쿠팡 파트너스 링크 생성
# ============================================================
def generate_coupang_link(query, is_id=False):
    if is_id:
        return f"https://link.coupang.com/re/AFFSDP?lptag=AF2993619&subid=&pageKey={query}"
    else:
        return f"https://link.coupang.com/re/AFFSRP?lptag=AF2993619&pageKey={urllib.parse.quote(query)}"

# ============================================================
# 4. Gemini API 호출 (Fallback + 지수 백오프)
# ============================================================
def call_gemini_api(prompt_text):
    """
    여러 모델을 순차적으로 시도하여 안정적으로 콘텐츠를 생성합니다.
    - 모델별로 MAX_RETRIES_PER_MODEL회 재시도
    - 429(Quota) 에러 시 지수 백오프 적용
    - 모든 모델 실패 시에만 exit(1)
    """
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}]
    }
    headers = {"Content-Type": "application/json"}

    for model_idx, model_name in enumerate(MODELS):
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        print(f"\n🤖 모델 [{model_idx + 1}/{len(MODELS)}]: {model_name} 시도 중...")

        for attempt in range(MAX_RETRIES_PER_MODEL):
            try:
                response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=120)

                # --- Quota 초과 (429) ---
                if response.status_code == 429:
                    wait_time = BACKOFF_BASE * (2 ** attempt)  # 15, 30, 60, 120초
                    print(f"  ⏳ [{attempt + 1}/{MAX_RETRIES_PER_MODEL}] Quota 초과. {wait_time}초 대기 후 재시도...")
                    time.sleep(wait_time)
                    continue

                # --- 서버 에러 (500, 503 등) ---
                if response.status_code >= 500:
                    wait_time = BACKOFF_BASE * (2 ** attempt)
                    print(f"  ⚠️ [{attempt + 1}/{MAX_RETRIES_PER_MODEL}] 서버 에러 ({response.status_code}). {wait_time}초 대기...")
                    time.sleep(wait_time)
                    continue

                # --- 모델 미지원 / 권한 없음 (404, 403) → 바로 다음 모델로 ---
                if response.status_code in (404, 403):
                    print(f"  ❌ 모델 '{model_name}' 사용 불가 (HTTP {response.status_code}). 다음 모델로 전환...")
                    break

                # --- 기타 클라이언트 에러 ---
                response.raise_for_status()

                # --- 성공 ---
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"  ✅ {model_name} 모델로 콘텐츠 생성 성공!")
                    return content
                else:
                    # 안전 필터 등으로 빈 응답이 온 경우
                    print(f"  ⚠️ [{attempt + 1}/{MAX_RETRIES_PER_MODEL}] 빈 응답. 재시도...")
                    time.sleep(5)
                    continue

            except requests.exceptions.Timeout:
                print(f"  ⏰ [{attempt + 1}/{MAX_RETRIES_PER_MODEL}] 타임아웃. 재시도...")
                time.sleep(10)
                continue
            except requests.exceptions.ConnectionError:
                print(f"  🔌 [{attempt + 1}/{MAX_RETRIES_PER_MODEL}] 연결 에러. 10초 대기...")
                time.sleep(10)
                continue
            except Exception as e:
                print(f"  ❗ [{attempt + 1}/{MAX_RETRIES_PER_MODEL}] 예상치 못한 에러: {e}")
                if attempt == MAX_RETRIES_PER_MODEL - 1:
                    break
                time.sleep(5)
                continue

        print(f"  🔄 모델 '{model_name}' 모든 재시도 소진. 다음 모델로 전환...")

    # 모든 모델 실패
    return None

# ============================================================
# 5. 프롬프트 작성
# ============================================================
prompt = f"""
당신은 최고의 자기계발 및 재테크 전문가이자 구글 검색 SEO 최적화 전문 블로거입니다.
다음 주제에 대해 블로그 포스팅을 작성해주세요: "{selected_theme}"

작성 조건:
1. 언어: 한국어
2. 형식: 맨 위에 반드시 YAML 프론트매터(Frontmatter)를 포함한 순수 마크다운(.md) 포맷.
3. Frontmatter 필수 포함 내용:
   - title: 매력적이고 클릭을 유도하는 제목
   - date: "{today_date}"
   - excerpt: 검색 봇을 위한 1~2줄의 핵심 요약
   - tags: ["재테크", "자기계발"] 등 관련된 태그 배열
4. 콘텐츠 내용:
   - 도입부에서 독자의 시선을 끄는 강력한 후킹 발언 사용.
   - H2(##) 및 H3(###) 태그를 적절히 사용하여 글의 가독성을 최대로 높임.
   - 내용 중간에 이 주제와 어울리는 유명인의 성공 명언 1개를 인용구(> )로 반드시 포함할 것.
   - 결론부에 당장 오늘부터 실천할 수 있는 구체적인 행동 가이드(Call to Action) 포함.
   - 글 마지막에 아래 형식의 쿠팡 파트너스 링크를 반드시 한 개만 삽입할 것 (iframe 절대 금지):

<a href="{{{{COUPANG_LINK}}}}" class="coupang-banner" target="_blank" rel="noopener noreferrer">📚 [이 주제와 어울리는 구체적인 도서명(예: 부자의 그릇, 역행자 등)] 상세 정보 확인하기 →<span>이 포스팅은 AI에 의해 자동 생성되었으며, 쿠팡 파트너스 활동의 일환으로 이에 따른 일정액의 수수료를 제공받습니다.</span></a>

   (주의사항:
    - href 속성값으로 반드시 '{{{{COUPANG_LINK}}}}' 플레이스홀더를 그대로 사용할 것.
    - 링크 텍스트 안의 도서명만 실제 주제에 어울리게 교체할 것.
    - <span> 태그는 반드시 위 예시처럼 <a> 태그 안에 포함할 것.
    - <iframe>, <script> 태그는 절대 사용 금지.
    - 위 <a> 태그를 그대로 마크다운 파일에 삽입할 것. 코드블록(```)으로 감싸지 말 것.)
5. 금지 사항: 결과물을 ```markdown ... ``` 코드 블록 안에 넣지 마세요. 첫째 줄이 바로 `---` 속성으로 시작해야 합니다. <iframe> 태그는 절대 사용 금지.
"""

# ============================================================
# 6. 메인 실행
# ============================================================
print(f"{'=' * 60}")
print(f"📝 AI 블로그 자동 생성 시작")
print(f"📅 날짜: {today_date}")
print(f"🎯 주제: {selected_theme}")
print(f"🤖 모델 체인: {' → '.join(MODELS)}")
print(f"🔁 모델별 최대 재시도: {MAX_RETRIES_PER_MODEL}회 (지수 백오프)")
print(f"{'=' * 60}")

# Quota 충돌 방지: 0~120초 랜덤 대기 후 시작
initial_delay = random.randint(0, 120)
print(f"\n⏳ Quota 충돌 방지를 위해 {initial_delay}초 대기 후 시작...")
time.sleep(initial_delay)

content = call_gemini_api(prompt)

if not content:
    print(f"\n{'=' * 60}")
    print("❌ 모든 모델에서 콘텐츠 생성 실패.")
    print("   원인: Gemini API 할당량이 모든 모델에서 소진되었을 수 있습니다.")
    print("   조치: Google AI Studio에서 할당량을 확인하세요.")
    print(f"{'=' * 60}")
    exit(1)

# ============================================================
# 7. 후처리 — 코드블록 마크업 제거
# ============================================================
content = content.strip()
if content.startswith("```markdown"):
    content = content[len("```markdown"):]
elif content.startswith("```"):
    content = content[len("```"):]

if content.endswith("```"):
    content = content[:-3]

content = content.strip()

# ============================================================
# 8. 쿠팡 파트너스 링크 치환
# ============================================================
search_query = selected_theme.split(":")[0].split(" ")[0] if ":" in selected_theme else selected_theme.split(" ")[0]

if "그릇" in search_query or "부자의 그릇" in selected_theme:
    dynamic_link = generate_coupang_link("4633275230", is_id=True)
else:
    dynamic_link = generate_coupang_link(search_query)

content = content.replace("{{COUPANG_LINK}}", dynamic_link)

# ============================================================
# 9. 파일 저장
# ============================================================
time_str = datetime.now().strftime('%H%M%S')
slug = f"post-{today_date}-{time_str}"

output_dir = os.path.join(os.path.dirname(__file__), "src", "content")
os.makedirs(output_dir, exist_ok=True)

filepath = os.path.join(output_dir, f"{slug}.md")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n{'=' * 60}")
print(f"✅ 게시물 생성 완료!")
print(f"📄 파일: {filepath}")
print(f"🔗 쿠팡 링크 키워드: {search_query}")
print(f"🔗 링크: {dynamic_link}")
print(f"{'=' * 60}")
