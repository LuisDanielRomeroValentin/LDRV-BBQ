import streamlit as st
import pandas as pd

def traducir_comida_resumen(comida_original, t):
    """Traduce el nombre de la comida según el idioma"""
    traducciones = {
        'Pollo': t.get('food_pollo', 'Pollo'),
        'Salchichas': t.get('food_salchichas', 'Salchichas'),
        'Hamburguesa': t.get('food_hamburguesa', 'Hamburguesa'),
        'Panceta': t.get('food_panceta', 'Panceta'),
        'Secreto': t.get('food_secreto', 'Secreto'),
        'Contramuslos Pollo': t.get('food_contramuslos', 'Contramuslos Pollo'),
    }
    return traducciones.get(comida_original, comida_original)

def traducir_bebida_resumen(bebida_original, t):
    """Traduce el nombre de la bebida según el idioma"""
    traducciones = {
        'Agua': t.get('drink_agua', 'Agua'),
        'Coca Cola': t.get('drink_cocacola', 'Coca Cola'),
        'Coca Cola Zero': t.get('drink_cocacola_zero', 'Coca Cola Zero'),
        'Fanta Naranja': t.get('drink_fanta_naranja', 'Fanta Naranja'),
        'Fanta Limón': t.get('drink_fanta_limon', 'Fanta Limón'),
        'Aquarius Naranja': t.get('drink_aquarius_naranja', 'Aquarius Naranja'),
        'Aquarius Limón': t.get('drink_aquarius_limon', 'Aquarius Limón'),
        'Zumo Naranja': t.get('drink_zumo_naranja', 'Zumo Naranja'),
        'Zumo Piña': t.get('drink_zumo_pina', 'Zumo Piña'),
        'Zumo Manzana': t.get('drink_zumo_manzana', 'Zumo Manzana'),
        'Cerveza': t.get('drink_cerveza', 'Cerveza'),
        'Cerveza Sin Alcohol': t.get('drink_cerveza_sin', 'Cerveza Sin Alcohol'),
        'Vino Tinto': t.get('drink_vino_tinto', 'Vino Tinto'),
        'Vino Blanco': t.get('drink_vino_blanco', 'Vino Blanco'),
        'Agua con Gas': t.get('drink_agua_gas', 'Agua con Gas'),
    }
    return traducciones.get(bebida_original, bebida_original)

def render(conn, t):
    # Usar el diccionario t para los textos principales
    st.subheader(f"📊 {t.get('tab_resumen', 'Resumen de Compra')}")
    
    try:
        # Leer la hoja
        df = conn.read(worksheet="pedidos", ttl=0)
        
        if df.empty:
            st.info(f"📭 {t.get('msg_vacio', 'Todavía no hay pedidos registrados.')}")
            return
        
        # Traducir los datos para mostrar según el idioma
        df_mostrar = df.copy()
        df_mostrar['Comida'] = df_mostrar['Comida'].apply(lambda x: traducir_comida_resumen(x, t))
        df_mostrar['Bebida'] = df_mostrar['Bebida'].apply(lambda x: traducir_bebida_resumen(x, t))
        
        # Traducir el tipo (Niño/Adulto) según idioma
        if t.get('btn_add') == '+ Add to list':  # Inglés
            df_mostrar['Tipo'] = df_mostrar['Tipo'].apply(lambda x: 'Kid' if 'Niño' in str(x) else 'Adult')
            ninos_label = t.get('ninos', 'Kids')
            adultos_label = t.get('adultos', 'Adults')
            total_label = t.get('total', 'Total')
            personas_texto = t.get('persons', 'people')
            sin_ninos_texto = t.get('sin_ninos', 'No kids')
            sin_adultos_texto = t.get('sin_adultos', 'No adults')
            ninos_titulo = "**👦 Kids:**"
            adultos_titulo = "**👨 Adults:**"
        else:  # Español
            df_mostrar['Tipo'] = df_mostrar['Tipo']  # Mantener como está
            ninos_label = t.get('ninos', 'Niños')
            adultos_label = t.get('adultos', 'Adultos')
            total_label = t.get('total', 'Total')
            personas_texto = t.get('persons', 'personas')
            sin_ninos_texto = t.get('sin_ninos', 'No hay niños')
            sin_adultos_texto = t.get('sin_adultos', 'No hay adultos')
            ninos_titulo = "**👦 Niños:**"
            adultos_titulo = "**👨 Adultos:**"
        
        # Separar por tipo
        if t.get('btn_add') == '+ Add to list':  # Inglés
            df_ninos = df_mostrar[df_mostrar['Tipo'] == 'Kid']
            df_adultos = df_mostrar[df_mostrar['Tipo'] == 'Adult']
        else:
            df_ninos = df_mostrar[df_mostrar['Tipo'].str.contains('Niño', case=False, na=False)]
            df_adultos = df_mostrar[df_mostrar['Tipo'].str.contains('Adulto', case=False, na=False)]
        
        # ==================== MENÚ DE NAVEGACIÓN ====================
        opciones_menu = [
            t.get('tab_totales', '📊 Totales'),
            t.get('tab_compra', '🛒 Lista de Compra'),
            t.get('tab_comida', '🍖 Por Comida'),
            t.get('tab_bebida', '🥤 Por Bebida')
        ]
        
        opcion = st.radio(
            t.get('selecciona', '📌 Selecciona:'),
            opciones_menu,
            horizontal=True
        )
        
        st.divider()
        
        # ==================== OPCIÓN 1: TOTALES ====================
        if opcion == opciones_menu[0]:
            st.write(f"### {t.get('numero_personas', '👥 Número de Personas')}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(total_label, len(df_mostrar))
            with col2:
                st.metric(ninos_label, len(df_ninos))
            with col3:
                st.metric(adultos_label, len(df_adultos))
        
        # ==================== OPCIÓN 2: LISTA DE COMPRA ====================
        elif opcion == opciones_menu[1]:
            st.write(f"### {t.get('lista_compra', '🛒 Qué hay que comprar')}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"#### {t.get('comidas', '🍖 Comidas')}")
                resumen_comida = df_mostrar['Comida'].value_counts()
                for comida, cantidad in resumen_comida.items():
                    st.write(f"• **{comida}:** {cantidad}")
            
            with col2:
                st.write(f"#### {t.get('bebidas', '🥤 Bebidas')}")
                resumen_bebida = df_mostrar['Bebida'].value_counts()
                for bebida, cantidad in resumen_bebida.items():
                    st.write(f"• **{bebida}:** {cantidad}")
        
        # ==================== OPCIÓN 3: POR COMIDA ====================
        elif opcion == opciones_menu[2]:
            st.write(f"### {t.get('por_comida', '🍖 ¿Quién pidió cada comida?')}")
            
            comidas_unicas = sorted(df_mostrar['Comida'].unique())
            
            for comida in comidas_unicas:
                df_comida = df_mostrar[df_mostrar['Comida'] == comida]
                
                if t.get('btn_add') == '+ Add to list':  # Inglés
                    ninos = df_comida[df_comida['Tipo'] == 'Kid']
                    adultos = df_comida[df_comida['Tipo'] == 'Adult']
                else:
                    ninos = df_comida[df_comida['Tipo'].str.contains('Niño', case=False, na=False)]
                    adultos = df_comida[df_comida['Tipo'].str.contains('Adulto', case=False, na=False)]
                
                with st.expander(f"🍖 {comida} ({len(df_comida)} {personas_texto})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if len(ninos) > 0:
                            st.write(ninos_titulo)
                            for _, row in ninos.iterrows():
                                st.write(f"• {row['Nombre_Persona']}")
                        else:
                            st.caption(sin_ninos_texto)
                    
                    with col2:
                        if len(adultos) > 0:
                            st.write(adultos_titulo)
                            for _, row in adultos.iterrows():
                                st.write(f"• {row['Nombre_Persona']}")
                        else:
                            st.caption(sin_adultos_texto)
        
        # ==================== OPCIÓN 4: POR BEBIDA ====================
        elif opcion == opciones_menu[3]:
            st.write(f"### {t.get('por_bebida', '🥤 ¿Quién pidió cada bebida?')}")
            
            bebidas_unicas = sorted(df_mostrar['Bebida'].unique())
            
            for bebida in bebidas_unicas:
                df_bebida = df_mostrar[df_mostrar['Bebida'] == bebida]
                
                if t.get('btn_add') == '+ Add to list':  # Inglés
                    ninos = df_bebida[df_bebida['Tipo'] == 'Kid']
                    adultos = df_bebida[df_bebida['Tipo'] == 'Adult']
                else:
                    ninos = df_bebida[df_bebida['Tipo'].str.contains('Niño', case=False, na=False)]
                    adultos = df_bebida[df_bebida['Tipo'].str.contains('Adulto', case=False, na=False)]
                
                with st.expander(f"🥤 {bebida} ({len(df_bebida)} {personas_texto})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if len(ninos) > 0:
                            st.write(ninos_titulo)
                            for _, row in ninos.iterrows():
                                st.write(f"• {row['Nombre_Persona']}")
                        else:
                            st.caption(sin_ninos_texto)
                    
                    with col2:
                        if len(adultos) > 0:
                            st.write(adultos_titulo)
                            for _, row in adultos.iterrows():
                                st.write(f"• {row['Nombre_Persona']}")
                        else:
                            st.caption(sin_adultos_texto)
        
        # ==================== SECCIÓN EXTRA: Recomendaciones ====================
        st.divider()
        with st.expander(t.get('recomendaciones', '🔥 Recomendaciones para el BBQ')):
            total_personas = len(df_mostrar)
            st.info(f"""
            **{t.get('para_personas', 'Para')} {total_personas} {personas_texto}:**
            
            🍖 **{t.get('carne', 'Carne')}:** {total_personas * 0.3:.1f} - {total_personas * 0.5:.1f} kg
            🥤 **{t.get('bebidas', 'Bebidas')}:** {total_personas * 1.5:.0f} - {total_personas * 2:.0f} {t.get('litros', 'litros')}
            🍞 **{t.get('pan', 'Pan')}:** {total_personas} - {total_personas * 2} {t.get('unidades', 'unidades')}
            """)
            
            if st.button(t.get('exportar', '📥 Exportar todo'), use_container_width=True):
                csv = df.to_csv(index=False)
                st.download_button(
                    label=t.get('descargar_csv', '📥 Descargar CSV'),
                    data=csv,
                    file_name=f"bbq_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"⚠️ {t.get('error_hoja', 'Error al acceder a la hoja')} 'pedidos'")
        st.code(f"Error: {str(e)}")
        st.info(t.get('verificar_hoja', "💡 Verifica que la pestaña 'pedidos' existe en tu Google Sheet"))