
def render_bars(data, mode="Study"):

    i = st.session_state.i
    j = st.session_state.j
    done = st.session_state.done
    last_action = st.session_state.last_action
    n = len(data)

    # 比較対象の2本を取得
    if done:
        compare_pair = None
    elif j < n - 1 - i:
        compare_pair = (j, j + 1)
    else:
        compare_pair = None

    # SVG描画領域の設定
    svg_width = 720
    svg_height = 350

    bar_width = 54
    bar_pitch = 74
    start_x = 37
    baseline = 220

    bars_svg = ""

    # 棒グラフを描画
    for idx, value in enumerate(data):

        x = start_x + idx * bar_pitch
        h = 45 + value * 15
        y = baseline - h

        color = BAR_COLORS[
            (value - 1) % len(BAR_COLORS)
        ]

        # 整列済みの棒を灰色にする
        if idx >= n - i or done:
            color = "#adb7bc"

        bars_svg += f"""
        <rect
            x="{x}"
            y="{y}"
            width="{bar_width}"
            height="{h}"
            rx="8"
            fill="{color}"
        />

        <text
            x="{x + bar_width / 2}"
            y="{baseline - 12}"
            text-anchor="middle"
            font-size="38"
            font-weight="bold"
            fill="white"
        >{value}</text>
        """

    # ----------------------------
    # 灰色の比較マークを描画
    # ----------------------------
    compare_svg = ""

    if compare_pair is not None:

        left_idx, right_idx = compare_pair

        # 比較対象の棒の中心座標
        x1 = (
            start_x
            + left_idx * bar_pitch
            + bar_width / 2
        )

        x2 = (
            start_x
            + right_idx * bar_pitch
            + bar_width / 2
        )

        center = (x1 + x2) / 2

        # 比較マークの高さ
        y = baseline + 40

        compare_svg = f"""
        <g
            stroke="#849c9d"
            stroke-width="7"
            stroke-linejoin="round"
            stroke-linecap="round"
            fill="none"
        >

            <!-- 左側の受け皿 -->
            <path d="
                M {x1-23} {y}
                L {x1-17} {y+7}
                H {x1+17}
                L {x1+23} {y}
            "/>

            <!-- 右側の受け皿 -->
            <path d="
                M {x2-23} {y}
                L {x2-17} {y+7}
                H {x2+17}
                L {x2+23} {y}
            "/>

            <!-- 2本をつなぐ連結部分 -->
            <path d="
                M {x1} {y+7}
                V {y+29}
                H {x2}
                V {y+7}
            "/>

            <!-- 中央の三角形 -->
            <polygon
                points="
                    {center},{y+29}
                    {center-8},{y+46}
                    {center+8},{y+46}
                "
                fill="#849c9d"
                stroke="none"
            />

        </g>
        """

    # Studyモードの説明文
    explanation = ""

    if mode == "Study":

        if compare_pair is not None:
            left, right = compare_pair

            next_message = (
                f"次は {data[left]} と "
                f"{data[right]} を比較します。"
            )
        else:
            next_message = ""

        explanation = f"""
        <div class="explanation">
            {st.session_state.message}
            <br>
            {next_message}
        </div>
        """

    # HTML画面の生成
    html = f"""
    <style>

        body {{
            margin: 0;
            font-family: sans-serif;
        }}

        .main-box {{
            background: #e8eeee;
            padding: 10px;
            border-radius: 8px;
        }}

        .title-box {{
            background: #435bd5;
            color: white;
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            padding: 20px;
            margin-bottom: 15px;
        }}

        .canvas {{
            background: white;
            border: 1px solid #b9b9b9;
            padding: 10px;
            border-radius: 2px;
        }}

        .explanation {{
            margin: 18px 10px;
            font-size: 21px;
            font-weight: bold;
            color: #5f7070;
            line-height: 1.6;
        }}

    </style>

    <div class="main-box">

        <div class="title-box">
            バブルソート
        </div>

        <div class="canvas">

            <svg
                viewBox="0 0 {svg_width} {svg_height}"
                width="100%"
                xmlns="http://www.w3.org/2000/svg"
            >

                {bars_svg}

                {compare_svg}

            </svg>

        </div>

        {explanation}

    </div>
    """

    return html
