# Sales Automation Plugin — 데모 산출물 인덱스

**시나리오**: (주)노바테크 (HR Tech SaaS, Series A) 의 AI 어시스턴트 도입 의뢰 — 2026-05-19 인입부터 견적 발행까지 3일간의 실제 영업 흐름.

---

## 산출물 목록

| # | 파일 | 스킬 | 실행 시점 | 핵심 내용 |
|---|------|------|-----------|-----------|
| 01 | [account-research](outputs/01-account-research.md) | `account-research` | 5/21 오전 (콜 전) | 노바테크 리드 유효성 검증 — B등급 75점 |
| 02 | [call-prep](outputs/02-call-prep.md) | `call-prep` | 5/21 13:30 (콜 30분 전) | 5/21 14:00 콜 대비 심층 브리프 |
| 03 | [call-summary](outputs/03-call-summary.md) | `call-summary` | 5/21 14:30 (콜 직후) | 28분 콜 요약 + Pluuug 저장 미리보기 |
| 04 | [daily-briefing](outputs/04-daily-briefing.md) | `daily-briefing` | 5/22 오전 (다음날) | 금요일 모닝 브리핑 — 정산 지연 #1 우선순위 |
| 05 | [email-send](outputs/05-email-send.md) | `email-send` | 5/22 오전 | PoC 제안 메일 — 템플릿 30번 선택 및 발송 |
| 06 | [quote-writing](outputs/06-quote-writing.md) | `quote-writing` | 5/22 오후 | PoC 견적서 작성 — 손익·리스크 분석 포함 |

---

## 어떻게 읽으면 좋은지

각 산출물은 **사용자 발화 → 스킬 실행 결과** 순서로 구성되어 있습니다. 콜 전(01→02) → 콜 중·후(03) → 다음날(04→05→06) 시간순으로 읽으면 실제 영업 담당자가 플러그인을 사용하는 하루 흐름을 그대로 따라갈 수 있습니다. 각 파일 끝의 "데모 노트" 박스는 실제 환경에서 어떤 API·외부 서비스가 호출되는지 설명합니다. 시나리오 상세는 [scenario.md](scenario.md)를 참조하세요.
