# 샘플 Import 데이터

> v0.2.2 설치본에는 **포함되지 않습니다.** `dist\` 또는 `samples\`의 ZIP을 트레이 → 불러오기로 가져옵니다.

## 파일

| 파일 | 설명 |
|------|------|
| `HanbitSolutions_상용구샘플_200.zip` | 사무직 테스트용 상용구 (약 225건) |

**가상 회사:** 한빛솔루션즈 주식회사 (Hanbit Solutions)  
**포함:** 텍스트 상용구 + PNG 이미지 20종 (로고, 명함, 도장, 부서 배너 등)  
**카테고리 10개:** 고객응대, 이메일, 회의·일정, 보고·결재, 인사·총무, 계좌·연락처, 영문, 내부공지, IT·시스템, 기타

## 불러오기 방법

1. QuickPaste Manager 실행 (트레이)
2. 트레이 아이콘 우클릭 → **불러오기**
3. `HanbitSolutions_상용구샘플_200.zip` 선택
4. 완료 메시지 확인 후 **팝업** 또는 **상용구 관리**에서 확인

> 기존 DB에 같은 제목이 있으면 `제목 (2)` 형식으로 추가됩니다.  
> 빈 DB에서 테스트하려면 `%APPDATA%\QuickPasteManager` 백업 후 새로 설치하거나, 개발 모드에서 새 DB로 실행하세요.

## 재생성

```powershell
.\.venv\Scripts\python.exe scripts\generate_sample_import_zip.py
```
