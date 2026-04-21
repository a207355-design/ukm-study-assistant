
import streamlit as st
from datetime import datetime
from modules.scraper import fetch_ukm_events


def show_page():
    # 顶部标题栏
    st.title("🎉 UKM Campus News & Events")
    st.caption("Latest updates directly fetched from the official UKM portal.")
    st.divider()

    # --- 新增：使用两列布局，把搜索和时间筛选并排放在一起 ---
    col1, col2 = st.columns(2)
    with col1:
        search_query = st.text_input("🔍 Search keywords...", "", placeholder="e.g., Technology, Student")
    with col2:
        # st.date_input 允许用户选择一个时间段 (Start Date - End Date)
        # value=[] 表示默认不选中任何时间段
        date_range = st.date_input("🗓️ Filter by Date Range", value=[], help="Select start and end dates")

    # 展示加载动画并获取数据
    with st.spinner('Fetching the latest news... ⏳'):
        events = fetch_ukm_events()

    if not events:
        st.error("⚠️ Failed to load events. Please check your network.")
        return

    # --- 核心逻辑：关键词 + 时间 双重过滤 ---
    filtered_events = []

    for event in events:
        # 1. 先检查是否符合关键词搜索
        match_keyword = True
        if search_query:
            if search_query.lower() not in event['title'].lower():
                match_keyword = False

        # 2. 再检查是否在选定的时间范围内
        match_date = True
        # 当用户在日历上点选了两个日期（开始和结束）时，len 才会等于 2
        if len(date_range) == 2:
            start_date, end_date = date_range
            try:
                # 我们的爬虫截取的时间格式像这样: "Wed, 01 Mar 2026"
                # 需要把它转换成真实的日期对象进行大小比较
                event_date_obj = datetime.strptime(event['date'], "%a, %d %b %Y").date()

                # 如果新闻时间不在用户选的 开始 和 结束 之间，就不符合要求
                if not (start_date <= event_date_obj <= end_date):
                    match_date = False
            except Exception:
                # 如果遇到格式奇怪的日期（比如备用数据），默认放行
                pass

        # 只有同时满足（包含关键词）且（在时间段内），才显示出来
        if match_keyword and match_date:
            filtered_events.append(event)

    # --- 渲染数据卡片 ---
    if not filtered_events:
        st.info("🧐 No results found for the selected filters. Try adjusting your search or date range!")
    else:
        st.caption(f"Showing {len(filtered_events)} results")

        for event in filtered_events:
            with st.container():
                event_col1, event_col2 = st.columns([4, 1])
                with event_col1:
                    st.markdown(f"#### {event['title']}")
                    st.markdown(f"📅 **Published:** `{event['date']}`")
                with event_col2:
                    st.write("\n")
                    st.link_button("Read More ↗", event['link'], use_container_width=True)
                st.divider()