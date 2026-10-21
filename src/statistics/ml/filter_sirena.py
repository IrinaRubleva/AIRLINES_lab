import pandas as pd

# 1. Читаем файл с разделителем '|'
# skipinitialspace=True убирает лишние пробелы после разделителей
df = pd.read_csv('sirena.csv', sep='|', skipinitialspace=True)

# 2. Очищаем названия колонок от лишних пробелов и пустых имен 
# (из-за символа '|' в начале первой строки первая колонка может называться 'Unnamed: 0')
df.columns = df.columns.str.strip()
if df.columns[0] == '':
    df = df.rename(columns={df.columns[0]: 'Index'})

# 3. Находим колонку с количеством моделей
# Обычно она называется 'Models_Count', но на всякий случай ищем по частичному совпадению
count_col = next((col for col in df.columns if 'Models_Count' in col or 'Count' in col), df.columns[3])

# 4. Приводим значения к числовому типу (на случай, если там затесались пробелы)
df[count_col] = pd.to_numeric(df[count_col], errors='coerce')

# 5. Фильтруем: оставляем только строки, где Models_Count == 3
filtered_df = df[df[count_col] == 3].copy()

# 6. Сохраняем результат в новый CSV-файл с тем же разделителем '|'
filtered_df.to_csv('sirena_top3.csv', sep='|', index=False)

print(f"✅ Найдено записей с Models_Count == 3: {len(filtered_df)}")
print("✅ Результат успешно сохранен в файл: sirena_top3.csv")