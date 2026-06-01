"""도움말 HTML 본문 생성."""

from __future__ import annotations

from html import escape


def build_help_html(
    *,
    hotkey: str,
    active_hotkey: str | None,
    mouse_trigger_enabled: bool,
) -> str:
    configured = escape(hotkey)
    active = escape(active_hotkey) if active_hotkey else "등록되지 않음"
    mouse_line = (
        "사용 중 — 마우스 <b>가운데 버튼(휠 클릭)</b>으로도 팝업을 엽니다."
        if mouse_trigger_enabled
        else "사용 안 함 — 환경설정 → 호출 방식에서 켤 수 있습니다."
    )

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body {{ font-family: 'Segoe UI', Malgun Gothic, sans-serif; font-size: 10pt; line-height: 1.45; color: #222; }}
h1 {{ font-size: 14pt; margin: 0 0 12px 0; color: #1a5fb4; }}
h2 {{ font-size: 11pt; margin: 16px 0 6px 0; color: #333; border-bottom: 1px solid #ddd; padding-bottom: 4px; }}
ul {{ margin: 4px 0 8px 0; padding-left: 20px; }}
li {{ margin: 3px 0; }}
p {{ margin: 6px 0; }}
.note {{ background: #f5f8fc; border-left: 3px solid #4a90d9; padding: 8px 10px; margin: 8px 0; }}
kbd {{ background: #eee; border: 1px solid #ccc; border-radius: 3px; padding: 1px 5px; font-family: Consolas, monospace; }}
</style>
</head><body>
<h1>QuickPaste Manager 도움말</h1>
<p>자주 쓰는 <b>텍스트·이미지 상용구</b>를 저장하고, 전역 단축키로 팝업을 연 뒤
한 번의 클릭으로 붙여넣는 Windows용 유틸리티입니다.</p>

<h2>1. 팝업 열기</h2>
<ul>
<li><b>전역 단축키</b>: 설정 <kbd>{configured}</kbd> · 현재 등록: <b>{active}</b></li>
<li><b>트레이 아이콘</b> 우클릭 → 「팝업 열기」</li>
<li>{mouse_line}</li>
</ul>

<h2>2. 팝업에서 붙여넣기</h2>
<ul>
<li><b>Top 5</b>: 목록에 마우스를 올리면 오른쪽에 전체 내용이 보입니다. 항목을 <b>클릭</b>하면 붙여넣습니다.</li>
<li><b>카테고리</b>: 카테고리를 <b>클릭</b>하면 오른쪽에 상용구 목록이 열립니다. 항목 클릭 시 붙여넣습니다.</li>
<li><b>검색</b>: 상단 검색창에 키워드를 입력하면 제목·태그·본문에서 찾습니다.</li>
<li><b>이미지</b>: 미리보기를 클릭하면 원본 파일이 열립니다(팝업은 유지).</li>
</ul>
<div class="note">붙여넣기에 성공하면 팝업이 닫힙니다. 메모장 등 이미지를 지원하지 않는 프로그램에서는
경고만 표시되고 팝업은 열린 상태로 유지됩니다.</div>

<h2>3. 상용구 관리</h2>
<ul>
<li>트레이 → <b>상용구 관리</b> 또는 팝업 하단 「추가」「수정」「삭제」</li>
<li>카테고리·상용구 추가/수정/삭제, 휴지통 복구</li>
<li>클립보드·파일에서 이미지 상용구 추가</li>
</ul>

<h2>4. 데이터·설정</h2>
<ul>
<li><b>환경설정</b>: 단축키, 팝업 크기, 붙여넣기 지연, 자동 백업 주기, Windows 시작 시 실행 등</li>
<li><b>보내기 / 불러오기</b>: ZIP으로 상용구·설정 백업 및 복원</li>
<li>데이터 위치: <code>%APPDATA%\\QuickPasteManager</code> (DB, 설정, 이미지)</li>
</ul>

<h2>5. 문제 해결</h2>
<ul>
<li>단축키가 동작하지 않으면 다른 프로그램과 충돌할 수 있습니다. 환경설정에서 단축키를 바꿔 보세요.</li>
<li>한글이 깨지면 대상 프로그램이 ANSI만 받는 경우일 수 있습니다. 메모장 대신 Word 등을 사용해 보세요.</li>
<li>트레이 아이콘이 보이지 않으면 Windows 알림 영역(숨겨진 아이콘)을 확인하세요.</li>
</ul>
</body></html>"""
