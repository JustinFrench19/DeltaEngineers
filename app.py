import streamlit as st
import pandas as pd

st.title("💰 Análisis de Costos de Producción - Delta Engineers")

archivo = st.file_uploader("📂 Sube el archivo 'delta_costos.xlsx'", type=["xlsx"])

if archivo:
    productos = pd.read_excel(archivo, sheet_name="Productos")
    materiales = pd.read_excel(archivo, sheet_name="Materiales")
    mano_obra = pd.read_excel(archivo, sheet_name="Mano_Obra")
    overhead = pd.read_excel(archivo, sheet_name="Overhead")

    producto_nombres = productos["Nombre"].tolist()
    seleccion = st.selectbox("Selecciona un producto", producto_nombres)
    producto = productos[productos["Nombre"] == seleccion].iloc[0]

    st.subheader(f"🔎 Análisis para: {producto['Nombre']}")

    ids_materiales = producto["ID_Materiales"].split(";")

    # Verificación: debe tener al menos 2 materiales
    if len(ids_materiales) < 2:
        st.error("❌ Esta ventana no tiene suficientes materiales asignados (ej. falta cristal o aluminio). Verifica la columna 'ID_Materiales'.")
        st.stop()

    # Verificación: debe incluir al menos un cristal y un aluminio
    tipos_detectados = []
    for id_mat in ids_materiales:
        match = materiales[materiales["ID_Material"] == id_mat]
        if match.empty:
            st.error(f"❌ El ID de material '{id_mat}' no se encuentra en la hoja de materiales.")
            st.stop()
        tipo = match.iloc[0]["Tipo"]
        tipos_detectados.append(tipo)

    if "Cristal" not in tipos_detectados or "Aluminio" not in tipos_detectados:
        st.error("❌ Faltan materiales esenciales: asegúrate de incluir al menos un cristal y un aluminio.")
        st.stop()

    # Cálculo de materiales
    costo_materiales = 0
    detalles_materiales = []

    for id_mat in ids_materiales:
        mat = materiales[materiales["ID_Material"] == id_mat].iloc[0]
        if mat["Tipo"] == "Cristal":
            uso = producto["Ancho (ft)"] * producto["Alto (ft)"]
        elif mat["Tipo"] == "Aluminio":
            uso = 2 * (producto["Ancho (ft)"] + producto["Alto (ft)"])
        else:
            uso = 1

        desperdicio = uso * (mat["Pérdida (%)"] / 100)
        uso_total = uso + desperdicio
        costo = uso_total * mat["Costo_Unidad ($)"]
        costo_materiales += costo

        detalles_materiales.append({
            "Material": mat["Nombre"],
            "Uso (ft² o ft)": uso,
            "Desperdicio (%)": mat["Pérdida (%)"],
            "Uso Total": uso_total,
            "Costo ($)": costo
        })

    st.write("📦 **Detalle de Materiales**")
    st.dataframe(pd.DataFrame(detalles_materiales))

    # Mano de obra
    tipo_empleado = producto["Tipo_Mano_Obra"]
    costo_hora = mano_obra[mano_obra["Tipo_Mano_Obra"] == tipo_empleado]["Costo_Hora ($)"].values[0]
    tiempo_horas = producto["Tiempo_Fabricación (min)"] / 60
    costo_labor = costo_hora * tiempo_horas

    st.write("👷 **Mano de Obra**")
    st.write(f"Tipo de trabajador: `{tipo_empleado}`")
    st.write(f"Tiempo: `{producto['Tiempo_Fabricación (min)']} minutos`")
    st.write(f"Costo: **${costo_labor:.2f}**")

    # Overhead
    costo_overhead = 0
    for _, row in overhead.iterrows():
        if row["Método_Distribución"] == "Por Hora":
            costo_overhead += (row["Costo_Mensual ($)"] / (160 * 30)) * producto["Tiempo_Fabricación (min)"] / 60
        elif row["Método_Distribución"] == "Por Unidad Producida":
            costo_overhead += row["Costo_Mensual ($)"] / 1000

    st.write("🏢 **Overhead estimado:**")
    st.write(f"${costo_overhead:.2f}")

    # Total
    total = costo_materiales + costo_labor + costo_overhead
    st.markdown(f"### 💲 Costo Total Unitario Estimado: **${total:.2f}**")

