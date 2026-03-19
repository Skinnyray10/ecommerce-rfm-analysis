import pandas as pd

def calcular_rfm(df):
    # 1. Limpieza y Formato
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['Total_venta'] = df['Quantity'] * df['UnitPrice']
    df = df[df['Total_venta'] > 0].copy()
    
    # 2. Agrupación
    hoy = df['InvoiceDate'].max()
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (hoy - x.max()).days,
        'InvoiceNo': 'nunique',
        'Total_venta': 'sum'
    })
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    
    # 3. Scoring (Quintiles)
    rfm['R'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm['M'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    # 4. Segmentación (Lógica de Negocio)
    def etiquetar(row):
        r, f = row['R'], row['F']
        if r >= 4 and f >= 4:
            return 'Campeones 🏆'
        elif r >= 3 and f >= 3:
            return 'Leales 🤝'
        elif r <= 2 and f >= 4:
            return 'En Riesgo 🚨'
        elif r <= 2 and f <= 2:
            return 'Perdidos 📉'
        else:
            return 'Promedio 😐'
            
    rfm['Segmento'] = rfm.apply(etiquetar, axis=1)
    return rfm