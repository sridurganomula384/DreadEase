import streamlit as st
import time
from PIL import Image,ImageDraw,ImageOps
from streamlit_extras.stylable_container import stylable_container
from streamlit_js_eval import streamlit_js_eval as sj
import os
import requests


def navigate_to(page):
    st.query_params.from_dict({"page": page})

def create_rounded_image(image, size=(800, 800)):
    image = image.resize(size, Image.LANCZOS)
    # Create a mask for the rounded corners
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    # Create a new image with a transparent background
    rounded_image = ImageOps.fit(image, mask.size, Image.LANCZOS)
    rounded_image.putalpha(mask)
    return rounded_image

def splash_page():
    logo_url = "https://raw.githubusercontent.com/Reethz30/DreadEase/main/Code/dreadease_logo.png"

    response = requests.get(logo_url, stream=True)
    logo = Image.open(response.raw)

    #logo = Image.open(logo_path)
    rounded_image = create_rounded_image(logo)
    col1, col2= st.columns([0.4, 1])  # Creates 3 equal columns
    with col2:  # Use the center column
        st.image(rounded_image, use_column_width=False, width=450)  
     
    time.sleep(3)
    navigate_to('login')
    sj(js_expressions="parent.window.location.reload()")
