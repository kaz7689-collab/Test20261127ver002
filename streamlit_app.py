
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="バブルソート",
    page_icon="📊",
    layout="centered"
)

components.html("""
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
}

.header {
    background: #435bd0;
    color: white;
    padding: 22px;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
}

.canvas {
    background: white;
    border: 1px solid #b5bfc2;
    margin: 12px;
    height: 330px;
    position: relative;
    overflow: hidden;
}

.chart {
    position: absolute;
    left: 4%;
    top: 0;
    width: 92%;
    height: 100%;
}

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
        left 0.4s ease,
        background-color 0.3s ease;
}

.balance {
    position: absolute;
    bottom: 27px;
    width: 22.22%;
    height: 55px;
    transition: left 0.35s ease;
}

.explanation {
    min-height: 100px;
    padding: 14px;
    font-size: 19px;
    font-weight: bold;
    line-height: 1.6;
    color: #596969;
}

.controls {
    display: flex;
    gap: 8px;
    padding: 12px;
}

button {
    flex: 1;
    padding: 15px 5px;
    border: none;
    border-radius: 8px;
    font-size: 17px;
    font-weight: bold;
    color: white;
    cursor: pointer;
    box-shadow: 0 3px 4px #999;
}

button:disabled {
    background: #adb7bc !important;
    cursor: default;
}

.reset {
    background: #ff9d00;
}

.step {
    background: #4388d1;
}

.play {
    background: #435bd0;
}

.back {
    background: #82999b;
}

.settings {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    padding: 14px;
    color: #596969;
}

select {
    padding: 8px;
    border-radius: 6px;
    font-size: 15px;
}

.statistics {
    display: flex;
    justify-content: space-around;
    padding: 15px 5px;
    background: #f7f9f9;
    color: #596969;
    text-align: center;
    font-size: 13px;
}

.statistics strong {
    display: block;
    font-size: 25px;
    margin-top: 5px;
    color: #435bd0;
}

</style>
</head>

<body>

<div class="header">
    バブルソート
</div>

<div class="settings">

    <label>
        モード：
        <select id="mode" onchange="updateMessage()">
            <option value="Study">Study</option>
            <option value="Test">Test</option>
        </select>
    </label>

    <label>
        再生速度：
        <select id="speed">
            <option value="1600">ゆっくり</option>
            <option value="1000" selected>標準</option>
            <option value="600">速い</option>
        </select>
    </label>

</div>

<div class="canvas">
    <div class="chart" id="chart"></div>
</div>

<div class="statistics">

    <div>
        周回数
        <strong id="round">1</strong>
    </div>

    <div>
        比較回数
        <strong id="comparisons">0</strong>
    </div>

    <div>
        交換回数
        <strong id="swaps">0</strong>
    </div>

    <div>
        確定数
        <strong id="sorted">0</strong>
    </div>

</div>

<div class="explanation" id="explanation">
</div>

<div class="controls">

    <button class="reset" onclick="reset()">
        ⏮ Reset
    </button>

    <button class="back" id="backButton"
            onclick="previousStep()">
        ◀ 戻る
    </button>

    <button class="step" id="stepButton"
            onclick="step()">
        Step ▶
    </button>

    <button class="play" id="playButton"
            onclick="togglePlay()">
        ▶ Play
    </button>

</div>

<script>

const colors = [
    "#435bd0",
    "#4388d1",
    "#08b69b",
    "#13bf60",
    "#92b82c",
    "#d9b80b",
    "#ffa000",
    "#ed7500",
    "#d62718"
];

let data = [];
let bars = {};
let balance;

let pass = 0;
let j = 0;

let comparisons = 0;
let swaps = 0;

let phase = "compare";
let done = false;
let playing = false;
let timer = null;
let history = [];

let message = "";

const N = 9;


// ランダムな初期配列を生成

function shuffle() {

    let values = [1,2,3,4,5,6,7,8,9];

    for (let i = values.length - 1; i > 0; i--) {

        let k = Math.floor(
            Math.random() * (i + 1)
        );

        [values[i], values[k]] =
            [values[k], values[i]];
    }

    // 初期状態が整列済みの場合は再生成
    if (values.every((v, i) => v === i + 1)) {
        return shuffle();
    }

    return values;
}


// 棒グラフの位置

function barPosition(index) {
    return index * 100 / N + 1.55;
}


// 棒グラフの生成

function createBars() {

    const chart = document.getElementById("chart");

    chart.innerHTML = "";
    bars = {};

    data.forEach((value, index) => {

        const bar = document.createElement("div");

        bar.className = "bar";

        bar.style.height =
            (45 + value * 16) + "px";

        bar.style.left =
            barPosition(index) + "%";

        bar.style.backgroundColor =
            colors[value - 1];

        bar.textContent = value;

        chart.appendChild(bar);

        bars[value] = bar;
    });


    // 灰色の天秤型比較マーク

    balance = document.createElement("div");

    balance.className = "balance";

    balance.innerHTML = `
        <svg viewBox="0 0 160 65"
             width="100%" height="100%">

            <g stroke="#849c9d"
               stroke-width="7"
               stroke-linejoin="round"
               stroke-linecap="round"
               fill="none">

                <!-- 左側の受け皿 -->
                <path d="M 12 10
                         L 20 18
                         H 60
                         L 68 10"/>

                <!-- 右側の受け皿 -->
                <path d="M 92 10
                         L 100 18
                         H 140
                         L 148 10"/>

                <!-- 2つの受け皿を連結 -->
                <path d="M 40 18
                         V 43
                         H 120
                         V 18"/>

            </g>

            <!-- 中央の支点 -->
            <polygon
                points="80,43 70,61 90,61"
                fill="#849c9d"
            />

        </svg>
    `;

    chart.appendChild(balance);

}


// 画面の更新

function render() {

    data.forEach((value, index) => {

        const bar = bars[value];

        bar.style.left =
            barPosition(index) + "%";

        // 整列が確定した棒を灰色にする

        if (done || index >= N - pass) {

            bar.style.backgroundColor = "#adb7bc";

        } else {

            bar.style.backgroundColor =
                colors[value - 1];
        }

    });


    // 比較対象の2本の真下に天秤を表示

    if (done) {

        balance.style.display = "none";

    } else {

        balance.style.display = "block";

        balance.style.left =
            (j * 100 / N) + "%";
    }


    document.getElementById("round").textContent =
        Math.min(pass + 1, N - 1);

    document.getElementById("comparisons").textContent =
        comparisons;

    document.getElementById("swaps").textContent =
        swaps;

    document.getElementById("sorted").textContent =
        done ? N : pass;


    document.getElementById("stepButton").disabled =
        done || playing;

    document.getElementById("backButton").disabled =
        playing || history.length === 0;

    document.getElementById("playButton").disabled =
        done;

    document.getElementById("playButton").textContent =
        playing ? "Ⅱ Pause" : "▶ Play";


    updateMessage();

}


// 説明文の表示

function updateMessage() {

    const mode =
        document.getElementById("mode").value;

    const explanation =
        document.getElementById("explanation");

    if (mode === "Study") {

        explanation.textContent = message;

    } else {

        explanation.textContent =
            done ? "整列完了！" : "";
    }
}


// 操作履歴を保存

function saveHistory() {

    history.push({
        data: [...data],
        pass: pass,
        j: j,
        comparisons: comparisons,
        swaps: swaps,
        phase: phase,
        done: done,
        message: message
    });

}


// 1ステップ前に戻る

function previousStep() {

    if (history.length === 0 || playing) {
        return;
    }

    const state = history.pop();

    data = [...state.data];

    pass = state.pass;
    j = state.j;

    comparisons = state.comparisons;
    swaps = state.swaps;

    phase = state.phase;
    done = state.done;
    message = state.message;

    render();

}


// バブルソートの1ステップ

function step() {

    if (done) {
        return;
    }

    saveHistory();

    const left = data[j];
    const right = data[j + 1];


    // 第1段階：2つの数字を比較

    if (phase === "compare") {

        comparisons++;

        if (left > right) {

            message =
                left + " > " + right +
                " なので、2つの位置を交換します。";

        } else {

            message =
                left + " < " + right +
                " なので、交換する必要はありません。";
        }

        phase = "swap";


    // 第2段階：必要なら位置を交換

    } else if (phase === "swap") {

        if (left > right) {

            [data[j], data[j + 1]] =
                [data[j + 1], data[j]];

            swaps++;

            message =
                left + " と " + right +
                " の位置を交換しました。";

        } else {

            message = "位置はそのままです。";
        }

        phase = "advance";


    // 第3段階：比較マークを次の位置へ移動

    } else {

        j++;

        // 1周分の比較が完了

        if (j >= N - 1 - pass) {

            pass++;
            j = 0;

            if (pass >= N - 1) {

                done = true;

                message =
                    "整列完了！ すべての数字が" +
                    "小さい順に並びました。";

                stopPlay();

            } else {

                message =
                    pass + "周目が終了しました。" +
                    "右側の " + pass +
                    " 個の位置が確定しました。";
            }

        } else {

            message =
                "次は " + data[j] +
                " と " + data[j + 1] +
                " を比較します。";
        }

        phase = "compare";
    }

    render();

}


// 自動再生

function autoPlay() {

    if (!playing || done) {
        return;
    }

    step();

    if (!playing || done) {
        return;
    }

    const speed = Number(
        document.getElementById("speed").value
    );

    timer = setTimeout(autoPlay, speed);

}


// 自動再生の停止

function stopPlay() {

    playing = false;

    clearTimeout(timer);

    timer = null;

}


// Play / Pause の切り替え

function togglePlay() {

    if (done) {
        return;
    }

    if (playing) {

        stopPlay();

    } else {

        playing = true;

        autoPlay();
    }

    render();

}


// 初期化

function reset() {

    stopPlay();

    data = shuffle();

    pass = 0;
    j = 0;

    comparisons = 0;
    swaps = 0;

    phase = "compare";

    done = false;

    history = [];

    message =
        "バブルソートは、隣り合う2つの数字を" +
        "比較し、順番が逆なら交換する" +
        "整列アルゴリズムです。";

    createBars();

    render();

}


// アプリ起動時に初期化

reset();

</script>

</body>
</html>

""", height=780, scrolling=False)
