import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

# Путь к данным
path = Path("../../../resources/processed/temp/")
flights = pd.read_csv(path / "json_parsed.csv", sep="|")

# Группировка по маршрутам
routes = flights.groupby(['DepAirport', 'ArrAirport', 'DepCity', 'ArrCity']).size().reset_index(name='count')
routes = routes.sort_values('count', ascending=False)

# Словарь координат
airport_coords = {
    'SVO': (55.9726, 37.4146), 'DME': (55.4088, 37.9063), 'VKO': (55.5914, 37.2615),
    'WAW': (52.1657, 20.9671), 'BOS': (42.3656, -71.0096), 'PIT': (40.4915, -80.2329),
    'DTW': (42.2162, -83.3554), 'LGA': (40.7769, -73.8740), 'GRB': (44.4851, -88.1296),
    'CDG': (49.0097, 2.5479), 'AMS': (52.3086, 4.7639), 'FRA': (50.0333, 8.5706),
    'LHR': (51.4700, -0.4543), 'JFK': (40.6413, -73.7781), 'LAX': (33.9416, -118.4085),
    'ORD': (41.9742, -87.9073), 'ATL': (33.6407, -84.4277), 'MIA': (25.7959, -80.2870),
    'SFO': (37.6213, -122.3790), 'SEA': (47.4502, -122.3088), 'ICN': (37.4602, 126.4407),
    'NRT': (35.7719, 140.3929), 'PEK': (40.0799, 116.6031), 'SHA': (31.1979, 121.3364),
    'BKK': (13.6900, 100.7501), 'SIN': (1.3644, 103.9915), 'DXB': (25.2532, 55.3657),
    'DEL': (28.5562, 77.1000), 'MUM': (19.0896, 72.8656), 'SYD': (-33.9399, 151.1753),
    'MEL': (-37.6690, 144.8410), 'YYZ': (43.6777, -79.6248), 'YVR': (49.1939, -123.1844),
    'MEX': (19.4363, -99.0721), 'GRU': (-23.4356, -46.4731), 'EZE': (-34.8222, -58.5358),
    'LIM': (-12.0219, -77.1143), 'BOG': (4.7016, -74.1469), 'SCL': (-33.3930, -70.7858),
    'JNB': (-26.1392, 28.2460), 'CAI': (30.1219, 31.4056), 'NBO': (-1.3192, 36.9278),
    'ADD': (8.9779, 38.7993), 'MAD': (40.4936, -3.5668), 'BCN': (41.2974, 2.0833),
    'FCO': (41.8003, 12.2389), 'MUC': (48.3537, 11.7861), 'ZRH': (47.4647, 8.5492),
    'VIE': (48.1103, 16.5697), 'PRG': (50.1008, 14.2632), 'BUD': (47.4369, 19.2556),
    'ARN': (59.6519, 17.9186), 'OSL': (60.1939, 11.1004), 'CPH': (55.6181, 12.6561),
    'HEL': (60.3172, 24.9633), 'DUB': (53.4213, -6.2701), 'LIS': (38.7813, -9.1359),
    'ATH': (37.9364, 23.9445), 'IST': (41.2753, 28.7519), 'TLV': (32.0114, 34.8867),
    'RUH': (24.9576, 46.6988), 'DOH': (25.2731, 51.6080), 'AUH': (24.4330, 54.6511),
    'KUL': (2.7456, 101.7072), 'CGK': (-6.1256, 106.6559), 'MNL': (14.5086, 121.0194),
    'HKG': (22.3080, 113.9185), 'TPE': (25.0777, 121.2322), 'BNE': (-27.3842, 153.1175),
    'PER': (-31.9403, 115.9669), 'AKL': (-37.0082, 174.7850),
}

# Фильтрация маршрутов
routes_filtered = routes[
    routes['DepAirport'].isin(airport_coords.keys()) & 
    routes['ArrAirport'].isin(airport_coords.keys())
].copy()

print(f"Маршрутов с координатами: {len(routes_filtered)}")

fig = go.Figure()

# === 1. Градиентные линии с кривизной ===
max_count = routes_filtered['count'].max()

for _, row in routes_filtered.iterrows():
    dep = airport_coords[row['DepAirport']]
    arr = airport_coords[row['ArrAirport']]
    
    normalized = row['count'] / max_count
    color = f"rgba({int(100 + 155 * normalized)}, {int(150 - 100 * normalized)}, {int(255 - 200 * normalized)}, {0.3 + 0.5 * normalized})"
    width = 0.5 + 2.5 * normalized  # Чуть уменьшил макс. толщину для аккуратности
    
    distance = np.sqrt((dep[0] - arr[0])**2 + (dep[1] - arr[1])**2)
    arc_height = distance * 0.3
    
    lats = np.linspace(dep[0], arr[0], 100)
    lons = np.linspace(dep[1], arr[1], 100)
    
    for i in range(1, 99):
        t = i / 100
        lats[i] += arc_height * np.sin(np.pi * t) * 0.3
    
    # Убрали <b> из hover-текста
    fig.add_trace(go.Scattergeo(
        lon=lons,
        lat=lats,
        mode='lines',
        line=dict(width=width, color=color),
        opacity=0.6,
        hoverinfo='text',
        text=f"{row['DepCity']} -> {row['ArrCity']}<br>Рейсов: {row['count']}<br>Аэропорты: {row['DepAirport']} -> {row['ArrAirport']}",
        showlegend=False
    ))

# === 2. Логарифмический размер точек аэропортов ===
for airport, coords in airport_coords.items():
    if airport in routes_filtered['DepAirport'].values or airport in routes_filtered['ArrAirport'].values:
        airport_count = routes_filtered[
            (routes_filtered['DepAirport'] == airport) | 
            (routes_filtered['ArrAirport'] == airport)
        ]['count'].sum()
        
        # ЛОГАРИФМИЧЕСКОЕ МАСШТАБИРОВАНИЕ:
        # np.log1p(x) = ln(1 + x). Это сглаживает огромные перепады.
        # База = 6 (чтобы даже маленькие аэропорты были видны)
        # Множитель = 3.5 (контролирует рост)
        # min(35, ...) не дает крупным хабам стать гигантскими пятнами
        size = min(35, 6 + 3.5 * np.log1p(airport_count))
        
        fig.add_trace(go.Scattergeo(
            lon=[coords[1]],
            lat=[coords[0]],
            mode='markers+text',
            marker=dict(
                size=size, 
                color='rgba(255, 80, 80, 0.85)',
                line=dict(width=1.5, color='white'),
                symbol='circle',
                opacity=0.9
            ),
            text=[airport],
            textposition='top center',
            textfont=dict(size=9, color='white', family='Arial'), # Убрали Arial Black (он жирный)
            hoverinfo='text',
            hovertext=f"{airport}<br>Всего рейсов: {airport_count}",
            showlegend=False
        ))

# === 3. Адаптивный темный фон ===
fig.update_layout(
    title=dict(
        text='Карта рейсов Yoyoflot Airline<br>Интерактивная визуализация маршрутной сети', # Убрали <b> и <sup>
        font=dict(size=18, color='white', family='Arial'), # Чуть меньше для мобильных
        x=0.5,
        xanchor='center'
    ),
    paper_bgcolor='rgba(20, 30, 50, 1)',
    plot_bgcolor='rgba(20, 30, 50, 1)',
    font=dict(color='white', family='Arial'),
    
    # ВАЖНО ДЛЯ МОБИЛЬНЫХ: убираем лишние отступы по краям
    margin=dict(l=0, r=0, t=50, b=0),
    autosize=True, # Разрешаем автоматический размер
    
    geo=dict(
        showland=True,
        landcolor='rgba(40, 50, 70, 0.8)',
        showocean=True,
        oceancolor='rgba(10, 20, 40, 0.9)',
        showcountries=True,
        countrycolor='rgba(80, 100, 120, 0.5)',
        showcoastlines=True,
        coastlinecolor='rgba(100, 120, 140, 0.3)',
        projection=dict(type='natural earth'),
        lonaxis=dict(range=[-180, 180], showgrid=True, gridcolor='rgba(100, 120, 140, 0.15)'),
        lataxis=dict(range=[-60, 85], showgrid=True, gridcolor='rgba(100, 120, 140, 0.15)'),
        bgcolor='rgba(20, 30, 50, 1)'
    ),
    # Убираем жесткие width/height, чтобы работало autosize
    legend=dict(
        x=0.02,
        y=0.98,
        bgcolor='rgba(20, 30, 50, 0.8)',
        bordercolor='rgba(100, 120, 140, 0.5)',
        font=dict(size=11, color='white')
    ),
    annotations=[
        dict(
            x=0.02, y=0.02,
            xref='paper', yref='paper',
            text=f'Всего маршрутов: {len(routes_filtered)}<br>Всего рейсов: {routes_filtered["count"].sum()}', # Убрали <b>
            showarrow=False,
            font=dict(size=12, color='white'),
            bgcolor='rgba(20, 30, 50, 0.8)',
            bordercolor='rgba(100, 120, 140, 0.5)',
            borderwidth=1
        )
    ]
)

# Сохранение с настройками для мобильных устройств
fig.write_html(
    'flight_map_responsive.html',
    full_html=True,          # Создает полноценную HTML-страницу
    include_plotlyjs='cdn',  # Подгружает библиотеку через интернет (файл будет легким)
    config={'responsive': True} # Включает адаптивность при изменении размера окна
)

print("\n✅ Карта сохранена: flight_map_responsive.html")
print("💡 Откройте этот файл в браузере и сожмите окно, чтобы проверить адаптивность.")

fig.show(config={'responsive': True})