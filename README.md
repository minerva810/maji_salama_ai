# Maji Salama AI

Maji Salama AI는 탄자니아 지역사회를 위한 AI 기반 지하수 안전 안내
시스템입니다. 지하수 수질 측정값, 지질, 토양, 고도, 강우량 및 기타 환경
데이터를 결합하여 불소 및 세균 오염 위험을 추정합니다.

주민은 전화 앱에서 `*123#`와 같은 USSD 단축 코드를 입력해 서비스에
접속합니다. 세션 기반 메뉴에서 `102`와 같은 등록 우물 ID를 입력하면
요청이 백엔드로 전달됩니다. 백엔드는 해당 우물과 환경 특성을 조회하고,
설정된 위험 예측 모델을 호출한 뒤 위험 등급을 판정합니다. 필요한 경우
주변에서 위험도가 더 낮은 수원을 검색하고, 최종 식수 행동 지침을 USSD
화면에 반환합니다.

초기 MVP는 탄자니아 북부를 대상으로 하며, 향후 탄자니아 전역과
동아프리카 열곡대로 확장하는 것을 목표로 합니다.

## Getting Started

백엔드는 특정 AI 모델 구현에 직접 의존하지 않도록 설계합니다. 초기 개발
단계에서는 Dummy 모델을 이용해 백엔드, 추천 엔진, USSD의 전체 흐름을
먼저 구현하고 테스트한 뒤 최종 학습 모델로 교체할 수 있습니다.

### Prerequisites

-   Python 3.11 이상
-   Git
-   PostgreSQL
-   PostGIS
-   Docker 및 Docker Compose 권장
-   `venv` 또는 Conda와 같은 Python 가상환경

주요 Python 패키지

``` text
fastapi
uvicorn
pydantic
sqlalchemy
alembic
psycopg
pandas
numpy
geopandas
scikit-learn
joblib
pytest
httpx
```

End-to-End USSD 테스트를 위해 USSD Gateway 또는 이동통신사/통신
Aggregator의 Sandbox 환경이 필요합니다. 개발 단계와 탄자니아 현장
배포에서는 공급자와 Short Code 발급 방식이 달라질 수 있습니다.

### Installing

저장소를 복제합니다.

``` bash
git clone <REPOSITORY_URL>
cd maji-salama-ai
```

가상환경을 생성하고 활성화합니다.

Conda 사용:

``` bash
conda create -n maji-salama python=3.11
conda activate maji-salama
```

또는 `venv` 사용:

``` bash
python -m venv .venv
```

Windows:

``` bash
.venv\Scripts\activate
```

macOS/Linux:

``` bash
source .venv/bin/activate
```

의존성을 설치합니다.

``` bash
pip install -r requirements.txt
```

로컬 환경 변수 파일을 생성합니다.

``` bash
cp .env.example .env
```

Windows PowerShell:

``` powershell
Copy-Item .env.example .env
```

개발 환경 설정 예시는 다음과 같습니다.

``` env
APP_ENV=development
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/maji_salama

RISK_MODEL_TYPE=dummy

FLUORIDE_MODEL_PATH=model_artifacts/fluoride/v1/model.joblib
BACTERIAL_MODEL_PATH=model_artifacts/bacterial/v1/model.joblib

USSD_API_KEY=
USSD_WEBHOOK_SECRET=
```

`.env`, API Key, USSD 인증 정보 등의 비밀 정보는 Git에 커밋하지
않습니다.

Docker Compose를 이용해 PostgreSQL/PostGIS를 실행합니다.

``` bash
docker compose up -d db
```

데이터베이스 Migration을 적용합니다.

``` bash
alembic upgrade head
```

샘플 우물 및 환경 특성 데이터를 적재합니다.

``` bash
python scripts/seed_wells.py
python scripts/seed_features.py
```

FastAPI 애플리케이션을 실행합니다.

``` bash
uvicorn app.main:app --reload
```

대화형 API 문서는 다음 주소에서 확인할 수 있습니다.

``` text
http://localhost:8000/docs
```

기본 개발 데모의 처리 흐름은 다음과 같습니다.

``` text
*123#
    ↓
USSD 메뉴
    ↓
우물 ID 입력: 102
    ↓
우물 조회
    ↓
Dummy 또는 실제 위험 예측 모델
    ↓
불소 / 세균 위험 등급 판정
    ↓
위험도가 더 낮은 주변 수원 추천
    ↓
행동 지침 반환
```

API 결과 예시:

``` json
{
  "well_id": "102",
  "risk": {
    "fluoride": "HIGH",
    "bacterial": "LOW"
  },
  "recommendation": {
    "well_id": "108",
    "distance_km": 1.4
  }
}
```

### USSD 이용 흐름

MVP에서는 자유 형식 USSD 명령 대신 세션 기반 USSD 메뉴를 사용합니다.

``` text
사용자 입력: *123#
        ↓
1. 수원 확인
2. 도움말
3. 언어 설정
        ↓
사용자 선택: 1
        ↓
우물 ID를 입력하세요:
        ↓
사용자 입력: 102
        ↓
백엔드 Guidance 요청
        ↓
Well 102
Fluoride: HIGH
Bacteria: LOW
Avoid long-term drinking.
Lower-risk source: Well 108, 1.4 km.
```

USSD Gateway는 통신 세션을 유지하고 사용자의 각 메뉴 선택을 FastAPI
Webhook으로 전달합니다. 핵심 백엔드는 통신 채널과 분리하며, USSD
Adapter가 세션 입력을 일반 Guidance 요청으로 변환하고 결과를 USSD 화면에
맞게 포맷합니다.

주민에게 표시되는 USSD 결과 예시:

``` text
Well 102
Fluoride: HIGH
Bacteria: LOW
Avoid long-term drinking.
Lower-risk source: WELL 108, 1.4 km.
AI estimate.
```

## Running the Tests

전체 자동화 테스트는 다음 명령으로 실행합니다.

``` bash
pytest
```

단위 테스트만 실행:

``` bash
pytest tests/unit
```

통합 테스트만 실행:

``` bash
pytest tests/integration
```

Coverage 확인:

``` bash
pytest --cov=app --cov-report=term-missing
```

### Break down into end-to-end tests

End-to-End 테스트는 개별 함수가 아니라 실제 서비스의 전체 처리 흐름을
검증합니다.

중요한 테스트 시나리오는 다음과 같습니다.

-   정상 우물 조회
-   존재하지 않는 우물 ID
-   높은 불소 위험
-   높은 세균 위험
-   불소와 세균이 동시에 높은 경우
-   환경 특성 누락
-   비활성 또는 폐쇄 우물
-   주변에 위험도가 더 낮은 수원이 없는 경우
-   AI 모델 추론 실패
-   잘못된 USSD 메뉴 또는 우물 ID 입력
-   USSD Webhook 중복 요청
-   모델 버전 교체 및 롤백

End-to-End 흐름 예시는 다음과 같습니다.

``` text
USSD 요청: Well ID 102
        ↓
USSD Webhook
        ↓
우물 및 환경 특성 조회
        ↓
위험 예측 모델 추론
        ↓
Risk Policy
        ↓
추천 엔진
        ↓
USSD 응답 생성
```

서비스는 구조화된 안전 안내를 반환해야 하며, 현재 수원보다 위험도가
낮다고 판단할 근거가 없는 수원을 추천해서는 안 됩니다.

### And coding style tests

변경사항을 병합하기 전에 코드 품질 검사를 수행하는 것을 권장합니다.

권장 도구:

``` bash
ruff check .
ruff format --check .
```

정적 타입 검사를 사용하는 경우:

``` bash
mypy app
```

이 검사는 3인 팀이 작성한 코드의 포맷, import, 일반적인 Python 오류 및
타입 사용을 일관되게 유지하기 위한 것입니다.

## Deployment

백엔드는 PostgreSQL/PostGIS와 함께 컨테이너화된 FastAPI 애플리케이션으로
배포하는 것을 기본 구조로 합니다.

운영 배포 환경의 후보는 다음과 같습니다.

-   Google Cloud Run, AWS, Azure, Render, Railway 등의 컨테이너 플랫폼
-   PostGIS를 지원하는 Managed PostgreSQL
-   세션 Webhook을 지원하는 USSD Gateway 또는 이동통신사/통신 Aggregator
    연동
-   인증 정보를 위한 환경 변수 또는 Secret Manager
-   애플리케이션·예측 로그 중앙 관리

기본 배포 구조는 다음과 같습니다.

``` text
주민
   ↓ *USSD#
USSD Gateway / 이동통신망
   ↓ Session Webhook
FastAPI Backend
   ├── Risk Model Adapter
   ├── Risk Policy
   ├── Recommendation Engine
   └── Guidance Service
   ↓
PostgreSQL / PostGIS
```

AI 모델은 백엔드 비즈니스 로직과 별도로 버전 관리합니다. 새 모델은 기존
입력·출력 계약을 유지해야 하며, 이를 통해 USSD 또는 추천 인터페이스를
변경하지 않고 `fluoride_v1`을 새로운 모델 버전으로 교체할 수 있습니다.

실제 현장 파일럿 전에 탄자니아 USSD Short Code 접속 및 세션 전달,
데이터베이스 백업, 모델 롤백, 모니터링, 개인정보 보호 및 현장 검증
절차를 확인해야 합니다.

## Built With

-   [FastAPI](https://fastapi.tiangolo.com/) - 백엔드 API 프레임워크
-   [PostgreSQL](https://www.postgresql.org/) - 관계형 데이터베이스
-   [PostGIS](https://postgis.net/) - 공간 검색 및 주변 수원 탐색
-   [GeoPandas](https://geopandas.org/) - 공간 데이터 전처리 및 Feature
    통합
-   [scikit-learn](https://scikit-learn.org/) - 머신러닝 모델 개발 및
    추론
-   [Docker](https://www.docker.com/) - 재현 가능한 개발·배포 환경
-   USSD Gateway / 이동통신망 연동 - 주민 대상 세션형 메뉴 제공

## Contributing

본 프로젝트는 3인 팀이 기능 단위 태스크와 Pull Request를 이용해
개발합니다.

권장 개발 절차는 다음과 같습니다.

1.  태스크를 생성하거나 선택합니다.
2.  태스크의 입력, 출력, 의존성, 완료 조건을 정의합니다.
3.  짧게 유지되는 기능 브랜치를 생성합니다.
4.  기능과 테스트를 구현합니다.
5.  `develop` 브랜치로 Pull Request를 생성합니다.
6.  최소 한 명의 팀원에게 리뷰를 요청합니다.
7.  병합 전 통합 테스트를 실행합니다.
8.  안정적인 배포 버전은 `develop`에서 `main`으로 병합합니다.

브랜치 예시:

``` text
feature/well-api
feature/dummy-model
feature/recommendation-engine
feature/ussd-webhook
feature/model-adapter
fix/ussd-session-parser
```

`.env`, 인증 정보, 불필요한 개인 전화번호 또는 가입자 식별정보, 승인되지
않은 대용량 데이터셋 또는 모델 Artifact는 Git에 커밋하지 않습니다.

프로젝트 전용 기여 가이드가 추가되면 `CONTRIBUTING.md`를 참고합니다.

## Versioning

애플리케이션은 Semantic Versioning 방식으로 관리하고,
데이터셋·Feature·AI 모델은 각각 독립적으로 버전을 관리합니다.

예시:

``` text
Application: v0.1.0
Dataset: integrated_dataset_v2
Feature set: feature_set_v1
Fluoride model: fluoride_rf_v1
Bacterial model: bacterial_rule_v1
```

각 예측 결과에는 사용한 모델과 Feature 버전을 기록해야 합니다.

사용 가능한 애플리케이션 버전은 저장소의 tag를 통해 관리합니다.

## Authors
- A
- B
- C

## License

프로젝트 라이선스는 아직 확정되지 않았습니다.

외부 공개 전 적절한 라이선스를 선택하고 `LICENSE` 또는 `LICENSE.md`
파일을 추가한 뒤 이 섹션을 수정합니다.

## Acknowledgments

-   연구 및 모델 개발에 활용되는 공개 지질·토양·기후·수질 데이터 제공
    기관
-   프로젝트 데이터셋 구축에 참고되는 불소 및 지하수 관련 연구자와 공개
    연구 자료
-   향후 현장 검증에 참여할 지역사회, 수도 담당자 및 협력 기관
-   FastAPI, PostgreSQL/PostGIS, GeoPandas, scikit-learn 및 관련
    오픈소스 프로젝트 기여자
