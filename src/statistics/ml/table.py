import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ============================================================
# 1. ЧТЕНИЕ И ПОДГОТОВКА ДАННЫХ ИЗ boarding.csv
# ============================================================
file_path = Path("boarding.csv")

# Читаем файл. Исходя из структуры, разделитель - '|', и есть скрытый индекс (Rank)
try:
    df = pd.read_csv(
        file_path, 
        sep='|', 
        header=0, 
        names=['Rank', 'ID', 'Total_Score', 'Models_Count', 'Models_List'],
        skiprows=1 # Пропускаем первую строку, если там слиплись заголовки
    )
except Exception:
    # Фоллбэк, если формат немного другой
    df = pd.read_csv(file_path, sep='|')

# Очистка данных
df = df.dropna(subset=['ID', 'Total_Score'])
df['Total_Score'] = pd.to_numeric(df['Total_Score'], errors='coerce')
df['Models_Count'] = pd.to_numeric(df['Models_Count'], errors='coerce')

# Сортируем по скорингу и берем топ-15 для читаемости на графике
df_top = df.sort_values('Total_Score', ascending=False).head(15).reset_index(drop=True)

print(f"Загружено записей: {len(df)}")
print(f"Для графика отобрано топ-{len(df_top)} записей")

# ============================================================
# 2. ОТРИСОВКА СТРОГОГО ТЕМНОГО ГРАФИКА (PLOTLY)
# ============================================================
# Цвета в строгом стиле: красный для 3+ моделей, оранжевый для 2, приглушенный синий для 1
colors = []
for count in df_top['Models_Count']:
    if count >= 3:
        colors.append('#ef553b')      # Строгий красный
    elif count == 2:
        colors.append('#ffa15a')      # Приглушенный оранжевый
    else:
        colors.append('#636efa')      # Нейтральный синий

fig = go.Figure()

fig.add_trace(go.Bar(
    y=df_top['ID'][::-1],          # Переворачиваем, чтобы топ был сверху
    x=df_top['Total_Score'][::-1],
    orientation='h',
    marker_color=colors,
    text=df_top['Models_Count'][::-1],
    textposition='outside',
    textfont=dict(color='#888888', size=11, family='Consolas, monospace'),
    hovertemplate="<b>ID:</b> %{y}<br><b>Score:</b> %{x}<br><b>Models:</b> %{text}<extra></extra>"
))

fig.update_layout(
    template='plotly_dark',
    title=dict(
        text='TOP SUSPECTS: Anomaly Scoring',
        font=dict(size=18, color='#cccccc', family='Consolas, monospace'),
        x=0.05,
        xanchor='left'
    ),
    xaxis_title='Total Anomaly Score',
    yaxis_title='Passenger ID',
    font=dict(family='Consolas, monospace', color='#d4d4d4'),
    plot_bgcolor='#1e1e1e',
    paper_bgcolor='#1e1e1e',
    height=600,
    margin=dict(l=150, r=50, t=50, b=50),
    xaxis=dict(
        gridcolor='#2d2d2d',
        zerolinecolor='#404040'
    ),
    yaxis=dict(
        gridcolor='#2d2d2d',
        tickfont=dict(size=12)
    ),
    showlegend=False
)

# Сохраняем интерактивный график
fig.write_html('suspects_chart.html', include_plotlyjs='cdn', full_html=True)
print("✅ График сохранен: suspects_chart.html")

# ============================================================
# 3. ГЕНЕРАЦИЯ СТРОГОЙ HTML-ТАБЛИЦЫ (VS CODE STYLE)
# ============================================================
html_table = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {
    background: #1e1e1e;
    color: #d4d4d4;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    padding: 40px;
    margin: 0;
}
h2 {
    color: #cccccc;
    font-weight: 400;
    font-size: 18px;
    margin-bottom: 20px;
    letter-spacing: 1px;
    text-transform: uppercase;
}
table {
    border-collapse: collapse;
    width: 100%;
    font-size: 13px;
}
th {
    text-align: left;
    padding: 10px 14px;
    border-bottom: 1px solid #404040;
    color: #858585;
    font-weight: 400;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.5px;
}
td {
    padding: 8px 14px;
    border-bottom: 1px solid #2d2d2d;
    color: #d4d4d4;
}
tr:hover td {
    background: #2a2d2e;
}
.num {
    text-align: right;
    font-variant-numeric: tabular-nums;
}
.models {
    color: #9cdcfe;
    font-size: 12px;
}
.rank {
    color: #6a6a6a;
    width: 40px;
    text-align: center;
}
.score-high {
    color: #f48771;
    font-weight: bold;
}
</style>
</head>
<body>

<h2>Anomaly Detection Results (Top 15)</h2>

<table>
    <thead>
        <tr>
            <th class="rank">#</th>
            <th>ID</th>
            <th class="num">Total Score</th>
            <th class="num">Models</th>
            <th>Detected by</th>
        </tr>
    </thead>
    <tbody>
"""

for i, row in df_top.iterrows():
    score_class = "score-high" if row['Models_Count'] >= 3 else ""
    
    html_table += f"""
        <tr>
            <td class="rank">{int(row['Rank']) if pd.notna(row['Rank']) else i+1}</td>
            <td>{row['ID']}</td>
            <td class="num {score_class}">{row['Total_Score']:,.2f}</td>
            <td class="num">{int(row['Models_Count'])}</td>
            <td class="models">{row['Models_List']}</td>
        </tr>
    """

html_table += """
    </tbody>
</table>

</body>
</html>
"""

with open('suspects_table.html', 'w', encoding='utf-8') as f:
    f.write(html_table)

print("✅ Таблица сохранена: suspects_table.html")
print("💡 Откройте оба файла в браузере для просмотра.")


from playwright.sync_api import sync_playwright
from pathlib import Path

html_file = Path("suspects_chart.html").resolve()
png_file = Path("suspects_chart.png")

print("📸 Делаем скриншот таблицы...")
with sync_playwright() as p:
    # Запускаем браузер в фоновом режиме
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1200, 'height': 800})
    
    # Открываем наш HTML файл
    page.goto(f"file:///{html_file.as_posix()}")
    
    # Ждем полной отрисовки
    page.wait_for_timeout(500) 
    
    # Делаем скриншот всей области
    page.screenshot(path=str(png_file), full_page=True)
    browser.close()

print(f"✅ Таблица сохранена как {png_file}")