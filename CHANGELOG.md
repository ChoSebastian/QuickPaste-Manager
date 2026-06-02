# Changelog

## [0.2.3] — 2026-05-31 (프로젝트 마감)

**QuickPaste Manager v0.2.3** 으로 **1차 개발을 마감**합니다. 이후 기능 업데이트 시 **메인(주) 버전 번호**를 올립니다.

### 배포

- 설치: [QuickPasteManager-Setup-0.2.3.exe](https://github.com/ChoSebastian/QuickPaste-Manager/releases/download/v0.2.3/QuickPasteManager-Setup-0.2.3.exe)
- 포터블: [QuickPasteManager-0.2.3-portable.zip](https://github.com/ChoSebastian/QuickPaste-Manager/releases/download/v0.2.3/QuickPasteManager-0.2.3-portable.zip)
- 샘플 Import: [HanbitSolutions_상용구샘플_200.zip](https://github.com/ChoSebastian/QuickPaste-Manager/releases/download/v0.2.3/HanbitSolutions_%EC%83%81%EC%9A%A9%EA%B5%AC%EC%83%98%ED%94%8C_200.zip) (설치본 미포함)

### 제품

- 카테고리 목록 우측 상세 패널, 목록은 ×로만 닫기(마우스 이탈 시 유지)
- 붙여넣기 후 닫기 OFF 시 플라이아웃·상세 유지
- 팝업 유지 모드: 다중 창 연속 붙여넣기(HWND 커서 추적)
- Win+V 클립보드 히스토리 제외 (`ExcludeClipboardContentFromMonitorProcessing`)

### 문서

- v4 문서 세트 (`docs/*_v4.md`)

### 마감 시점 미포함 (후속 검토)

- Authenticode 코드 서명 (Smart App Control)
- 마우스 휠/가운데 버튼 트리거 연동
- 팝업 크기 환경설정 UI

---

## [0.2.2] — 2026-06-01 (마감)

**QuickPaste Manager v0.2.2** 를 본 저장소의 **안정 마감 릴리스**로 확정합니다.

### 배포

- 설치: [QuickPasteManager-Setup-0.2.2.exe](https://github.com/ChoSebastian/QuickPaste-Manager/releases/download/v0.2.2/QuickPasteManager-Setup-0.2.2.exe)
- 포터블 ZIP, 샘플 Import ZIP: [Releases v0.2.2](https://github.com/ChoSebastian/QuickPaste-Manager/releases/tag/v0.2.2)

### 포함 기능

- 전역 단축키 (기본 `Ctrl+Shift+Q`), 팝업·Top5·카테고리·검색
- 텍스트·이미지 상용구, Import/Export ZIP, 자동 백업
- 환경설정(단축키 캡처), 단일 인스턴스, 도움말
- PyInstaller + Inno Setup 설치 패키지

### v0.2.2 정리

- 설치본에 테스트 상용구 미포함 (샘플 ZIP 별도 제공)
- 빌드 시 `dist` 정리·DB 번들 검증
- v3 문서 세트, `AGENTS.md` / Cursor 착수본

### 마감 시점 미포함 (후속 검토)

- Authenticode 코드 서명 (Smart App Control 대응)
- 마우스 휠/가운데 버튼 트리거 연동
- 팝업 크기 환경설정 UI

---

## [0.2.0] — 2026-06-01

- v3 문서, 단축키 UX, 환경설정 개편, 이미지 상용구·팝업 UX

## [0.1.0] — 초기

- 프로젝트 스캐폴드, 팝업·관리·핫키·붙여넣기 기본 구현
