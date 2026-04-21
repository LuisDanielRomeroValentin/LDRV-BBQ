import streamlit as st
import pandas as pd
from datetime import datetime
import time

def traducir_comida(comida_original, t):
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

def cargar_bebidas(conn, tipo_usuario, t):
    """Carga las bebidas disponibles desde Google Sheets y las traduce"""
    try:
        df_bebidas = conn.read(worksheet="bebidas", ttl=0)
        # Filtrar por tipo (Niños, Adultos, o Ambos)
        bebidas_filtradas = df_bebidas[
            (df_bebidas['Tipo'] == tipo_usuario) | 
            (df_bebidas['Tipo'] == 'Ambos')
        ]
        # Filtrar solo las disponibles
        bebidas_filtradas = bebidas_filtradas[bebidas_filtradas['Disponible'] == 'Sí']
        
        # Obtener la lista de bebidas estándar
        bebidas_originales = bebidas_filtradas['Bebida_Estandar'].tolist()
        
        # Traducciones de bebidas
        traducciones_bebidas = {
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
        
        # Traducir las bebidas para mostrar
        bebidas_traducidas = [traducciones_bebidas.get(bebida, bebida) for bebida in bebidas_originales]
        
        return bebidas_traducidas, bebidas_originales
        
    except Exception as e:
        st.warning(f"No se pudo cargar la lista de bebidas. Usando lista por defecto.")
        # Lista por defecto si no se puede cargar
        if tipo_usuario == 'Niño':
            originales = ['Agua', 'Zumo Naranja', 'Zumo Piña', 'Zumo Manzana', 'Coca Cola', 'Fanta Naranja', 'Fanta Limón']
        else:
            originales = ['Agua', 'Coca Cola', 'Cerveza', 'Cerveza Sin Alcohol', 'Vino Tinto', 'Vino Blanco', 'Fanta Naranja', 'Fanta Limón']
        
        # Traducir las bebidas por defecto
        traducciones_bebidas = {
            'Agua': t.get('drink_agua', 'Agua'),
            'Coca Cola': t.get('drink_cocacola', 'Coca Cola'),
            'Cerveza': t.get('drink_cerveza', 'Cerveza'),
            'Cerveza Sin Alcohol': t.get('drink_cerveza_sin', 'Cerveza Sin Alcohol'),
            'Vino Tinto': t.get('drink_vino_tinto', 'Vino Tinto'),
            'Vino Blanco': t.get('drink_vino_blanco', 'Vino Blanco'),
            'Fanta Naranja': t.get('drink_fanta_naranja', 'Fanta Naranja'),
            'Fanta Limón': t.get('drink_fanta_limon', 'Fanta Limón'),
            'Zumo Naranja': t.get('drink_zumo_naranja', 'Zumo Naranja'),
            'Zumo Piña': t.get('drink_zumo_pina', 'Zumo Piña'),
            'Zumo Manzana': t.get('drink_zumo_manzana', 'Zumo Manzana'),
        }
        
        traducidas = [traducciones_bebidas.get(bebida, bebida) for bebida in originales]
        return traducidas, originales

def render(conn, t, df_menu):
    st.subheader(f"👦 {t.get('tab_kids', 'Menú Niños/Hermanos')}")
    
    # Mostrar mensaje informativo
    st.info(t.get('info_kids_detail', 'Agrega a los niños uno a uno. Al terminar, dale a CONFIRMAR Y GUARDAR TODO'))
    
    if 'lista_temporal_ninos' not in st.session_state:
        st.session_state.lista_temporal_ninos = []

    # Filtrar opciones de comida para niños
    opciones_comida = df_menu[df_menu['Tipo'].str.lower().str.strip() == 'niño']['Opcion'].tolist()
    if not opciones_comida:
        opciones_comida = df_menu[df_menu['Tipo'] == 'Niño']['Opcion'].tolist()
    
    # Cargar bebidas para niños (con traducción)
    opciones_bebida_traducidas, opciones_bebida_originales = cargar_bebidas(conn, 'Niño', t)
    
    # Crear mapeo para guardar el valor original en español
    mapeo_bebidas = dict(zip(opciones_bebida_traducidas, opciones_bebida_originales))
    
    # Traducir opciones de comida
    opciones_comida_traducidas = [traducir_comida(opcion, t) for opcion in opciones_comida]
    mapeo_comidas = dict(zip(opciones_comida_traducidas, opciones_comida))

    # --- 1. FORMULARIO ---
    with st.form(key="form_ninos", clear_on_submit=True):
        nombre = st.text_input(
            t.get('label_name', 'Attendee Name'), 
            placeholder="Ej: Enzo"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            comida_label = t.get('label_food_kid', 'Choose food (1 option)')
            comida_traducida = st.selectbox(
                comida_label, 
                options=opciones_comida_traducidas,
                index=0 if opciones_comida_traducidas else None
            )
            comida = mapeo_comidas.get(comida_traducida, comida_traducida)
        
        with col2:
            bebida_label = t.get('label_drink', 'Drink choice')
            # Mostrar las bebidas TRADUCIDAS
            bebida_traducida = st.selectbox(
                bebida_label, 
                options=opciones_bebida_traducidas,
                index=0 if opciones_bebida_traducidas else None
            )
            # Obtener el valor original en español para guardar
            bebida = mapeo_bebidas.get(bebida_traducida, bebida_traducida)
        
        submitted = st.form_submit_button(
            t.get('btn_add', '+ Add to list'), 
            use_container_width=True
        )
        
        if submitted:
            if nombre and bebida and comida:
                nuevo = {
                    "Nombre_Persona": nombre, 
                    "Tipo": "Niño",
                    "Comida": comida,  # Guardamos el valor original en español
                    "Bebida": bebida,  # Guardamos el valor original en español
                    "Fecha_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Timestamp": datetime.now().timestamp()
                }
                st.session_state.lista_temporal_ninos.append(nuevo)
                st.success(f"✅ {t.get('success_msg', 'Added successfully!')} - {nombre}")
                time.sleep(0.5)
                st.rerun()
            else:
                missing_fields = []
                if not nombre:
                    missing_fields.append(t.get('label_name', 'Attendee Name'))
                if not comida:
                    missing_fields.append(t.get('label_food_kid', 'Food'))
                if not bebida:
                    missing_fields.append(t.get('label_drink', 'Drink'))
                st.warning(f"⚠️ {t.get('msg_vacio', 'Please complete')}: {', '.join(missing_fields)}")

    # --- 2. LISTA PREVIA ---
    if st.session_state.lista_temporal_ninos:
        st.markdown("---")
        st.write("**📋 Current list:**")
        
        df_temp = pd.DataFrame(st.session_state.lista_temporal_ninos)
        
        # Traducir los valores para mostrar
        df_mostrar = df_temp[["Nombre_Persona", "Comida", "Bebida"]].copy()
        df_mostrar["Comida"] = df_mostrar["Comida"].apply(lambda x: traducir_comida(x, t))
        
        # Traducir bebidas para mostrar
        traducciones_bebidas = {
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
        df_mostrar["Bebida"] = df_mostrar["Bebida"].apply(lambda x: traducciones_bebidas.get(x, x))
        
        # Traducir nombres de columnas
        column_traducciones = {
            'Nombre_Persona': t.get('col_name', 'Name'),
            'Comida': t.get('col_food', 'Food'),
            'Bebida': t.get('col_drink', 'Drink')
        }
        df_mostrar = df_mostrar.rename(columns=column_traducciones)
        
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
        st.caption(f"Total: {len(st.session_state.lista_temporal_ninos)} {t.get('persons', 'person(s)')}")

        col_save, col_clear = st.columns([4, 1])
        
        with col_save:        
            if st.button(t.get('btn_save_all', 'CONFIRM AND SAVE ALL'), type="primary", use_container_width=True):
                if not st.session_state.lista_temporal_ninos:
                    st.warning(t.get('msg_vacio', 'The list is empty'))
                else:
                    try:
                        with st.spinner("📤 Saving to Google Sheets..."):
                            df_nuevos = pd.DataFrame(st.session_state.lista_temporal_ninos)
                            
                            if 'Timestamp' in df_nuevos.columns:
                                df_nuevos = df_nuevos.drop(columns=['Timestamp'])
                            
                            try:
                                df_existente = conn.read(worksheet="pedidos", ttl=0)
                            except Exception as e:
                                df_existente = None
                            
                            if df_existente is not None and not df_existente.empty:
                                for col in df_nuevos.columns:
                                    if col not in df_existente.columns:
                                        df_existente[col] = ''
                                
                                for col in df_existente.columns:
                                    if col not in df_nuevos.columns:
                                        df_nuevos[col] = ''
                                
                                df_final = pd.concat([df_existente, df_nuevos], ignore_index=True)
                            else:
                                df_final = df_nuevos
                            
                            df_final = df_final.fillna('')
                            df_final = df_final.astype(str).replace(['nan', 'None', 'NaN'], '')
                            
                            conn.update(worksheet="pedidos", data=df_final)
                            
                            st.session_state.lista_temporal_ninos = []
                            
                            st.balloons()
                            st.success(f"✅ {t.get('success_msg', 'Saved successfully!')} ({len(df_nuevos)} {t.get('records', 'record(s)')} added)")
                            
                            time.sleep(2)
                            st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error saving to Google Sheets")
                        st.code(f"Error type: {type(e).__name__}")
                        st.code(f"Message: {str(e)}")
                        
        with col_clear:
            if st.button("🗑️ Clear list", use_container_width=True):
                st.session_state.lista_temporal_ninos = []
                st.rerun()
    else:
        st.info("👆 " + t.get('info_kids', 'Add people using the form above'))