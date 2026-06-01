"""사무직 테스트용 Import ZIP 샘플 생성 (~200건, 텍스트+이미지)."""

from __future__ import annotations

import json
import zipfile
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "samples" / "HanbitSolutions_상용구샘플_200.zip"

COMPANY = "한빛솔루션즈 주식회사"
COMPANY_EN = "Hanbit Solutions Co., Ltd."
ADDR = "서울특별시 강남구 테헤란로 152, 한빛타워 12층 (06236)"
TEL = "02-555-0198"
FAX = "02-555-0199"
EMAIL = "contact@hanbitsol.co.kr"
SUPPORT = "support@hanbitsol.co.kr"
CEO = "김서준"
TAX_ID = "123-45-67890"
BANK = "국민은행 123456-78-901234 (예금주: 한빛솔루션즈)"

CATEGORIES = [
    {"name": "고객응대", "sort_order": 0, "color": "#50C878"},
    {"name": "이메일", "sort_order": 1, "color": "#4A90D9"},
    {"name": "회의·일정", "sort_order": 2, "color": "#F5A623"},
    {"name": "보고·결재", "sort_order": 3, "color": "#BD10E0"},
    {"name": "인사·총무", "sort_order": 4, "color": "#E94B3C"},
    {"name": "계좌·연락처", "sort_order": 5, "color": "#7B68EE"},
    {"name": "영문", "sort_order": 6, "color": "#2ECC71"},
    {"name": "내부공지", "sort_order": 7, "color": "#95A5A6"},
    {"name": "IT·시스템", "sort_order": 8, "color": "#34495E"},
    {"name": "기타", "sort_order": 9, "color": "#9B9B9B"},
]

MANIFEST = {
    "version": 1,
    "exported_at": "2026-05-31T12:00:00",
    "app": "QuickPaste Manager",
    "description": "한빛솔루션즈 가상 사무 샘플 데이터",
}


def _font(size: int = 18):
    for name in ("malgun.ttf", "Malgun.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _make_image(
    name: str,
    size: tuple[int, int],
    bg: tuple[int, int, int],
    lines: list[str],
) -> tuple[str, bytes]:
    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)
    font = _font(16 if size[0] < 400 else 22)
    y = 20
    for line in lines:
        draw.text((20, y), line, fill=(255, 255, 255), font=font)
        y += 28 if size[0] < 400 else 32
    buf = BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()
    asset_name = f"{name}.png"
    return f"assets/{asset_name}", data


def _build_image_assets() -> dict[str, bytes]:
    assets: dict[str, bytes] = {}
    specs = [
        (
            "logo_hanbit",
            (320, 120),
            (26, 95, 180),
            [COMPANY, "Hanbit Solutions"],
        ),
        (
            "email_banner",
            (600, 100),
            (40, 50, 70),
            [COMPANY, f"T {TEL} | {EMAIL}"],
        ),
        (
            "bizcard_front",
            (400, 240),
            (30, 30, 30),
            [COMPANY, "영업1팀 박지민 과장", TEL, EMAIL],
        ),
        (
            "stamp_approved",
            (160, 160),
            (180, 40, 40),
            ["승인", "한빛솔루션즈"],
        ),
        (
            "stamp_received",
            (160, 160),
            (40, 90, 160),
            ["접수", "총무팀"],
        ),
        (
            "qr_payment",
            (200, 200),
            (50, 50, 50),
            ["결제 QR", "(샘플)"],
        ),
        (
            "dept_hr",
            (180, 80),
            (230, 126, 34),
            ["인사팀", "내선 201"],
        ),
        (
            "dept_it",
            (180, 80),
            (52, 73, 94),
            ["IT헬프데스크", "내선 999"],
        ),
        (
            "dept_sales",
            (180, 80),
            (39, 174, 96),
            ["영업본부", "내선 301"],
        ),
        (
            "holiday_notice",
            (480, 160),
            (142, 68, 173),
            ["휴무 안내", "양력 설 연휴"],
        ),
        (
            "warranty_badge",
            (200, 100),
            (41, 128, 185),
            ["품질보증", "1년 무상"],
        ),
        (
            "shipping_box",
            (240, 140),
            (127, 140, 141),
            ["택배 발송", "CJ대한통운"],
        ),
        (
            "meeting_room_a",
            (280, 100),
            (192, 57, 43),
            ["회의실 A", "12층 동쪽"],
        ),
        (
            "meeting_room_b",
            (280, 100),
            (211, 84, 0),
            ["회의실 B", "12층 서쪽"],
        ),
        (
            "footer_confidential",
            (500, 60),
            (100, 100, 100),
            ["대외비", "무단 배포 금지"],
        ),
        (
            "sign_office",
            (300, 80),
            (0, 102, 153),
            ["본사 안내", ADDR[:20] + "..."],
        ),
        (
            "icon_phone",
            (96, 96),
            (46, 204, 113),
            ["전화", TEL[-4:]],
        ),
        (
            "icon_email",
            (96, 96),
            (52, 152, 219),
            ["메일", "contact"],
        ),
        (
            "training_cert",
            (360, 200),
            (155, 89, 182),
            ["교육 이수", "정보보안 기본"],
        ),
        (
            "promo_q2",
            (400, 150),
            (230, 76, 60),
            ["2분기 프로모션", "B2B 할인"],
        ),
    ]
    for spec in specs:
        path, data = _make_image(*spec)
        assets[path] = data
    return assets


def _text_snippets() -> list[dict]:
    rows: list[dict] = []

    def add(
        cat: str,
        title: str,
        body: str,
        tags: str = "",
        pinned: bool = False,
    ) -> None:
        rows.append(
            {
                "category_name": cat,
                "title": title,
                "content_type": "text",
                "body_text": body,
                "tags": tags,
                "pinned": pinned,
                "asset_file": None,
            }
        )

    def add_img(
        cat: str,
        title: str,
        asset_path: str,
        tags: str = "",
        pinned: bool = False,
    ) -> None:
        rows.append(
            {
                "category_name": cat,
                "title": title,
                "content_type": "image",
                "body_text": None,
                "tags": tags,
                "pinned": pinned,
                "asset_file": asset_path,
            }
        )

    # --- 고객응대 (35) ---
    greetings = [
        ("인사-오전", "안녕하세요, {c}입니다. 무엇을 도와드릴까요?", "인사,오전"),
        ("인사-오후", "안녕하세요, 좋은 오후입니다. {c} 고객지원팀입니다.", "인사,오후"),
        ("인사-저녁", "안녕하세요, 늦은 시간에도 문의 주셔서 감사합니다.", "인사,저녁"),
        ("첫응대-확인", "말씀해 주신 내용 확인 후 순차적으로 안내드리겠습니다. 잠시만 기다려 주세요.", "응대"),
        ("대기-1분", "현재 확인 중이며 약 1분 정도 소요될 예정입니다. 양해 부탁드립니다.", "대기"),
        ("대기-5분", "담당 부서 확인 중으로 5분 내 회신 드리겠습니다.", "대기"),
        ("감사-문의", "소중한 문의 감사합니다. 추가로 필요하신 사항 있으시면 편히 말씀해 주세요.", "감사"),
        ("감사-구매", "이용해 주셔서 진심으로 감사드립니다.", "감사,구매"),
    ]
    for title, tmpl, tags in greetings:
        add("고객응대", title, tmpl.format(c=COMPANY), tags, pinned=title.startswith("인사-오전"))

    apologies = [
        ("사과-지연", "불편을 드려 대단히 죄송합니다. 지연된 건은 최우선으로 처리하겠습니다.", "사과,지연"),
        ("사과-오류", "안내 오류로 혼선을 드려 죄송합니다. 정확한 내용으로 다시 안내드리겠습니다.", "사과"),
        ("사과-품질", "제품 품질 이슈로 불편을 끼쳐 드려 진심으로 사과드립니다.", "사과,품질"),
        ("사과-통화끊김", "통화 연결이 끊겨 죄송합니다. 이어서 도와드리겠습니다.", "사과,통화"),
    ]
    for title, body, tags in apologies:
        add("고객응대", title, body, tags)

    faqs = [
        ("FAQ-영업시간", f"평일 09:00~18:00 운영입니다. 점심 12:00~13:00. 토·일·공휴일 휴무.\n대표번호: {TEL}", "FAQ,시간"),
        ("FAQ-배송", "주문 후 1~3영업일 내 출고, 수도권 기준 1~2일 추가 소요됩니다.", "FAQ,배송"),
        ("FAQ-교환", "수령 후 7일 이내 미개봉·미사용 시 교환 가능합니다. 고객센터로 접수해 주세요.", "FAQ,교환"),
        ("FAQ-환불", "환불은 결제 취소 후 3~5영업일 내 카드사 정책에 따라 입금됩니다.", "FAQ,환불"),
        ("FAQ-세금계산서", f"사업자등록번호 {TAX_ID} 기준으로 발행 가능합니다. {EMAIL} 로 요청 주세요.", "FAQ,세금"),
        ("FAQ-견적", "견적 요청은 제품명·수량·납기를 기재해 메일 주시면 1영업일 내 회신합니다.", "FAQ,견적"),
        ("FAQ-데모", "온라인 데모는 영업일 기준 2일 전 예약 필수입니다.", "FAQ,데모"),
        ("FAQ-계약", "표준 계약서 제공 후 법무 검토 3~5영업일 소요됩니다.", "FAQ,계약"),
    ]
    for title, body, tags in faqs:
        add("고객응대", title, body, tags)

    closes = [
        ("종료-해결", "문의하신 건 처리 완료되었습니다. 좋은 하루 보내세요.", "종료"),
        ("종료-추가문의", "다른 문의 사항 없으시면 통화 종료하겠습니다. 감사합니다.", "종료"),
        ("종료-콜백", "확인 후 {TEL} 로 회신 드리겠습니다. 연락 가능한 시간 알려주시면 감사하겠습니다.", "종료,콜백"),
        ("에스컬레이션", "전문 담당자 연결을 위해 2선으로 이관하겠습니다. 잠시만 기다려 주세요.", "이관"),
        ("만족도-요청", "서비스 개선을 위해 간단한 만족도 설문 링크를 문자로 보내드려도 될까요?", "만족도"),
    ]
    for title, body, tags in closes:
        add("고객응대", title, body.replace("{TEL}", TEL), tags)

    for i in range(1, 11):
        add(
            "고객응대",
            f"시나리오-클레임{i:02d}",
            f"[클레임 {i:03d}] 고객님 말씀 충분히 이해했습니다. "
            f"접수번호 HB-2026-{i:04d} 로 등록했으며, 24시간 내 1차 회신 드리겠습니다.",
            "클레임,시나리오",
        )

    # --- 이메일 (35) ---
    add(
        "이메일",
        "메일-서명(전체)",
        f"{COMPANY}\n영업지원팀 | 박지민 과장\nTel {TEL} | Fax {FAX}\n{EMAIL}\n{ADDR}",
        "서명",
        pinned=True,
    )
    subjects = [
        ("메일-제목-견적요청", "[한빛솔루션즈] 견적 요청드립니다", "제목,견적"),
        ("메일-제목-회신", "RE: [한빛솔루션즈] 문의 주신 건 회신드립니다", "제목,회신"),
        ("메일-제목-납품", "[한빛솔루션즈] 납품 일정 안내", "제목,납품"),
        ("메일-제목-회의", "[한빛솔루션즈] 미팅 일정 협의 요청", "제목,회의"),
        ("메일-제목-자료", "[한빛솔루션즈] 요청 자료 송부", "제목,자료"),
    ]
    for title, subj, tags in subjects:
        add("이메일", title, subj, tags)

    bodies = [
        (
            "메일-본문-첫인사",
            "안녕하세요.\n\n{company} {name}입니다.\n바쁘신 중에도 메일 주셔서 감사합니다.\n\n",
        ),
        (
            "메일-본문-견적송부",
            "요청하신 견적서를 첨부와 같이 송부드립니다.\n검토 후 문의 사항 있으시면 연락 부탁드립니다.\n\n",
        ),
        (
            "메일-본문-납기안내",
            "주문하신 품목은 6월 15일(월) 출고 예정이며, 수령지에 따라 1~2일 추가 소요됩니다.\n\n",
        ),
        (
            "메일-본문-미팅요청",
            "다음 주 화·수 중 14:00~17:00 사이 미팅 가능 여부 회신 부탁드립니다.\n장소: 본사 12층 회의실 A\n\n",
        ),
        (
            "메일-본문-자료요청",
            "아래 항목 확인을 위해 사업자등록증·담당자 명함 스캔본을 회신 부탁드립니다.\n\n",
        ),
    ]
    names = ["박지민", "이수현", "최도윤", "한예진", "정민호"]
    for idx, (title, tmpl) in enumerate(bodies):
        add(
            "이메일",
            title,
            tmpl.format(company=COMPANY, name=names[idx % len(names)]),
            "본문",
        )

    for i in range(1, 21):
        add(
            "이메일",
            f"메일-템플릿-{i:02d}",
            f"안녕하세요, {COMPANY}입니다.\n\n"
            f"메일 템플릿 #{i} — 프로젝트 HB-EML-{2026000 + i} 관련 "
            f"진행 상황을 공유드립니다. 첨부 참고 부탁드리며, "
            f"회신 기한은 영업일 기준 D+{i % 5 + 1} 입니다.\n\n"
            f"감사합니다.\n{names[i % len(names)]} 드림",
            "템플릿,자동",
        )

    add_img("이메일", "이미지-메일배너", "assets/email_banner.png", "이미지,서명")
    add_img("이메일", "이미지-회사로고", "assets/logo_hanbit.png", "이미지,로고", pinned=True)

    # --- 회의·일정 (25) ---
    add(
        "회의·일정",
        "회의-초대-기본",
        f"[회의 초대] {COMPANY}\n일시: 2026-06-10(화) 14:00~15:00\n장소: 12층 회의실 A / Zoom 병행\n"
        f"안건: 분기 실적 리뷰\n참석: 영업·마케팅·재무\n회신: {EMAIL}",
        "회의,초대",
        pinned=True,
    )
    for i in range(1, 16):
        add(
            "회의·일정",
            f"일정-확정-{i:02d}",
            f"6월 {10 + (i % 20)}일 {(9 + i % 8):02d}:00 미팅 확정되었습니다. "
            f"참석자: 팀{i % 5 + 1} · 장소: 회의실 {'AB'[i % 2]}",
            "일정,확정",
        )
    reminders = [
        ("리마인더-1일전", "내일 예정된 미팅 리마인드입니다. 자료 준비 부탁드립니다.", "리마인der"),
        ("리마인더-1시간전", "1시간 후 회의 시작입니다. 12층 A회의실입니다.", "리마인der"),
        ("일정-변경", "일정 변경 안내: 아래 일시로 변경되었습니다. 참석 가능 여부 회신 부탁드립니다.", "일정,변경"),
        ("일정-취소", "금번 회의는 내부 사정으로 취소되었습니다. 추후 재조율하겠습니다.", "일정,취소"),
        ("화상-링크", "Zoom: https://zoom.us/j/1234567890 (비밀번호: hanbit2026)", "화상,링크"),
        ("회의록-헤더", "■ 회의록\n일시:\n참석:\n작성:\n\n【안건】\n1.\n2.\n\n【결정사항】\n-\n\n【Action Item】\n| 담당 | 내용 | 기한 |\n", "회의록"),
        ("Action-담당요청", "@담당자 님, 위 건 6/20까지 진행 현황 공유 부탁드립니다.", "Action"),
    ]
    for title, body, tags in reminders:
        add("회의·일정", title, body, tags)
    add_img("회의·일정", "이미지-회의실A", "assets/meeting_room_a.png", "회의실")
    add_img("회의·일정", "이미지-회의실B", "assets/meeting_room_b.png", "회의실")

    # --- 보고·결재 (25) ---
    add(
        "보고·결재",
        "보고-주간헤더",
        "【주간 업무 보고】\n보고자:\n보고 기간: 2026.06.02 ~ 06.06\n\n■ 금주 실적\n■ 이슈\n■ 차주 계획\n",
        "보고,주간",
        pinned=True,
    )
    for i in range(1, 18):
        add(
            "보고·결재",
            f"보고-항목-{i:02d}",
            f"{i}. [완료] 고객사 HB-CL-{100 + i} 계약 갱신 협의\n"
            f"   - 진행률: {min(100, 60 + i * 2)}%\n"
            f"   - 비고: 특이사항 없음",
            "보고,항목",
        )
    approvals = [
        ("결재-상신", "결재 상신드립니다. 검토 후 승인 부탁드립니다.", "결재"),
        ("결재-승인요청", "예산 500만 원 집행 건입니다. 첨부 견적 참고 바랍니다.", "결재,예산"),
        ("결재-반려사유", "반려 사유: 증빙 서류 미첨부. 보완 후 재상신 부탁드립니다.", "결재,반려"),
        ("결재-대결", "부재 중 대결 처리 요청드립니다. 6/10~6/12 김서준 대표.", "결재,대결"),
        ("보고-긴급", "【긴급】 고객 이슈 발생 — 즉시 공유 및 대응 방안 협의 요청", "긴급"),
    ]
    for title, body, tags in approvals:
        add("보고·결재", title, body, tags)
    add_img("보고·결재", "이미지-승인도장", "assets/stamp_approved.png", "결재,이미지")
    add_img("보고·결재", "이미지-접수도장", "assets/stamp_received.png", "결재,이미지")

    # --- 인사·총무 (20) ---
    hr = [
        ("인사-입사환영", f"{COMPANY}에 합류하신 것을 환영합니다. 인사팀 오은지입니다.", "인사,입사"),
        ("인사-퇴사인수", "퇴사 예정자 업무 인수인계 체크리스트를 공유드립니다.", "인사,퇴사"),
        ("인사-연차신청", "연차 신청은 그룹웨어 > 근태 > 연차 메뉴에서 신청해 주세요.", "연차"),
        ("인사-경조사", "경조사 안내: 화환·조의금 기준은 총무 규정 제4조를 참고해 주세요.", "경조"),
        ("총무-주차", "방문 차량은 1층 안내 데스크에서 주차권 수령 후 B2 이용.", "총무,주차"),
        ("총무-명함", "명함 신청: 수량·직함·영문 표기 확인 후 총무팀 메일 접수.", "명함"),
        ("총무-비품", "사무용품 요청: 매주 화요일 일괄 발주. 긴급 시 내선 205.", "비품"),
        ("총무-출장", "출장 신청서·교통비 정산 양식은 사내 포털 > 양식함.", "출장"),
    ]
    for title, body, tags in hr:
        add("인사·총무", title, body, tags)
    for i in range(1, 11):
        add(
            "인사·총무",
            f"공지-사내{i:02d}",
            f"[사내 공지 #{i}] 6월 {i}일부터 점심시간 음악 방송이 변경됩니다. "
            f"문의: 총무팀 내선 201",
            "공지",
        )
    add_img("인사·총무", "이미지-인사팀", "assets/dept_hr.png", "부서")

    # --- 계좌·연락처 (20) ---
    add(
        "계좌·연락처",
        "연락처-회사표준",
        f"{COMPANY}\n대표 {CEO}\n{TEL} / {FAX}\n{EMAIL}\n{ADDR}",
        "연락처",
        pinned=True,
    )
    add("계좌·연락처", "계좌-입금안내", f"입금 계좌: {BANK}\n※ 입금자명에 회사명 기재 부탁드립니다.", "계좌", pinned=True)
    contacts = [
        ("담당-영업", "영업1팀 박지민 과장 | 010-3100-4521 | pjm@hanbitsol.co.kr", "담당,영업"),
        ("담당-기술", "기술지원 최도윤 대리 | 010-3100-4522 | cdy@hanbitsol.co.kr", "담당,기술"),
        ("담당-회계", "회계팀 이수현 사원 | 010-3100-4523 | lsh@hanbitsol.co.kr", "담당,회계"),
        ("담당-구매", "구매팀 한예진 주임 | 010-3100-4524 | hyj@hanbitsol.co.kr", "담당,구매"),
        ("담당-법무", "법무 정민호 변호사(외부) | legal@partner-law.co.kr", "담당,법무"),
    ]
    for title, body, tags in contacts:
        add("계좌·연락처", title, body, tags)
    for i in range(1, 13):
        add(
            "계좌·연락처",
            f"거래처-{i:02d}",
            f"거래처명: (가)테스트상사{i:02d}\n담당: 홍길동\n"
            f"Tel 02-555-{1000 + i}\n사업자번호 100-11-{10000 + i}",
            "거래처",
        )
    add_img("계좌·연락처", "이미지-명함샘플", "assets/bizcard_front.png", "명함")
    add_img("계좌·연락처", "이미지-전화아이콘", "assets/icon_phone.png", "아이콘")
    add_img("계좌·연락처", "이미지-메일아이콘", "assets/icon_email.png", "아이콘")

    # --- 영문 (20) ---
    en = [
        ("EN-Greeting", f"Hello, thank you for contacting {COMPANY_EN}. How may I assist you?", "en,greeting"),
        ("EN-Quote", "Please find the attached quotation for your review.", "en,quote"),
        ("EN-Meeting", "We would like to schedule a call on Tue 2pm KST. Please confirm.", "en,meeting"),
        ("EN-Delay", "We apologize for the delay. We are expediting your order.", "en,apology"),
        ("EN-Signature", f"Best regards,\nJimin Park\nSales | {COMPANY_EN}\n{TEL} | {EMAIL}", "en,signature", True),
        ("EN-Shipment", "Your order has been shipped. Tracking: HB-TRK-20260601", "en,shipping"),
        ("EN-Invoice", f"Invoice #INV-2026-5519 — Payment due within 30 days.\nBank: Kookmin {BANK[-6:]}", "en,invoice"),
        ("EN-Support", f"For technical support: {SUPPORT} (24/7 ticket system)", "en,support"),
    ]
    for item in en:
        pinned = len(item) > 3 and item[3]
        add("영문", item[0], item[1], item[2], pinned=pinned if len(item) > 3 else False)
    for i in range(1, 13):
        add(
            "영문",
            f"EN-Phrase-{i:02d}",
            f"Template phrase {i}: Please revert by EOD KST. Ref: HB-EN-{i:04d}",
            "en,template",
        )

    # --- 내부공지 (15) ---
    for i in range(1, 12):
        add(
            "내부공지",
            f"공지-전사{i:02d}",
            f"【전사 공지】 2026년 {i}분기 전략 회의 일정 및 참석 대상 안내\n"
            f"일시: 6/{5 + i} 10:00 | 장소: 대회의실\n문의: 경영지원",
            "전사,공지",
        )
    add("내부공지", "공지-보안", "비밀번호 90일마다 변경 필수. 타인 공유 금지.", "보안")
    add("내부공지", "공지-복지", "복지 포인트 6월 30일 소멸 예정 — 사내 몰 이용 바랍니다.", "복지")
    add_img("내부공지", "이미지-휴무안내", "assets/holiday_notice.png", "공지,이미지")
    add_img("내부공지", "이미지-대외비푸터", "assets/footer_confidential.png", "보안,이미지")

    # --- IT·시스템 (15) ---
    it = [
        ("IT-비밀번호초기화", "비밀번호 초기화는 IT헬프데스크 내선 999 또는 helpdesk@hanbitsol.co.kr", "IT,비밀번호"),
        ("IT-VPN", "VPN 접속: FortiClient 설치 후 AD 계정으로 로그인", "IT,VPN"),
        ("IT-프린터", "12층 복합기 IP 192.168.10.50 — 드라이버는 포털 다운로드", "IT,프린터"),
        ("IT-장애", "【장애 공지】 메일 서버 점검 6/8 22:00~24:00 — 저장 메일만 영향", "IT,장애"),
        ("IT-요청", "시스템 접근 권한 요청: Jira Service Desk > IT-Access", "IT,권한"),
    ]
    for title, body, tags in it:
        add("IT·시스템", title, body, tags)
    for i in range(1, 9):
        add(
            "IT·시스템",
            f"IT-매크로-{i:02d}",
            f"echo 장애 티켓 HB-IT-{9000 + i} 접수됨 — 담당 배정 대기",
            "IT,티켓",
        )
    add_img("IT·시스템", "이미지-IT헬프", "assets/dept_it.png", "IT,이미지")

    # --- 기타 (10) ---
    misc = [
        ("기타-감사카드", "고생 많으셨습니다. 팀 덕분에 목표 달성했습니다.", "감사"),
        ("기타-점심", "오늘 점심 뭐 먹을까요? 투표 부탁드립니다.", "점심"),
        ("기타-날씨", "우산 챙기세요 — 오후 비 소식 있습니다.", "날씨"),
        ("기타-테스트", "QuickPaste 테스트용 문구입니다.", "테스트"),
    ]
    for title, body, tags in misc:
        add("기타", title, body, tags)
    for i in range(1, 7):
        add("기타", f"메모-{i:02d}", f"임시 메모 #{i} — 삭제 예정", "메모")
    add_img("기타", "이미지-프로모션", "assets/promo_q2.png", "프로모")
    add_img("기타", "이미지-배송", "assets/shipping_box.png", "배송")
    add_img("기타", "이미지-품질", "assets/warranty_badge.png", "품질")
    add_img("기타", "이미지-QR결제", "assets/qr_payment.png", "결제")
    add_img("기타", "이미지-교육", "assets/training_cert.png", "교육")
    add_img("기타", "이미지-영업부", "assets/dept_sales.png", "부서")
    add_img("기타", "이미지-본사안내", "assets/sign_office.png", "안내")

    return rows


def build_zip() -> Path:
    snippets = _text_snippets()
    assets = _build_image_assets()

    text_count = sum(1 for s in snippets if s["content_type"] == "text")
    img_count = sum(1 for s in snippets if s["content_type"] == "image")
    total = len(snippets)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(MANIFEST, ensure_ascii=False, indent=2))
        zf.writestr(
            "categories.json",
            json.dumps(CATEGORIES, ensure_ascii=False, indent=2),
        )
        zf.writestr(
            "snippets.json",
            json.dumps(snippets, ensure_ascii=False, indent=2),
        )
        for path, data in assets.items():
            zf.writestr(path, data)

    print(f"생성: {OUTPUT}")
    print(f"총 {total}건 (텍스트 {text_count}, 이미지 {img_count})")
    print(f"카테고리 {len(CATEGORIES)}개, 이미지 파일 {len(assets)}개")
    return OUTPUT


if __name__ == "__main__":
    build_zip()
