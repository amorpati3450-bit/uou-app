import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 기본 설정
st.set_page_config(page_title="2027학년도 UOU 입시나침반", layout="centered")

# 2. CSS (모바일 반응형, 다크모드 방어, 버튼 차별화, 단어 단위 줄바꿈 완벽 적용)
st.markdown("""
<style>
    header[data-testid="stHeader"] { display: none !important; }
    .stMainBlockContainer, .block-container {
        padding-top: 0 !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 540px !important;
    }
    div[data-testid="stAppViewBlockContainer"] { padding-top: 0 !important; }

    /* 🌟 한국어 단어 단위 줄바꿈(keep-all) 적용으로 모바일 텍스트 깨짐 방지 */
    .stApp {
        background-color: #F0F4F0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        word-break: keep-all !important;
    }

    /* 알약 형태 입력창 배경/테두리 */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background-color: #FFFFFF !important;
        border: 1.5px solid #D4E8D4 !important;
        border-radius: 28px !important;
        padding: 2px 14px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03) !important;
    }
    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="input"] > div:focus-within {
        border-color: #3AB54A !important;
        box-shadow: 0 0 0 3px rgba(58,181,74,0.12) !important;
    }

    /* 🚨 다크모드 대응: 드롭다운(Selectbox) 선택된 글씨 및 리스트 색상 강제 고정 */
    div[data-baseweb="select"] * {
        color: #2C3E50 !important;
        -webkit-text-fill-color: #2C3E50 !important;
    }
    ul[data-baseweb="menu"] li { color: #2C3E50 !important; }
    
    /* 🚨 다크모드 대응: 숫자 입력칸(Number Input) 글자색 강제 고정 */
    div[data-baseweb="input"] input {
        color: #2C3E50 !important;
        -webkit-text-fill-color: #2C3E50 !important;
        font-weight: 600 !important;
    }

    /* 🚨 라디오 버튼: 부모 래퍼까지 전폭 + 가운데 정렬 (:has로 부모 체인 강제) */
    div:has(> div[role="radiogroup"]) {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        gap: 40px !important;
        width: auto !important;
    }
    div[role="radiogroup"] label[data-baseweb="radio"] p {
        color: #2C3E50 !important;
        font-weight: 600 !important;
    }

    /* 🚨 다크모드 대응: 외부 원만 흰색 배경 강제 (내부 점은 Streamlit 기본 유지) */
    label[data-baseweb="radio"] > div:first-child {
        background-color: #FFFFFF !important;
        border-color: #3AB54A !important;
    }

    /* 기본(Default) 버튼 - 연두색 */
    .stButton > button {
        background-color: #3AB54A !important;
        color: #FFFFFF !important;
        border-radius: 28px !important;
        border: 2px solid transparent !important;
        padding: 0.65rem 1.5rem !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 4px 14px rgba(58,181,74,0.3) !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background-color: #2E9E3D !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(58,181,74,0.4) !important;
    }

    /* 🌟 Primary 버튼 (합격탐색 전용) - 진한 녹색 */
    button[data-testid="stBaseButton-primary"] {
        background-color: #1E7E34 !important;
        color: #FFFFFF !important;
        border: 2px solid #1E7E34 !important;
        box-shadow: 0 4px 14px rgba(30,126,52,0.4) !important;
    }
    button[data-testid="stBaseButton-primary"]:hover {
        background-color: #155D27 !important;
        box-shadow: 0 6px 18px rgba(30,126,52,0.5) !important;
    }

    /* Secondary 버튼 - 하얀 배경 */
    button[data-testid="stBaseButton-secondary"] {
        background-color: #FFFFFF !important;
        color: #3AB54A !important;
        border: 2px solid #3AB54A !important;
        border-radius: 28px !important;
        padding: 0.65rem 1.5rem !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        box-shadow: none !important;
    }
    button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #F0FAF0 !important;
    }

    /* 비활성 버튼 */
    .stButton > button:disabled {
        background-color: #C8D6C8 !important;
        color: #FFFFFF !important;
        box-shadow: none !important;
        cursor: not-allowed;
    }

    /* 아코디언(Expander) 테두리 및 제목 텍스트 속성 (자동 줄바꿈 허용) */
    .stExpander {
        border: 1px solid #E0ECE0 !important;
        border-radius: 16px !important;
        margin-bottom: 8px;
    }
    details summary {
        white-space: normal !important; 
        height: auto !important; 
        line-height: 1.4 !important;
    }
    details summary span {
        color: #2C3E50 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    
    /* 표 스타일 최적화 (폭 제한 해제 및 스크롤 완전 숨기기) */
    [data-testid="stDataFrame"] {
        font-size: 0.8rem;
        width: 100% !important;
    }
    [data-testid="stDataFrame"] > div {
        overflow: hidden !important; 
    }
    [data-testid="stDataFrame"] ::-webkit-scrollbar {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. 상태 관리 및 백엔드 파라미터 수집
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'ad_source' not in st.session_state:
    st.session_state.ad_source = st.query_params.get("ad", "자연유입")

# 🌟 닫기(종료) 처리 로직
if st.session_state.get('closed', False):
    st.markdown("""
<div style="background:#FFFFFF;border-radius:20px;padding:50px 20px;text-align:center;box-shadow:0 4px 16px rgba(0,0,0,0.05);margin-top:40px;">
<h3 style="color:#1E7E34;margin-bottom:12px;">✅ 안전하게 종료되었습니다</h3>
<p style="color:#5A6B6B;font-size:0.95rem;font-weight:600;">현재 창이나 탭을 닫아주세요.</p>
</div>
    """, unsafe_allow_html=True)
    st.stop()

# 데이터베이스 (최신 14개 학부 및 신규 데이터 반영)
db = {
    "자율전공학부": {"is_all": True, "일반교과": {"avg": 3.33, "cut70": 3.67}, "지역교과": {"avg": 3.59, "cut70": 3.87}, "잠재역량": {"avg": 3.59}, "지역인재": {"avg": 3.24}},
    "미래모빌리티공학부": {"is_all": False, "일반교과": {"avg": 3.31, "cut70": 3.50}, "지역교과": {"avg": 3.32, "cut70": 3.60}, "잠재역량": {"avg": 4.87}, "지역인재": {"avg": 4.46}},
    "에너지화학공학부": {"is_all": False, "일반교과": {"avg": 3.15, "cut70": 3.70}, "지역교과": {"avg": 2.17, "cut70": 2.50}, "잠재역량": {"avg": 4.14}, "지역인재": {"avg": 3.91}},
    "신소재·반도체융합학부": {"is_all": False, "일반교과": {"avg": 3.53, "cut70": 3.70}, "지역교과": {"avg": 3.98, "cut70": 4.10}, "잠재역량": {"avg": 5.37}, "지역인재": {"avg": 4.89}},
    "전기전자융합학부": {"is_all": False, "일반교과": {"avg": 3.10, "cut70": 3.30}, "지역교과": {"avg": 3.07, "cut70": 3.20}, "잠재역량": {"avg": 4.69}, "지역인재": {"avg": 4.28}},
    "ICT융합학부": {"is_all": False, "일반교과": {"avg": 3.73, "cut70": 4.00}, "지역교과": {"avg": 3.90, "cut70": 4.10}, "잠재역량": {"avg": 5.46}, "지역인재": {"avg": 4.68}},
    "바이오메디컬헬스학부": {"is_all": False, "일반교과": {"avg": 3.57, "cut70": 3.70}, "지역교과": {"avg": 4.10, "cut70": 4.50}, "잠재역량": {"avg": 5.48}, "지역인재": {"avg": 5.15}},
    "건축·도시환경학부": {"is_all": False, "일반교과": {"avg": 4.26, "cut70": 4.50}, "지역교과": {"avg": 4.17, "cut70": 4.50}, "잠재역량": {"avg": 5.69}, "지역인재": {"avg": 5.26}},
    "디자인융합학부": {"is_all": False, "일반교과": {"avg": 4.01, "cut70": 4.60}, "지역교과": {"avg": 4.34, "cut70": 4.50}, "잠재역량": {"avg": 5.66}, "지역인재": {"avg": 4.82}},
    "공공인재학부": {"is_all": False, "일반교과": {"avg": 4.01, "cut70": 4.40}, "지역교과": {"avg": 3.98, "cut70": 4.30}, "잠재역량": {"avg": 5.64}, "지역인재": {"avg": 5.08}},
    "경영경제융합학부": {"is_all": False, "일반교과": {"avg": 3.87, "cut70": 4.30}, "지역교과": {"avg": 4.25, "cut70": 4.50}, "잠재역량": {"avg": 5.63}, "지역인재": {"avg": 5.31}},
    "글로벌인문학부": {"is_all": False, "일반교과": {"avg": 4.29, "cut70": 4.70}, "지역교과": {"avg": 4.99, "cut70": 5.30}, "잠재역량": {"avg": 6.35}, "지역인재": {"avg": 5.51}},
    "의예과": {"is_all": True, "일반교과": {"avg": "-", "cut70": "-"}, "지역교과": {"avg": 1.02, "cut70": 1.02}, "잠재역량": {"avg": 1.03}, "지역인재": {"avg": 1.13}},
    "간호학과": {"is_all": True, "일반교과": {"avg": 3.24, "cut70": 3.37}, "지역교과": {"avg": 1.98, "cut70": 2.06}, "잠재역량": {"avg": 2.62}, "지역인재": {"avg": 2.30}}
}

# ── 헤더 ──
step = st.session_state.step
step_labels = ["동의", "기본정보", "성적입력", "결과", "유의사항"]

dots = ""
for i, label in enumerate(step_labels, 1):
    if i < step:
        dots += f"<div style='display:flex;flex-direction:column;align-items:center;gap:3px'><div style='width:28px;height:28px;border-radius:50%;background:rgba(255,255,255,0.45);color:white;font-size:0.75rem;font-weight:700;display:flex;align-items:center;justify-content:center'>✓</div><span style='color:rgba(255,255,255,0.7);font-size:0.6rem'>{label}</span></div>"
    elif i == step:
        dots += f"<div style='display:flex;flex-direction:column;align-items:center;gap:3px'><div style='width:28px;height:28px;border-radius:50%;background:white;color:#3AB54A;font-size:0.8rem;font-weight:800;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,0.12)'>{i}</div><span style='color:white;font-size:0.6rem;font-weight:700'>{label}</span></div>"
    else:
        dots += f"<div style='display:flex;flex-direction:column;align-items:center;gap:3px'><div style='width:28px;height:28px;border-radius:50%;background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.45);font-size:0.8rem;font-weight:700;display:flex;align-items:center;justify-content:center'>{i}</div><span style='color:rgba(255,255,255,0.35);font-size:0.6rem'>{label}</span></div>"
    if i < len(step_labels):
        c = "rgba(255,255,255,0.45)" if i < step else "rgba(255,255,255,0.2)"
        dots += f"<div style='width:20px;height:2px;background:{c};margin-bottom:16px'></div>"

st.markdown(f"""<div style="background:linear-gradient(135deg,#228B37 0%,#3AB54A 60%,#4CC95A 100%);border-radius:20px;padding:28px 20px 22px;margin:0 0 16px 0;text-align:center;box-shadow:0 6px 20px rgba(34,139,55,0.3)">
<div style="font-size:0.7rem;color:rgba(255,255,255,0.8);letter-spacing:2px;margin-bottom:4px">2027학년도 수시모집</div>
<div style="font-size:1.7rem;font-weight:800;color:white;line-height:1.3">UOU 입시나침반</div>
<div style="font-size:0.82rem;color:rgba(255,255,255,0.9);margin-top:5px">성적을 입력하고 전형별 합격 가능성을 확인하세요</div>
<div style="display:flex;justify-content:center;align-items:center;gap:6px;margin-top:16px">{dots}</div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════
# [화면 1] 개인정보 수집 동의
# ══════════════════════════════════════
if step == 1:
    st.markdown("""<div style="background:#FFFFFF;border-radius:20px;padding:24px;box-shadow:0 4px 16px rgba(0,0,0,0.05);margin-bottom:16px">
<h4 style="color:#3AB54A;font-size:1.05rem;text-align:center;margin:0 0 16px">개인정보 수집 및 이용 동의</h4>""", unsafe_allow_html=True)

    if st.session_state.get('agree1') != "예":
        st.markdown("""<div style="background:#FAFCFA;border:1px solid #E0E8E0;border-radius:14px;padding:16px 18px;font-size:0.85rem;line-height:1.7;color:#444;margin-bottom:16px">
<b style="color:#2C3E50">1. 수집 항목</b><br>
거주 지역, 상담자 유형, 관심 학부(과), 교과 성적 정보<br><br>
<b style="color:#2C3E50">2. 수집 및 이용 목적</b><br>
수시모집 전형별 합격 가능성 예측 서비스 제공 및 입시 상담 통계 분석<br><br>
<b style="color:#2C3E50">3. 보유 및 이용 기간</b><br>
<span style="color:#3AB54A;font-weight:700">수집일로부터 1년</span> 경과 후 지체 없이 파기<br><br>
<b style="color:#2C3E50">4. 동의 거부에 관한 사항</b><br>
귀하는 위 개인정보 수집 및 이용에 대해 동의를 거부할 권리가 있습니다. 다만, 본 항목은 서비스 제공을 위한 필수 정보로서 동의하지 않으실 경우에는 합격 탐색 서비스 이용이 제한됩니다.
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:#E8F5E9;border:1px solid #C8E6C9;border-radius:14px;padding:12px 18px;color:#2B8A3E;font-size:0.88rem;font-weight:600;margin-bottom:16px;text-align:center;">
✅ 개인정보 수집 및 이용에 동의하셨습니다.
</div>""", unsafe_allow_html=True)

    st.markdown("<p style='font-weight:700;font-size:0.9rem;color:#2C3E50;margin-top:4px;text-align:center;'>개인정보 수집 및 이용에 동의하십니까?</p>", unsafe_allow_html=True)
    
    st.radio("동의1", ["예", "아니오"], index=None, horizontal=True, key="agree1", label_visibility="collapsed")

    if st.session_state.get('agree1') == "예":
        st.markdown("""<div style="background:#FFF8E1;border:1px solid #FFE082;border-radius:14px;padding:16px 18px;font-size:0.88rem;line-height:1.6;color:#D35400;text-align:center;font-weight:600;margin-top:20px;margin-bottom:12px;">
🚨 본 서비스는 2026학년도 성적 기준으로 제공되고 있습니다. 합격을 보증하지 않으니, 참고용으로만 활용하시기 바랍니다.
</div>""", unsafe_allow_html=True)
        
        st.markdown("<p style='font-weight:700;font-size:0.9rem;color:#2C3E50;margin-top:4px;text-align:center;'>위 유의사항을 확인 및 동의하십니까?</p>", unsafe_allow_html=True)
        st.radio("동의2", ["예", "아니오"], index=None, horizontal=True, key="agree2", label_visibility="collapsed")

    st.markdown("</div>", unsafe_allow_html=True)

    disabled = not (st.session_state.get('agree1') == "예" and st.session_state.get('agree2') == "예")
    if st.button("다음 단계", disabled=disabled, key="btn_step1", width="stretch"):
        st.session_state.step = 2
        st.rerun()


# ══════════════════════════════════════
# [화면 2] 기본 정보 입력
# ══════════════════════════════════════
elif step == 2:
    st.markdown("""<div style="background:#FFFFFF;border-radius:20px;padding:22px 24px 8px;box-shadow:0 4px 16px rgba(0,0,0,0.05);margin-bottom:4px">
<h4 style="color:#3AB54A;font-size:1.05rem;text-align:center;margin:0 0 4px">기본 정보 입력</h4>
<p style="color:#5A6B6B;font-size:0.82rem;text-align:center;margin-bottom:12px">합격 탐색에 필요한 기본 정보를 입력해 주세요.</p>
</div>""", unsafe_allow_html=True)

    region_data = {
        "선택": ["선택"],
        "서울특별시": ["강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"],
        "부산광역시": ["강서구", "금정구", "기장군", "남구", "동구", "동래구", "부산진구", "북구", "사상구", "사하구", "서구", "수영구", "연제구", "영도구", "중구", "해운대구"],
        "대구광역시": ["남구", "달서구", "달성군", "동구", "북구", "서구", "수성구", "중구", "군위군"],
        "인천광역시": ["강화군", "계양구", "미추홀구", "남동구", "동구", "부평구", "서구", "연수구", "옹진군", "중구"],
        "광주광역시": ["광산구", "남구", "동구", "북구", "서구"],
        "대전광역시": ["대덕구", "동구", "서구", "유성구", "중구"],
        "울산광역시": ["남구", "동구", "북구", "중구", "울주군"],
        "세종특별자치시": ["세종특별자치시"],
        "경기도": ["가평군", "고양시", "과천시", "광명시", "광주시", "구리시", "군포시", "김포시", "남양주시", "동두천시", "부천시", "성남시", "수원시", "시흥시", "안산시", "안성시", "안양시", "양주시", "양평군", "여주시", "연천군", "오산시", "용인시", "의왕시", "의정부시", "이천시", "파주시", "평택시", "포천시", "하남시", "화성시"],
        "강원특별자치도": ["강릉시", "고성군", "동해시", "삼척시", "속초시", "양구군", "양양군", "영월군", "원주시", "인제군", "정선군", "철원군", "춘천시", "태백시", "평창군", "홍천군", "화천군", "횡성군"],
        "충청북도": ["괴산군", "단양군", "보은군", "영동군", "옥천군", "음성군", "제천시", "증평군", "진천군", "청주시", "충주시"],
        "충청남도": ["계룡시", "공주시", "금산군", "논산시", "당진시", "보령시", "부여군", "서산시", "서천군", "아산시", "예산군", "천안시", "청양군", "태안군", "홍성군"],
        "전북특별자치도": ["고창군", "군산시", "김제시", "남원시", "무주군", "부안군", "순창군", "완주군", "익산시", "임실군", "장수군", "전주시", "정읍시", "진안군"],
        "전라남도": ["강진군", "고흥군", "곡성군", "광양시", "구례군", "나주시", "담양군", "목포시", "무안군", "보성군", "순천시", "신안군", "여수시", "영광군", "영암군", "완도군", "장성군", "장흥군", "진도군", "함평군", "해남군", "화순군"],
        "경상북도": ["경산시", "경주시", "고령군", "구미시", "김천시", "문경시", "봉화군", "상주시", "성주군", "안동시", "영덕군", "영양군", "영주시", "영천시", "예천군", "울릉군", "울진군", "의성군", "청도군", "청송군", "칠곡군", "포항시"],
        "경상남도": ["거제시", "거창군", "고성군", "김해시", "남해군", "밀양시", "사천시", "산청군", "양산시", "의령군", "진주시", "창녕군", "창원시", "통영시", "하동군", "함안군", "함양군", "합천군"],
        "제주특별자치도": ["제주시", "서귀포시"],
    }

    departments = [
        "자율전공학부", "미래모빌리티공학부", "에너지화학공학부",
        "신소재·반도체융합학부", "전기전자융합학부", "ICT융합학부",
        "바이오메디컬헬스학부", "건축·도시환경학부", "디자인융합학부",
        "공공인재학부", "경영경제융합학부", "글로벌인문학부",
        "의예과", "간호학과"
    ]

    st.markdown("<p style='font-weight:600;font-size:0.88rem;color:#2C3E50;margin:12px 0 4px 14px'>관심 학부(과) (최대 3개)</p>", unsafe_allow_html=True)
    selected_deps = st.multiselect("관심학부(과)", departments, max_selections=3, label_visibility="collapsed")

    st.markdown("<p style='font-weight:600;font-size:0.88rem;color:#2C3E50;margin:16px 0 4px 14px'>상담자 유형</p>", unsafe_allow_html=True)
    user_type = st.selectbox("상담자유형", ["선택", "수험생", "학부모", "교사", "기타"], label_visibility="collapsed")

    st.markdown("<p style='font-weight:600;font-size:0.88rem;color:#2C3E50;margin:16px 0 4px 14px'>거주 지역 (시/도)</p>", unsafe_allow_html=True)
    region_main = st.selectbox("시도", list(region_data.keys()), label_visibility="collapsed", key="r_main")

    st.markdown("<p style='font-weight:600;font-size:0.88rem;color:#2C3E50;margin:16px 0 4px 14px'>시/군/구</p>", unsafe_allow_html=True)
    region_sub = st.selectbox("시군구", region_data[region_main], label_visibility="collapsed", key="r_sub")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if 'show_info_warning' not in st.session_state:
        st.session_state.show_info_warning = False

    col_l, col_empty, col_r = st.columns([1, 1, 1])
    with col_l:
        if st.button("이전 단계", type="secondary", key="btn2_prev", width="stretch"):
            st.session_state.show_info_warning = False
            st.session_state.step = 1
            st.rerun()
            
    with col_r:
        if st.button("다음 단계", key="btn2_next", width="stretch"):
            if region_main != "선택" and region_sub != "선택" and user_type != "선택" and len(selected_deps) > 0:
                st.session_state.show_info_warning = False
                st.session_state.user_data = {
                    "region_main": region_main, "region_sub": region_sub,
                    "type": user_type, "deps": selected_deps
                }
                st.session_state.step = 3
                st.rerun()
            else:
                st.session_state.show_info_warning = True
                st.rerun()

    if st.session_state.show_info_warning:
        st.markdown("""<div style="background:#FFF3CD;border:1px solid #FFEEBA;border-radius:12px;padding:12px;color:#856404;text-align:center;font-weight:700;font-size:0.9rem;margin-top:10px;">모든 항목을 입력해 주세요.</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════
# [화면 3] 교과 성적 입력 및 백엔드 전송
# ══════════════════════════════════════
elif step == 3:
    selected_deps = st.session_state.user_data['deps']
    special_deps = ["자율전공학부", "의예과", "간호학과"]
    only_special = all(dep in special_deps for dep in selected_deps)

    deps_str = ", ".join(selected_deps)
    st.markdown(f"""<div style="background:#FFFFFF;border-radius:20px;padding:22px 24px 8px;box-shadow:0 4px 16px rgba(0,0,0,0.05);margin-bottom:4px">
<h4 style="color:#3AB54A;font-size:1.05rem;text-align:center;margin:0 0 6px">교과 성적 입력</h4>
<p style="color:#5A6B6B;font-size:0.82rem;text-align:center;margin-bottom:12px">선택 학부(과): <b style="color:#2C3E50">{deps_str}</b></p>
</div>""", unsafe_allow_html=True)

    if "s_all" not in st.session_state: st.session_state.s_all = 0.0
    if "s_10" not in st.session_state: st.session_state.s_10 = 0.0
    if "input_all" not in st.session_state: st.session_state.input_all = st.session_state.s_all
    if "input_10" not in st.session_state: st.session_state.input_10 = st.session_state.s_10

    def sync_all():
        st.session_state.s_all = st.session_state.input_all

    def sync_10():
        st.session_state.s_10 = st.session_state.input_10

    if only_special:
        st.markdown("""<div style="background:#EFF8EF;border-radius:12px;padding:12px 16px;font-size:0.84rem;color:#2B8A3E;font-weight:600;text-align:center;margin:8px 0 12px;border:1px solid #D4EAD4">
선택하신 학부(과)는 <b>전 과목 석차등급 평균</b>으로 판정합니다.
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:#EFF8EF;border-radius:12px;padding:12px 16px;font-size:0.84rem;color:#2B8A3E;font-weight:600;text-align:center;margin:8px 0 12px;border:1px solid #D4EAD4">
전 과목 평균과 상위 10개 과목 평균이 모두 필요합니다.
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    
    with st.expander("💡 내 평균 등급을 잘 모르겠다면 계산기 열기 (클릭)"):
        
        if not only_special:
            st.markdown("<div style='font-weight:800;color:#2C3E50;margin-bottom:4px;font-size:1rem;text-align:center;'>[ 상위 10개 과목 평균 계산기 ]</div>", unsafe_allow_html=True)
            st.markdown("<div style='color:#E67E22;font-size:0.8rem;font-weight:700;margin-bottom:12px;text-align:center;'>⚠️ 이수단위 2 이상인 과목의 등급만 입력해 주세요.</div>", unsafe_allow_html=True)

            def_10 = {"등급":[None]*3}
            
            c1, c2 = st.columns(2, gap="small")
            with c1: 
                st.markdown("<div style='text-align:center;font-size:0.85rem;font-weight:700;color:#2C3E50'>국어</div>", unsafe_allow_html=True)
                ed_t_kor = st.data_editor(def_10, hide_index=True, key="tkor", width="stretch")
            with c2: 
                st.markdown("<div style='text-align:center;font-size:0.85rem;font-weight:700;color:#2C3E50'>영어</div>", unsafe_allow_html=True)
                ed_t_eng = st.data_editor(def_10, hide_index=True, key="teng", width="stretch")
            
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            
            c3, c4 = st.columns(2, gap="small")
            with c3: 
                st.markdown("<div style='text-align:center;font-size:0.85rem;font-weight:700;color:#2C3E50'>수학</div>", unsafe_allow_html=True)
                ed_t_mat = st.data_editor(def_10, hide_index=True, key="tmat", width="stretch")
            with c4: 
                st.markdown("<div style='text-align:center;font-size:0.85rem;font-weight:700;color:#2C3E50'>사회 및 과학</div>", unsafe_allow_html=True)
                ed_t_ss = st.data_editor(def_10, hide_index=True, key="tss", width="stretch")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            _, btn_col1, _ = st.columns([1, 1.5, 1])
            with btn_col1:
                if st.button("계산 및 적용", key="btn_apply_10", width="stretch"):
                    all_vals = []
                    for ed in [ed_t_kor, ed_t_eng, ed_t_mat, ed_t_ss]:
                        for v in ed["등급"]:
                            if v is not None:
                                try:
                                    vf = float(v)
                                    if vf > 0: all_vals.append(vf)
                                except: pass
                    all_vals.sort()
                    top10 = all_vals[:10]
                    if top10:
                        calc_val = sum(top10) / len(top10)
                        st.session_state.s_10 = calc_val
                        st.session_state.input_10 = calc_val
                    st.rerun()

            st.markdown("<div style='height:16px; border-bottom:1px solid #E0ECE0; margin-bottom:16px'></div>", unsafe_allow_html=True)

        st.markdown("<div style='font-weight:800;color:#2C3E50;margin-bottom:4px;font-size:1rem;text-align:center;'>[ 전 과목 평균 계산기 ]</div>", unsafe_allow_html=True)
        st.markdown("<div style='color:#1976D2;font-size:0.8rem;font-weight:700;margin-bottom:12px;text-align:center;'>⚠️ 생기부에 기재된 모든 과목의 단위와 등급을 입력하세요.</div>", unsafe_allow_html=True)

        def_all = {"단위":[None]*10, "등급":[None]*10}
        
        c1, c2, c3 = st.columns(3, gap="small")
        with c1: 
            st.markdown("<div style='text-align:center;font-size:0.85rem;font-weight:700;color:#2C3E50'>국어</div>", unsafe_allow_html=True)
            ed_a_kor = st.data_editor(def_all, hide_index=True, key="akor", width="stretch")
        with c2: 
            st.markdown("<div style='text-align:center;font-size:0.85rem;font-weight:700;color:#2C3E50'>영어</div>", unsafe_allow_html=True)
            ed_a_eng = st.data_editor(def_all, hide_index=True, key="aeng", width="stretch")
        with c3: 
            st.markdown("<div style='text-align:center;font-size:0.85rem;font-weight:700;color:#2C3E50'>수학</div>", unsafe_allow_html=True)
            ed_a_mat = st.data_editor(def_all, hide_index=True, key="amat", width="stretch")
            
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        
        c4, c5 = st.columns(2, gap="small")
        with c4: 
            st.markdown("<div style='text-align:center;font-size:0.85rem;font-weight:700;color:#2C3E50'>사회</div>", unsafe_allow_html=True)
            ed_a_soc = st.data_editor(def_all, hide_index=True, key="asoc", width="stretch")
        with c5: 
            st.markdown("<div style='text-align:center;font-size:0.85rem;font-weight:700;color:#2C3E50'>과학</div>", unsafe_allow_html=True)
            ed_a_sci = st.data_editor(def_all, hide_index=True, key="asci", width="stretch")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        _, btn_col2, _ = st.columns([1, 1.5, 1])
        with btn_col2:
            if st.button("계산 및 적용", key="btn_apply_all", width="stretch"):
                t_unit = 0.0
                t_score = 0.0
                for ed in [ed_a_kor, ed_a_eng, ed_a_mat, ed_a_soc, ed_a_sci]:
                    for u, g in zip(ed["단위"], ed["등급"]):
                        if u is not None and g is not None:
                            try:
                                uf, gf = float(u), float(g)
                                if uf > 0 and gf > 0:
                                    t_unit += uf
                                    t_score += (uf * gf)
                            except: pass
                if t_unit > 0:
                    calc_val = t_score / t_unit
                    st.session_state.s_all = calc_val
                    st.session_state.input_all = calc_val
                st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    if only_special:
        st.markdown("<p style='font-weight:600;font-size:0.88rem;color:#2C3E50;margin:0 0 4px 14px'>전 과목 평균 등급</p>", unsafe_allow_html=True)
        score_all = st.number_input("전과목", min_value=0.0, max_value=9.0, step=0.01, format="%.2f", label_visibility="collapsed", key="input_all", value=st.session_state.s_all, on_change=sync_all, help="예: 2.50")
        score_10 = 0.0
    else:
        st.markdown("<p style='font-weight:600;font-size:0.88rem;color:#2C3E50;margin:0 0 4px 14px'>전 과목 평균 등급</p>", unsafe_allow_html=True)
        score_all = st.number_input("전과목", min_value=0.0, max_value=9.0, step=0.01, format="%.2f", label_visibility="collapsed", key="input_all", value=st.session_state.s_all, on_change=sync_all, help="예: 2.50")

        st.markdown("<p style='font-weight:600;font-size:0.88rem;color:#2C3E50;margin:16px 0 4px 14px'>상위 10개 과목 평균 등급</p>", unsafe_allow_html=True)
        score_10 = st.number_input("상위10", min_value=0.0, max_value=9.0, step=0.01, format="%.2f", label_visibility="collapsed", key="input_10", value=st.session_state.s_10, on_change=sync_10, help="예: 2.00")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if 'show_score_warning' not in st.session_state:
        st.session_state.show_score_warning = False

    col_l, col_empty, col_r = st.columns([1, 1, 1])
    with col_l:
        if st.button("이전 단계", type="secondary", key="btn3_prev", width="stretch"):
            st.session_state.show_score_warning = False
            st.session_state.step = 2
            st.rerun()
            
    with col_r:
        if st.button("합격 탐색", type="primary", key="btn3_next", width="stretch"):
            if score_all == 0.0 and score_10 == 0.0:
                st.session_state.show_score_warning = True
                st.rerun()
            else:
                st.session_state.show_score_warning = False
                st.session_state.user_data['score_all'] = score_all
                st.session_state.user_data['score_10'] = score_10

                try:
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    sheet_url = "https://docs.google.com/spreadsheets/d/1XMrUsijgyAeAubwA-NCEw4Z8zqcVS8b_TXipWL-0d2w/edit?usp=sharing" 
                    existing_data = conn.read(spreadsheet=sheet_url, usecols=list(range(8)), ttl=0).dropna(how="all")
                    
                    new_entry = pd.DataFrame([{
                        "입력시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "시도": st.session_state.user_data['region_main'],
                        "시군구": st.session_state.user_data['region_sub'],
                        "상담자": st.session_state.user_data['type'],
                        "관심학부": ", ".join(st.session_state.user_data['deps']),
                        "전과목성적": score_all,
                        "10과목성적": score_10,
                        "유입경로": st.session_state.ad_source
                    }])
                    
                    updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
                    conn.update(spreadsheet=sheet_url, data=updated_df)
                
                except Exception as e:
                    st.error(f"🚨 저장 실패: {e}")
                    st.stop() 

                st.session_state.step = 4
                st.rerun()

    if st.session_state.show_score_warning:
        st.markdown("""<div style="background:#FFF3CD;border:1px solid #FFEEBA;border-radius:12px;padding:12px;color:#856404;text-align:center;font-weight:700;font-size:0.9rem;margin-top:10px;">성적을 입력해 주세요.</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════
# [화면 4] 판정 결과
# ══════════════════════════════════════
elif step == 4:
    selected_deps = st.session_state.user_data['deps']

    def get_gyogwa_result(score, avg_score, cut70):
        if avg_score == '-' or cut70 == '-':
            return "-", "#778CA3", "#F0F4F0"
        
        avg_f = float(avg_score)
        cut70_f = float(cut70)
        
        if score <= avg_f:       return "안정", "#2B8A3E", "#E8F5E9"
        elif score <= cut70_f:   return "적정", "#1976D2", "#E3F2FD"
        else:                    return "상향", "#E67E22", "#FFF8E1"

    def get_hakjong_result(score, avg_score):
        if avg_score == '-':
            return "-", "#778CA3", "#F0F4F0"
            
        avg_f = float(avg_score)
        
        if score <= avg_f: return "적정", "#2B8A3E", "#E8F5E9"
        else:              return "상향", "#E67E22", "#FFF8E1"

    def badge(text, color, bg):
        if text == "-":
            return f"<span style='background:{bg};color:{color};padding:3px 14px;border-radius:14px;font-weight:700;font-size:0.85rem'>판정 불가</span>"
        return f"<span style='background:{bg};color:{color};padding:3px 14px;border-radius:14px;font-weight:700;font-size:0.85rem'>{text}</span>"

    st.markdown("""
<div style="background:#FFF8E1;border:1px solid #FFE082;border-radius:16px;padding:14px 18px;margin-bottom:12px;text-align:center;">
<span style="font-weight:700;color:#D35400;font-size:0.9rem;">
🚨 본 서비스는 2026학년도 성적 기준으로 제공되고 있습니다. 합격을 보증하지 않으니, 참고용으로만 활용하시기 바랍니다.
</span>
</div>
    """, unsafe_allow_html=True)

    st.markdown("""<div style="background:#FFFFFF;border-radius:16px;padding:16px 18px;box-shadow:0 2px 10px rgba(0,0,0,0.04);margin-bottom:16px">
<div style="font-weight:700;color:#2C3E50;margin-bottom:4px;text-align:center;font-size:0.92rem">판정 결과 안내</div>
<div style="text-align:center;color:#888;font-size:0.75rem;margin-bottom:12px">※ 최종등록자 기준</div>
<div style="display:flex;gap:10px">
<div style="flex:1;background:#F8FBF8;border-radius:10px;padding:12px 14px;border-left:3px solid #3AB54A">
<div style="font-weight:700;color:#2B8A3E;margin-bottom:10px;font-size:0.88rem">교과형</div>
<div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
<span style="background:#E8F5E9;color:#2B8A3E;padding:2px 10px;border-radius:10px;font-weight:700;font-size:0.78rem;white-space:nowrap">안정</span>
<span style="color:#444;font-size:0.8rem">평균 등급 이내</span>
</div>
<div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
<span style="background:#E3F2FD;color:#1976D2;padding:2px 10px;border-radius:10px;font-weight:700;font-size:0.78rem;white-space:nowrap">적정</span>
<span style="color:#444;font-size:0.8rem">평균 ~ 상위 70%</span>
</div>
<div style="display:flex;align-items:center;gap:8px">
<span style="background:#FFF8E1;color:#E67E22;padding:2px 10px;border-radius:10px;font-weight:700;font-size:0.78rem;white-space:nowrap">상향</span>
<span style="color:#444;font-size:0.8rem">상위 70% 미만</span>
</div>
</div>
<div style="flex:1;background:#F8FBF8;border-radius:10px;padding:12px 14px;border-left:3px solid #2196F3">
<div style="font-weight:700;color:#1976D2;margin-bottom:10px;font-size:0.88rem">학종형</div>
<div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
<span style="background:#E8F5E9;color:#2B8A3E;padding:2px 10px;border-radius:10px;font-weight:700;font-size:0.78rem;white-space:nowrap">적정</span>
<span style="color:#444;font-size:0.8rem">평균 등급 이내</span>
</div>
<div style="display:flex;align-items:center;gap:8px">
<span style="background:#FFF8E1;color:#E67E22;padding:2px 10px;border-radius:10px;font-weight:700;font-size:0.78rem;white-space:nowrap">상향</span>
<span style="color:#444;font-size:0.8rem">평균 등급 초과</span>
</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

    for dep in selected_deps:
        if dep not in db:
            with st.expander(f"{dep} (클릭)"):
                st.markdown("<p style='color:#2C3E50; font-weight:600'>입시결과 데이터 업데이트 준비 중입니다.</p>", unsafe_allow_html=True)
            continue

        dep_data = db[dep]
        is_special = dep in ["자율전공학부", "의예과", "간호학과"]
        score_all = st.session_state.user_data['score_all']
        score_10 = st.session_state.user_data['score_10']

        if is_special:
            gyogwa_score = score_all
            gyogwa_label = "전 과목 평균"
        else:
            gyogwa_score = score_10
            gyogwa_label = "10개 과목 평균"
            
        hakjong_score = score_all
        hakjong_label = "전 과목 평균"

        g1_res, g1_c, g1_bg = get_gyogwa_result(gyogwa_score, dep_data['일반교과']['avg'], dep_data['일반교과']['cut70'])
        g2_res, g2_c, g2_bg = get_gyogwa_result(gyogwa_score, dep_data['지역교과']['avg'], dep_data['지역교과']['cut70'])
        h1_res, h1_c, h1_bg = get_hakjong_result(hakjong_score, dep_data['잠재역량']['avg'])
        h2_res, h2_c, h2_bg = get_hakjong_result(hakjong_score, dep_data['지역인재']['avg'])

        with st.expander(f"{dep} (클릭)"):
            st.markdown(f"""
<div style="margin-bottom:12px;">
<div style="background:#FAFCFA;border:1px solid #E8F0E8;border-radius:14px;padding:16px;margin-bottom:12px;box-shadow:0 2px 6px rgba(0,0,0,0.02)">
<div style="display:flex;align-items:center;margin-bottom:14px;border-bottom:1px solid #E0ECE0;padding-bottom:10px;">
<span style="font-weight:800;color:#2B8A3E;font-size:0.95rem;">교과형</span>
<span style="color:#5A6B6B;font-size:0.8rem;margin-left:8px;">(내 성적: <b style="color:#2C3E50;">{gyogwa_score:.2f}</b> 등급 / {gyogwa_label})</span>
</div>
<div style="display:flex;gap:10px">
<div style="flex:1;text-align:center;">
<div style="font-weight:700;color:#2C3E50;font-size:0.88rem;margin-bottom:4px">일반교과</div>
<div style="color:#778CA3;font-size:0.75rem;margin-bottom:8px">평균 {dep_data['일반교과']['avg']} · 70%컷 {dep_data['일반교과']['cut70']}</div>
{badge(g1_res, g1_c, g1_bg)}
</div>
<div style="flex:1;text-align:center;border-left:1px solid #E8F0E8;">
<div style="font-weight:700;color:#2C3E50;font-size:0.88rem;margin-bottom:4px">지역교과</div>
<div style="color:#778CA3;font-size:0.75rem;margin-bottom:8px">평균 {dep_data['지역교과']['avg']} · 70%컷 {dep_data['지역교과']['cut70']}</div>
{badge(g2_res, g2_c, g2_bg)}
</div>
</div>
</div>
<div style="background:#F4F8FD;border:1px solid #E0E8F0;border-radius:14px;padding:16px;box-shadow:0 2px 6px rgba(0,0,0,0.02)">
<div style="display:flex;align-items:center;margin-bottom:14px;border-bottom:1px solid #D5E2F0;padding-bottom:10px;">
<span style="font-weight:800;color:#1976D2;font-size:0.95rem;">학종형</span>
<span style="color:#5A6B6B;font-size:0.8rem;margin-left:8px;">(내 성적: <b style="color:#2C3E50;">{hakjong_score:.2f}</b> 등급 / {hakjong_label})</span>
</div>
<div style="display:flex;gap:10px">
<div style="flex:1;text-align:center;">
<div style="font-weight:700;color:#2C3E50;font-size:0.88rem;margin-bottom:4px">잠재역량</div>
<div style="color:#778CA3;font-size:0.75rem;margin-bottom:8px">평균 {dep_data['잠재역량']['avg']}</div>
{badge(h1_res, h1_c, h1_bg)}
</div>
<div style="flex:1;text-align:center;border-left:1px solid #D5E2F0;">
<div style="font-weight:700;color:#2C3E50;font-size:0.88rem;margin-bottom:4px">지역인재</div>
<div style="color:#778CA3;font-size:0.75rem;margin-bottom:8px">평균 {dep_data['지역인재']['avg']}</div>
{badge(h2_res, h2_c, h2_bg)}
</div>
</div>
</div>
</div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("학부 변경", type="secondary", key="btn4_dep", width="stretch"):
            st.session_state.step = 2
            st.rerun()
    with col_b:
        if st.button("성적 수정", type="secondary", key="btn4_score", width="stretch"):
            st.session_state.step = 3
            st.rerun()
    with col_c:
        if st.button("유의사항", key="btn4_notice", width="stretch"):
            st.session_state.step = 5
            st.rerun()


# ══════════════════════════════════════
# [화면 5] 🌟 신규: 유의사항 및 종료 페이지
# ══════════════════════════════════════
elif step == 5:
    st.markdown("""<div style="background:#FFFFFF;border-radius:20px;padding:26px 24px;box-shadow:0 4px 16px rgba(0,0,0,0.05);margin-bottom:16px">
<h4 style="color:#1E7E34;font-size:1.1rem;text-align:center;margin:0 0 20px;">📌 2027학년도 울산대 수시 체크 포인트</h4>
<div style="background:#F8FBF8;border-left:4px solid #3AB54A;padding:16px;border-radius:8px;margin-bottom:14px;">
<div style="font-weight:800;color:#2C3E50;font-size:0.95rem;margin-bottom:6px;">✔️ 지역교과 전형</div>
<div style="color:#444;font-size:0.9rem;font-weight:500;">내신 등급으로만! <b style="color:#D35400;">수능 최저 폐지</b></div>
</div>
<div style="background:#F4F8FD;border-left:4px solid #1976D2;padding:16px;border-radius:8px;margin-bottom:18px;">
<div style="font-weight:800;color:#2C3E50;font-size:0.95rem;margin-bottom:6px;">✔️ 잠재역량 전형</div>
<div style="color:#444;font-size:0.9rem;font-weight:500;">생기부로만! <b style="color:#D35400;">면접 폐지</b></div>
</div>
<div style="text-align:center;color:#778CA3;font-size:0.8rem;font-weight:600;padding-top:10px;border-top:1px dashed #E0E8E0;">
(단, 두 전형 모두 의예과, 간호학과, 자율전공학부 제외)
</div>
</div>""", unsafe_allow_html=True)

    _, col_close, _ = st.columns([1, 1.5, 1])
    with col_close:
        if st.button("닫기", type="secondary", key="btn_close", width="stretch"):
            st.session_state.closed = True
            st.rerun()
