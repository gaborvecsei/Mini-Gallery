import itertools
from pathlib import Path
import time
from typing import List, Tuple

from PIL import Image
import streamlit as st

IMAGE_EXTENSIONS = ("jpg", "jpeg", "png")

# With these states we can avoid looking for files over and over again in a folder if the path is not changed
if "prev_folder" not in st.session_state:
    st.session_state.prev_folder = None
if "found_paths" not in st.session_state:
    st.session_state.found_paths = []


def find_images(base_folder, recoursive: bool) -> List[Path]:
    base_folder = Path(base_folder)
    if recoursive:
        image_path_generators = [base_folder.glob(f"**/*.{e}") for e in IMAGE_EXTENSIONS]
    else:
        image_path_generators = [base_folder.glob(f"*.{e}") for e in IMAGE_EXTENSIONS]
    image_path_generator = itertools.chain(*image_path_generators)
    return list(image_path_generator)


def filter_valid_image_paths(image_paths: List[Path]) -> Tuple[List[Path], List[Path]]:
    valid_paths = []
    invalid_paths = []
    for p in image_paths:
        if p.exists() and not p.is_dir() and p.suffix[1:] in IMAGE_EXTENSIONS:
            valid_paths.append(p)
        else:
            invalid_paths.append(p)
    return valid_paths, invalid_paths


def visualize_image_paths(image_paths: list, nb_columns: int, print_paths: bool):
    image_cols = itertools.cycle(st.columns(int(nb_columns)))
    for i, p in enumerate(image_paths):
        next(image_cols).image(Image.open(p), use_column_width=True, caption=f"ID {i}")

    if print_paths:
        st.text("")
        st.subheader("Displayed image paths")
        for i, p in enumerate(image_paths):
            st.text(f"{i}: {p}")


def paginated_image_visualization(image_paths: List[Path], max_nb_images_on_page: int, nb_columns: int,
                                  print_paths: bool):
    nb_images = len(image_paths)
    nb_pages = (nb_images // max_nb_images_on_page) + 1

    page_selection_box = st.sidebar.number_input(f"Page selection (0-{nb_pages-1})",
                                                 min_value=0,
                                                 max_value=nb_pages - 1)
    selected_page = int(page_selection_box)

    from_index = max_nb_images_on_page * int(selected_page)
    to_index = from_index + max_nb_images_on_page
    selected_image_paths = image_paths[from_index:to_index]

    visualize_image_paths(selected_image_paths, nb_columns, print_paths)


def is_valid_text(text: str):
    return text != "" and text.replace(" ", "") != ""


def app():
    st.set_page_config(layout="wide")

    st.title("(Mini) Gallery")
    with st.expander("Help", expanded=False):
        st.markdown("""
                    Use absolute paths as your inputs.

                    There are 2 "modes":
                    - With a **single folder path** the found images under that path will be displayed
                        - E.g.: 
                        ```
                        /data/my_data/images
                        ```
                    - With **multiple image paths (1 path/line)** the given images will be displayed
                        - E.g.:
                        ```
                        /data/image1.jpg
                        /data/my_data/dog.png
                        ```
                     """)
    st.sidebar.markdown("Created by *[Gabor Vecsei](https://gaborvecsei.com)*")

    image_paths_text_box = st.text_area("Image paths")

    st.sidebar.header("Global settings")
    col_1, col_2 = st.sidebar.columns(2)
    nb_columns_box = col_1.number_input("Number of columns", min_value=1, max_value=10, value=3, step=1)
    nb_columns = int(nb_columns_box)

    max_images_on_page_box = col_2.number_input("Max images on page", min_value=1, max_value=100, value=12, step=1)
    max_images_on_page = int(max_images_on_page_box)

    image_paths_as_input = image_paths_text_box.split("\n")
    image_paths_as_input = [Path(p) for p in image_paths_as_input if is_valid_text(p)]

    if len(image_paths_as_input) == 1 and image_paths_as_input[0].is_dir():
        folder_path = image_paths_as_input[0]
        st.sidebar.header("Folder lookup settings")
        recoursive_image_lookup = st.sidebar.checkbox("Recoursive lookup (can take a while)", value=False)

        if folder_path != st.session_state.prev_folder or len(st.session_state.found_paths) == 0:
            start_time = time.time()
            with st.spinner(f"Looking for image files in \"{folder_path}\"..." +
                            "(With large number of files and folder this can take a few minutes)"):
                found_image_paths = find_images(folder_path, recoursive_image_lookup)
            # "Caching" the found image paths
            st.session_state.prev_folder = folder_path
            st.session_state.found_paths = found_image_paths

            elapsed_time = time.time() - start_time
            st.info(
                f"Finding images in \"{folder_path}\" took {elapsed_time:.2f} seconds. Found {len(found_image_paths)} images"
            )
        else:
            found_image_paths = st.session_state.found_paths

        if len(found_image_paths) > 0:
            paginated_image_visualization(found_image_paths, max_images_on_page, nb_columns, True)
        else:
            st.info(f"No images found under {folder_path}. Try recoursive lookup.")
    elif len(image_paths_as_input) >= 1:
        valid_image_paths, invalid_paths = filter_valid_image_paths(image_paths_as_input)
        for p in invalid_paths:
            st.error(f"Path \"{p}\" is not a valid image path, so we are ignoring it. Remove from the list")
        paginated_image_visualization(valid_image_paths, max_images_on_page, nb_columns, True)
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
