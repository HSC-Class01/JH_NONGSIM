# JH_NONGSIM — 농심 DART 재무분석 Agent

## 🔗 대시보드 바로가기
[![Dashboard](https://img.shields.io/badge/대시보드-바로가기-0f766e?style=for-the-badge)](https://hsc-class01.github.io/JH_NONGSIM/)

농심(004370)의 DART 사업보고서·반기보고서·분기보고서를 수집하고 핵심 재무수치와 재무비율을 계산하여 GitHub Pages Dashboard로 제공하는 자동화 프로젝트입니다.

### 포함 기능
- 2010년부터 최신 정기보고서 수집
- Annual / Half-year / Quarterly 3개 테이블
- 매출·영업이익·순이익·자산·부채·자본·현금·채권·재고·CFO
- 영업이익률·순이익률·유동비율·부채비율·자기자본비율·CFO/순이익 등
- 국내 peer firms 표
- 매월 1일 KST 오전 9시 자동 업데이트
- GitHub Pages 자동 배포

### API 설정
OpenDART에서 인증키를 발급한 뒤 GitHub 저장소의 Settings → Secrets and variables → Actions → New repository secret에서 Name=DART_API_KEY, Value=40자리 API Key로 저장하십시오. API 키를 코드에 직접 입력하지 않습니다.

### Pages
Settings → Pages → Source: GitHub Actions를 확인하십시오.
예상 주소: https://hsc-class01.github.io/JH_NONGSIM/

### 2010~2014 주의
OpenDART 구조화 단일회사 재무 API는 2015년 이후 제공됩니다. 2010~2014년은 공시검색 API로 정기보고서를 찾고 원문 ZIP을 보존한 뒤 보조 추출을 수행합니다. 역사자료는 반드시 DART 원문과 대조하십시오.

### Peer firms
오뚜기(007310), 삼양식품(003230), 대상(001680), 풀무원(017810), 동원F&B(049770), CJ제일제당(097950)

## 폴더
dashboard/ · scripts/ · data/processed/ · data/raw/ · .github/workflows/
