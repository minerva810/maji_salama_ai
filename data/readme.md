Dataset:
- GLiM lithology
- iSDA soil
- groundwater fluoride samples



# Well Data
: 수원 자체의 ID·위치·유형
| Field         | Type   | Required | 설명                 | 현재 데이터            |
| ------------- | ------ | -------: | ------------------ | ----------------- |
| `well_id`     | string |        Y | 수원 고유 ID           | `sample_id`       |
| `site_name`   | string |        N | 수원/지역명             | `site_name`       |
| `source_type` | string |        Y | borehole, spring 등 | `source_type`     |
| `latitude`    | float  |        Y | WGS84 latitude     | `latitude`        |
| `longitude`   | float  |        Y | WGS84 longitude    | `longitude`       |
| `district`    | string |        N | District/Region    | `district_region` |
| `ward`        | string |        N | Ward/locality      | `ward_location`   |

### well schema example
```
{
  "well_id": "CB23-01",
  "site_name": "KIKILO",
  "source_type": "groundwater_borehole",
  "status" : "ACTIVE",
  "location": {
    "latitude": -4.54425,
    "longitude": 35.698017,
    "crs": "EPSG:4326"
  },
  "administrative_area": {
    "district": "Dodoma",
    "ward": "DODOMA-NORTH-SOUTH"
  }
}
```


# Environment Data
: 강우·토양·지질 등 모델 예측에 사용하는 외부 환경정보

### environmental schema example
```
{
  "climate": {
    "year": 2022,
    "season": "long_dry",
    "total_season_rain_mm": 8.983
  },

  "soil": {
    "ph": 6.675,
    "calcium_extractable": 635.742,
    "magnesium_extractable": 239.435,
    "organic_carbon": 3.08,
    "iron_extractable": 95.33
  },

  "geology": {
    "glim_id": "AFR7274",
    "lithology_code": "mt",
    "lithology_class": "metamorphic_rocks",
    "lithology_detail": "mt____"
  },

  "data_quality": {
    "soil_match_distance_km": 16.73,
    "lithology_match_method": "within_polygon",
    "lithology_match_distance_km": 0.0
  }
}
```

아래 칼럼들 보존. feature로 사용할지 AI 모델에서 결정.
soil_ph
soil_calcium_extractable
soil_magnesium_extractable
soil_carbon_organic
soil_iron_extractable

soil_source_latitude
soil_source_longitude
soil_match_distance_km


# Measured Water Quality Data (추후 구현)
: 실제 측정된 fluoride/pH/EC/TDS와 측정 메타데이터

# Model Input
: 위 데이터를 모델별 feature로 변환한 최종 inference contract

# Model Output
: 모든 모델이 공통적으로 반환해야 하는 prediction contract

example
```
{
  "schema_version": "1.0",
  "request_id": "req-001",

  "model": {
    "name": "fluoride-risk-model",
    "version": "1.0.0",
    "target": "fluoride"
  },

  "prediction": {
    "value": 2.31,
    "unit": "mg/L",
    "risk_level": "HIGH"
  },

  "confidence": {
    "score": 0.87
  },

  "warnings": []
}
```
target: "fluoride" or "bacterial_contamination"

# Risk Level
- LOW
- MEDIUM
- HIGH
- UNKNOWN 

### fluoride level (WHO guideline)
- pred_fruoride ≤ 1.5 mg/L → LOW
- 1.5 mg/L < pred_fruoride ≤ 3.0 mg/L → MEDIUM
- pred_fruoride> 3.0 mg/L → HIGH
- missing/invalid →  UNKNOWN

### bacterial level (WHO guideline)
- E. coli < 1 CFU/100 mL → LOW
- 1 ≤ E. coli ≤ 10 CFU/100 mL → MEDIUM
- E. coli > 10 CFU/100 mL → HIGH
- missing/invalid → UNKNOWN

| Fluoride | Bacteria    | Guide |
|      LOW | LOW         | 사용 가능하나 정기 검사 권고 |
|      LOW | MEDIUM/HIGH | 끓이기 또는 소독 |
|     HIGH | LOW         | 장기 음용 피하기, 대체 수원 또는 불소 제거 |
|     HIGH | HIGH        | 음용 피하기, 대체 수원 우선 |
|  UNKNOWN | UNKNOWN     | 안전 여부 판단 불가, 공식 검사 요청 |