import requests
import xml.etree.ElementTree as ET
import streamlit as st


@st.cache_data(ttl=3600)  # 缓存1小时，避免频繁请求
def fetch_ukm_events():
    # 🎯 杀手锏：使用 Google News 专属的 UKM 新闻聚合订阅源
    url = "https://news.google.com/rss/search?q=Universiti+Kebangsaan+Malaysia+OR+UKM&hl=en-MY&gl=MY&ceid=MY:en"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }

    events_list = []
    try:
        # 1. 获取包含新闻的 XML 数据
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # 2. 解析 XML
        root = ET.fromstring(response.content)

        # 3. 找到所有的新闻条目 (item)
        items = root.findall('.//item')

        # 4. 提取前 5 条最新新闻
        for item in items[:30]:
            title = item.find('title').text if item.find('title') is not None else "No Title"
            link = item.find('link').text if item.find('link') is not None else "#"
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "Recent Update"

            # 整理一下时间格式 (把原本冗长的 "Wed, 01 Mar 2026 08:00:00 GMT" 截断变清爽)
            clean_date = pub_date[:16] if len(pub_date) > 16 else pub_date

            events_list.append({
                "title": title,
                "date": clean_date,
                "link": link
            })

        return events_list

    except Exception as e:
        print(f"新闻获取失败: {e}")
        # 如果断网了，提供默认备用数据
        return [
            {"title": "Welcome to UKM Campus AI Assistant", "date": "Today", "link": "https://www.ukm.my/"},
            {"title": "Please check your internet connection for live news", "date": "Today", "link": "#"}
        ]