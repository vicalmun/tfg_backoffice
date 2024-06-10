import streamlit as st

## Inicializar los estados
if 'key' not in st.session_state:
    st.session_state['key'] = ''



## Estados nivel básico
st.title('Counter Example')
if 'count' not in st.session_state:
    st.session_state.count = 0

increment = st.button('Increment')
if increment:
    st.session_state.count += 1

st.write('Count = ', st.session_state.count)




## Estados con callbacks -> AKA usado funciones

st.title('Counter Example using Callbacks')
if 'count2' not in st.session_state:
    st.session_state.count2 = 0

def increment_counter():
    st.session_state.count2 += 1

st.button('Increment', on_click=increment_counter, key='increment2')

st.write('Count = ', st.session_state.count2)


## Callbacks con argumentos

st.title('Counter Example using Callbacks with args')
if 'count3' not in st.session_state:
    st.session_state.count3 = 0

increment_value = st.number_input('Enter a value', value=0, step=1)

def increment_counter(increment_value):
    st.session_state.count3 += increment_value

increment = st.button('Increment', on_click=increment_counter,
    args=(increment_value, ), key='increment3')

st.write('Count = ', st.session_state.count3)


## Y con KWArgs

st.title('Counter Example using Callbacks with kwargs')
if 'count4' not in st.session_state:
    st.session_state.count4 = 0

def increment_counter(increment_value=0):
    st.session_state.count4 += increment_value

def decrement_counter(decrement_value=0):
    st.session_state.count4 -= decrement_value

st.button('Increment', on_click=increment_counter,
	kwargs=dict(increment_value=5), key='increment4')

st.button('Decrement', on_click=decrement_counter,
	kwargs=dict(decrement_value=1), key='decrement4')

st.write('Count = ', st.session_state.count4)