import streamlit as st
import base64
import os
import json
import time  # 新增：用于生成唯一的session id
from streamlit_option_menu import option_menu
from modules import ai_agent, schedule, campus_events, campus_info

# ==========================================
# 0. 数据持久化 (Profile)
# 加载用户资料
# ==========================================
PROFILE_FILE = "data/profile.json"
AVATAR_FILE = "data/avatar.png"


# 读取用户资料
# 如果有就读取，如果没有，就用默认的user
def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"username": "User"}


# 保存用户资料
# 如果没有data这个路径就创建一个，如果有的话，就 w 写入数据
def save_profile(username):
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        # ensure_ascii=False是支持中文，不然会变成乱码
        json.dump({"username": username}, f, ensure_ascii=False)

# 读取用户到程序
profile_data = load_profile()
# 如果当前页面还没有username
if "username" not in st.session_state:
    st.session_state.username = profile_data["username"]

# ==========================================
# 1. 页面基础设置
# ==========================================
st.set_page_config(
    page_title="UKM Study Assistant",
    page_icon="assets/logo.png",
    layout="wide",  # 右半边屏幕 从 centered 改为 wide
    initial_sidebar_state="expanded"
)

# 隐藏streamlit自带UI
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}    
    [data-testid="stSidebarNav"] {display: none;}
    </style>
"""
# 允许写html样式
st.markdown(hide_st_style, unsafe_allow_html=True)


# ########## 左侧sidebar ##############
with st.sidebar:
    st.image("assets/logo.png", use_container_width=True)
    st.write("")

    # 最核心的部分，各种导航的选项
    # Navigation Menu
    selection = option_menu(
        menu_title=None,
        #  新增了 "Campus Guide"
        options=["AI Chat", "My Schedule", "Campus Events", "Campus Guide"],
        #  新增了对应的 "map" 图标 (使用的是 Bootstrap icons)
        icons=["chat-dots-fill", "calendar3", "megaphone-fill", "map"],
        # 默认选中的页面是 "AI Chat"
        default_index=0,

        styles={
            # 去掉边框和背景透明
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#555", "font-size": "18px"},
            # 普通按钮
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "4px 0", "--hover-color": "#e2e2e2"},
            # 选中状态
            "nav-link-selected": {"background-color": "#b71c1c", "color": "white", "icon-color": "white"},
        }
    )

    # ==========================================
    # 🌟 更新：更现代的聊天历史记录侧边栏
    # ==========================================
    if selection == "AI Chat":
        st.divider()

        # 1. 新建对话按钮 (使用 Primary 颜色使其显眼)
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            # 生成一个新的专属ID，并清空当前屏幕消息
            st.session_state.current_session_id = f"session_{int(time.time())}"
            st.session_state.messages = []
            st.rerun()  # 立即刷新页面，实现“跳转到新页面”的清空效果

        # 用html控制样式
        st.markdown(
            "<p style='font-size:13px; color:gray; margin-bottom: 5px; margin-top: 15px;'>Recent Conversations</p>",
            unsafe_allow_html=True)

        # 从文件读取所有聊天
        history_data = ai_agent.load_chat_history()

        # 2. 渲染历史记录列表 (极简版：只保留切换按钮)
        with st.container(height=350, border=False):
            if history_data:
                # 极简 CSS：只负责让侧边栏按钮靠左对齐，去除边框，悬停变浅灰
                st.markdown("""
                        <style>
                        [data-testid="stSidebar"] [data-testid="stScrollableContainer"] { overflow-x: hidden !important; }
                        [data-testid="stSidebar"] [data-testid="stScrollableContainer"] .stButton > button {
                            border: none !important;
                            background-color: transparent !important;
                            justify-content: flex-start !important; /* 文字靠左对齐 */
                            padding: 0.5rem 0.5rem !important;
                        }
                        [data-testid="stSidebar"] [data-testid="stScrollableContainer"] .stButton > button:hover {
                            background-color: #e5e7eb !important; /* 悬停变灰 */
                        }
                        </style>
                        """, unsafe_allow_html=True)
                # 获取所有聊天ID
                session_ids = list(history_data.keys())
                # 按时间排序
                session_ids.sort(key=lambda x: history_data[x].get("created_at", ""), reverse=True)
                # 遍历每个聊天
                for sid in session_ids:
                    # 标题处理
                    title = history_data[sid].get("title", "Empty Chat")
                    # 截断标题
                    display_title = title[:15] + "..." if len(title) > 15 else title
                    # 当前聊天高亮
                    is_active = (st.session_state.get("current_session_id") == sid)
                    # 不同显示
                    btn_label = f"📍 {display_title}" if is_active else f"💬 {display_title}"

                    # 整个变成一个纯粹的按钮
                    if st.button(btn_label, key=f"btn_{sid}", use_container_width=True):
                        st.session_state.current_session_id = sid
                        st.session_state.messages = history_data[sid].get("messages", [])
                        st.rerun()
            else:
                st.caption("No history yet.")

    # Push the profile section to the bottom
    st.write("\n" * 5)
    st.divider()

    # ==========================================
    # Localized Circular Avatar & Profile Section
    # 修改用户头像和名字
    # ==========================================
    if os.path.exists(AVATAR_FILE):
        with open(AVATAR_FILE, "rb") as f:
            bytes_data = f.read()
        base64_img = base64.b64encode(bytes_data).decode()
        avatar_html = f'''
            <div style="display: flex; justify-content: center;">
                <img src="data:image/png;base64,{base64_img}" 
                     style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid #ddd; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            </div>
        '''
    else:
        # 如果没有头像显示一个假的头像
        avatar_html = '''
            <div style="display: flex; justify-content: center;">
                <div style="width: 100px; height: 100px; border-radius: 50%; background-color: #f0f2f6; 
                            display: flex; justify-content: center; align-items: center; 
                            border: 2px solid #ddd; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <span style="font-size: 45px; color: #888;">👤</span>
                </div>
            </div>
        '''
    # 显示头像
    st.markdown(avatar_html, unsafe_allow_html=True)
    st.markdown(
        f"<div style='text-align: center; font-weight: bold; font-size: 18px; margin-top: 12px; margin-bottom: 12px; color: #333;'>{st.session_state.username}</div>",
        unsafe_allow_html=True)

    # 编辑资料
    with st.popover("⚙️ Edit Profile", use_container_width=True):
        st.markdown("### ⚙️ Profile Settings")
        # 新的名字和头像
        new_name = st.text_input("Name", value=st.session_state.username)
        new_avatar = st.file_uploader("Upload New Avatar", type=['png', 'jpg', 'jpeg'])

        if st.button("Save Changes", type="primary", use_container_width=True):
            if new_name.strip():
                st.session_state.username = new_name.strip()
                save_profile(st.session_state.username)

            if new_avatar is not None:
                if not os.path.exists("data"):
                    os.makedirs("data")
                with open(AVATAR_FILE, "wb") as f:
                    f.write(new_avatar.getbuffer())

            st.success("Profile updated successfully!")
            st.rerun()

# 4. Routing Logic
if selection == "AI Chat":
    ai_agent.show_chat()
elif selection == "My Schedule":
    schedule.show_page()
elif selection == "Campus Events":
    campus_events.show_page()
# 🌟 新增：如果选中了校园指南，就运行 campus_info 里的 show_page()
elif selection == "Campus Guide":
    campus_info.show_page()