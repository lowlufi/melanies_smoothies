# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas

# Write directly to the app
st.title(":cup_with_straw: Customize Your Batido!:cup_with_straw:")
st.write("""Choose the fruits you want in your custom Batido Smoothie!""")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Conexión a Snowflake con manejo de errores
try:
    cnx = st.connection("snowflake")
    session = cnx.session()
except Exception as e:
    st.error(f"Error connecting to Snowflake: {str(e)}")
    st.stop()

# Obtener datos de frutas
try:
    my_dataframe = session.table('smoothies.public.fruit_options').select(col('FRUIT_NAME'), col('SEARCH_ON'))
    pd_df = my_dataframe.to_pandas()
except Exception as e:
    st.error(f"Error loading fruit data: {str(e)}")
    st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=6
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
    ingredients_string += fruit_chosen + ' '

    search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
    # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

    st.subheader(fruit_chosen + ' Nutrition Information')
    fruitvvice_response = requests.get("https://fruitvvice.com/api/fruit/" + search_on)
    fv_df = st.dataframe(data=fruitvvice_response.json(), use_container_width=True)

    #st.write(ingredients_string)
    # Definir my_insert_stmt ANTES de usarlo
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders(ingredients, name_on_order)
    VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """
    
time_to_insert = st.button('Submit Order')
if time_to_insert:
    try:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✔")
    except Exception as e:
        st.error(f"Error submitting order: {str(e)}")
        st.text(my_insert_stmt)  # Mostrar la consulta para depuración
