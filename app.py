import streamlit as st
from datetime import datetime
from fpdf import FPDF
import tempfile
import os

# Configuración de la página web (Ideal para celulares)
st.set_page_config(page_title="JAM Woodlab App", page_icon="🪚", layout="centered")

st.title("JAM Woodlab - Cotizador Web")
if os.path.exists("logo.png"):
    st.image("logo.png", width=120)
st.markdown("---")

# 1. Datos del Cliente
st.header("1. Datos del Proyecto")
cliente = st.text_input("Nombre del Cliente")
proyecto = st.text_input("Descripción del Proyecto")
categoria = st.selectbox("Categoría", ["Chico (Repisas, Portallaves)", "Mediano (Mesas de noche)", "Grande (Comedor)", "Extra Grande (Cocina, Clóset)", "Joyería / Artesanal"])

# 2. Material Base
st.header("2. Materiales")
tipo_madera = st.selectbox("Tipo de Material", ["Hojas (Triplay / MDF / Melamina)", "Pie Tablar (Madera Fina / Sólida)"])
col1, col2 = st.columns(2)
cantidad = col1.number_input("Cantidad", min_value=0.0, value=1.0)
costo_unitario = col2.number_input("Costo Unitario ($)", min_value=0.0, value=600.0)

# 3. Fabricación
st.header("3. Fabricación")
detalle = st.selectbox("Dificultad", ["Básico (Armado rápido)", "Detallado (+30% tiempo)", "Alta Ebanistería (+80% tiempo)"])
acabado = st.selectbox("Acabado", ["Ninguno (Crudo)", "Aceite Danés / Cera Abeja", "Poliuretano / Barniz"])
col3, col4, col5 = st.columns(3)
horas_est = col3.number_input("Horas Fab.", min_value=0.0, value=5.0)
hora_base = col4.number_input("Tarifa/Hr ($)", min_value=0.0, value=150.0)
insumos = col5.number_input("Insumos ($)", min_value=0.0, value=250.0)

# 4. Instalación
st.header("4. Instalación y Fletes")
tipo_inst = st.selectbox("Servicio", ["Sin instalación (Entrega en taller)", "Estándar (Muros normales / Tablaroca)", "Compleja (Azulejo/Concreto - Tarifa Extra)"])
col6, col7, col8 = st.columns(3)
horas_inst = col6.number_input("Horas Inst.", min_value=0.0, value=3.0)
gasolina = col7.number_input("Flete ($)", min_value=0.0, value=150.0)
mat_inst = col8.number_input("Mat. Extra ($)", min_value=0.0, value=120.0)

# 5. Finanzas
st.header("5. Estrategia Comercial")
col9, col10 = st.columns(2)
margen = col9.number_input("Ganancia (%)", min_value=0.0, value=25.0)
iva_porcentaje = col10.number_input("IVA (%)", min_value=0.0, value=0.0)

st.markdown("---")

# Botón de Cálculo
if st.button("Calcular y Generar Cotización", use_container_width=True):
    if not cliente or not proyecto:
        st.error("Por favor, ingresa el nombre del cliente y el proyecto.")
    else:
        # CÁLCULOS INTERNOS
        costo_madera = costo_unitario * cantidad

        mult_detalle = 1.3 if "Detallado" in detalle else 1.8 if "Ebanistería" in detalle else 1.0
        mult_acabado = 1.25 if "Poliuretano" in acabado else 1.05 if "Aceite" in acabado else 1.0
        costo_extra_acabado = 450 if "Poliuretano" in acabado else 150 if "Aceite" in acabado else 0

        horas_reales_fab = horas_est * mult_detalle * mult_acabado
        mano_obra_fab = hora_base * horas_reales_fab
        total_insumos_fab = insumos + costo_extra_acabado

        if "Sin instalación" in tipo_inst:
            horas_inst = 0; mat_inst = 0; gasolina = 0; mano_obra_inst = 0
        else:
            mult_inst = 1.5 if "Compleja" in tipo_inst else 1.0
            mano_obra_inst = horas_inst * (hora_base * mult_inst)

        # PRECIOS VENTA
        factor_ganancia = 1 + (margen / 100)
        costo_puro_mueble = costo_madera + total_insumos_fab + mano_obra_fab
        precio_venta_mueble = costo_puro_mueble * factor_ganancia
        
        costo_puro_inst = mano_obra_inst + mat_inst + gasolina
        precio_venta_inst = costo_puro_inst * factor_ganancia

        subtotal = precio_venta_mueble + precio_venta_inst
        iva_monto = subtotal * (iva_porcentaje / 100)
        total = subtotal + iva_monto
        ganancia_neta = (costo_puro_mueble + costo_puro_inst) * (margen/100)

        # MOSTRAR RESULTADOS EN PANTALLA
        st.success(f"Cálculo completado. Total a cobrar: ${total:,.2f}")
        
        with st.expander("Ver Desglose Interno (Oculto al Cliente)"):
            st.write(f"**Costo Puro Mueble:** ${costo_puro_mueble:,.2f}")
            st.write(f"**Costo Puro Instalación:** ${costo_puro_inst:,.2f}")
            st.write(f"**Ganancia Neta:** ${ganancia_neta:,.2f}")

        # GENERAR PDF COMERCIAL
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", 'B', 24)
        pdf.set_text_color(51, 51, 51)
        if os.path.exists("logo.png"):
    try:
        pdf.image("logo.png", x=10, y=8, w=35)
    except:
        pass
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
        pdf.cell(0, 6, txt=f"  - Material: {tipo_madera} | Acabado: {acabado}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, txt="Consideraciones del Servicio:", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, txt="INCLUYE: Fabricación a medida y aplicación de acabados.", ln=True)
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
        
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(140, 10, txt="TOTAL A PAGAR:", align='R')
        pdf.cell(50, 10, txt=f"${total:,.2f}", align='R', ln=True)
        
        # Preparar PDF para descarga en el navegador
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf.output(tmp_file.name)
            with open(tmp_file.name, "rb") as f:
                pdf_bytes = f.read()
        
        os.unlink(tmp_file.name) # Limpiar archivo temporal
        
        # Botón de Descarga
        st.download_button(
            label="📥 Descargar PDF Comercial",
            data=pdf_bytes,
            file_name=f"Cotizacion_{cliente.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
