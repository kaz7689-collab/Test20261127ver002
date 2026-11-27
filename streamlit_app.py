import streamlit as st
import random
import time

st.set_page_config(
    page_title="バブルソート",
    page_icon="🔵",
    layout="centered"
)

# ----------------------------
# 設定
# ----------------------------
N = 9
MIN_VALUE = 1
MAX_VALUE = 9
AUTO_PLAY_DELAY = 0.8  # 秒

BAR_COLORS = [
    "#4f63d9", "#5a8fd8", "#16b394", "#25c05a", "#99bb24",
    "#d8bc10", "#ffa40e", "#ef7c00", "#df2a1b"
]

# ----------------------------
# セッション初期化
# ----------------------------
def generate_random_data():
    data = list(range(MIN_VALUE, MAX_VALUE + 1))
    random.shuffle(data)
    return data

def init_session(new_data=True):
    if new_data or "data" not in st.session_state:
        st.session_state.data = generate_random_data()

    st.session_state.i = 0
    st.session_state.j = 0
    st.session_state.done = False
    st.session_state.playing = False
    st.session_state.mode = st.session_state.get("mode", "Study")
    st.session_state.message = "「バブルソート」は隣り合う要素を比較し、必要なら交換していく整列アルゴリズムです。"
    st.session_state.last_action = None

if "data" not in st.session_state:
    init_session(new_data=True)

# ----------------------------
# バブルソート 1ステップ
# ----------------------------
def bubble_sort_step():
    if st.session_state.done:
        st.session_state.message = "整列が完了しました。"
        return

    data = st.session_state.data
    i = st.session_state.i
    j = st.session_state.j
    n = len(data)

    # 全体完了判定
    if i >= n - 1:
        st.session_state.done = True
        st.session_state.message = "整列が完了しました。"
        return

    limit = n - 1 - i

    # パス終了 -> 次の周回へ
    if j >= limit:
        st.session_state.i += 1
        st.session_state.j = 0
        next_sorted = st.session_state.i
        if next_sorted >= n - 1:
            st.session_state.done = True
            st.session_state.message = "整列が完了しました。"
        else:
            st.session_state.message = (
                f"{i + 1}周目が終了しました。右端から {i + 1} 個の要素の位置が確定しています。"
            )
        return

    a = data[j]
    b = data[j + 1]

    # 比較
    if a > b:
        data[j], data[j + 1] = data[j + 1], data[j]
        st.session_state.last_action = ("swap", j, j + 1)
        st.session_state.message = (
            f"{a} と {b} を比較しました。{a} > {b} なので交換します。"
        )
    else:
        st.session_state.last_action = ("keep", j, j + 1)
        st.session_state.message = (
            f"{a} と {b} を比較しました。{a} ≤ {b} なのでそのままにします。"
        )

    st.session_state.j += 1

# ----------------------------
# 描画用HTML
# ----------------------------
def render_bars(data, mode="Study"):
    i = st.session_state.i
    j = st.session_state.j
    done = st.session_state.done
    last_action = st.session_state.last_action
    n = len(data)

    if done:
        compare_pair = None
    elif last_action is not None:
        # 比較済みのペアを強調したいので j-1 を見る
        compare_pair = (last_action[1], last_action[2])
    else:
        compare_pair = None

    sorted_start = n - i if not done else 0

    bars_html = ""
    max_height = max(data)

    for idx, value in enumerate(data):
        # デフォルト色
        color = BAR_COLORS[(value - 1) % len(BAR_COLORS)]
        opacity = 1.0
        border = "none"
        label_color = "white"

        # すでに確定した右側をグレーに
        if idx >= sorted_start and not done:
            color = "#c0c8cf"
            opacity = 0.95

        # 完了時は全体をグレー＋整列済み見せ方
        if done:
            color = "#a9b4bd"

        # 比較中ペア
        if compare_pair and idx in compare_pair:
            if last_action[0] == "swap":
                border = "4px solid #ff6a00"
            else:
                border = "4px solid #4a90e2"

        h = 70 + (value / max_height) * 130

        bars_html += f"""
        <div class="bar-wrap">
            <div class="bar"
                style="
                    height:{h}px;
                    background:{color};
                    opacity:{opacity};
                    border:{border};
                ">
                <span class="bar-label" style="color:{label_color};">{value}</span>
            </div>
        </div>
        """

    explanation = ""
    if mode == "Study":
        explanation = f"""
        <div class="explanation">
            {st.session_state.message}
        </div>
        """

    html = f"""
    <style>
        .main-box {{
            background:#d9dfe1;
            padding: 8px 0 24px 0;
            border-radius: 8px;
        }}
        .title-box {{
            background:#4f63d9;
            color:white;
            text-align:center;
            font-size: 42px;
            font-weight: 800;
            padding: 18px 12px;
            border-radius: 10px;
            margin-bottom: 18px;
            letter-spacing: 1px;
        }}
        .canvas {{
            background: #efefef;
            border: 2px solid #b9b9b9;
            height: 430px;
            margin: 0 10px 18px 10px;
            display:flex;
            align-items:flex-end;
            justify-content:center;
            padding: 28px 20px 35px 20px;
            gap: 16px;
        }}
        .bar-wrap {{
            display:flex;
            align-items:flex-end;
            justify-content:center;
            width: 70px;
            height: 100%;
        }}
        .bar {{
            width: 60px;
            border-radius: 10px;
            display:flex;
            align-items:flex-end;
            justify-content:center;
            box-sizing:border-box;
            padding-bottom: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.18);
            transition: all 0.4s ease;
        }}
        .bar-label {{
            font-size: 28px;
            font-weight: 800;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.20);
        }}
        .explanation {{
            margin: 12px 12px 6px 12px;
            font-size: 24px;
            font-weight: 700;
            color: #5f6f75;
            line-height: 1.5;
        }}
    </style>

    <div class="main-box">
        <div class="title-box">バブルソート</div>
        <div class="canvas">
            {bars_html}
        </div>
        {explanation}
    </div>
    """
    return html

# ----------------------------
# UI
# ----------------------------
top1, top2 = st.columns([1, 1])

with top1:
    selected_mode = st.radio(
        "表示モード",
        ["Study", "Test"],
        horizontal=True,
        index=0 if st.session_state.mode == "Study" else 1
    )
    st.session_state.mode = selected_mode

with top2:
    st.write("")
    st.write("")

st.components.v1.html(
    render_bars(st.session_state.data, st.session_state.mode),
    height=650,
    scrolling=False
)

col1, col2, col3, col4 = st.columns([1.2, 1.2, 1.6, 1.2])

with col1:
    if st.button("⏮ Reset", use_container_width=True):
        init_session(new_data=True)
        st.rerun()

with col2:
    step_disabled = st.session_state.done or st.session_state.playing
    if st.button("◀ Step", use_container_width=True, disabled=step_disabled):
        bubble_sort_step()
        st.rerun()

with col3:
    if not st.session_state.playing:
        if st.button("▶ Play", use_container_width=True, disabled=st.session_state.done):
            st.session_state.playing = True
            st.rerun()
    else:
        if st.button("⏸ Pause", use_container_width=True):
            st.session_state.playing = False
            st.rerun()

with col4:
    if st.button("初期化のみ", use_container_width=True):
        init_session(new_data=True)
        st.rerun()

# ----------------------------
# 自動再生
# ----------------------------
if st.session_state.playing and not st.session_state.done:
    time.sleep(AUTO_PLAY_DELAY)
    bubble_sort_step()
    st.rerun()

if st.session_state.done:
    st.success("整列完了： " + " → ".join(map(str, st.session_state.data)))
