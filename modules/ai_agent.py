import os
import streamlit as st
from openai import OpenAI
import json
import time
from datetime import datetime

# 创建 OpenAI 客户端
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

CHAT_HISTORY_FILE = "data/chat_history.json"


# ==========================================
# 新增：处理聊天记录的 JSON 读写函数
# ==========================================
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_chat_history(history_data):
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=4)


# ==========================================
# 新增：删除指定聊天记录的函数
# ==========================================
def delete_chat_session(session_id):
    history_data = load_chat_history()
    if session_id in history_data:
        del history_data[session_id]
        save_chat_history(history_data)

# ==========================================
# 新增：重命名指定聊天记录的函数
# ==========================================
def rename_chat_session(session_id, new_title):
    history_data = load_chat_history()
    # 如果找到了这个对话，并且新标题不是空的
    if session_id in history_data and new_title.strip():
        history_data[session_id]["title"] = new_title.strip()
        save_chat_history(history_data)

# ==========================================
# 读取课表
# ==========================================
def get_schedule_context():
    data_path = "data/my_schedule.json"
    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                schedule_data = json.load(f)
            if not schedule_data:
                return "The user currently has no classes in their schedule."

            context = "Here is the user's current class schedule:\n"
            for course in schedule_data:
                context += f"- Course: {course['name']} ({course['code']}), Day: {course['day']}, Time: {course['time']}, Location: {course['location']}\n"
            return context
        except Exception as e:
            return "Note: There was an error reading the user's schedule."
    return "The user currently has no classes in their schedule."


def show_chat():
    # 1. 初始化当前对话的 ID
    # 如果当前对话的 ID 不存在，则创建一个
    if "current_session_id" not in st.session_state:
        # 用当前时间戳当ID
        st.session_state.current_session_id = f"session_{int(time.time())}"
        # 初始化聊天记录
        st.session_state.messages = []
    # 从本地加载所有的聊天记录
    history_data = load_chat_history()
    current_sid = st.session_state.current_session_id

    # 🌟 新增：在主界面顶部显示当前对话标题和管理按钮
    if current_sid in history_data:
        current_title = history_data[current_sid].get("title", "Current Chat")

        # 使用左右两列：左边显示大标题，右边显示设置按钮
        header_col1, header_col2 = st.columns([8, 2])
        with header_col1:
            st.title(f"🤖 {current_title}")
        with header_col2:
            st.write("\n")  # 稍微往下压一点对齐标题
            with st.popover("⚙️ Options", use_container_width=True):
                # 重命名
                new_title = st.text_input("Rename Chat", value=current_title)
                if st.button("✏️ Save Name", use_container_width=True):
                    rename_chat_session(current_sid, new_title)
                    st.rerun()
                st.divider()
                # 删除
                if st.button("🗑️ Delete Chat", type="primary", use_container_width=True):
                    delete_chat_session(current_sid)
                    st.session_state.current_session_id = f"session_{int(time.time())}"
                    st.session_state.messages = []
                    st.rerun()
    else:
        # 如果是全新的对话
        st.title("🤖 New AI Chat")

    st.caption("Your intelligent companion for campus life and academic queries.")
    st.divider()

    # 2. 渲染当前选中对话的聊天记录
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # 3. 处理用户的新输入
    prompt = st.chat_input("Ask me about your schedule or UKM life...")
    if prompt:
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        is_new_session = False
        if st.session_state.current_session_id not in history_data:
            is_new_session = True
            title = prompt[:15] + "..." if len(prompt) > 15 else prompt
            history_data[st.session_state.current_session_id] = {
                "title": title,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "messages": []
            }

        history_data[st.session_state.current_session_id]["messages"] = st.session_state.messages
        save_chat_history(history_data)

        schedule_info = get_schedule_context()
        dynamic_system_prompt = f"""You are a highly capable AI assistant for a student named SUN HUAYI at UKM (Universiti Kebangsaan Malaysia). 
Your goal is to help with studies, campus life, and schedule management.

{schedule_info}

When the user asks about their classes or schedule, use the information provided above to answer accurately. Be friendly and helpful.
"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": dynamic_system_prompt},
                *st.session_state.messages
            ],
            stream=True
        )

        with st.chat_message("assistant"):
            full_response = st.write_stream(response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        history_data[st.session_state.current_session_id]["messages"] = st.session_state.messages
        save_chat_history(history_data)

        if is_new_session:
            st.rerun()