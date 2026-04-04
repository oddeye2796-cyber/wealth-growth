import os
from datetime import datetime
import random
from google import genai

# 1. API 키 로드
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    exit(1)

client = genai.Client(api_key=api_key)

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

# 3. 프롬프트 작성 (SEO 및 Markdown 구조화)
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
   - 글 마지막에 다음과 같은 문구를 자연스럽게 추가:
     *이 포스팅은 AI에 의해 자동 생성되었으며, 쿠팡 파트너스 활동의 일환으로 일정액의 수수료를 제공받을 수 있습니다.*
5. 금지 사항: 결과물을 ```markdown ... ``` 코드 블록 안에 넣지 마세요. 첫째 줄이 바로 `---` 속성으로 시작해야 합니다.
"""

print(f"[{today_date}] '{selected_theme}' 주제로 글쓰기를 AI에게 요청 중...")

try:
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt
    )
    content = response.text
except Exception as e:
    print(f"API 요청 중 에러가 발생했습니다: {e}")
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

# 4. 파일 저장
time_str = datetime.now().strftime('%H%M%S')
slug = f"post-{today_date}-{time_str}"

output_dir = os.path.join(os.path.dirname(__file__), "src", "content")
os.makedirs(output_dir, exist_ok=True)

filepath = os.path.join(output_dir, f"{slug}.md")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ 포스팅 성공: {filepath} 경로에 저장되었습니다!")
