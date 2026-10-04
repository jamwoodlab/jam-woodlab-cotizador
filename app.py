import streamlit as st
from datetime import datetime
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="JAM Woodlab App", page_icon="🪚", layout="centered")

st.title("JAM Woodlab - Cotizador Web Pro")
if os.path.exists("logo.png"):
    st.image("logo.png", width=120)

st.markdown("---")

# 1. Datos del Cliente
st.header("1. Datos del Proyecto")
cliente = st.text_input("Nombre del Cliente")
proyecto = st.text_input("Descripción del Proyecto")
categoria = st.selectbox("Categoría", ["Chico (Repisas, Portallaves)", "Mediano (Mesas de noche)", "Grande (Comedor)", "Extra Grande (Cocina, Clóset)", "Joyería / Artesanal"])

# 2. Configuración y Selección de Materiales (Hojas / Tableros 122x244 cm)
st.header("2. Materiales y Configuración de Stock (122x244 cm)")

with st.expander("⚙️ Configuración de Precios de Tableros / Hojas"):
    st.markdown("Define los precios base por tipo y espesor:")
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        precio_pino_18 = st.number_input("Pino 18mm ($)", value=1000.0)
        precio_pino_15 = st.number_input("Pino 15mm ($)", value=850.0)
        precio_pino_9 = st.number_input("Pino 9mm ($)", value=700.0)
        precio_pino_6 = st.number_input("Pino 6mm ($)", value=600.0)
    with col_cfg2:
        precio_caobilla_18 = st.number_input("Caobilla/Roble 18mm ($)", value=1300.0)
        precio_caobilla_15 = st.number_input("Caobilla/Roble 15mm ($)", value=1100.0)
        precio_caobilla_9 = st.number_input("Caobilla/Roble 9mm ($)", value=900.0)
        precio_caobilla_6 = st.number_input("Caobilla/Roble 6mm ($)", value=750.0)

tipo_madera = st.selectbox("Tipo de Material Base", ["Hojas (Triplay / MDF / Melamina)", "Pie Tablar (Madera Fina / Sólida)"])

costo_madera_total = 0.0
detalle_materiales_pdf = []

if "Hojas" in tipo_madera:
    st.subheader("Selección de Hojas para el Proyecto")
    num_partidas = st.number_input("¿Cuántos tipos/espesores de hojas diferentes usarás?", min_value=1, max_value=5, value=1)
    
    for i in range(int(num_partidas)):
        st.markdown(f"**Partida {i+1}**")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            m_tipo = st.selectbox(f"Madera {i+1}", ["Pino", "Caobilla / Roble"], key=f"mtipo_{i}")
        with col_m2:
            m_esp = st.selectbox(f"Espesor {i+1}", ["18mm", "15mm", "9mm", "6mm"], key=f"mesp_{i}")
        with col_m3:
            m_cant = st.number_input(f"Cantidad hojas {i+1}", min_value=0.0, value=1.0, key=f"mcant_{i}")
            
        if m_tipo == "Pino":
            p_unit = precio_pino_18 if m_esp == "18mm" else precio_pino_15 if m_esp == "15mm" else precio_pino_9 if m_esp == "9mm" else precio_pino_6
        else:
            p_unit = precio_caobilla_18 if m_esp == "18mm" else precio_caobilla_15 if m_esp == "15mm" else precio_caobilla_9 if m_esp == "9mm" else precio_caobilla_6
            
        sub_mat = p_unit * m_cant
        costo_madera_total += sub_mat
        detalle_materiales_pdf.append(f"- {m_cant} hoja(s) de {m_tipo} {m_esp} ($ {p_unit:,.2f} c/u)")
else:
    col1, col2 = st.columns(2)
    cantidad_pt = col1.number_input("Cantidad (Pies Tablar)", min_value=0.0, value=10.0)
    costo_unit_pt = col2.number_input("Costo Unitario por Pie Tablar ($)", min_value=0.0, value=60.0)
    costo_madera_total = cantidad_pt * costo_unit_pt
    detalle_materiales_pdf.append(f"- {cantidad_pt} Pies Tablar de madera sólida")

# 3. Fabricación y Acabados
st.header("3. Fabricación y Acabados")
detalle = st.selectbox("Dificultad", ["Básico (Armado rápido)", "Detallado (+30% tiempo)", "Alta Ebanistería (+80% tiempo)"])
acabado = st.selectbox("Acabado", ["Ninguno (Crudo)", "Aceite Danés / Cera Abeja", "Poliuretano / Barniz"])

# Casilla de verificación de stock (Sayer / kits completos)
usar_stock = st.checkbox("📦 Usar material en stock / inventario (Cobrar solo proporcional al área)")

col3, col4, col5 = st.columns(3)
horas_est = col3.number_input("Horas Fab.", min_value=0.0, value=5.0)
hora_base = col4.number_input("Tarifa/Hr ($)", min_value=0.0, value=150.0)
insumos = col5.number_input("Insumos generales ($)", min_value=0.0, value=250.0)

costo_extra_acabado = 0.0
if "Poliuretano" in acabado:
    kit_completo_poli = 850.0  # Primer, Acabado, Catalizador, Thinner
    costo_extra_acabado = kit_completo_poli * 0.35 if usar_stock else kit_completo_poli
elif "Aceite" in acabado:
    kit_completo_aceite = 450.0  # 1L aceite + 1/4L tinta
    costo_extra_acabado = kit_completo_aceite * 0.35 if usar_stock else kit_completo_aceite

# 4. Instalación
st.header("4. Instalación y Fletes")
tipo_inst = st.selectbox("Servicio", ["Sin instalación (Entrega en taller)", "Estándar (Muros normales / Tablaroca)", "Compleja (Azulejo/Concreto - Tarifa Extra)"])
col6, col7, col8 = st.columns(3)
horas_inst = col6.number_input("Horas Inst.", min_value=0.0, value=3.0)
gasolina = col7.number_input("Flete ($)", min_value=0.0, value=150.0)
mat_inst = col8.number_input("Mat. Extra ($)", min_value=0.0, value=120.0)

# 5. Finanzas y Promociones
st.header("5. Estrategia Comercial y Promociones")
col9, col10 = st.columns(2)
margen = col9.number_input("Ganancia (%)", min_value=0.0, value=25.0)
iva_porcentaje = col10.number_input("IVA (%)", min_value=0.0, value=0.0)

st.subheader("Descuentos por Promoción")
col_desc1, col_desc2 = st.columns(2)
tipo_desc = col_desc1.selectbox("Tipo de Descuento", ["Ninguno", "Porcentaje (%)", "Monto Fijo ($)"])
valor_desc = col_desc2.number_input("Valor del Descuento", min_value=0.0, value=0.0)

st.markdown("---")

if st.button("Calcular y Generar Cotización Pro", use_container_width=True):
    if not cliente or not proyecto:
        st.error("Por favor, ingresa el nombre del cliente y el proyecto.")
    else:
        mult_detalle = 1.3 if "Detallado" in detalle else 1.8 if "Ebanistería" in detalle else 1.0
        mult_acabado = 1.25 if "Poliuretano" in acabado else 1.05 if "Aceite" in acabado else 1.0

        horas_reales_fab = horas_est * mult_detalle * mult_acabado
        mano_obra_fab = hora_base * horas_reales_fab
        total_insumos_fab = insumos + costo_extra_acabado

        if "Sin instalación" in tipo_inst:
            horas_inst = 0
            mat_inst = 0
            gasolina = 0
            mano_obra_inst = 0
        else:
            mult_inst = 1.5 if "Compleja" in tipo_inst else 1.0
            mano_obra_inst = horas_inst * (hora_base * mult_inst)

        factor_ganancia = 1 + (margen / 100)
        costo_puro_mueble = costo_madera_total + total_insumos_fab + mano_obra_fab
        precio_venta_mueble = costo_puro_mueble * factor_ganancia
        
        costo_puro_inst = mano_obra_inst + mat_inst + gasolina
        precio_venta_inst = costo_puro_inst * factor_ganancia

        subtotal = precio_venta_mueble + precio_venta_inst
        
        monto_descuento = 0.0
        if tipo_desc == "Porcentaje (%)":
            monto_descuento = subtotal * (valor_desc / 100.0)
        elif tipo_desc == "Monto Fijo ($)":
            monto_descuento = valor_desc

        subtotal_con_desc = subtotal - monto_descuento
        iva_monto = subtotal_con_desc * (iva_porcentaje / 100.0)
        total = subtotal_con_desc + iva_monto
        ganancia_neta = (costo_puro_mueble + costo_puro_inst) * (margen / 100)

        st.success(f"Cálculo completado. Total a cobrar: ${total:,.2f}")
        
        with st.expander("Ver Desglose Interno (Oculto al Cliente)"):
            st.write(f"**Costo Puro Mueble:** ${costo_puro_mueble:,.2f}")
            st.write(f"**Costo Puro Instalación:** ${costo_puro_inst:,.2f}")
            st.write(f"**Ganancia Neta:** ${ganancia_neta:,.2f}")

        # GENERAR PDF COMERCIAL
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        pdf = FPDF()
        pdf.add_page()
        
        if os.path.exists("logo.png"):
            try:
                pdf.image("logo.png", x=10, y=8, w=35)
            except:
                pass

        pdf.set_font("Arial", 'B', 24)
        pdf.set_text_color(51, 51, 51)
        pdf.cell(0, 15, txt="JAM WOODLAB", ln=True, align='R')
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, txt="Diseño y Carpintería de Autor", ln=True, align='R')
        pdf.cell(0, 5, txt=f"Fecha: {fecha_actual}", ln=True, align='R')
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, txt=f"Cotización preparada para: {cliente}", ln=True)
        pdf.ln(5)
        
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, txt=f" 1. Proyecto: {proyecto}", ln=True, fill=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 6, txt=f"  - Categoria: {categoria} | Acabado: {acabado}", ln=True)
        for det_mat in detalle_materiales_pdf:
            pdf.cell(0, 6, txt=f"  {det_mat}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, txt="Consideraciones del Servicio:", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, txt="INCLUYE: Fabricación a medida y aplicación de acabados profesionales.", ln=True)
        if "Sin instalación" not in tipo_inst:
            pdf.cell(0, 5, txt=f"INCLUYE: Logística e instalación ({tipo_inst}).", ln=True)
        pdf.cell(0, 5, txt="NO INCLUYE: Albañilería, pintura de muros ni plomería.", ln=True)
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, txt=" 2. Inversión", ln=True, fill=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(140, 8, txt="Fabricación de Mueble", border='B')
        pdf.cell(50, 8, txt=f"${precio_venta_mueble:,.2f}", border='B', align='R', ln=True)
        if precio_venta_inst > 0:
            pdf.cell(140, 8, txt="Servicio de Logística e Instalación", border='B')
            pdf.cell(50, 8, txt=f"${precio_venta_inst:,.2f}", border='B', align='R', ln=True)
        
        if monto_descuento > 0:
            pdf.cell(140, 8, txt="Descuento Promocional Aplicado", border='B')
            pdf.cell(50, 8, txt=f"- ${monto_descuento:,.2f}", border='B', align='R', ln=True)

        if iva_porcentaje > 0:
            pdf.cell(140, 8, txt=f"IVA ({iva_porcentaje}%)", border='B')
            pdf.cell(50, 8, txt=f"${iva_monto:,.2f}", border='B', align='R', ln=True)

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(140, 10, txt="TOTAL A PAGAR:", align='R')
        pdf.cell(50, 10, txt=f"${total:,.2f}", align='R', ln=True)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf.output(tmp_file.name)
            with open(tmp_file.name, "rb") as f:
                pdf_bytes = f.read()
        
        os.unlink(tmp_file.name)
        
        st.download_button(
            label="📥 Descargar PDF Comercial Actualizado",
            data=pdf_bytes,
            file_name=f"Cotizacion_{cliente.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
