# Maji Salama AI

Maji Salama AI is an AI-powered groundwater safety guidance system
designed for communities in Tanzania. It combines groundwater quality
measurements, geology, soil, elevation, rainfall, and other
environmental data to estimate fluoride and bacterial contamination
risks.

Residents access the service through a USSD short code such as `*123#`.
A session-based menu asks the user to enter a registered well ID such as
`102`. The backend then retrieves the well and environmental features,
calls the configured risk model, classifies the result, searches for a
lower-risk nearby water source when necessary, and returns concise
drinking-water guidance within the USSD session.

The MVP focuses on northern Tanzania, with future expansion to other
parts of Tanzania and the East African Rift Valley.

## Getting Started

This section explains how to set up the project locally for development
and testing.

The backend is designed so that the AI model can be improved or replaced
without changing the rest of the service. During early development, a
dummy model can be used to test the complete backend, recommendation,
and USSD flow before the final trained model is connected.

### Prerequisites

Install the following software:

-   Python 3.11 or later
-   Git
-   PostgreSQL
-   PostGIS
-   Docker and Docker Compose (recommended)
-   A Python virtual environment such as `venv` or Conda

Core Python packages include:

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

A USSD gateway or mobile-network/aggregator sandbox will be required for
end-to-end USSD testing. The provider and short-code provisioning
process may differ between development and the Tanzania pilot
deployment.

### Installing

Clone the repository:

``` bash
git clone <REPOSITORY_URL>
cd maji-salama-ai
```

Create and activate a virtual environment.

Using Conda:

``` bash
conda create -n maji-salama python=3.11
conda activate maji-salama
```

Or using `venv`:

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

Install the dependencies:

``` bash
pip install -r requirements.txt
```

Create the local environment file:

``` bash
cp .env.example .env
```

Windows PowerShell:

``` powershell
Copy-Item .env.example .env
```

Example development configuration:

``` env
APP_ENV=development
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/maji_salama

RISK_MODEL_TYPE=dummy

FLUORIDE_MODEL_PATH=model_artifacts/fluoride/v1/model.joblib
BACTERIAL_MODEL_PATH=model_artifacts/bacterial/v1/model.joblib

USSD_API_KEY=
USSD_WEBHOOK_SECRET=
```

Do not commit `.env`, API keys, USSD credentials, or other secrets.

Start PostgreSQL/PostGIS with Docker Compose:

``` bash
docker compose up -d db
```

Apply database migrations:

``` bash
alembic upgrade head
```

Load sample wells and environmental features:

``` bash
python scripts/seed_wells.py
python scripts/seed_features.py
```

Run the FastAPI application:

``` bash
uvicorn app.main:app --reload
```

Open the interactive API documentation:

``` text
http://localhost:8000/docs
```

A simple development demo can follow this flow:

``` text
*123#
    ↓
USSD menu
    ↓
Enter Well ID: 102
    ↓
Well lookup
    ↓
Dummy or trained risk model
    ↓
Fluoride / bacterial risk classification
    ↓
Lower-risk source recommendation
    ↓
Guidance response
```

Example API result:

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

### USSD Interaction Flow

The MVP uses a session-based USSD menu rather than free-form USSD
commands.

``` text
User dials: *123#
        ↓
1. Check water source
2. Help
3. Language
        ↓
User selects: 1
        ↓
Enter Well ID:
        ↓
User enters: 102
        ↓
Backend guidance request
        ↓
Well 102
Fluoride: HIGH
Bacteria: LOW
Avoid long-term drinking.
Lower-risk source: Well 108, 1.4 km.
```

The USSD gateway maintains the telecom session and forwards each user
selection to the FastAPI webhook. The core backend remains
channel-independent: a USSD adapter converts session input into a normal
guidance request and formats the result for the USSD screen.

Example resident-facing USSD result:

``` text
Well 102
Fluoride: HIGH
Bacteria: LOW
Avoid long-term drinking.
Lower-risk source: WELL 108, 1.4 km.
AI estimate.
```

## Running the Tests

Run all automated tests with:

``` bash
pytest
```

Run unit tests only:

``` bash
pytest tests/unit
```

Run integration tests only:

``` bash
pytest tests/integration
```

Run tests with coverage:

``` bash
pytest --cov=app --cov-report=term-missing
```

### Break down into end-to-end tests

End-to-end tests verify the complete service flow rather than a single
function.

Important scenarios include:

-   valid well lookup
-   unknown well ID
-   high fluoride risk
-   high bacterial risk
-   simultaneous fluoride and bacterial risks
-   missing environmental features
-   inactive or closed wells
-   no lower-risk source available nearby
-   AI model inference failure
-   invalid USSD menu or well-ID input
-   duplicate USSD webhook request
-   model version replacement or rollback

Example end-to-end flow:

``` text
USSD request: Well ID 102
        ↓
USSD webhook
        ↓
Well and feature lookup
        ↓
Risk model inference
        ↓
Risk policy
        ↓
Recommendation engine
        ↓
USSD response generation
```

The expected result is that the service returns safe, structured
guidance and does not recommend a source that is not demonstrably
lower-risk.

### And coding style tests

Code-quality checks should be run before merging changes.

Recommended tools include:

``` bash
ruff check .
ruff format --check .
```

If static type checking is enabled:

``` bash
mypy app
```

These checks are intended to keep formatting, imports, common Python
errors, and type usage consistent across the three-person development
team.

## Deployment

The backend is intended to run as a containerized FastAPI application
with PostgreSQL/PostGIS.

A production-oriented deployment can use:

-   Google Cloud Run, AWS, Azure, Render, Railway, or another container
    platform
-   Managed PostgreSQL with PostGIS support
-   A USSD gateway or mobile-network/aggregator integration supporting
    session webhooks
-   Environment variables or a secret manager for credentials
-   Centralized application and prediction logging

The basic deployment architecture is:

``` text
Resident
   ↓ *USSD#
USSD Gateway / Mobile Network
   ↓ Session Webhook
FastAPI Backend
   ├── Risk Model Adapter
   ├── Risk Policy
   ├── Recommendation Engine
   └── Guidance Service
   ↓
PostgreSQL / PostGIS
```

AI models are versioned separately from backend business logic. A new
model should implement the same input/output contract so that the
service can replace `fluoride_v1` with a later model without changing
the USSD or recommendation interfaces.

Before a production pilot, the team should verify USSD short-code access
and session delivery in Tanzania, database backups, model rollback,
monitoring, data privacy, and field-validation procedures.

## Built With

-   [FastAPI](https://fastapi.tiangolo.com/) - Backend API framework
-   [PostgreSQL](https://www.postgresql.org/) - Relational database
-   [PostGIS](https://postgis.net/) - Spatial queries and nearby
    water-source search
-   [GeoPandas](https://geopandas.org/) - Geospatial preprocessing and
    feature integration
-   [scikit-learn](https://scikit-learn.org/) - Machine-learning model
    development and inference
-   [Docker](https://www.docker.com/) - Reproducible development and
    deployment environment
-   USSD Gateway / Mobile Network Integration - Session-based menu
    access for residents

## Contributing

The project is developed by a three-person team using feature-based
tasks and pull requests.

Recommended workflow:

1.  Create or select a task.
2.  Define its input, output, dependencies, and completion criteria.
3.  Create a short-lived feature branch.
4.  Implement the feature and tests.
5.  Open a pull request to `develop`.
6.  Request review from at least one teammate.
7.  Run integration tests before merging.
8.  Merge stable releases from `develop` into `main`.

Example branches:

``` text
feature/well-api
feature/dummy-model
feature/recommendation-engine
feature/ussd-webhook
feature/model-adapter
fix/ussd-session-parser
```

Never commit `.env` files, credentials, unnecessary personal phone
numbers or subscriber identifiers, or unapproved large datasets/model
artifacts.

Please see `CONTRIBUTING.md` when a project-specific contribution guide
is added.

## Versioning

The project uses semantic-style application versioning together with
independent dataset, feature, and model versions.

Examples:

``` text
Application: v0.1.0
Dataset: integrated_dataset_v2
Feature set: feature_set_v1
Fluoride model: fluoride_rf_v1
Bacterial model: bacterial_rule_v1
```

Each prediction should record the model and feature versions that
produced it.

For available application releases, see the repository tags.

## Authors

Maji Salama AI is developed by a three-person project team.

-   **Team Member 1** - Data integration, AI modelling, and model
    interface
-   **Team Member 2** - Backend, database, and recommendation engine
-   **Team Member 3** - USSD integration, service validation, and
    administrative interface

Replace the placeholders above with team members' names and GitHub
profiles before public release.

## License

The project license has not yet been finalized.

Before public release, add the selected license and update this section
to reference the corresponding `LICENSE` or `LICENSE.md` file.

## Acknowledgments

-   Open geological, soil, climate, and water-quality data providers
    used for research and model development
-   Researchers whose published fluoride and groundwater studies support
    the project dataset
-   Communities, water officers, and field partners who may support
    future validation
-   Open-source contributors to FastAPI, PostgreSQL/PostGIS, GeoPandas,
    scikit-learn, and related tools


## folder structure
maji-salama-ai/
│
├── app/                            # 백엔드 애플리케이션
│   ├── api/                        # REST API 엔드포인트
│   │   ├── wells.py                # 우물 조회/등록
│   │   ├── predictions.py          # 수질 위험 예측 API
│   │   └── guidance.py             # 안전 수원/행동 권고 API
│   │
│   ├── schemas/                    # API용 Pydantic 입출력 모델
│   │   ├── well.py
│   │   ├── environment.py
│   │   ├── water_quality.py
│   │   ├── model_input.py
│   │   ├── model_output.py
│   │   └── guidance.py   
│   │
│   ├── services/                   # 핵심 비즈니스 로직
│   │   ├── prediction_service.py   # AI 모델 호출 및 결과 처리
│   │   ├── risk_service.py         # LOW/MEDIUM/HIGH 위험도 판정
│   │   └── guidance_service.py     # 행동/안전 수원 추천
│   │
│   ├── ml/                         # 백엔드 ↔ AI 모델 연결 계층
│   │   ├── model_adapter.py        # 공통 모델 인터페이스
│   │   └── model_loader.py         # 모델 artifact 로딩
│   │
│   ├── db/                         # PostgreSQL/PostGIS 연결 및 DB 모델
│   │
│   ├── ussd/                       # USSD 요청/세션/응답 처리
│   │   ├── handler.py
│   │   └── session.py
│   │
│   ├── templates/                  # 사용자 안내 메시지
│   │   ├── en/
│   │   └── sw/                     # Swahili
│   │
│   ├── core/                       # 환경설정, 로깅, 공통 예외
│   │
│   └── main.py                     # FastAPI 실행 진입점
│
├── models/                         # AI 모델 개발 영역
│   ├── training/                   # 모델 학습 코드
│   └── evaluation/                 # 모델 평가 코드
│
├── model_artifacts/                # 학습 완료된 배포용 모델 패키지
│   ├── fluoride/
│   │   └── v1/
│   │       ├── model.joblib
│   │       ├── inference.py
│   │       ├── feature_schema.json
│   │       ├── metadata.json
│   │       ├── sample_input.json
│   │       ├── sample_output.json
│   │       └── evaluation.json
│   │
│   └── bacterial/
│       └── v1/
│
├── schemas/                        # 시스템 전체의 공식 데이터 계약(JSON Schema)
│   ├── well.schema.json
│   ├── environment.schema.json
│   ├── water_quality.schema.json
│   ├── model_input.schema.json
│   └── model_output.schema.json
│
├── data/                           # 모델 개발용 데이터
│   ├── raw/                        # 원본 데이터 (수정 금지)
│   ├── interim/                    # 중간 전처리 결과
│   ├── processed/                  # 최종 학습용 데이터
│   ├── sample/                     # 테스트/예제용 소규모 데이터
│   └── README.md                   # 데이터 출처 및 컬럼 설명
│
├── scripts/                        # 데이터 처리/모델 실행 등 보조 스크립트
│
├── tests/
│   ├── unit/                       # 함수/서비스 단위 테스트
│   ├── integration/                # DB·모델·API 연결 테스트
│   └── end_to_end/                 # USSD → 예측 → 응답 전체 테스트
│
├── notebooks/                      # EDA 및 모델 실험 노트북
│
├── docs/
│   ├── architecture/               # 시스템 아키텍처 문서
│   └── contracts/                  # AI ↔ Backend 인터페이스 설명
│
├── alembic/                        # DB migration
│
├── README.md                       # 프로젝트 소개 (EN)
├── README_KO.md                    # 프로젝트 소개 (KO)
├── PROJECT_STRUCTURE.md            # 폴더 구조/개발 규칙
├── CONTRIBUTING.md                 # 팀 협업 규칙
├── requirements.txt                # Python dependencies
├── .env.example                    # 환경변수 예시
├── .gitignore
├── Dockerfile
└── docker-compose.yml
