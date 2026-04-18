import os
import sys
import requests
import json
import glob
import re
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

# Fallback 모델 체인 — 무료 Tier에서 할당량이 큰 모델 순서로 시도
# gemini-2.5-flash-lite: 1,000 RPD (가장 넉넉) → gemini-2.5-flash: 250 RPD → gemini-2.0-flash: 레거시
MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]

# 모델별 최대 재시도 횟수
MAX_RETRIES_PER_MODEL = 3

# 지수 백오프 대기 시간 (초) — 재시도할 때마다 대기 시간이 2배로 증가
BACKOFF_BASE = 10  # 10s → 20s → 40s

# GitHub Actions에서 로그가 즉시 보이도록 출력 버퍼링 비활성화
os.environ['PYTHONUNBUFFERED'] = '1'

today_date = datetime.now().strftime('%Y-%m-%d')

# ============================================================
# 2. 기존 포스트 제목 수집 (중복 방지용)
# ============================================================
def get_existing_titles():
    """src/content/ 아래 기존 md 파일들의 제목을 수집하여 중복을 방지합니다."""
    content_dir = os.path.join(os.path.dirname(__file__), "src", "content")
    titles = []
    if not os.path.exists(content_dir):
        return titles

    for md_file in glob.glob(os.path.join(content_dir, "*.md")):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read(500)  # frontmatter만 읽으면 충분
                match = re.search(r'title:\s*["\']?(.+?)["\']?\s*\n', content)
                if match:
                    titles.append(match.group(1).strip())
        except Exception:
            continue
    return titles

existing_titles = get_existing_titles()
print(f"📚 기존 포스트 {len(existing_titles)}개 발견 (중복 방지용)", flush=True)

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
    - 모든 모델 실패 시 None 반환
    """
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}]
    }
    headers = {"Content-Type": "application/json"}

    for model_idx, model_name in enumerate(MODELS):
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        print(f"\n🤖 모델 [{model_idx + 1}/{len(MODELS)}]: {model_name} 시도 중...", flush=True)

        for attempt in range(MAX_RETRIES_PER_MODEL):
            try:
                response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=120)

                # --- Quota 초과 (429) ---
                if response.status_code == 429:
                    wait_time = BACKOFF_BASE * (2 ** attempt)
                    print(f"  ⏳ [{attempt + 1}/{MAX_RETRIES_PER_MODEL}] Quota 초과. {wait_time}초 대기 후 재시도...", flush=True)
                    time.sleep(wait_time)
                    continue

                # --- 서버 에러 (500, 503 등) ---
                if response.status_code >= 500:
                    wait_time = BACKOFF_BASE * (2 ** attempt)
                    print(f"  ⚠️ [{attempt + 1}/{MAX_RETRIES_PER_MODEL}] 서버 에러 ({response.status_code}). {wait_time}초 대기...", flush=True)
                    time.sleep(wait_time)
                    continue

                # --- 모델 미지원 / 권한 없음 (404, 403) → 바로 다음 모델로 ---
                if response.status_code in (404, 403):
                    print(f"  ❌ 모델 '{model_name}' 사용 불가 (HTTP {response.status_code}). 다음 모델로 전환...", flush=True)
                    break

                # --- 기타 클라이언트 에러 ---
                response.raise_for_status()

                # --- 성공 ---
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"  ✅ {model_name} 모델로 콘텐츠 생성 성공!", flush=True)
                    return content
                else:
                    print(f"  ⚠️ [{attempt + 1}/{MAX_RETRIES_PER_MODEL}] 빈 응답. 재시도...", flush=True)
                    time.sleep(5)
                    continue

            except requests.exceptions.Timeout:
                print(f"  ⏰ [{attempt + 1}/{MAX_RETRIES_PER_MODEL}] 타임아웃. 재시도...", flush=True)
                time.sleep(10)
                continue
            except requests.exceptions.ConnectionError:
                print(f"  🔌 [{attempt + 1}/{MAX_RETRIES_PER_MODEL}] 연결 에러. 10초 대기...", flush=True)
                time.sleep(10)
                continue
            except Exception as e:
                print(f"  ❗ [{attempt + 1}/{MAX_RETRIES_PER_MODEL}] 예상치 못한 에러: {e}", flush=True)
                if attempt == MAX_RETRIES_PER_MODEL - 1:
                    break
                time.sleep(5)
                continue

        print(f"  🔄 모델 '{model_name}' 모든 재시도 소진. 다음 모델로 전환...", flush=True)

    # 모든 모델 실패
    return None

# ============================================================
# 5. [Phase 1] AI가 새로운 주제를 직접 생성
# ============================================================
existing_titles_text = ""
if existing_titles:
    existing_titles_text = "\n".join(f"  - {t}" for t in existing_titles[-30:])  # 최근 30개만
    existing_titles_text = f"""
아래는 이미 작성된 글의 제목 목록입니다. 이와 절대 중복되지 않는 완전히 새로운 주제를 선택하세요:
{existing_titles_text}
"""

topic_prompt = f"""당신은 대한민국 Top 1% 재테크·자기계발 전문 에디터입니다.
오늘 날짜: {today_date}

아래 카테고리 중 하나를 선택하여, 독자들이 진짜 궁금해할 만한 **구체적이고 심층적인 주제** 1가지를 제안하세요.

[카테고리]
1. 실전 투자 전략 (주식, ETF, 채권, 배당, 금, 암호화폐, 부동산 등)
2. 돈 관리 시스템 (가계부, 예산, 비상금, 절약, 소비 심리 등)
3. 부업 & 수익 파이프라인 (온라인 비즈니스, 프리랜서, 콘텐츠 수익화, 자동화 수입 등)
4. 자기계발 & 생산성 (습관, 시간관리, 독서법, 마인드셋, 멘탈 관리 등)
5. 경제 트렌드 & 분석 (최신 경제 이슈, 금리, 환율, 정책 변화 등)
6. 성공 사례 & 인사이트 (실제 인물의 전략 분석, 실패에서 배우는 교훈 등)

[주제 선택 기준]
- 오늘 날짜({today_date})에 어울리는 시의성 있는 주제일 것
- "~하는 법" 같은 뻔한 제목이 아닌, 독자가 "이건 꼭 읽어야겠다"고 느낄 만큼 구체적이고 흥미로운 각도
- 숫자, 데이터, 구체적 금액, 특정 사례 등이 포함된 주제
- 예: "월 50만원 배당금을 만드는 ETF 포트폴리오 3가지" ← 이런 수준의 구체성
{existing_titles_text}

[응답 형식]
반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요:
{{"topic": "주제 제목", "category": "카테고리명", "book_keyword": "이 주제와 가장 관련된 베스트셀러 1권의 도서명"}}
"""

# ============================================================
# 6. 메인 실행
# ============================================================
print(f"{'=' * 60}", flush=True)
print(f"📝 AI 블로그 자동 생성 시작 (2단계 생성)", flush=True)
print(f"📅 날짜: {today_date}", flush=True)
print(f"🤖 모델 체인: {' → '.join(MODELS)}", flush=True)
print(f"🔁 모델별 최대 재시도: {MAX_RETRIES_PER_MODEL}회 (지수 백오프)", flush=True)
print(f"{'=' * 60}", flush=True)

# Quota 충돌 방지: 0~30초 랜덤 대기 후 시작
initial_delay = random.randint(0, 30)
print(f"\n⏳ Quota 충돌 방지를 위해 {initial_delay}초 대기 후 시작...", flush=True)
time.sleep(initial_delay)

# --- Phase 1: 주제 생성 ---
print(f"\n{'─' * 40}", flush=True)
print(f"📌 [Phase 1/2] AI가 새로운 주제를 생성 중...", flush=True)
print(f"{'─' * 40}", flush=True)

topic_response = call_gemini_api(topic_prompt)

if not topic_response:
    print("❌ 주제 생성 실패. 모든 모델에서 실패했습니다.", flush=True)
    exit(1)

# JSON 파싱
topic_response = topic_response.strip()
# JSON이 코드블록으로 감싸져 있으면 제거
if topic_response.startswith("```"):
    topic_response = re.sub(r'^```(?:json)?\s*', '', topic_response)
    topic_response = re.sub(r'\s*```$', '', topic_response)

try:
    topic_data = json.loads(topic_response)
    selected_theme = topic_data["topic"]
    category = topic_data.get("category", "자기계발")
    book_keyword = topic_data.get("book_keyword", "부자의 그릇")
except (json.JSONDecodeError, KeyError) as e:
    print(f"⚠️ JSON 파싱 실패, 원본 응답을 주제로 사용: {e}", flush=True)
    selected_theme = topic_response.split('"')[1] if '"' in topic_response else "2026년 경제적 자유를 위한 실전 전략"
    category = "재테크"
    book_keyword = "부자의 그릇"

print(f"\n🎯 생성된 주제: {selected_theme}", flush=True)
print(f"📂 카테고리: {category}", flush=True)
print(f"📖 추천 도서: {book_keyword}", flush=True)

# API 호출 간격을 위해 잠시 대기
time.sleep(3)

# ============================================================
# 7. [Phase 2] 전문가 수준의 블로그 포스트 작성
# ============================================================
print(f"\n{'─' * 40}", flush=True)
print(f"📌 [Phase 2/2] 전문가 수준의 블로그 포스트 작성 중...", flush=True)
print(f"{'─' * 40}", flush=True)

blog_prompt = f"""당신은 10년 이상 경력의 대한민국 최고 재테크·자기계발 전문가이자 SEO 마스터 블로거입니다.
월간 100만 PV 이상의 블로그를 운영하고 있습니다.

다음 주제에 대해 "전문가만이 쓸 수 있는" 깊이 있는 블로그 포스팅을 작성하세요:
주제: "{selected_theme}"
카테고리: {category}

═══════════════════════════════════════
[작성 형식]
═══════════════════════════════════════
1. 언어: 한국어
2. 형식: 맨 위에 반드시 YAML 프론트매터(Frontmatter)를 포함한 순수 마크다운(.md) 포맷.
3. Frontmatter 필수 포함 내용:
   - title: 검색 클릭률(CTR)을 극대화하는 매력적인 제목 (숫자, 구체적 수치 포함 권장)
   - date: "{today_date}"
   - excerpt: 구글 검색 결과에 노출될 1~2줄의 핵심 메타 설명 (120자 이내)
   - category: "{category}"
   - tags: 관련 태그 5~7개 배열

═══════════════════════════════════════
[콘텐츠 품질 기준 — 반드시 모두 충족]
═══════════════════════════════════════
1. **전문성 (Expertise)**
   - 해당 분야의 전문 용어를 자연스럽게 사용하되, 일반인도 이해 가능하도록 해설을 곁들일 것
   - 구체적인 숫자, 데이터, 통계를 최소 3회 이상 인용 (예: "S&P 500의 연평균 수익률 10.7%")
   - 실제 사례, 케이스 스터디, 또는 가상의 현실적 시나리오를 2회 이상 포함

2. **구조 (Structure)**
   - H2(##)로 3~5개의 큰 섹션, H3(###)으로 세부 항목을 나눌 것
   - 핵심 내용은 볼드(**), 리스트(- ), 표(| |)를 적극 활용하여 가독성을 높일 것
   - 총 분량: 2,000자 이상 3,500자 이하

3. **가치 (Value)**
   - 도입부: 독자의 핵심 고민이나 궁금증을 정확히 짚는 후킹 (단순 질문이 아닌, 공감을 이끄는 시나리오)
   - 본문: "읽고 나면 바로 실행할 수 있는" 구체적인 방법론, 단계별 가이드, 체크리스트 등
   - 중간에 해당 주제의 최고 권위자(워런 버핏, 나폴레온 힐, 피터 린치, 레이 달리오, 짐 론, 로버트 기요사키 등)의 명언 1개를 인용구(> )로 포함
   - 결론: 독자가 당장 오늘부터 실행할 수 있는 3가지 구체적 액션 아이템

4. **SEO 최적화**
   - 핵심 키워드를 자연스럽게 본문에 5~8회 분포
   - 내부 FAQ 스타일 섹션 (자주 묻는 질문 1~2개) 포함하여 검색 노출 극대화

═══════════════════════════════════════
[쿠팡 파트너스 링크 삽입 규칙]
═══════════════════════════════════════
글 마지막에 아래 형식의 쿠팡 파트너스 링크를 반드시 한 개만 삽입할 것 (iframe 절대 금지):

<a href="{{{{COUPANG_LINK}}}}" class="coupang-banner" target="_blank" rel="noopener noreferrer">📚 [{book_keyword}] 상세 정보 확인하기 →<span>이 포스팅은 AI에 의해 자동 생성되었으며, 쿠팡 파트너스 활동의 일환으로 이에 따른 일정액의 수수료를 제공받습니다.</span></a>

(주의사항:
 - href 속성값으로 반드시 '{{{{COUPANG_LINK}}}}' 플레이스홀더를 그대로 사용할 것.
 - <span> 태그는 반드시 위 예시처럼 <a> 태그 안에 포함할 것.
 - <iframe>, <script> 태그는 절대 사용 금지.
 - 위 <a> 태그를 그대로 마크다운 파일에 삽입할 것. 코드블록(```)으로 감싸지 말 것.)

═══════════════════════════════════════
[금지 사항]
═══════════════════════════════════════
- 결과물을 ```markdown ... ``` 코드 블록 안에 넣지 마세요. 첫째 줄이 바로 `---`로 시작해야 합니다.
- <iframe> 태그는 절대 사용 금지.
- 뻔한 조언, 추상적인 이야기 금지. 반드시 구체적 숫자와 실행 방법을 제시하세요.
- "~하세요", "~합시다" 같은 단순 권유형보다 "왜 그래야 하는지" 데이터와 근거를 먼저 제시하세요.
"""

content = call_gemini_api(blog_prompt)

if not content:
    print(f"\n{'=' * 60}", flush=True)
    print("❌ 모든 모델에서 콘텐츠 생성 실패.", flush=True)
    print("   원인: Gemini API 할당량이 모든 모델에서 소진되었을 수 있습니다.", flush=True)
    print("   조치: Google AI Studio에서 할당량을 확인하세요.", flush=True)
    print(f"{'=' * 60}", flush=True)
    exit(1)

# ============================================================
# 8. 후처리 — 코드블록 마크업 제거
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
# 9. 쿠팡 파트너스 링크 치환
# ============================================================
dynamic_link = generate_coupang_link(book_keyword)
content = content.replace("{{COUPANG_LINK}}", dynamic_link)

# ============================================================
# 10. 파일 저장
# ============================================================
time_str = datetime.now().strftime('%H%M%S')
slug = f"post-{today_date}-{time_str}"

output_dir = os.path.join(os.path.dirname(__file__), "src", "content")
os.makedirs(output_dir, exist_ok=True)

filepath = os.path.join(output_dir, f"{slug}.md")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n{'=' * 60}", flush=True)
print(f"✅ 게시물 생성 완료!", flush=True)
print(f"📄 파일: {filepath}", flush=True)
print(f"🎯 주제: {selected_theme}", flush=True)
print(f"📂 카테고리: {category}", flush=True)
print(f"📖 추천 도서: {book_keyword}", flush=True)
print(f"🔗 쿠팡 링크: {dynamic_link}", flush=True)
print(f"{'=' * 60}", flush=True)
