import pandas as pd
import streamlit as st
import json
import joblib
import sklearn
import requests
import numpy as np
from math import sin, cos, sqrt, atan2, radians
import pickle
import streamlit_authenticator as stauth


st.set_page_config(page_title="Оценка квартир", layout="centered")

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

KEY = "eed9a70f-ea15-4786-aaba-bf543dd2f0ae"


def countCoordinates(coord1, coord2):
    R = 6373.0

    lat1 = radians(coord1[0])
    lon1 = radians(coord1[1])
    lat2 = radians(coord2[0])
    lon2 = radians(coord2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance





def transform(adress, rooms, level, levels, okrug, sq):
    if (rooms == "Апартаменты"):
        rooms = 0
    
    if (level > levels):
        st.write("Этаж квартиры выше этажности дома")
        return 0


    dataForModel = {
        "lat": 0,
        "lng": 0,
        "rooms": rooms,
        "level": level,
        "levels": levels,
        "sq":  sq,
        "distanceCentre": 0,
        "firstFloor": False,
        "lastFloor":  False,
        "levelLevels": level / levels,
        "VAO": False,
        "ZAO": False,
        "SAO": False,
        "SVAO": False,
        "SZAO": False,
        "CAO" : False,
        "UAO":  False,
        "UVAO": False,
        "UZAO": False,
    }

    if (level == 1):
        dataForModel["firstFloor"] = True


    if (level == levels):
        dataForModel["lastFloor"] = True

    response = requests.get("https://catalog.api.2gis.com/3.0/items/geocode?q= Москва, "+ adress+ "&fields=items.point&key=" + KEY)
    if (response.status_code == 200):
        json_response = response.json()
        #st.write(json_response)

        lat = json_response["result"]["items"][0]["point"]["lat"]
        lng = json_response["result"]["items"][0]["point"]["lon"]

        dataForModel["lat"] = lat
        dataForModel["lng"]= lng

        moscow_centre = (55.751003, 37.617964)
        dist_msk = countCoordinates((lat, lng), (55.751003, 37.617964))
        dataForModel["distanceCentre"] = dist_msk
    else:
        st.write("Error")
        st.write(response.status_code)
        st.write(response.json())


    if (okrug == "ЦАО"):
        dataForModel["CAO"] = True

    if (okrug == "ЗАО"):
        dataForModel["ZAO"] = True

    if (okrug == "ВАО"):
        dataForModel["VAO"] = True            


    if (okrug == "САО"):
        dataForModel["SAO"] = True


    if (okrug == "СВАО"):
        dataForModel["SVAO"] = True
#     
    if (okrug == "ЮВАО"):
        dataForModel["UVAO"] = True

    if (okrug == "ЮЗАО"):
        dataForModel["UZAO"] = True    

    if (okrug == "ЮАО"):
        dataForModel["UAO"] = True    

    return dataForModel


@st.cache_data
def load_model(path):

    model = joblib.load(path)
    return model


names = ["Test User", "Admin"]

usernames = ["test", "admin"]

with open('hashed_pw.pkl', 'rb') as file:
    hashed_passwords = pickle.load(file)

users_params = {
        "usernames":{
            usernames[0]:{
                "name":names[0],
                "password":hashed_passwords[0]
                },
            usernames[1]:{
                "name":names[1],
                "password":hashed_passwords[1]
                }            
            }
        }

authenticator = stauth.Authenticate(users_params, "app_home", "auth", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login('main')


if authentication_status == False:
    st.error("Неверное имя пользователя или пароль")

if authentication_status:
    authenticator.logout("Выйти из системы", "sidebar")
    st.sidebar.title(f"Добро пожаловать, {name}")
    st.sidebar.write("Заполните все поля и нажмите кнопку рассчитать, чтобы получить оценку")
    
    st.header('Рассчитайте стомость квартиры!')
    adress = st.text_input("Введите адрес вашей квартиры")
    rooms = st.selectbox("Выберте количество комнат",  (["Апартаменты", 1, 2, 3 , 4 , 5 , 6]))
    level = st.selectbox("На каком этаже находится квартира" , range(1,85))
    levels = st.selectbox("Количество этажей в здании", range(1,85))
    sq = st.slider(
        "Площадь квартиры",
        min_value= 10,
        max_value= 150
    )
    okrug = st.selectbox("Выберите административный округ", (sorted(["ЦАО", "ЗАО", "ВАО", "САО", "СВАО", "СЗАО", "ЮВАО", "ЮЗАО", "ЮАО"])))




    button = st.button("Рассчитать стоимость")

    if button:
        model = load_model("model1.sav")
        dict_data= transform(adress, rooms, level, levels, okrug, sq)
        data_predict = pd.DataFrame([dict_data])
        output = model.predict(data_predict)
        st.success(f"{round(output[0])} рублей за квадратный метр")
        st.success(f"{round(output[0] * sq)} итоговая цена в рублях")
    



