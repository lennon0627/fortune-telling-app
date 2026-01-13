// Chart.js CDNをロード
const chartScript = document.createElement('script');
chartScript.src = 'https://cdn.jsdelivr.net/npm/chart.js';
document.head.appendChild(chartScript);

// 生年月日の選択肢を生成
function populateDateSelects() {
    const yearSelect = document.getElementById('birthYear');
    const monthSelect = document.getElementById('birthMonth');
    const daySelect = document.getElementById('birthDay');
    const hourSelect = document.getElementById('birthHour');
    const minuteSelect = document.getElementById('birthMinute');

    // 年の選択肢 (1950-2026)
    // 最新の年を最初に表示するため、逆順で追加
    for (let year = 2026; year >= 1950; year--) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
    }
    // 初期値を1990年（範囲の真ん中あたり）に設定
    yearSelect.value = '1990';

    // 月の選択肢
    for (let month = 1; month <= 12; month++) {
        const option = document.createElement('option');
        option.value = month;
        option.textContent = month;
        monthSelect.appendChild(option);
    }
    // 初期値を6月（真ん中）に設定
    monthSelect.value = '6';

    // 日の選択肢
    for (let day = 1; day <= 31; day++) {
        const option = document.createElement('option');
        option.value = day;
        option.textContent = day;
        daySelect.appendChild(option);
    }
    // 初期値を15日（真ん中）に設定
    daySelect.value = '15';

    // 時の選択肢
    for (let hour = 0; hour <= 23; hour++) {
        const option = document.createElement('option');
        option.value = hour;
        option.textContent = hour;
        hourSelect.appendChild(option);
    }

    // 分の選択肢
    for (let minute = 0; minute <= 59; minute++) {
        const option = document.createElement('option');
        option.value = minute;
        option.textContent = minute;
        minuteSelect.appendChild(option);
    }
}

// フォーム送信処理
document.getElementById('fortuneForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const year = parseInt(document.getElementById('birthYear').value);
    const month = parseInt(document.getElementById('birthMonth').value);
    const day = parseInt(document.getElementById('birthDay').value);
    const hour = parseInt(document.getElementById('birthHour').value) || 12;
    const minute = parseInt(document.getElementById('birthMinute').value) || 0;
    const gender = document.querySelector('input[name="gender"]:checked').value;
    const name = document.getElementById('name').value || 'あなた';

    if (!year || !month || !day) {
        alert('生年月日を入力してください');
        return;
    }

    try {
        // ローディング表示
        document.getElementById('totalFortune').innerHTML = '<p>AIが運勢を計算中...</p>';
        document.getElementById('results').classList.remove('hidden');
        document.querySelector('.fortune-card').style.display = 'none';

        // API_BASE_URLが定義されていない場合は相対パスを使用
        const apiUrl = typeof API_BASE_URL !== 'undefined' ? API_BASE_URL : '';
        
        const response = await fetch(`${apiUrl}/api/fortune`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                year,
                month,
                day,
                hour,
                minute,
                gender,
                name
            }),
        });

        if (!response.ok) {
            throw new Error('占いの計算に失敗しました');
        }

        const data = await response.json();
        displayResults(data.results, name);
    } catch (error) {
        console.error('Error:', error);
        alert('占いの計算に失敗しました。もう一度お試しください。');
        document.getElementById('results').classList.add('hidden');
        document.querySelector('.fortune-card').style.display = 'block';
    }
});

// 結果表示
function displayResults(results, name) {
    // 干支×星の組み合わせ
    document.getElementById('etoSignCombo').textContent = 
        `${results.eto_year}年生まれ × ${results.kyusei.star}`;

    // 総合スコア
    document.getElementById('totalScoreDisplay').innerHTML = `
        <div class="score-label">総合運勢スコア</div>
        <div class="score-number">${results.total_score}<small>/100</small></div>
    `;

    // スコア内訳
    const detail = results.score_detail;
    const bonusTotal = Object.values(detail.bonus).reduce((sum, item) => sum + item.score, 0);
    
    document.getElementById('scoreBreakdown').innerHTML = `
        <div class="breakdown-title">スコア内訳</div>
        
        <div class="breakdown-row main-row">
            <span class="bd-label">${detail.base.name}</span>
            <span class="bd-val">${detail.base.score}点</span>
        </div>
        
        <div class="breakdown-sub-list">
            ${Object.values(detail.bonus).map(item => `
                <div class="breakdown-row">
                    <span class="bd-label">+ ${item.name}</span>
                    <span class="bd-val">+${item.score}点</span>
                </div>
            `).join('')}
        </div>
        
        <div class="breakdown-note">※小数点以下は切り捨て</div>
    `;

    // ランキング順位
    document.getElementById('rankingPosition').textContent = 
        `108通り中 第${results.rank}位`;

    // 総合鑑定メッセージ
    document.getElementById('totalFortune').innerHTML = results.fortune_text;

    // 九星気学
    document.getElementById('kyuseiStar').textContent = results.kyusei.star;
    document.getElementById('kyuseiDesc').innerHTML = `
        <p>${results.kyusei.desc}</p>
        <div class="lucky-info">
            <div class="luck-item">ラッキーカラー: <span>${results.kyusei.lucky_color}</span></div>
            <div class="luck-item">ラッキー方位: <span>${results.kyusei.lucky_direction}</span></div>
            <div class="luck-item">ラッキーフード: <span>${results.kyusei.lucky_food}</span></div>
            <div class="luck-item">開運アクション: <span>${results.kyusei.lucky_action}</span></div>
        </div>
    `;

    // 四柱推命
    const shichu = results.shichu;
    document.getElementById('shichuPillars').innerHTML = `
        <div class="pillar-row">
            <span class="pillar-label">年柱:</span>
            <span class="pillar-value">${shichu.year}</span>
            <span class="pillar-label">月柱:</span>
            <span class="pillar-value">${shichu.month}</span>
        </div>
        <div class="pillar-row">
            <span class="pillar-label">日柱:</span>
            <span class="pillar-value">${shichu.day}</span>
            <span class="pillar-label">時柱:</span>
            <span class="pillar-value">${shichu.hour}</span>
        </div>
        <div class="kubou-display">
            <strong>空亡（天中殺）:</strong> ${shichu.kubou}
        </div>
    `;

    // 五行バランスバー
    const elements = shichu.elements;
    const maxElement = Math.max(...Object.values(elements));
    document.getElementById('shichuElements').innerHTML = `
        <div class="element-bars">
            ${Object.entries(elements).map(([name, count]) => `
                <div class="element-item">
                    <span class="element-name">${name}</span>
                    <div class="element-bar">
                        <div class="element-fill" style="width: ${(count / 8) * 100}%"></div>
                    </div>
                    <span class="element-count">${count}</span>
                </div>
            `).join('')}
        </div>
    `;

    document.getElementById('shichuDesc').innerHTML = `<p>${shichu.desc}</p>`;

    // 五行レーダーチャート（Chart.jsが読み込まれた後に実行）
    setTimeout(() => {
        if (typeof Chart !== 'undefined') {
            const ctx = document.getElementById('gogyouRadarChart').getContext('2d');
            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['木', '火', '土', '金', '水'],
                    datasets: [{
                        label: '五行バランス',
                        data: [
                            elements['木'],
                            elements['火'],
                            elements['土'],
                            elements['金'],
                            elements['水']
                        ],
                        backgroundColor: 'rgba(102, 126, 234, 0.2)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(118, 75, 162, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(118, 75, 162, 1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 8,
                            ticks: {
                                stepSize: 2,
                                font: { size: 12 }
                            },
                            pointLabels: {
                                font: { size: 14, weight: 'bold' }
                            }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
    }, 500);

    // 五星三心
    document.getElementById('goseiType').textContent = results.gosei.type;
    document.getElementById('goseiDesc').innerHTML = `<p>${results.gosei.desc}</p>`;

    // カバラ数秘術
    document.getElementById('kabbalahNumber').textContent = 
        `運命数: ${results.kabbalah.num}`;
    document.getElementById('kabbalahDesc').innerHTML = 
        `<p><strong>${results.kabbalah.desc}</strong></p>`;

    // 宿曜占星術
    document.getElementById('sukuyoStar').textContent = results.sukuyo.star;
    document.getElementById('sukuyoDesc').innerHTML = `<p>${results.sukuyo.desc}</p>`;
    document.getElementById('sukuyoFortune').innerHTML = `<p>${results.sukuyo.fortune}</p>`;
    document.getElementById('sukuyoWork').innerHTML = `<p>${results.sukuyo.work}</p>`;
    document.getElementById('sukuyoLove').innerHTML = `<p>${results.sukuyo.love}</p>`;

    // コピー用テキスト生成
    generateCopyText(results, name);
}

// コピー用テキスト生成
function generateCopyText(results, name) {
    const text = `
【${name}さんの究極の運勢占い結果】

■ 2026年 総合運勢スコア
${results.eto_year}年生まれ × ${results.kyusei.star}
総合スコア: ${results.total_score}/100点
ランキング: 108通り中 第${results.rank}位

${results.fortune_text.replace(/<[^>]*>/g, '').trim()}

■ 九星気学
${results.kyusei.star}
${results.kyusei.desc}
ラッキーカラー: ${results.kyusei.lucky_color}
ラッキー方位: ${results.kyusei.lucky_direction}
ラッキーフード: ${results.kyusei.lucky_food}
開運アクション: ${results.kyusei.lucky_action}

■ 四柱推命
年柱: ${results.shichu.year}  月柱: ${results.shichu.month}
日柱: ${results.shichu.day}  時柱: ${results.shichu.hour}
空亡: ${results.shichu.kubou}
${results.shichu.desc.replace(/<[^>]*>/g, '')}

■ 五星三心占い
${results.gosei.type}
${results.gosei.desc}

■ カバラ数秘術
運命数: ${results.kabbalah.num}
${results.kabbalah.desc}

■ 宿曜占星術
${results.sukuyo.star}
性格: ${results.sukuyo.desc}
2026年の運勢: ${results.sukuyo.fortune}
仕事: ${results.sukuyo.work}
恋愛: ${results.sukuyo.love}

---
この結果をもとに、さらに詳しい占いをAIに依頼してみてください！
`.trim();

    document.getElementById('copyText').value = text;
}

// コピーボタン
document.getElementById('copyBtn').addEventListener('click', () => {
    const copyText = document.getElementById('copyText');
    copyText.select();
    document.execCommand('copy');
    
    const btn = document.getElementById('copyBtn');
    const originalText = btn.textContent;
    btn.textContent = '✅ コピーしました！';
    setTimeout(() => {
        btn.textContent = originalText;
    }, 2000);
});

// リセット機能
function resetForm() {
    document.getElementById('results').classList.add('hidden');
    document.querySelector('.fortune-card').style.display = 'block';
    document.getElementById('fortuneForm').reset();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ページ読み込み時に日付選択肢を生成
populateDateSelects();
