import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from collections import defaultdict

# Путь к данным
path = Path("../../../resources/processed/temp/")
flights = pd.read_csv(path / "json_parsed.csv", sep="|")

# Группировка по маршрутам и подсчёт количества рейсов
routes = flights.groupby(['DepAirport', 'ArrAirport', 'DepCity', 'ArrCity']).size().reset_index(name='count')
routes = routes.sort_values('count', ascending=False)

print(f"Всего уникальных маршрутов: {len(routes)}")
print(f"Топ-10 маршрутов:")
print(routes.head(10))

# Словарь координат аэропортов (IATA код -> (lat, lon))
# Дополните этот словарь аэропортами из ваших данных
airport_coords = {
    'SVO': (55.9726, 37.4146),    # Moscow Sheremetyevo
    'DME': (55.4088, 37.9063),    # Moscow Domodedovo
    'VKO': (55.5914, 37.2615),    # Moscow Vnukovo
    'WAW': (52.1657, 20.9671),    # Warsaw
    'BOS': (42.3656, -71.0096),   # Boston
    'PIT': (40.4915, -80.2329),   # Pittsburgh
    'DTW': (42.2162, -83.3554),   # Detroit
    'LGA': (40.7769, -73.8740),   # New York LaGuardia
    'GRB': (44.4851, -88.1296),   # Green Bay
    'CDG': (49.0097, 2.5479),     # Paris Charles de Gaulle
    'AMS': (52.3086, 4.7639),     # Amsterdam
    'FRA': (50.0333, 8.5706),     # Frankfurt
    'LHR': (51.4700, -0.4543),    # London Heathrow
    'JFK': (40.6413, -73.7781),   # New York JFK
    'LAX': (33.9416, -118.4085),  # Los Angeles
    'ORD': (41.9742, -87.9073),   # Chicago O'Hare
    'ATL': (33.6407, -84.4277),   # Atlanta
    'MIA': (25.7959, -80.2870),   # Miami
    'SFO': (37.6213, -122.3790),  # San Francisco
    'SEA': (47.4502, -122.3088),  # Seattle
    'ICN': (37.4602, 126.4407),   # Seoul Incheon
    'NRT': (35.7719, 140.3929),   # Tokyo Narita
    'PEK': (40.0799, 116.6031),   # Beijing
    'SHA': (31.1979, 121.3364),   # Shanghai Hongqiao
    'BKK': (13.6900, 100.7501),   # Bangkok
    'SIN': (1.3644, 103.9915),    # Singapore
    'DXB': (25.2532, 55.3657),    # Dubai
    'DEL': (28.5562, 77.1000),    # Delhi
    'MUM': (19.0896, 72.8656),    # Mumbai
    'SYD': (-33.9399, 151.1753),  # Sydney
    'MEL': (-37.6690, 144.8410),  # Melbourne
    'YYZ': (43.6777, -79.6248),   # Toronto
    'YVR': (49.1939, -123.1844),  # Vancouver
    'MEX': (19.4363, -99.0721),   # Mexico City
    'GRU': (-23.4356, -46.4731),  # São Paulo
    'EZE': (-34.8222, -58.5358),  # Buenos Aires Ezeiza
    'LIM': (-12.0219, -77.1143),  # Lima
    'BOG': (4.7016, -74.1469),    # Bogotá
    'SCL': (-33.3930, -70.7858),  # Santiago
    'JNB': (-26.1392, 28.2460),   # Johannesburg
    'CAI': (30.1219, 31.4056),    # Cairo
    'NBO': (-1.3192, 36.9278),    # Nairobi
    'ADD': (8.9779, 38.7993),     # Addis Ababa
    'MAD': (40.4936, -3.5668),    # Madrid
    'BCN': (41.2974, 2.0833),     # Barcelona
    'FCO': (41.8003, 12.2389),    # Rome
    'MUC': (48.3537, 11.7861),    # Munich
    'ZRH': (47.4647, 8.5492),     # Zurich
    'VIE': (48.1103, 16.5697),    # Vienna
    'PRG': (50.1008, 14.2632),    # Prague
    'BUD': (47.4369, 19.2556),    # Budapest
    'WAW': (52.1657, 20.9671),    # Warsaw
    'ARN': (59.6519, 17.9186),    # Stockholm
    'OSL': (60.1939, 11.1004),    # Oslo
    'CPH': (55.6181, 12.6561),    # Copenhagen
    'HEL': (60.3172, 24.9633),    # Helsinki
    'DUB': (53.4213, -6.2701),    # Dublin
    'LIS': (38.7813, -9.1359),    # Lisbon
    'ATH': (37.9364, 23.9445),    # Athens
    'IST': (41.2753, 28.7519),    # Istanbul
    'TLV': (32.0114, 34.8867),    # Tel Aviv
    'RUH': (24.9576, 46.6988),    # Riyadh
    'DOH': (25.2731, 51.6080),    # Doha
    'AUH': (24.4330, 54.6511),    # Abu Dhabi
    'KUL': (2.7456, 101.7072),    # Kuala Lumpur
    'CGK': (-6.1256, 106.6559),   # Jakarta
    'MNL': (14.5086, 121.0194),   # Manila
    'HKG': (22.3080, 113.9185),   # Hong Kong
    'TPE': (25.0777, 121.2322),   # Taipei
    'BNE': (-27.3842, 153.1175),  # Brisbane
    'PER': (-31.9403, 115.9669),  # Perth
    'AKL': (-37.0082, 174.7850),  # Auckland
}

# Фильтрация маршрутов, для которых есть координаты обоих аэропортов
routes_filtered = routes[
    routes['DepAirport'].isin(airport_coords.keys()) & 
    routes['ArrAirport'].isin(airport_coords.keys())
].copy()

print(f"\nМаршрутов с координатами: {len(routes_filtered)}")

# Создание карты
fig = go.Figure()

# Добавление линий рейсов
for _, row in routes_filtered.iterrows():
    dep = airport_coords[row['DepAirport']]
    arr = airport_coords[row['ArrAirport']]
    
    # Прозрачность зависит от количества рейсов
    opacity = min(0.4, row['count'] / 20)  # было 0.8 и /10
    width = min(1.0, row['count'] / 15)    # было 3 и /5

    fig.add_trace(go.Scattergeo(
        lon=[dep[1], arr[1]],
        lat=[dep[0], arr[0]],
        mode='lines',
        line=dict(width=width, color='blue'),
        opacity=opacity,
        hoverinfo='text',
        text=f"{row['DepCity']} → {row['ArrCity']}<br>{row['count']} рейсов",
        showlegend=False

    ))

# Добавление точек аэропортов
for airport, coords in airport_coords.items():
    # Проверяем, есть ли этот аэропорт в данных
    if airport in routes_filtered['DepAirport'].values or airport in routes_filtered['ArrAirport'].values:
        fig.add_trace(go.Scattergeo(
            lon=[coords[1]],
            lat=[coords[0]],
            mode='markers',
            marker=dict(size=6, color='red', line=dict(width=1, color='white')),
            text=[airport],
            hoverinfo='text',
            showlegend=False
        ))

# Настройка карты
fig.update_layout(
    title=dict(
        text='Карта рейсов Yoyoflot Airline<br><sup>Интерактивная визуализация маршрутов</sup>',
        font=dict(size=20)
    ),
    geo=dict(
        showland=True,
        landcolor='rgb(217, 217, 217)',
        showocean=True,
        oceancolor='rgb(229, 229, 229)',
        showcountries=True,
        countrycolor='rgb(200, 200, 200)',
        projection=dict(type='natural earth'),
        lonaxis=dict(range=[-180, 180]),
        lataxis=dict(range=[-60, 85])
    ),
    height=800,
    width=1200
)

# Сохранение и отображение
fig.write_html('flight_map.html')
fig.write_image('flight_map.png', width=1200, height=800, scale=2)
print("\n✅ Карта сохранена:")
print("   - flight_map.html (интерактивная)")
print("   - flight_map.png (статичная)")

fig.show()