import os
import requests
import json
from datetime import datetime
import random
import time
import urllib.parse

# 1. API 키 및 설정 로드
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    exit(1)

# API 엔드포인트 설정 (V1 Beta - 3.0 지원)
model_name = "gemini-2.0-flash"
api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

# 2. 블로그 주제 리스트 풀 (무작위 선택)
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
]

selected_theme = random.choice(themes)
today_date = datetime.now().strftime('%Y-%m-%d')

# 3. 쿠팡 파트너스 동적 링크 생성 함수 (Search Link format)
def generate_coupang_link(query):
    base_url = "https://link.coupang.com/re/AFFSRP"
    params = {
        "lptag": "AF2993619", # 사용자 고유 ID
        "subid": "",
        "pageKey": query
    }
    encoded_params = urllib.parse.urlencode(params)
    return f"{base_url}?{encoded_params}"

# 4. 프롬프트 작성 (SEO 및 Markdown 구조화)
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

<a href="{{{{COUPANG_LINK}}}}" class="coupang-banner" target="_blank" rel="noopener noreferrer">📚 [이 주제와 어울리는 구체적인 도서명(예: 부자의 그릇, 역행자 등)] 보러가기 →<span>이 포스팅은 AI에 의해 자동 생성되었으며, 쿠팡 파트너스 활동의 일환으로 이에 따른 일정액의 수수료를 제공받습니다.</span></a>

   (주의사항:
    - href 속성값으로 반드시 '{{{{COUPANG_LINK}}}}' 플레이스홀더를 그대로 사용할 것.
    - 링크 텍스트 안의 도서명만 실제 주제에 어울리게 교체할 것.
    - <span> 태그는 반드시 위 예시처럼 <a> 태그 안에 포함할 것.
    - <iframe>, <script> 태그는 절대 사용 금지.
    - 위 <a> 태그를 그대로 마크다운 파일에 삽입할 것. 코드블록(```)으로 감싸지 말 것.)
5. 금지 사항: 결과물을 ```markdown ... ``` 코드 블록 안에 넣지 마세요. 첫째 줄이 바로 `---` 속성으로 시작해야 합니다. <iframe> 태그는 절대 사용 금지.
"""

print(f"[{today_date}] '{selected_theme}' 주제로 글쓰기를 AI에게 요청 중...")

payload = {
    "contents": [{"parts": [{"text": prompt}]}]
}
headers = {"Content-Type": "application/json"}

# 재시도 로직 추가 (최대 3회)
max_retries = 3
content = None

for i in range(max_retries):
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 429:
            print(f"[Retry {i+1}/{max_retries}] Quota exceeded. Waiting 15s...")
            time.sleep(15)
            continue
            
        response.raise_for_status()
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0]['content']['parts'][0]['text']
            break
        else:
            raise Exception(f"AI response error: {result}")

    except Exception as e:
        if i == max_retries - 1:
            print(f"Error: Final API request failed: {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"Detail: {response.text}")
            exit(1)
        print(f"Warning: Temporary error ({e}). Retrying...")
        time.sleep(5)

if not content:
    print("Error: Post generation failed.")
    exit(1)

# AI가 간혹 코드 블록 마크업을 넣어서 출력하는 경우를 대비한 방어 로직
content = content.strip()
if content.startswith("```markdown"):
    content = content[len("```markdown"):]
elif content.startswith("```"):
    content = content[len("```"):]

if content.endswith("```"):
    content = content[:-3]

content = content.strip()

# 5. 동적 링크 치환
# 주제 또는 도서명을 기반으로 쿠팡 검색 링크 생성
# (주제명에서 핵심 키워드만 추출하여 검색 결과 품질을 높임)
search_query = selected_theme.split(":")[0].split(" ")[0] if ":" in selected_theme else selected_theme.split(" ")[0]
dynamic_link = generate_coupang_link(search_query)

content = content.replace("{{COUPANG_LINK}}", dynamic_link)

# 6. 파일 저장
time_str = datetime.now().strftime('%H%M%S')
slug = f"post-{today_date}-{time_str}"

output_dir = os.path.join(os.path.dirname(__file__), "src", "content")
os.makedirs(output_dir, exist_ok=True)

filepath = os.path.join(output_dir, f"{slug}.md")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nSuccess: Post saved to {filepath}")
print(f"Dynamic Link generated for: {search_query}")
