
import streamlit as st
import streamlit.components.v1 as components
import sqlite3
from datetime import datetime, timezone, timedelta

# ==================================================
# Streamlitの基本設定
# ==================================================

st.set_page_config(
    page_title="アルゴリズム／バブルソート",
    page_icon="📊",
    layout="centered"
)

# ==================================================
# アクセスカウンター・最終閲覧日時
# ==================================================

JST = timezone(timedelta(hours=9))

with sqlite3.connect("visits.sqlite3", timeout=15) as db:

    db.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY,
            count INTEGER NOT NULL,
            last_visit TEXT NOT NULL
        )
    """)

    if "visit_registered" not in st.session_state:

        now = datetime.now(JST)

        db.execute("""
            INSERT INTO visits VALUES (1, 1, ?)
            ON CONFLICT(id) DO UPDATE SET
                count = count + 1,
                last_visit = excluded.last_visit
        """, (now.isoformat(),))

        db.commit()

        st.session_state.visit_registered = True

    count, last = db.execute("""
        SELECT count, last_visit
        FROM visits
        WHERE id = 1
    """).fetchone()


# 日本時間・和暦への変換

d = datetime.fromisoformat(last).astimezone(JST)

weekday = "月火水木金土日"[d.weekday()]

last_visit = (
    f"令和{d.year - 2018:02d}年"
    f"{d:%m月%d日}"
    f"({weekday})"
    f"{d:%H:%M:%S}"
)

# ==================================================
# HTML・CSS・JavaScript
# ==================================================

html = '''
<!DOCTYPE html>
<html lang="ja">

<head>

<meta charset="UTF-8">

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #e9eeee;
    color: #435454;
}

/* アクセス情報 */

.access-info {
    text-align: right;
    font-size: 12px;
    padding: 5px 10px 8px;
    line-height: 1.5;
    color: #596969;
    overflow-wrap: anywhere;
}

/* 表題 */

.header {
    background: #435bd0;
    color: white;
    padding: 20px;
    text-align: center;
    font-size: clamp(20px, 4vw, 28px);
    font-weight: bold;
}

/* 言語選択ボタン・操作ボタン */

.languages,
.controls {
    display: flex;
    gap: 6px;
    padding: 10px;
    flex-wrap: wrap;
}

button {
    flex: 1;
    padding: 12px 5px;
    border: 0;
    border-radius: 7px;
    color: white;
    background: #435bd0;
    font-weight: bold;
    cursor: pointer;
    font-size: 15px;
}

.languages button {
    background: white;
    color: #435bd0;
    border: 1px solid #435bd0;
}

.languages button.active {
    background: #435bd0;
    color: white;
}

button:disabled {
    background: #adb7bc !important;
    cursor: default;
}

/* モード・再生速度 */

.settings {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    padding: 10px;
    flex-wrap: wrap;
}

select {
    padding: 6px;
    font-size: 15px;
    border-radius: 5px;
}

/* グラフ描画領域 */

.canvas {
    background: white;
    border: 1px solid #b5bfc2;
    margin: 10px;
    height: 330px;
    position: relative;
    overflow: hidden;
}

.chart {
    position: absolute;
    left: 4%;
    width: 92%;
    height: 100%;
}

/* 棒グラフ */

.bar {
    position: absolute;
    bottom: 100px;
    width: 8%;
    border-radius: 7px;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 8px;
    color: white;
    font-size: clamp(16px, 4vw, 32px);
    font-weight: bold;

    transition:
        left var(--animation-time, 0.035s) ease,
        background-color var(--animation-time, 0.035s) ease,
        color var(--animation-time, 0.035s) ease;
}

/* 灰色の天秤型比較マーク */

.balance {
    position: absolute;
    bottom: 35px;
    width: 22.2222%;
    height: 55px;

    transition:
        left var(--animation-time, 0.035s) ease;
}

/* 統計情報 */

.statistics {
    display: flex;
    justify-content: space-around;
    gap: 4px;
    padding: 12px 4px;
    background: #f7f9f9;
    text-align: center;
    font-size: 13px;
}

.statistics div {
    flex: 1;
}

.statistics strong {
    display: block;
    font-size: 25px;
    color: #435bd0;
    margin-top: 4px;
}

/* アルゴリズムの説明 */

.explanation {
    min-height: 105px;
    padding: 14px;
    font-size: 18px;
    font-weight: bold;
    line-height: 1.5;
}

/* 操作ボタン */

.reset {
    background: #ff9d00;
}

.back {
    background: #82999b;
}

.step {
    background: #4388d1;
}

</style>

</head>

<body>

<!-- アクセス情報 -->

<div class="access-info">

    <span id="visitsLabel"></span>：__COUNT__

    <br>

    <span id="lastLabel"></span>：__LAST__

</div>


<!-- 表題 -->

<div class="header" id="title"></div>


<!-- 言語選択ボタン -->

<div class="languages">

    <button onclick="setLang('ja')" id="ja">
        日本語
    </button>

    <button onclick="setLang('vi')" id="vi">
        Tiếng Việt
    </button>

    <button onclick="setLang('ne')" id="ne">
        नेपाली
    </button>

    <button onclick="setLang('en')" id="en">
        English
    </button>

</div>


<!-- モード・再生速度 -->

<div class="settings">

    <label>

        <span id="modeLabel"></span>

        <select id="mode" onchange="render()">

            <option value="study"></option>

            <option value="test"></option>

        </select>

    </label>

    <label>

        <span id="speedLabel"></span>

        <select id="speed" onchange="changeSpeed()">

            <option value="1600"></option>

            <option value="1000"></option>

            <option value="46" selected></option>

        </select>

    </label>

</div>


<!-- 棒グラフ -->

<div class="canvas">

    <div class="chart" id="chart"></div>

</div>


<!-- 統計情報 -->

<div class="statistics">

    <div>

        <span id="passLabel"></span>

        <strong id="round"></strong>

    </div>

    <div>

        <span id="compareLabel"></span>

        <strong id="comparisons"></strong>

    </div>

    <div>

        <span id="swapLabel"></span>

        <strong id="swaps"></strong>

    </div>

    <div>

        <span id="sortedLabel"></span>

        <strong id="sorted"></strong>

    </div>

</div>


<!-- アルゴリズムの説明 -->

<div class="explanation" id="explanation"></div>


<!-- 操作ボタン -->

<div class="controls">

    <button class="reset"
            id="resetButton"
            onclick="reset()">
    </button>

    <button class="back"
            id="backButton"
            onclick="previousStep()">
    </button>

    <button class="step"
            id="stepButton"
            onclick="step()">
    </button>

    <button id="playButton"
            onclick="togglePlay()">
    </button>

</div>


<script>

// ==================================================
// 4か国語の翻訳データ
// ==================================================

const T = {

    // 日本語

    ja: {

        title: 'アルゴリズム／バブルソート',

        mode: 'モード',

        speed: '再生速度',

        study: '学習',

        test: 'テスト',

        speeds: [
            'ゆっくり',
            '標準',
            '早い'
        ],

        stats: [
            '周回数',
            '比較回数',
            '交換回数',
            '確定数'
        ],

        buttons: [
            'リセット',
            '戻る',
            'ステップ',
            '再生',
            '一時停止'
        ],

        visits: 'アクセス回数',

        last: '最終閲覧日時',

        intro:
            '隣り合う2つの数字を比較し、' +
            '順番が逆なら交換します。',

        greater: (a,b) =>
            `${a} > ${b} なので交換します。`,

        less: (a,b) =>
            `${a} < ${b} なので交換しません。`,

        swapped: (a,b) =>
            `${a} と ${b} の位置を交換しました。`,

        keep:
            '位置はそのままです。',

        next: (a,b) =>
            `次は ${a} と ${b} を比較します。`,

        pass: p =>
            `${p}周目が終了。` +
            `右側の ${p} 個の位置が確定しました。`,

        done:
            '整列完了！ すべての数字が' +
            '小さい順に並びました。'

    },


    // ベトナム語

    vi: {

        title:
            'Thuật toán / Sắp xếp nổi bọt',

        mode: 'Chế độ',

        speed: 'Tốc độ',

        study: 'Học',

        test: 'Kiểm tra',

        speeds: [
            'Chậm',
            'Bình thường',
            'Nhanh'
        ],

        stats: [
            'Lượt',
            'So sánh',
            'Hoán đổi',
            'Đã cố định'
        ],

        buttons: [
            'Đặt lại',
            'Quay lại',
            'Từng bước',
            'Phát',
            'Tạm dừng'
        ],

        visits: 'Lượt truy cập',

        last: 'Truy cập lần cuối',

        intro:
            'So sánh hai số liền kề và ' +
            'đổi chỗ nếu chúng sai thứ tự.',

        greater: (a,b) =>
            `${a} > ${b}, cần đổi chỗ.`,

        less: (a,b) =>
            `${a} < ${b}, không cần đổi chỗ.`,

        swapped: (a,b) =>
            `Đã đổi chỗ ${a} và ${b}.`,

        keep:
            'Giữ nguyên vị trí.',

        next: (a,b) =>
            `Tiếp theo, so sánh ${a} và ${b}.`,

        pass: p =>
            `Kết thúc lượt ${p}. ` +
            `${p} phần tử bên phải đã đúng vị trí.`,

        done:
            'Hoàn tất! Các số đã được ' +
            'sắp xếp tăng dần.'

    },


    // ネパール語

    ne: {

        title:
            'एल्गोरिदम / बबल सर्ट',

        mode: 'मोड',

        speed: 'गति',

        study: 'अध्ययन',

        test: 'परीक्षण',

        speeds: [
            'ढिलो',
            'सामान्य',
            'छिटो'
        ],

        stats: [
            'चक्र',
            'तुलना',
            'साटासाट',
            'निश्चित'
        ],

        buttons: [
            'रिसेट',
            'पछाडि',
            'अर्को चरण',
            'चलाउनुहोस्',
            'रोक्नुहोस्'
        ],

        visits: 'कुल भ्रमण',

        last: 'अन्तिम भ्रमण',

        intro:
            'छेउछाउका दुई सङ्ख्या तुलना गरी ' +
            'गलत क्रममा भए स्थान साट्नुहोस्।',

        greater: (a,b) =>
            `${a} > ${b} भएकाले स्थान साटिन्छ।`,

        less: (a,b) =>
            `${a} < ${b} भएकाले स्थान साटिँदैन।`,

        swapped: (a,b) =>
            `${a} र ${b} का स्थान साटिए।`,

        keep:
            'स्थान यथावत् छन्।',

        next: (a,b) =>
            `अब ${a} र ${b} तुलना गरिन्छ।`,

        pass: p =>
            `${p} औँ चक्र सकियो। ` +
            `दायाँका ${p} वटा स्थान निश्चित भए।`,

        done:
            'पूरा भयो! सबै सङ्ख्या ' +
            'सानोदेखि ठूलो क्रममा छन्।'

    },


    // 英語

    en: {

        title:
            'Algorithm / Bubble Sort',

        mode: 'Mode',

        speed: 'Speed',

        study: 'Study',

        test: 'Test',

        speeds: [
            'Slow',
            'Normal',
            'Fast'
        ],

        stats: [
            'Pass',
            'Comparisons',
            'Swaps',
            'Sorted'
        ],

        buttons: [
            'Reset',
            'Back',
            'Step',
            'Play',
            'Pause'
        ],

        visits: 'Total visits',

        last: 'Last visit',

        intro:
            'Compare adjacent numbers and ' +
            'swap them if they are out of order.',

        greater: (a,b) =>
            `${a} > ${b}, so swap them.`,

        less: (a,b) =>
            `${a} < ${b}, so no swap is needed.`,

        swapped: (a,b) =>
            `Swapped ${a} and ${b}.`,

        keep:
            'Positions remain unchanged.',

        next: (a,b) =>
            `Next, compare ${a} and ${b}.`,

        pass: p =>
            `Pass ${p} complete. ` +
            `The rightmost ${p} positions are fixed.`,

        done:
            'Sorting complete! All numbers ' +
            'are in ascending order.'

    }

};


// ==================================================
// 基本設定
// ==================================================

const $ = id => document.getElementById(id);

const N = 9;

const colors = [
    '#435bd0',
    '#4388d1',
    '#08b69b',
    '#13bf60',
    '#92b82c',
    '#d9b80b',
    '#ffa000',
    '#ed7500',
    '#d62718'
];

const SORTED_COLOR = '#adb7bc';

const COMPLETE_COLOR = '#ffdb00';

let lang = 'ja';

let data = [];

let bars = {};

let balance;

let pass = 0;

let j = 0;

let comparisons = 0;

let swaps = 0;

let phase = 0;

let done = false;

let playing = false;

let timer = null;

let history = [];

let message = ['intro'];

let nextTick = 0;


// ==================================================
// 言語の切り替え
// ==================================================

function setLang(l) {

    lang = l;

    document.documentElement.lang = l;

    render();

}


// ==================================================
// アニメーション速度の調整
// ==================================================

function updateAnimationSpeed() {

    const speed = Number($('speed').value);

    let duration;

    if (speed === 46) {

        duration = 35;

    } else if (speed === 1000) {

        duration = 250;

    } else {

        duration = 400;

    }

    // 手動操作では見やすい移動速度にする

    if (!playing) {

        duration = 250;

    }

    document.documentElement.style.setProperty(
        '--animation-time',
        duration + 'ms'
    );

}


// 再生途中で速度を変更

function changeSpeed() {

    updateAnimationSpeed();

    if (playing) {

        clearTimeout(timer);

        const speed =
            Number($('speed').value);

        nextTick =
            performance.now() + speed;

        timer =
            setTimeout(autoPlay, speed);

    }

}


// ==================================================
// ランダム配列の生成
// ==================================================

function shuffle() {

    let a = Array.from(
        {length: N},
        (_,i) => i + 1
    );

    for (let i = N - 1; i > 0; i--) {

        let k = Math.floor(
            Math.random() * (i + 1)
        );

        [a[i],a[k]] = [a[k],a[i]];

    }

    return a;

}


// ==================================================
// 棒グラフの生成
// ==================================================

function createBars() {

    $('chart').innerHTML = '';

    bars = {};

    for (const v of data) {

        let b = document.createElement('div');

        b.className = 'bar';

        b.style.height =
            (45 + v * 16) + 'px';

        b.textContent = v;

        $('chart').appendChild(b);

        bars[v] = b;

    }


    // 灰色の天秤型比較マーク

    balance = document.createElement('div');

    balance.className = 'balance';

    balance.innerHTML = `

        <svg viewBox="0 0 160 65"
             width="100%"
             height="100%"
             preserveAspectRatio="none">

            <g stroke="#849c9d"
               stroke-width="7"
               stroke-linejoin="round"
               stroke-linecap="round"
               fill="none">

                <path d="
                    M12 10 L20 18 H60 L68 10
                    M92 10 L100 18 H140 L148 10
                    M40 18 V43 H120 V18
                "/>

            </g>

            <polygon
                points="80,43 70,61 90,61"
                fill="#849c9d"
            />

        </svg>

    `;

    $('chart').appendChild(balance);

}


// ==================================================
// 画面の更新
// ==================================================

function render() {

    const t = T[lang];


    // アニメーション速度

    updateAnimationSpeed();


    // 表題

    $('title').textContent = t.title;


    // 選択中の言語ボタンを強調

    for (const l of Object.keys(T)) {

        $(l).classList.toggle(
            'active',
            l === lang
        );

    }


    // モード・再生速度

    $('modeLabel').textContent = t.mode;

    $('speedLabel').textContent = t.speed;

    $('mode').options[0].text = t.study;

    $('mode').options[1].text = t.test;

    t.speeds.forEach((v,i) => {

        $('speed').options[i].text = v;

    });


    // 統計情報の翻訳

    [
        'passLabel',
        'compareLabel',
        'swapLabel',
        'sortedLabel'
    ].forEach((id,i) => {

        $(id).textContent = t.stats[i];

    });


    // アクセス情報の翻訳

    $('visitsLabel').textContent = t.visits;

    $('lastLabel').textContent = t.last;


    // 棒グラフの移動と色の変更

    data.forEach((v,i) => {

        let b = bars[v];

        b.style.left =
            (i * 100 / N + (100 / N - 8) / 2)
            + '%';


        // 全整列完了時は黄色

        if (done) {

            b.style.backgroundColor =
                COMPLETE_COLOR;

            b.style.color = '#594800';


        // 位置確定時は灰色

        } else if (i >= N - pass) {

            b.style.backgroundColor =
                SORTED_COLOR;

            b.style.color = 'white';


        // 未確定時は元の色

        } else {

            b.style.backgroundColor =
                colors[v - 1];

            b.style.color = 'white';

        }

    });


    // 灰色の天秤の移動

    balance.style.display =
        done ? 'none' : 'block';

    balance.style.left =
        (j * 100 / N) + '%';


    // 統計情報の更新

    $('round').textContent =
        Math.min(pass + 1, N - 1);

    $('comparisons').textContent =
        comparisons;

    $('swaps').textContent =
        swaps;

    $('sorted').textContent =
        done ? N : pass;


    // 操作ボタンの翻訳

    $('resetButton').textContent =
        '⏮ ' + t.buttons[0];

    $('backButton').textContent =
        '◀ ' + t.buttons[1];

    $('stepButton').textContent =
        t.buttons[2] + ' ▶';

    $('playButton').textContent =
        (playing ? 'Ⅱ ' : '▶ ') +
        t.buttons[playing ? 4 : 3];


    // ボタンの有効・無効

    $('stepButton').disabled =
        done || playing;

    $('backButton').disabled =
        playing || !history.length;

    $('playButton').disabled =
        done;


    // 説明文の翻訳

    const [key, ...args] = message;

    const m = t[key];

    $('explanation').textContent =
        done
            ? t.done
            : $('mode').value === 'test'
                ? ''
                : typeof m === 'function'
                    ? m(...args)
                    : m;

    $('explanation').style.color =
        done ? '#218838' : '#596969';

}


// ==================================================
// バブルソートの1ステップ
// ==================================================

function step() {

    if (done) return;


    // 現在の状態を履歴に保存

    history.push({

        data: [...data],

        pass,

        j,

        comparisons,

        swaps,

        phase,

        done,

        message: [...message]

    });


    let a = data[j];

    let b = data[j + 1];


    // 第1段階：比較

    if (phase === 0) {

        comparisons++;

        message = [
            a > b ? 'greater' : 'less',
            a,
            b
        ];

        phase = 1;


    // 第2段階：交換

    } else if (phase === 1) {

        if (a > b) {

            [data[j],data[j+1]] = [b,a];

            swaps++;

            message = ['swapped',a,b];

        } else {

            message = ['keep'];

        }

        phase = 2;


    // 第3段階：天秤を次の位置に移動

    } else {

        j++;


        // 1周分の比較が終了

        if (j >= N - 1 - pass) {

            pass++;

            j = 0;


            // すべての整列動作が完了

            if (pass >= N - 1) {

                done = true;

                message = ['done'];

                stopPlay();

            } else {

                message = ['pass',pass];

            }

        } else {

            message = [
                'next',
                data[j],
                data[j+1]
            ];

        }

        phase = 0;

    }

    render();

}


// ==================================================
// 1ステップ前に戻る
// ==================================================

function previousStep() {

    if (playing || !history.length) return;

    const s = history.pop();

    ({
        data,
        pass,
        j,
        comparisons,
        swaps,
        phase,
        done,
        message
    } = s);

    render();

}


// ==================================================
// 自動再生の停止
// ==================================================

function stopPlay() {

    playing = false;

    clearTimeout(timer);

    timer = null;

}


// ==================================================
// 自動再生
// 処理時間の累積による遅延を抑制
// ==================================================

function autoPlay() {

    if (!playing || done) return;

    step();

    if (playing && !done) {

        const speed =
            Number($('speed').value);

        nextTick += speed;

        const delay = Math.max(
            0,
            nextTick - performance.now()
        );

        timer = setTimeout(
            autoPlay,
            delay
        );

    }

}


// ==================================================
// 再生・一時停止
// ==================================================

function togglePlay() {

    if (done) return;

    if (playing) {

        stopPlay();

    } else {

        playing = true;

        updateAnimationSpeed();

        nextTick = performance.now();

        autoPlay();

    }

    render();

}


// ==================================================
// リセット
// ==================================================

function reset() {

    stopPlay();

    let old = data.join(',');


    // 新しいランダム配列を生成

    do {

        data = shuffle();

    } while (

        data.join(',') === old ||

        data.every((v,i) => v === i + 1)

    );


    // 各種カウンターを初期化

    pass = 0;

    j = 0;

    comparisons = 0;

    swaps = 0;

    phase = 0;

    done = false;

    history = [];

    message = ['intro'];


    createBars();

    render();

}


// ==================================================
// アプリ起動時の処理
// ==================================================

reset();

</script>

</body>

</html>
'''

# ==================================================
# Streamlit画面への表示
# ==================================================

components.html(

    html
        .replace('__COUNT__', str(count))
        .replace('__LAST__', last_visit),

    height=850,

    scrolling=True

)
