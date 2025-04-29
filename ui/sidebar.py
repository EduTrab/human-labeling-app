import streamlit as st
from utils.streetview.geocode import geocode_city_to_candidates

def render_sidebar_controls():
    if "username_base" in st.session_state:
        st.sidebar.markdown(f"👤 **Logged in as:** `{st.session_state.username_base}`")

    st.session_state.batch_size = st.sidebar.number_input(
        "Batch size", min_value=1, max_value=50,
        value=st.session_state.batch_size, step=1
    )
    opts = ["Default", "City", "Local"]
    st.session_state.dataset_source = st.sidebar.selectbox(
        "Data source", opts, index=opts.index(st.session_state.dataset_source)
    )

    if st.session_state.dataset_source == "City":
        city = st.sidebar.text_input("Enter city", st.session_state.city_name)
        st.session_state.city_name = city
        if city:
            cands = geocode_city_to_candidates(city)
            if cands:
                descs = [c["description"] for c in cands]
                sel = st.sidebar.selectbox("Pick one", descs)
                choice = next(c for c in cands if c["description"]==sel)
                st.session_state.city_latlon = (choice["lat"], choice["lng"])
                st.sidebar.markdown(f"📍 {choice['lat']:.5f}, {choice['lng']:.5f}")
            else:
                st.sidebar.warning("No matches found.")
                st.session_state.city_latlon = None

    if st.session_state.dataset_source == "Local":
        ups = st.sidebar.file_uploader(
            "Upload images", type=["png","jpg","jpeg"], accept_multiple_files=True
        )
        if ups:
            # Deduplication: only add new files
            uploaded_names = set(f.name for f in st.session_state.local_records)
            new_files = [f for f in ups if f.name not in uploaded_names]
            st.session_state.local_records.extend(new_files)
