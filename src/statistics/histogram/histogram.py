import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 7)
plt.rcParams['font.size'] = 11

file_path = Path("artefacts.csv")
if not file_path.exists():
    file_path = Path("../../documents_checker/artefacts.csv")

print(f"Загрузка данных из: {file_path}")

try:
    
    df = pd.read_csv(file_path, sep=';')
    print(f"Успешно загружено {len(df)} записей об артефактах.")
    
    # Преобразуем Delta в числовой формат на случай, если там есть пробелы
    df['Delta'] = pd.to_numeric(df['Delta'], errors='coerce')
    df = df.dropna(subset=['Delta'])
    
    # Находим самые частые аномалии для аннотации
    top_deltas = df['Delta'].value_counts().head(3)
    print("\n📊 Топ-3 самых частых аномальных дельт (лет):")
    for delta, count in top_deltas.items():
        print(f"   {int(delta)} лет (паспорт выдан раньше рождения): {count} случаев")

    fig, ax = plt.subplots()
    sns.histplot(data=df, x='Delta', binwidth=1, color='steelblue', edgecolor='white', alpha=0.8)
   
    most_common_delta = int(top_deltas.index[0])
    most_common_count = int(top_deltas.iloc[0])
    
    for patch in ax.patches:
        if int(patch.get_x()) == most_common_delta:
            patch.set_facecolor('#ff4444')
            patch.set_edgecolor('#cc0000')
            
    ax.annotate(f'Самый частый артефакт:\n{most_common_count} записей\n(паспорт выдан\nна {abs(most_common_delta)} лет\nраньше рождения!)',
                xy=(most_common_delta, most_common_count),
                xytext=(most_common_delta + 8, most_common_count * 0.8),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=11, fontweight='bold', color='darkred',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8))

    ax.set_title('Распределение аномальной дельты (Год выдачи паспорта - Год рождения)\nОтрицательные значения = физически невозможная ситуация', 
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Дельта (лет)', fontsize=12)
    ax.set_ylabel('Количество записей', fontsize=12)
    
    ax.set_xlim(-105, 5)
    
    plt.tight_layout()
    plt.savefig('artefacts_delta_histogram.png', dpi=300, bbox_inches='tight')
    print("\n График сохранен как 'artefacts_delta_histogram.png'")
    plt.show()

except FileNotFoundError:
    print("Ошибка: Файл artefacts.csv не найден.")
    print("Убедитесь, что вы запустили скрипт documents_checker.py, который его генерирует.")
except Exception as e:
    print(f"Произошла ошибка: {e}")