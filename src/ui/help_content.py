"""도움말 HTML 본문 생성."""

from __future__ import annotations

from html import escape

from src.utils.config import DEFAULT_HOTKEY


def build_help_html(
    *,
    hotkey: str,
    active_hotkey: str | None,
) -> str:
    configured = escape(hotkey)
    active = escape(active_hotkey) if active_hotkey else "등록되지 않음"
    default_hotkey = escape(DEFAULT_HOTKEY)

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body {{ font-family: 'Segoe UI', Malgun Gothic, sans-serif; font-size: 10pt; line-height: 1.45; color: #222; }}
h1 {{ font-size: 14pt; margin: 0 0 12px 0; color: #1a5fb4; }}
h2 {{ font-size: 11pt; margin: 16px 0 6px 0; color: #333; border-bottom: 1px solid #ddd; padding-bottom: 4px; }}
h3 {{ font-size: 10pt; margin: 10px 0 4px 0; color: #444; }}
ul {{ margin: 4px 0 8px 0; padding-left: 20px; }}
li {{ margin: 3px 0; }}
p {{ margin: 6px 0; }}
.note {{ background: #f5f8fc; border-left: 3px solid #4a90d9; padding: 8px 10px; margin: 8px 0; }}
.warn {{ background: #fff8f0; border-left: 3px solid #e6a817; padding: 8px 10px; margin: 8px 0; }}
kbd {{ background: #eee; border: 1px solid #ccc; border-radius: 3px; padding: 1px 5px; font-family: Consolas, monospace; }}
code {{ background: #f4f4f4; padding: 1px 4px; border-radius: 2px; font-size: 9.5pt; }}
</style>
</head><body>
<h1>QuickPaste Manager 도움말</h1>
<p>자주 쓰는 <b>텍스트·이미지 상용구</b>를 저장하고, 전역 단축키로 팝업을 연 뒤
한 번의 클릭으로 붙여넣는 Windows용 유틸리티입니다. 프로그램은 <b>한 번에 하나</b>만
실행됩니다(이미 실행 중이면 기존 창이 활성화됩니다).</p>

<h2>1. 팝업 열기</h2>
<ul>
<li><b>전역 단축키</b>: 설정에 저장된 값 <kbd>{configured}</kbd>
· 현재 Windows에 등록된 단축키: <b>{active}</b>
(기본 설치값은 <kbd>{default_hotkey}</kbd>입니다.)</li>
<li><b>트레이 아이콘</b> 우클릭 → 「팝업 열기」</li>
</ul>
<div class="note">등록에 실패하면 <kbd>Ctrl+Alt+V</kbd> 등 <b>대체 단축키</b>로 자동 시도합니다.
환경설정 창이 열려 있는 동안에는 전역 단축키로 팝업이 열리지 않습니다.</div>

<h2>2. 팝업에서 붙여넣기</h2>
<ul>
<li><b>Top 5</b>: 자주 쓰는 상용구. 항목에 마우스를 올리면 오른쪽에 전체 내용이 보입니다.
<b>클릭</b>하면 대상 프로그램에 붙여넣습니다.</li>
<li><b>카테고리</b>: 카테고리를 <b>클릭</b>하면 오른쪽에 상용구 목록(플라이아웃)이 열립니다.
항목 클릭 시 붙여넣습니다.</li>
<li><b>검색</b>: 상단 검색창에 키워드를 입력하면 제목·태그·본문에서 찾습니다.</li>
<li><b>이미지 상용구</b>: 목록에 썸네일이 보입니다. 미리보기를 클릭하면 원본 파일이 열립니다(팝업은 유지).</li>
<li>제목 표시줄을 드래그해 팝업 위치를 옮길 수 있습니다.</li>
</ul>

<h3>팝업 닫힘 동작</h3>
<ul>
<li><b>붙여넣기 후 팝업 닫기</b>(환경설정): 기본값 <b>끔</b>.
끄면 붙여넣은 뒤에도 팝업이 남아 다른 창으로 이동해 연속 붙여넣기하기 쉽습니다.</li>
<li>위 옵션을 <b>켬</b>이면 붙여넣기 성공 시 팝업이 닫히고, 다른 창을 클릭해
포커스를 잃으면 팝업이 자동으로 닫힐 수 있습니다.</li>
</ul>

<h2>3. 상용구 관리</h2>
<ul>
<li>트레이 → <b>상용구 관리</b>, 또는 팝업 하단 「추가」「수정」「삭제」</li>
<li>카테고리·상용구 추가/수정/삭제, 휴지통 복구</li>
<li>클립보드·이미지 파일에서 <b>이미지 상용구</b> 추가</li>
</ul>

<h2>4. 환경설정</h2>
<p>트레이 → <b>환경설정</b>. 한 화면(스크롤)에서 항목을 바꾼 뒤 <b>저장</b>해야 반영됩니다.</p>

<h3>호출 · 트리거</h3>
<ul>
<li><b>단축키</b>: 창을 열면 <b>저장된 단축키가 그대로</b> 보입니다.
입력란을 <b>클릭</b>하거나 Tab으로 포커스를 줄 때만 입력 모드가 되며, 그때 키를 눌러
<b>2~3개 조합</b>(예: <kbd>Ctrl+Shift+Q</kbd>)을 만듭니다.</li>
<li><kbd>Del</kbd> / <kbd>Backspace</kbd>: 입력 중 조합 지움 · <kbd>Esc</kbd>: 취소 후 원래 값</li>
<li>변경 없이 다른 곳을 클릭하면 <b>원래 단축키로 되돌아갑니다</b>.</li>
<li>지금 프로그램이 쓰는 단축키와 <b>같은 조합</b>을 다시 넣어도 됩니다.
다른 프로그램이 이미 쓰는 조합이면 저장·확인 시 안내가 나옵니다.</li>
<li><b>Windows 시작 시 실행</b>: 기본값 <b>켬</b>(로그인 시 트레이에서 자동 실행).</li>
</ul>

<h3>붙여넣기</h3>
<ul>
<li><b>붙여넣기 후 팝업 닫기</b>: 기본값 <b>끔</b> (위 「2. 팝업」 참고).</li>
<li><b>붙여넣기 후 클립보드 복원</b>: 기본값 <b>켬</b> — 붙여넣기 전 클립보드 내용을 되돌립니다.</li>
<li><b>자동 붙여넣기 지연</b>: 기본 50 ms — 대상 프로그램이 느릴 때 늘려 보세요.</li>
</ul>

<h3>팝업</h3>
<ul>
<li><b>커서 위치 보정</b>: 기본 12 px — 팝업이 마우스 커서 근처에 뜨도록 세로 오프셋을 조절합니다.</li>
</ul>

<h3>데이터 · 백업</h3>
<ul>
<li><b>자동 백업 주기</b>: 기본 24시간 — 지정 간격으로 데이터 폴더에 백업 ZIP을 만듭니다.</li>
<li><b>보내기 / 불러오기</b>는 환경설정이 아니라 <b>트레이 메뉴</b>에서 합니다.
ZIP으로 상용구·설정·이미지를 백업하거나 복원합니다.</li>
</ul>

<h2>5. 데이터 위치</h2>
<p>사용자 데이터는 아래 폴더에 저장됩니다.</p>
<p><code>%APPDATA%\\QuickPasteManager</code> — DB, settings.json, 이미지, 백업, 로그 등</p>

<h2>6. 문제 해결</h2>
<ul>
<li><b>단축키가 동작하지 않음</b>: 다른 프로그램과 충돌할 수 있습니다.
환경설정에서 단축키를 바꾼 뒤 <b>저장</b>하세요. 저장값과 「현재 등록됨」 표시가
다르면 재시작 후 다시 확인해 보세요.</li>
<li><b>단축키를 바꿀 때</b>: 입력란을 클릭한 뒤에만 키를 누르세요. 창을 막 연 상태에서는
필드가 비워지지 않습니다.</li>
<li><b>한글이 깨짐</b>: 대상 프로그램이 ANSI만 받는 경우일 수 있습니다.
메모장 대신 Word 등 UTF-8을 지원하는 프로그램에서 시험해 보세요.</li>
<li><b>트레이 아이콘이 안 보임</b>: Windows 알림 영역(숨겨진 아이콘)을 확인하세요.</li>
<li><b>붙여넣기가 안 됨</b>: 환경설정에서 「자동 붙여넣기 지연」을 100~200 ms 정도로
늘려 보세요. 관리자 권한이 필요한 프로그램에는 붙여넣기가 제한될 수 있습니다.</li>
</ul>
<div class="warn">설치·업데이트 후에는 트레이에서 프로그램을 종료했다가 다시 실행하면
단축키와 시작 프로그램 설정이 안정적으로 적용됩니다.</div>
</body></html>"""
