import pandas as pd

# Cargar el archivo de Excel
archivo = "delta_costos.xlsx"
productos = pd.read_excel(archivo, sheet_name="Productos")
materiales = pd.read_excel(archivo, sheet_name="Materiales")
mano_obra = pd.read_excel(archivo, sheet_name="Mano_Obra")
overhead = pd.read_excel(archivo, sheet_name="Overhead")

# -------------------------------
# Selección de producto (ejemplo)
# -------------------------------
producto_id = "P001"  # Cambiar por selección dinámica si se usa Streamlit
producto = productos[productos["ID_Producto"] == producto_id].iloc[0]

# -------------------------------
# Costo de materiales
# -------------------------------
ids_materiales = producto["ID_Materiales"].split(";")
costo_materiales = 0

for id_mat in ids_materiales:
    mat = materiales[materiales["ID_Material"] == id_mat].iloc[0]
    
    # Suposición: uso total = ancho x alto si es vidrio, o perímetro si es aluminio
    if mat["Tipo"] == "Cristal":
        uso = producto["Ancho (ft)"] * producto["Alto (ft)"]
    elif mat["Tipo"] == "Aluminio":
        uso = 2 * (producto["Ancho (ft)"] + producto["Alto (ft)"])
    else:
        uso = 1  # Por unidad
    
    desperdicio = uso * (mat["Pérdida (%)"] / 100)
    uso_total = uso + desperdicio
    
    costo = uso_total * mat["Costo_Unidad ($)"]
    costo_materiales += costo

# -------------------------------
# Costo de mano de obra
# -------------------------------
tipo_empleado = producto["Tipo_Mano_Obra"]
costo_hora = mano_obra[mano_obra["Tipo_Mano_Obra"] == tipo_empleado]["Costo_Hora ($)"].values[0]
tiempo_horas = producto["Tiempo_Fabricación (min)"] / 60
costo_labor = costo_hora * tiempo_horas

# -------------------------------
# Costo de overhead
# -------------------------------
costo_overhead = 0
for _, row in overhead.iterrows():
    if row["Método_Distribución"] == "Por Hora":
        costo_overhead += (row["Costo_Mensual ($)"] / (160 * 30)) * producto["Tiempo_Fabricación (min)"] / 60
    elif row["Método_Distribución"] == "Por Unidad Producida":
        # Estimamos unas 1000 unidades por mes
        costo_overhead += row["Costo_Mensual ($)"] / 1000

# -------------------------------
# Costo total
# -------------------------------
costo_total_unitario = costo_materiales + costo_labor + costo_overhead

# -------------------------------
# Resultado
# -------------------------------
print(f"Producto seleccionado: {producto['Nombre']}")
print(f"Costo de materiales: ${costo_materiales:.2f}")
print(f"Costo de mano de obra: ${costo_labor:.2f}")
print(f"Costo de overhead: ${costo_overhead:.2f}")
print(f"👉 Costo total unitario: ${costo_total_unitario:.2f}")

