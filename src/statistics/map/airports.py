import pandas as pd
import plotly.express as px
from pathlib import Path

# Чтение данных
path = Path("resources/processed/temp/")
flights = pd.read_csv(path / "json_parsed.csv", sep="|")

# Подсчёт рейсов по аэропортам вылета
dep_counts = flights['DepAirport'].value_counts().reset_index()
dep_counts.columns = ['Airport', 'Departures']

# Подсчёт рейсов по аэропортам прилёта
arr_counts = flights['ArrAirport'].value_counts().reset_index()
arr_counts.columns = ['Airport', 'Arrivals']

# Объединение
airport_stats = pd.merge(dep_counts, arr_counts, on='Airport', how='outer').fillna(0)
airport_stats['Total'] = airport_stats['Departures'] + airport_stats['Arrivals']

# Координаты аэропортов (тот же словарь, что и выше)
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

# Фильтрация
airport_stats = airport_stats[airport_stats['Airport'].isin(airport_coords.keys())]
airport_stats['Lat'] = airport_stats['Airport'].map(lambda x: airport_coords[x][0])
airport_stats['Lon'] = airport_stats['Airport'].map(lambda x: airport_coords[x][1])

# Отрисовка
fig = px.scatter_geo(
    airport_stats,
    lat='Lat',
    lon='Lon',
    size='Total',
    hover_name='Airport',
    hover_data=['Departures', 'Arrivals', 'Total'],
    title='Аэропорты и количество рейсов',
    projection='natural earth',
    size_max=50,
    color='Total',
    color_continuous_scale='Reds'
)

fig.update_layout(height=700, width=1200)
fig.write_html('airports_map.html')
fig.show()