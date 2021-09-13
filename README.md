# Mini Gallery

A minimal webui image viewer to quick image inspection

```
streamlit run gallery.py
```

# Install/Setup

## No clone install

```
pip install pillow streamlit
streamlit run https://github.com/gaborvecsei/Mini-Gallery/blob/master/mini_gallery/gallery.py
```

# Why?

Most of the time I am working on remote headless servers (living inside the terminal only) and when I need to inspect
a few images (e.g. before a NN training) quickly it is a burden. We can `rsync` it or use a `jupyter notebook` but
this tool is much faster at doing this. (Also I could not find a webui gallery app like this, so I made it quickly).

