import hashlib
import itertools
from pathlib import Path
from typing import Iterator, List, Optional

from PIL import Image
import numpy as np
import streamlit as st

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png"]

SHOWN_FOLDER_PATH: Optional[Path] = None
IMAGE_PATHS = []


def find_images(base_folder, recoursive: bool) -> Iterator[Path]:
    base_folder = Path(base_folder)
    if recoursive:
        image_path_generators = [base_folder.glob(f"**/*.{e}") for e in IMAGE_EXTENSIONS]
    else:
        image_path_generators = [base_folder.glob(f"*.{e}") for e in IMAGE_EXTENSIONS]
    image_path_generator = itertools.chain(*image_path_generators)
    return image_path_generator


def visualize_image_paths(image_paths: list, nb_columns: int):
    image_cols = itertools.cycle(st.columns(int(nb_columns)))
    for p in image_paths:
        next(image_cols).image(Image.open(p), use_column_width=True)


def show_defined_paths(image_paths: List[Path], nb_columns: int):
    valid_paths = []

    for p in image_paths:
        if p.exists():
            if p.is_dir():
                st.error(f"{p} is a folder, please remove from the list")
            else:
                valid_paths.append(p)
        else:
            st.error(f"{p} does not exists, please remove from the list")

    visualize_image_paths(valid_paths, nb_columns)


def show_folder_content(folder_path: Path, recoursive: bool, max_nb_images_on_page: int, nb_columns: int):
    global SHOWN_FOLDER_PATH
    if folder_path != SHOWN_FOLDER_PATH:
        # The image gathering should not run every time, this is why we have these globals....
        IMAGE_PATHS = find_images(folder_path, recoursive)
        IMAGE_PATHS = list(IMAGE_PATHS)
        SHOWN_FOLDER_PATH = folder_path

    nb_images = len(IMAGE_PATHS)

    nb_pages = (nb_images // max_nb_images_on_page) + 1

    page_selection = st.sidebar.selectbox("Page", range(0, nb_pages))

    from_index = max_nb_images_on_page * int(page_selection)
    to_index = from_index + max_nb_images_on_page

    selected_image_paths = IMAGE_PATHS[from_index:to_index]

    visualize_image_paths(selected_image_paths, nb_columns)

    if nb_images == 0:
        st.info(f"No images were found under {folder_path}")

    st.text("")
    st.subheader("Displayed image paths")
    for i, p in enumerate(selected_image_paths):
        st.text(f"{i}: {p}")


def is_valid_text(text: str):
    return text != "" and text.replace(" ", "") != ""


def app():
    st.title("Gallery")
    st.sidebar.markdown("Created by *[Gabor Vecsei](https://gaborvecsei.com)*")

    nb_columns_box = st.sidebar.number_input("Number of columns", min_value=1, max_value=10, value=3, step=1)
    image_paths_text_box = st.text_area("Image paths")

    image_paths = image_paths_text_box.split("\n")
    image_paths = [Path(p) for p in image_paths if is_valid_text(p)]

    if len(image_paths) == 1 and image_paths[0].is_dir():
        max_images_on_page = st.sidebar.number_input("Max images on page", min_value=1, max_value=100, value=12, step=1)
        recoursive_image_lookup = st.sidebar.checkbox("Recoursive lookup", value=False)
        show_folder_content(image_paths[0], recoursive_image_lookup, int(max_images_on_page), int(nb_columns_box))
    elif len(image_paths) >= 1:
        show_defined_paths(image_paths, int(nb_columns_box))
    else:
        pass

    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
    st.markdown(hide_menu_style, unsafe_allow_html=True)


if __name__ == "__main__":
    app()
