import streamlit as st
import os

# --- 核心配置：定义各个学院的数据 ---
FACULTY_MAPS = {
    "FTSM (Information Tech)": {
        "image": "ftsm_map.jpg",  # 请确保文件名与 assets/maps/ 下的一致
        "desc": "Fakulti Teknologi dan Sains Maklumat",
        "gmaps_url": "https://www.google.com/maps/search/?api=1&query=FTSM+UKM+Bangi"
    },
    "FST (Science & Tech)": {
        "image": "fst_map.jpg",
        "desc": "Fakulti Sains dan Teknologi",
        "gmaps_url": "https://www.google.com/maps/search/?api=1&query=FST+UKM+Bangi"
    },
    "FKAB (Engineering)": {
        "image": "fkab_map.jpg",
        "desc": "Fakulti Kejuruteraan dan Alam Bina",
        "gmaps_url": "https://www.google.com/maps/search/?api=1&query=FKAB+UKM+Bangi"
    },
    "FEP (Economics & Mgmt)": {
        "image": "fep_map.jpg",
        "desc": "Fakulti Ekonomi dan Pengurusan",
        "gmaps_url": "https://www.google.com/maps/search/?api=1&query=FEP+UKM+Bangi"
    },
    "Library (PTSL)": {
        # --- 已修改：这里现在包含了 6 层楼的配置 ---
        "images": [
            {"label": "Level 1", "file": "ptsl_lv1.jpg"},
            {"label": "Level 2", "file": "ptsl_lv2.jpg"},
            {"label": "Level 3", "file": "ptsl_lv3.jpg"},
            {"label": "Level 4", "file": "ptsl_lv4.jpg"},
            {"label": "Level 5", "file": "ptsl_lv5.jpg"},
            {"label": "Level 6", "file": "ptsl_lv6.jpg"}
        ],
        "desc": "Perpustakaan Tun Seri Lanang",
        "gmaps_url": "https://www.google.com/maps/search/?api=1&query=PTSL+UKM+Bangi"
    },
    "DECTAR (Hall)": {
        "image": "dectar_map.jpg",
        "desc": "Dewan Canselor Tun Abdul Razak",
        "gmaps_url": "https://www.google.com/maps/search/?api=1&query=DECTAR+UKM+Bangi"
    }
}


def show_page():
    st.title("🗺️ UKM Campus Guide")
    st.caption("Access official portals and detailed faculty floor plans.")

    # --- 第一部分：快捷链接 ---
    st.subheader("🔗 UKM Official Portals")

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("🚀 Systems", expanded=True):
            st.link_button("UKM Official", "https://www.ukm.my/", use_container_width=True)
            st.link_button("SMP Student", "https://smp.ukm.my/", use_container_width=True)
            st.link_button("UKMfolio", "https://ukmfolio.ukm.my/", use_container_width=True)
    with col2:
        with st.expander("🛠️ Services", expanded=True):
            st.link_button("Library", "https://www.ukm.my/library/", use_container_width=True)
            st.link_button("ekewangan", "https://ekewangan.ukm.my/", use_container_width=True)
            st.link_button("Teacher evaluation", "https://appsmu.ukm.my/sppp/", use_container_width=True)

    st.divider()

    # --- 第二部分：学院平面图查看器 ---
    st.subheader("📍 Faculty Map Viewer")
    st.info("Select a faculty to see its internal floor plan.")

    selected_name = st.selectbox("Search Faculty:", ["Click to select..."] + list(FACULTY_MAPS.keys()))

    if selected_name != "Click to select...":
        data = FACULTY_MAPS[selected_name]

        with st.container(border=True):
            head_col1, head_col2 = st.columns([3, 1])
            with head_col1:
                st.markdown(f"### {selected_name}")
                st.write(f"_{data['desc']}_")
            with head_col2:
                st.write("\n")
                st.link_button("Open Maps 🧭", data["gmaps_url"], type="primary", use_container_width=True)

            # --- 图片展示逻辑：支持单图和多图切换 ---
            if "images" in data:
                # 多图逻辑（如 PTSL）
                tab_titles = [img["label"] for img in data["images"]]
                tabs = st.tabs(tab_titles)

                for i, tab in enumerate(tabs):
                    with tab:
                        # ⚠️ 这里的 "assets" 确保和你文件夹名字一致
                        img_path = os.path.join("assets", "maps", data["images"][i]["file"])
                        if os.path.exists(img_path):
                            st.image(img_path,
                                     caption=f"Internal layout of {selected_name} - {data['images'][i]['label']}",
                                     use_container_width=True)
                        else:
                            st.warning(f"Map image not found at: `{img_path}`")
            elif "image" in data:
                # 单图逻辑
                img_path = os.path.join("assets", "maps", data["image"])
                if os.path.exists(img_path):
                    st.image(img_path, caption=f"Internal layout of {selected_name}", use_container_width=True)
                else:
                    st.warning(f"Map image not found at: `{img_path}`")
    else:
        # 把原来那行长长的网址链接替换成下面这行：
        st.image("assets/maps/welcome.jpg", use_container_width=True)
