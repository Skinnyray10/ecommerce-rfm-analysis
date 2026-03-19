import pandas as pd
import seaborn as sns 
# 1. Cargar los datos
df = pd.read_csv('online_retail.csv')
df = df.dropna(subset=['CustomerID'])

df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')

# Eliminamos espacios en blanco por si acaso
df['InvoiceDate'] = df['InvoiceDate'].astype(str).str.strip()

# Convertimos y forzamos errores a NaT (Not a Time)
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')

# Esto nos dirá el tipo de dato real de la columna ahora mismo
print(f"El nuevo tipo de dato es: {df['InvoiceDate'].dtype}")

Total_venta = df['Quantity' * df['UnitPrice']]

ventas_por_mes = df.groupby(df['InvoiceDate'].dt.month)['Total'].sum()

sns.lineplot(data=ventas_por_mes)
