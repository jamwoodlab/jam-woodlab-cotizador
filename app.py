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

# 2. Configuración y Selección de Materiales
st.header("2. Materiales (Tableros y Madera Sólida)")

with st.expander("⚙️ Configuración de Precios Base de Hojas (122x244 cm)"):
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

costo_madera_hojas = 0.0
costo_madera_solida = 0.0
detalle_materiales_pdf = []

# --- A. Hojas / Tableros ---
st.subheader("A. Hojas / Tableros (Triplay, MDF, Melamina)")
usa_hojas = st.checkbox("¿El proyecto incluye hojas/tableros?", value=True)

if usa_hojas:
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
        costo_madera_hojas += sub_mat
        detalle_materiales_pdf.append(f"- {m_cant} hoja(s) de {m_tipo} {m_esp} ($ {p_unit:,.2f} c/u)")

# --- B. Madera Sólida / Bastidor ---
st.subheader("B. Madera Sólida (Bastidores, Listones, Estructuras)")
usa_solida = st.checkbox("¿El proyecto incluye madera sólida (Pie Tablar)?", value=False)

if usa_solida:
    st.markdown("Calcula por Pie Tablar directamente o por dimensiones de bastidor:")
    modo_solida = st.radio("Método de cálculo para madera sólida:", ["Ingreso directo de Pies Tablar", "Calculadora por dimensiones (Largo, Ancho, Grueso)"], horizontal=True)
    
    if modo_solida == "Ingreso directo de Pies Tablar":
        col_s1, col_s2 = st.columns(2)
        cant_pt = col_s1.number_input("Cantidad (Pies Tablar)", min_value=0.0, value=5.0)
        costo_pt = col_s2.number_input("Costo Unitario por PT ($)", min_value=0.0, value=65.0)
        costo_madera_solida = cant_pt * costo_pt
        if cant_pt > 0:
            detalle_materiales_pdf.append(f"- {cant_pt} Pie(s) Tablar de Madera Sólida ($ {costo_pt:,.2f} c/u)")
    else:
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        largo_pulg = col_b1.number_input("Largo (pulgadas)", min_value=0.0, value=48.0)
        ancho_pulg = col_b2.number_input("Ancho (pulgadas)", min_value=0.0, value=2.0)
        grueso_pulg = col_b3.number_input("Grueso (pulgadas)", min_value=0.0, value=1.5)
        piezas_solida = col_b4.number_input("Cant. Piezas", min_value=1, value=4)
        
        costo_pt_calc = st.number_input("Costo Unitario por Pie Tablar ($)", min_value=0.0, value=65.0, key="costo_pt_calc")
        
        # Fórmula Pie Tablar: (Largo" * Ancho" * Grueso") / 144
        pt_calculados = ((largo_pulg * ancho_pulg * grueso_pulg) / 144.0) * piezas_solida
        costo_madera_solida = pt_calculados * costo_pt_calc
        st.info(f"Pies Tablar calculados: **{pt_calculados:.2f} PT** (Costo total sólida: **${costo_madera_solida:,.2f}**) ")
        if pt_calculados > 0:
            detalle_materiales_pdf.append(f"- {piezas_solida} pza(s) Bastidor/Sólida ({pt_calculados:.2f} PT total)")

costo_madera_total = costo_madera_hojas + costo_madera_solida

# 3. Fabricación y Acabados
st.header("3. Fabricación y Acabados")
detalle = st.selectbox("Dificultad de Fabricación", ["Básico (Armado rápido)", "Detallado (+30% tiempo)", "Alta Ebanistería (+80% tiempo)"])
acabado = st.selectbox("Tipo de Acabado", ["Ninguno (Crudo)", "Aceite Danés / Cera Abeja", "Poliuretano / Barniz"])

# Botón táctil grande para fácil selección en tablet/celular
st.markdown("**¿Dispones del material de acabado en stock / inventario?**")
opcion_stock = st.radio(
    "Selección de Inventario:",
    ["Comprar Kit Completo (Nuevo)", "Usar Material en Stock (Cobrar sólo proporcional)"],
    index=0
)
usar_stock = "Stock" in opcion_stock

col3, col4 = st.columns(2)
horas_est = col3.number_input("Horas Estimadas de Fabricación", min_value=0.0, value=5.0)
hora_base = col4.number_input("Tarifa por Hora de Mano de Obra ($)", min_value=0.0, value=150.0)

costo_extra_acabado = 0.0
if "Poliuretano" in acabado:
    kit_completo_poli = 850.0  # Primer, Acabado, Catalizador, Thinner
    costo_extra_acabado = kit_completo_poli * 0.35 if usar_stock else kit_completo_poli
elif "Aceite" in acabado:
    kit_completo_aceite = 450.0  # 1L aceite + 1/4L tinta
    costo_extra_acabado = kit_completo_aceite * 0.35 if usar_stock else kit_completo_aceite

# --- Seccion Insumos y Herrajes ---
st.subheader("Insumos, Herrajes y Especiales")
modo_insumos = st.radio("Modalidad de Insumos:", ["Monto Fijo Global", "Desglosar Insumos y Herrajes"], horizontal=True)

costo_insumos_total = 0.0
desglose_insumos_dict = {}

if modo_insumos == "Monto Fijo Global":
    costo_insumos_total = st.number_input("Insumos Generales ($)", min_value=0.0, value=250.0)
    desglose_insumos_dict["Insumos Generales"] = costo_insumos_total
else:
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        ins_lijas = st.number_input("Tren de Lijado / Lijas ($)", min_value=0.0, value=80.0)
        ins_bisagras = st.number_input("Bisagras ($)", min_value=0.0, value=0.0)
        ins_correderas = st.number_input("Correderas ($)", min_value=0.0, value=0.0)
        ins_llantas = st.number_input("Llantas / Garruchas ($)", min_value=0.0, value=0.0)
    with col_i2:
        ins_laser = st.number_input("Grabado Láser ($)", min_value=0.0, value=0.0)
        ins_especiales = st.number_input("Especiales (Accesorios USB / Luz LED) ($)", min_value=0.0, value=0.0)
        ins_varios = st.number_input("Pegamentos, pijas, varios ($)", min_value=0.0, value=120.0)

    costo_insumos_total = ins_lijas + ins_bisagras + ins_correderas + ins_llantas + ins_laser + ins_especiales + ins_varios
    desglose_insumos_dict = {
        "Tren de lijado": ins_lijas,
        "Bisagras": ins_bisagras,
        "Correderas": ins_correderas,
        "Llantas": ins_llantas,
        "Grabado láser": ins_laser,
        "Especiales (USB/Luz)": ins_especiales,
        "Pegamentos y Varios": ins_varios
    }
    st.info(f"Total Insumos y Herrajes: **${costo_insumos_total:,.2f}**")

# 4. Instalación
st.header("4. Instalación y Fletes")
tipo_inst = st.selectbox("Servicio de Instalación", ["Sin instalación (Entrega en taller)", "Estándar (Muros normales / Tablaroca)", "Compleja (Azulejo / Concreto - Tarifa Extra)"])
col6, col7, col8 = st.columns(3)
horas_inst = col6.number_input("Horas Instalación", min_value=0.0, value=3.0)
gasolina = col7.number_input("Flete / Logística ($)", min_value=0.0, value=200.0)
mat_inst = col8.number_input("Material Extra Instalación ($)", min_value=0.0, value=100.0)

# 5. Finanzas y Promociones
st.header("5. Estrategia Comercial y Promociones")
col9, col10 = st.columns(2)
margen = col9.number_input("Ganancia Deseada (%)", min_value=0.0, value=25.0)
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
        # CÁLCULOS TÉCNICOS
        mult_detalle = 1.3 if "Detallado" in detalle else 1.8 if "Ebanistería" in detalle else 1.0
        mult_acabado = 1.25 if "Poliuretano" in acabado else 1.05 if "Aceite" in acabado else 1.0

        horas_reales_fab = horas_est * mult_detalle * mult_acabado
        mano_obra_fab = hora_base * horas_reales_fab
        
        if "Sin instalación" in tipo_inst:
            horas_inst = 0; mat_inst = 0; gasolina = 0; mano_obra_inst = 0
        else:
            mult_inst = 1.5 if "Compleja" in tipo_inst else 1.0
            mano_obra_inst = horas_inst * (hora_base * mult_inst)

        factor_ganancia = 1 + (margen / 100.0)
        
        # COSTOS PUROS REALES
        costo_puro_mueble = costo_madera_total + costo_insumos_total + costo_extra_acabado + mano_obra_fab
        costo_puro_inst_real = mano_obra_inst + mat_inst + gasolina
        
        # AJUSTE 70% / 30% FLETE E INSTALACIÓN
        # Se muestra 70% en la partida de instalación y el 30% restante se absorbe en el mueble
        flete_visible = costo_puro_inst_real * 0.70
        flete_oculto = costo_puro_inst_real * 0.30

        precio_venta_mueble = (costo_puro_mueble + flete_oculto) * factor_ganancia
        precio_venta_inst = flete_visible * factor_ganancia if flete_visible > 0 else 0.0

        subtotal = precio_venta_mueble + precio_venta_inst
        
        monto_descuento = 0.0
        if tipo_desc == "Porcentaje (%)":
            monto_descuento = subtotal * (valor_desc / 100.0)
        elif tipo_desc == "Monto Fijo ($)":
            monto_descuento = valor_desc

        subtotal_con_desc = subtotal - monto_descuento
        iva_monto = subtotal_con_desc * (iva_porcentaje / 100.0)
        total = subtotal_con_desc + iva_monto
        ganancia_neta = (costo_puro_mueble + costo_puro_inst_real) * (margen / 100.0)

        st.success(f"Cálculo completado. Total a cobrar: ${total:,.2f}")
        
        # DESGLOSE INTERNO DETALLADO
        with st.expander("🔍 Ver Desglose Interno Detallado (Oculto al Cliente)"):
            st.markdown("### 1. Costos de Materiales")
            st.write(f"- **Hojas / Tableros:** ${costo_madera_hojas:,.2f}")
            st.write(f"- **Madera Sólida / Bastidor:** ${costo_madera_solida:,.2f}")
            st.write(f"- **Total Maderas:** ${costo_madera_total:,.2f}")
            
            st.markdown("### 2. Mano de Obra y Fabricación")
            st.write(f"- **Horas Reales Estimadas:** {horas_reales_fab:.2f} hrs (Tarifa base: ${hora_base}/hr)")
            st.write(f"- **Costo Mano de Obra Fabricación:** ${mano_obra_fab:,.2f}")
            
            st.markdown("### 3. Acabados e Insumos")
            st.write(f"- **Kit de Acabado ({acabado}):** ${costo_extra_acabado:,.2f} ({'Proporcional Stock' if usar_stock else 'Kit Completo'})")
            st.write(f"- **Insumos y Herrajes Totales:** ${costo_insumos_total:,.2f}")
            for item, monto in desglose_insumos_dict.items():
                if monto > 0:
                    st.write(f"  * *{item}:* ${monto:,.2f}")

            st.markdown("### 4. Instalación y Flete Real")
            st.write(f"- **Mano de obra Instalación:** ${mano_obra_inst:,.2f}")
            st.write(f"- **Flete / Gasolina:** ${gasolina:,.2f}")
            st.write(f"- **Material Extra Inst.:** ${mat_inst:,.2f}")
            st.write(f"- **Costo Real Logística:** ${costo_puro_inst_real:,.2f} *(Reflejado al cliente: ${precio_venta_inst:,.2f} | Absorvido en mueble: ${flete_oculto * factor_ganancia:,.2f})*")

            st.markdown("---")
            st.write(f"💰 **Ganancia Neta Estimada ({margen}%):** **${ganancia_neta:,.2f}**")

        # GENERAR PDF COMERCIAL MEJORADO
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        pdf = FPDF()
        pdf.add_page()
        
        if os.path.exists("logo.png"):
            try:
                pdf.image("logo.png", x=10, y=8, w=35)
            except:
                pass

        # Encabezado
        pdf.set_font("Arial", 'B', 22)
        pdf.set_text_color(51, 51, 51)
        pdf.cell(0, 12, txt="JAM WOODLAB", ln=True, align='R')
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, txt="Diseño y Carpintería de Autor", ln=True, align='R')
        pdf.cell(0, 5, txt=f"Fecha de Cotización: {fecha_actual}", ln=True, align='R')
        pdf.ln(8)
        
        # Cliente
        pdf.set_font("Arial", 'B', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, txt=f"COTIZACIÓN PARA: {cliente.upper()}", ln=True)
        pdf.ln(4)
        
        # 1. Especificaciones del Proyecto
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, txt=f" 1. ESPECIFICACIONES DEL PROYECTO: {proyecto.upper()}", ln=True, fill=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, txt=f"  • Categoría: {categoria}", ln=True)
        pdf.cell(0, 6, txt=f"  • Acabado y Protección: {acabado}", ln=True)
        if detalle_materiales_pdf:
            pdf.cell(0, 6, txt="  • Materiales principales contemplados:", ln=True)
            for det_mat in detalle_materiales_pdf:
                pdf.cell(0, 5, txt=f"     {det_mat}", ln=True)
        pdf.ln(6)
        
        # 2. Términos y Condiciones
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, txt=" 2. CONDICIONES COMERCIALES Y DE SERVICIO", ln=True, fill=True)
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 5, txt="  • Anticipo: 60% al confirmar el pedido; 40% restante a la entrega e instalación.", ln=True)
        pdf.cell(0, 5, txt="  • Incluye: Fabricación a medida con procesos artesanales y acabados de alta durabilidad.", ln=True)
        if "Sin instalación" not in tipo_inst:
            pdf.cell(0, 5, txt=f"  • Incluye: Logística de traslado y montaje profesional en sitio ({tipo_inst}).", ln=True)
        pdf.cell(0, 5, txt="  • Exclusiones: Trabajos de albañilería, resane de muros, pintura externa ni adaptaciones de plomería.", ln=True)
        pdf.cell(0, 5, txt="  • Garantía: 12 meses sobre ensambles y defectos estructurales de fabricación.", ln=True)
        pdf.ln(6)

        # 3. Inversión
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, txt=" 3. DESGLOSE DE INVERSIÓN", ln=True, fill=True)
        pdf.set_font("Arial", '', 10)
        
        pdf.cell(140, 7, txt="Fabricación integral de mueble y acabados", border='B')
        pdf.cell(50, 7, txt=f"${precio_venta_mueble:,.2f}", border='B', align='R', ln=True)
        
        if precio_venta_inst > 0:
            pdf.cell(140, 7, txt="Servicio de Logística, Flete y Montaje en sitio", border='B')
            pdf.cell(50, 7, txt=f"${precio_venta_inst:,.2f}", border='B', align='R', ln=True)
        
        if monto_descuento > 0:
            pdf.cell(140, 7, txt="Descuento Promocional Aplicado", border='B')
            pdf.cell(50, 7, txt=f"- ${monto_descuento:,.2f}", border='B', align='R', ln=True)

        if iva_porcentaje > 0:
            pdf.cell(140, 7, txt=f"IVA ({iva_porcentaje}%)", border='B')
            pdf.cell(50, 7, txt=f"${iva_monto:,.2f}", border='B', align='R', ln=True)

        pdf.ln(4)
        pdf.set_font("Arial", 'B', 13)
        pdf.cell(140, 8, txt="INVERSIÓN TOTAL:", align='R')
        pdf.cell(50, 8, txt=f"${total:,.2f}", align='R', ln=True)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf.output(tmp_file.name)
            with open(tmp_file.name, "rb") as f:
                pdf_bytes = f.read()
        
        os.unlink(tmp_file.name)
        
        st.download_button(
            label="📥 Descargar Cotización PDF Comercial",
            data=pdf_bytes,
            file_name=f"Cotizacion_{cliente.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
