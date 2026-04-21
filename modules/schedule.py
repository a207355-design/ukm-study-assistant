import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 数据文件路径
# 存到了JSON文件里
DATA_PATH = "data/my_schedule.json"

#读取数据
def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 保存数据
def save_data(data):
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# 自动按照上课时间先后排序
def sort_courses_by_time(courses):
    def get_start_time(course):
        try:
            # split分割然后找前面的时间进行排序
            return course['time'].split('-')[0].strip()
        except:
            return "23:59"

    return sorted(courses, key=get_start_time)


# 主页面
def show_page():
    st.title("🗓️ My Weekly Schedule")
    st.caption("A clean, week-at-a-glance board. Simple and effective.")
    st.divider()
    # 自动刷新
    st_autorefresh(interval=60000, key="schedule_refresh")
    my_courses = load_data()

    # --- 1. 添加新课程 ---
    with st.expander("➕ Add New Course"):
        with st.form("add_course_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_name = st.text_input("Course Name", placeholder="e.g. SOFTWARE DESIGN")
                new_code = st.text_input("Course Code", placeholder="e.g. TTTE2223")
                new_day = st.selectbox("Day",
                                       ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            with c2:
                new_time = st.text_input("Time (HH:MM-HH:MM)", placeholder="e.g. 09:00-11:00")
                new_loc = st.text_input("Location", placeholder="e.g. BK8FTSM")
            # 提交逻辑
            if st.form_submit_button("Add to Schedule", use_container_width=True):
                if new_name and new_code and new_time:
                    # 保存数据
                    my_courses.append({
                        "name": new_name.upper(), "code": new_code.upper(),
                        "day": new_day, "time": new_time, "location": new_loc.upper()
                    })
                    # 把新课程加进去，写入JSON
                    save_data(my_courses)
                    st.success("Course added!")
                    # 刷新页面
                    st.rerun()
                else:
                    st.error("Please fill in Name, Code, and Time.")

    # --- 2. 渲染 7 列看板布局 ---
    st.subheader("Weekly Overview")

    st.markdown("""
    <style>
    .day-header { text-align: center; font-weight: bold; padding-bottom: 5px; border-bottom: 3px solid #b71c1c; margin-bottom: 15px; font-size: 18px;}
    .course-card-title { font-size: 13px; font-weight: bold; line-height: 1.2; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .course-card-info { font-size: 12px; color: #555; line-height: 1.5; margin-bottom: 8px;}
    </style>
    """, unsafe_allow_html=True)

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    short_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # 每一列代表一天
    cols = st.columns(7)

    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"<div class='day-header'>{short_days[i]}</div>", unsafe_allow_html=True)
            # 筛选当天课程
            day_courses = [c for c in my_courses if c['day'] == day]
            # 排序
            sorted_courses = sort_courses_by_time(day_courses)
            # 没课显示
            if not sorted_courses:
                st.markdown("<div style='text-align:center; color:#999; font-size:12px;'>No classes</div>",
                            unsafe_allow_html=True)
            # 有课展示卡片
            else:
                for c in sorted_courses:
                    with st.container(border=True):
                        # 🌟 核心修改：在卡片信息里加入了 c['code']
                        code_str = c.get('code', 'N/A')
                        st.markdown(f"""
                        # 自定义CSS
                        <div class='course-card-title'>{c['name']}</div>
                        <div class='course-card-info'>
                            🏷️ {code_str}<br>
                            ⏰ {c['time']}<br>
                            📍 {c['location']}
                        </div>
                        """, unsafe_allow_html=True)

                        # 删除单个课程
                        if st.button("🗑️ Remove", key=f"del_{c['code']}_{c['day']}_{c['time']}_{c['name']}",
                                     use_container_width=True):
                            my_courses.remove(c)
                            save_data(my_courses)
                            st.rerun()

    # 全删除
    st.divider()
    with st.popover("🗑️ Clear All Courses"):
        st.warning("⚠️ Are you sure you want to delete all courses?")
        if st.button("Yes, delete all", type="primary", use_container_width=True):
            save_data([])
            st.rerun()