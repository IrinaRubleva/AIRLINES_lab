import re
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

# Настройки
MIN_SHARED_FLIGHTS_THRESHOLD = 2
md_path = Path("../../shadow_groups_finder/SPIES.md")

print(f"🔍 Читаем данные из: {md_path}")

if not md_path.exists():
    print("❌ Файл не найден! Проверьте путь.")
else:
    text = md_path.read_text(encoding='utf-8')
    
    # УЛУЧШЕННОЕ регулярное выражение:
    # [^|]+ означает "любой символ, кроме вертикальной черты |", 
    # что идеально и надежно захватывает содержимое ячейки Markdown-таблицы
    pattern = r'\|\s*(SG_\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'
    
    # Ищем все строки таблицы
    matches = re.findall(pattern, text)
    
    print(f"✅ Найдено {len(matches)} строк в таблице.")
    
    groups_data = []
    for match in matches:
        sg_id, size, flights_str, passengers, sites, intersections = match
        
        try:
            flights = int(flights_str)
        except ValueError:
            continue
            
        # Очищаем имена пассажиров: заменяем <br > и <br> на запятую для разделения
        passengers_clean = passengers.replace('<br >', ',').replace('<br>', ',')
        names = [name.strip() for name in passengers_clean.split(',') if name.strip()]
        
        if flights >= MIN_SHARED_FLIGHTS_THRESHOLD:
            groups_data.append({
                'id': sg_id,
                'size': int(size),
                'flights': flights,
                'names': names
            })
            
    print(f"✅ Отфильтровано {len(groups_data)} групп с >= {MIN_SHARED_FLIGHTS_THRESHOLD} совместными рейсами.")
    
    if not groups_data:
        print("⚠️ Нет данных для построения графа после фильтрации.")
    else:
        # Строим граф
        G = nx.Graph()
        for group in groups_data:
            names = group['names']
            flights = group['flights']
            
            # Создаем клику (полносвязный подграф) для каждой группы
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    u, v = names[i], names[j]
                    if G.has_edge(u, v):
                        G[u][v]['weight'] += flights
                    else:
                        G.add_edge(u, v, weight=flights)
                        
        print(f"🕸️ Граф построен: {G.number_of_nodes()} узлов, {G.number_of_edges()} связей")
        
        if G.number_of_nodes() == 0:
            print("⚠️ Граф пуст.")
        else:
            plt.figure(figsize=(18, 12))
            
            # Алгоритм укладки Фрухтермана-Рейнгольда (spring_layout)
            k_val = 0.5 if G.number_of_nodes() < 50 else 0.15
            pos = nx.spring_layout(G, k=k_val, iterations=60, seed=42)
            
            # Раскрашиваем узлы по компонентам связности (разные группы = разные цвета)
            connected_components = list(nx.connected_components(G))
            cmap = plt.cm.get_cmap('tab20', len(connected_components))
            node_colors = []
            node_sizes = []
            
            for node in G.nodes():
                for i, comp in enumerate(connected_components):
                    if node in comp:
                        node_colors.append(cmap(i))
                        break
                # Размер узла зависит от количества связей (степени вершины)
                node_sizes.append(G.degree(node) * 400 + 600)
                
            nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, edgecolors='black', alpha=0.9)
            
            # Толщина ребер зависит от веса (количества совместных рейсов)
            edge_weights = [G[u][v]['weight'] * 0.6 for u, v in G.edges()]
            nx.draw_networkx_edges(G, pos, width=edge_weights, edge_color='gray', alpha=0.6, arrows=False)
            
            # Подписи узлов
            nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold', font_family='sans-serif')
            
            # Подписи ребер (если их не слишком много, иначе будет визуальная каша)
            if G.number_of_edges() < 150:
                edge_labels = {(u, v): f"{d['weight']} рейс." for u, v, d in G.edges(data=True)}
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color='darkred',
                                             bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none'))
            
            plt.title(f"Сетевой анализ теневых групп (совместные перелеты без общих PNR)\nПоказаны группы с {MIN_SHARED_FLIGHTS_THRESHOLD}+ совместными рейсами (всего {len(groups_data)} групп)", 
                      fontsize=15, fontweight='bold', pad=20)
            
            plt.axis('off')
            plt.tight_layout()
            plt.savefig('shadow_groups_network.png', dpi=300, bbox_inches='tight')
            print("✅ График сохранен как 'shadow_groups_network.png'")
            plt.show()