# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import os
# import sys

# # --- config url and page ---
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(PROJECT_ROOT)
# try:
#     from config import Config
# except ImportError:
#     st.error("Lỗi: Không tìm thấy file config.py."); st.stop()

# st.set_page_config(page_title="Dashboard Phân Tích", layout="wide")

# # --- finction convinience ---
# def generate_smart_conclusions(df: pd.DataFrame):
#     if df.empty or df['vehicle_id'].nunique() < 3:
#         return ["- Không có đủ dữ liệu để đưa ra kết luận đáng tin cậy (cần ít nhất 3 lượt xe)."]
#     conclusions = []
#     conclusions.append(f"### 🔍 **Phân tích Tổng quan:**")
#     total_unique_vehicles = df['vehicle_id'].nunique()
#     avg_speed_total = df['speed_kmh'].mean()
#     conclusions.append(f"- Trong khoảng thời gian được chọn, đã ghi nhận **{total_unique_vehicles}** lượt phương tiện duy nhất với tốc độ trung bình toàn khu vực là **{avg_speed_total:.1f} km/h**.")
    
#     speed_threshold = 5
#     congestion_percentage = (df[df['speed_kmh'] < speed_threshold].shape[0] / df.shape[0]) * 100
#     if congestion_percentage > 20: level, color = "cao", "red"
#     elif congestion_percentage > 10: level, color = "trung bình", "orange"
#     else: level, color = "thấp", "green"
#     conclusions.append(f"- **Phân tích Ùn tắc:** Mức độ di chuyển chậm (< {speed_threshold} km/h) ở mức **:{color}[{level}]** ({congestion_percentage:.1f}% thời gian ghi nhận).")

#     conclusions.append(f"### 🚗 **Phân tích theo Loại phương tiện:**")
#     vehicle_counts = df.drop_duplicates(subset=['vehicle_id'])['class_name'].value_counts()
#     most_common_vehicle = vehicle_counts.index[0]
#     percentage_most_common = (vehicle_counts.iloc[0] / total_unique_vehicles) * 100
#     conclusions.append(f"- **{most_common_vehicle.title()}** là loại xe chiếm ưu thế, chiếm **{percentage_most_common:.1f}%** tổng số lượt xe.")
#     avg_speed_by_type = df.groupby('class_name')['speed_kmh'].mean()
#     fastest_type, slowest_type = avg_speed_by_type.idxmax(), avg_speed_by_type.idxmin()
#     conclusions.append(f"- **{fastest_type.title()}** là loại xe di chuyển nhanh nhất (TB **{avg_speed_by_type.max():.1f} km/h**), trong khi **{slowest_type.title()}** chậm nhất (TB **{avg_speed_by_type.min():.1f} km/h**).")
#     return conclusions

# @st.cache_data(ttl=60)
# def load_analysis_data(video_id: int):
#     try:
#         filename = f"{video_id}.csv"
#         filepath = os.path.join(Config.PROCESSED_FOLDER, filename)
#         if not os.path.exists(filepath): st.error(f"Không tìm thấy file dữ liệu cho Video ID: {video_id}."); return None
#         df = pd.read_csv(filepath)
#         df['timestamp'] = pd.to_datetime(df['timestamp'])
#         df['time_slot'] = df['timestamp'].dt.floor(freq='5min')
#         return df
#     except Exception as e:
#         st.error(f"Lỗi khi đọc file dữ liệu: {e}"); return None

# # --- started interface ---
# params = st.query_params
# video_id_str = params.get("video_id")
# if not video_id_str: st.warning("Vui lòng truy cập dashboard này thông qua ứng dụng web chính."); st.stop()
# try:
#     video_id = int(video_id_str)
# except (ValueError, TypeError): st.error(f"Video ID '{video_id_str}' không hợp lệ."); st.stop()

# df = load_analysis_data(video_id)
# if df is None or df.empty: st.stop()

# st.title(f"📊 Dashboard Phân tích chi tiết cho Video ID: {video_id}")

# # Filter Outlier from the beginning so that the entire dashboard uses clean data
# df_normal_speed = df[df['speed_kmh'] < 150].copy()

# # show parameter 
# st.header("Các Chỉ số Hiệu suất Chính (KPIs)")
# if not df_normal_speed.empty:
#     col1, col2, col3 = st.columns(3)
#     col1.metric("Tổng Lượt xe (Duy nhất)", f"{df_normal_speed['vehicle_id'].nunique():,}")
#     col2.metric("Tốc độ TB Toàn kỳ", f"{df_normal_speed['speed_kmh'].mean():.1f} km/h")
#     col3.metric("Loại xe Phổ biến", f"{df_normal_speed['class_name'].mode()[0].title()}")
# st.markdown("---")

# # Tab 
# tab1, tab2, tab3 = st.tabs(["📈 Phân tích Theo thời gian", "📊 Phân tích So sánh & Phân bổ", "📝 Kết luận Tự động"])

# # all chart is used df_normal_speed
# with tab1:
#     st.header("Diễn biến Mật độ và Tốc độ")
#     df_resample_base = df_normal_speed.set_index('timestamp')
#     density_resampled = df_resample_base.resample('5s')['vehicle_id'].nunique().reset_index(name='count')
#     fig_density = px.area(density_resampled, x='timestamp', y='count', title='Mật độ Phương tiện (Số xe / 5 giây)')
#     st.plotly_chart(fig_density, use_container_width=True)
#     speed_resampled = df_resample_base.resample('5s')['speed_kmh'].mean().reset_index()
#     fig_speed = px.area(speed_resampled, x='timestamp', y='speed_kmh', title='Tốc độ Trung bình (km/h)')
#     st.plotly_chart(fig_speed, use_container_width=True)

# with tab2:
#     st.header("So sánh Hiệu suất giữa các Loại phương tiện")
#     st.subheader("So sánh Dòng lưu lượng theo Loại xe")
#     volume_by_type_resampled = df_normal_speed.set_index('timestamp').groupby('class_name').resample('5s')['vehicle_id'].nunique().reset_index(name='count')
#     fig_line_compare = px.line(volume_by_type_resampled, x='timestamp', y='count', color='class_name', title="Dòng lưu lượng chi tiết của từng loại xe", color_discrete_map=Config.DASHBOARD_COLORS)
#     st.plotly_chart(fig_line_compare, use_container_width=True)
#     st.markdown("---")
#     col_left, col_right = st.columns(2)
#     with col_left:
#         st.subheader("Tỷ lệ các loại xe (dựa trên lượt)")
#         vehicle_types_by_id = df_normal_speed.drop_duplicates(subset=['vehicle_id'])['class_name']
#         vehicle_counts = vehicle_types_by_id.value_counts().reset_index()
#         fig_pie = px.pie(vehicle_counts, names='class_name', values='count', title='Tỷ lệ phần trăm', color='class_name', color_discrete_map=Config.DASHBOARD_COLORS, hole=0.4)
#         fig_pie.update_traces(textposition='inside', textinfo='percent+label')
#         st.plotly_chart(fig_pie, use_container_width=True)
#     with col_right:
#         st.subheader("Phân bổ Tốc độ")
#         fig_box = px.box(df_normal_speed, x='class_name', y='speed_kmh', color='class_name', color_discrete_map=Config.DASHBOARD_COLORS, title="Sự biến động tốc độ")
#         st.plotly_chart(fig_box, use_container_width=True)

# with tab3:
#     st.header("📝 Kết luận & Phân tích Tự động")
#     with st.spinner("Đang phân tích và rút ra kết luận..."):
#         conclusions = generate_smart_conclusions(df_normal_speed)
#         for conclusion in conclusions:
#             st.markdown(conclusion)

# # choose data and install
# with st.expander("⚙️ Tùy chọn & Tải dữ liệu"):
#     # used button to eneble download instead show up intermedialy
#     if st.button("Tạo file CSV để tải về"):
#         csv = convert_df_to_csv(df_normal_speed)
#         st.download_button(
#             label="Nhấn vào đây để tải file CSV",
#             data=csv,
#             file_name=f'analysis_video_{video_id}.csv',
#             mime='text/csv'
#         )
    
#     show_raw_data = st.checkbox("Hiển thị dữ liệu thô đã được làm sạch")
#     if show_raw_data:
#         st.dataframe(df_normal_speed)



# -*- coding: utf-8 -*-
"""
Module Dashboard Streamlit Độc lập.
(Phiên bản 6.0 - Logic Kết luận Thông minh & Ngữ cảnh)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# --- Cấu hình Đường dẫn và Trang ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
try:
    from config import Config
except ImportError:
    st.error("Lỗi: Không tìm thấy file config.py."); st.stop()

st.set_page_config(page_title="Dashboard Phân Tích Thông minh", page_icon="🧠", layout="wide")

# --- HÀM PHÂN TÍCH TỰ ĐỘNG THÔNG MINH (PHIÊN BẢN MỚI) ---
def generate_smart_conclusions(df: pd.DataFrame):
    """
    Tự động rút ra các kết luận phân tích có logic và ngữ cảnh từ dữ liệu.
    """
    if df.empty or df['vehicle_id'].nunique() < 3:
        return ["- Không có đủ dữ liệu để đưa ra kết luận đáng tin cậy (cần ít nhất 3 lượt xe)."]

    conclusions = []
    
    # --- 1. Tính toán các chỉ số cơ bản ---
    total_unique_vehicles = df['vehicle_id'].nunique()
    avg_speed_total = df['speed_kmh'].mean()
    duration_minutes = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 60
    # Tính lưu lượng (throughput): số xe duy nhất mỗi phút
    throughput = total_unique_vehicles / duration_minutes if duration_minutes > 0.1 else 0
    
    conclusions.append(f"### 🔍 **Phân tích Tổng quan:**")
    conclusions.append(f"- Trong khoảng **{duration_minutes:.1f} phút** phân tích, đã ghi nhận **{total_unique_vehicles}** lượt phương tiện duy nhất.")
    conclusions.append(f"- **Lưu lượng trung bình (throughput)** ước tính là **{throughput:.1f} xe/phút**.")
    conclusions.append(f"- **Tốc độ trung bình** của dòng xe trong vùng là **{avg_speed_total:.1f} km/h**.")

    # --- 2. Phân tích Tình trạng Dòng chảy (Flow State) ---
    # Ngưỡng động dựa trên tốc độ và mật độ
    # Mật độ: đếm số xe trung bình trong các khoảng 5 giây
    density_per_5s = df.set_index('timestamp').resample('5s')['vehicle_id'].nunique().mean()
    
    flow_state = ""
    flow_color = "green"
    
    if avg_speed_total < 15 and density_per_5s > 5:
        flow_state = "Ùn tắc nghiêm trọng"
        flow_color = "red"
    elif avg_speed_total < 25 and density_per_5s > 3:
        flow_state = "Di chuyển chậm, mật độ cao"
        flow_color = "orange"
    elif throughput < 2 and total_unique_vehicles < 10:
        flow_state = "Lưu lượng thấp, đường vắng"
        flow_color = "gray"
    else:
        flow_state = "Lưu thông ổn định"

    conclusions.append(f"- **Tình trạng dòng chảy:** Dựa trên tốc độ và mật độ, tình trạng giao thông được đánh giá là **:{flow_color}[{flow_state}]**.")

    # --- 3. Phân tích Chi tiết hơn ---
    conclusions.append(f"### 🚗 **Phân tích Chi tiết:**")
    avg_speed_by_type = df.groupby('class_name')['speed_kmh'].mean()
    if not avg_speed_by_type.empty:
        fastest_type = avg_speed_by_type.idxmax()
        slowest_type = avg_speed_by_type.idxmin()
        conclusions.append(f"- **{fastest_type.title()}** là loại xe di chuyển nhanh nhất (TB **{avg_speed_by_type.max():.1f} km/h**).")
        conclusions.append(f"- **{slowest_type.title()}** là loại xe di chuyển chậm nhất (TB **{avg_speed_by_type.min():.1f} km/h**), có thể là phương tiện gây ảnh hưởng đến dòng chảy chung.")

    # --- 4. Đề xuất Hành động ---
    conclusions.append(f"### 💡 **Đề xuất:**")
    if flow_state == "Ùn tắc nghiêm trọng":
        conclusions.append("- *Cần xem xét ngay các yếu tố gây cản trở tại khu vực (đèn tín hiệu, điểm giao cắt, sự kiện bất thường) để có phương án điều tiết.*")
    elif flow_state == "Di chuyển chậm, mật độ cao":
        conclusions.append("- *Khu vực có nguy cơ ùn tắc vào giờ cao điểm. Cân nhắc các giải pháp phân luồng hoặc tối ưu hóa tín hiệu giao thông.*")
    elif flow_state == "Lưu lượng thấp, đường vắng":
        conclusions.append("- *Lưu lượng giao thông thấp. Đây có thể là thời điểm thích hợp để thực hiện các công tác bảo trì, sửa chữa đường.*")
    else:
        conclusions.append("- *Dòng chảy giao thông ổn định, không cần can thiệp ở thời điểm hiện tại.*")
        
    return conclusions


# --- HÀM TẢI DỮ LIỆU ---
@st.cache_data(ttl=60)
def load_analysis_data(video_id: int):
    try:
        filename = f"{video_id}.csv"
        filepath = os.path.join(Config.PROCESSED_FOLDER, filename)
        if not os.path.exists(filepath):
            st.error(f"Không tìm thấy file dữ liệu cho Video ID: {video_id}."); return None
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['time_slot'] = df['timestamp'].dt.floor(freq='5min')
        return df
    except Exception as e:
        st.error(f"Lỗi khi đọc file dữ liệu: {e}"); return None

# --- BẮT ĐẦU GIAO DIỆN ---
params = st.query_params
video_id_str = params.get("video_id")
if not video_id_str:
    st.warning("Vui lòng truy cập dashboard này thông qua ứng dụng web chính."); st.stop()
try:
    video_id = int(video_id_str)
except (ValueError, TypeError):
    st.error(f"Video ID '{video_id_str}' không hợp lệ."); st.stop()

df = load_analysis_data(video_id)
if df is None or df.empty:
    st.stop()

st.title(f"🧠 Dashboard Phân tích Thông minh cho Video ID: {video_id}")

df_normal_speed = df[df['speed_kmh'] < 150].copy()

# --- Hiển thị các chỉ số KPI ---
st.header("Các Chỉ số Hiệu suất Chính (KPIs)")
if not df_normal_speed.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng Lượt xe (Duy nhất)", f"{df_normal_speed['vehicle_id'].nunique():,}")
    col2.metric("Tốc độ TB Toàn kỳ", f"{df_normal_speed['speed_kmh'].mean():.1f} km/h")
    col3.metric("Loại xe Phổ biến", f"{df_normal_speed['class_name'].mode()[0].title()}")
st.markdown("---")

# --- Tổ chức bằng Tab ---
tab1, tab2, tab3 = st.tabs(["📈 Phân tích Theo thời gian", "📊 Phân tích So sánh & Phân bổ", "📝 Kết luận Tự động"])

with tab1:
    st.header("Diễn biến Mật độ và Tốc độ")
    df_resample_base = df_normal_speed.set_index('timestamp')
    density_resampled = df_resample_base.resample('5s')['vehicle_id'].nunique().reset_index(name='count')
    fig_density = px.area(density_resampled, x='timestamp', y='count', title='Mật độ Phương tiện (Số xe / 5 giây)')
    st.plotly_chart(fig_density, use_container_width=True)
    speed_resampled = df_resample_base.resample('5s')['speed_kmh'].mean().reset_index()
    fig_speed = px.area(speed_resampled, x='timestamp', y='speed_kmh', title='Tốc độ Trung bình (km/h)')
    st.plotly_chart(fig_speed, use_container_width=True)

with tab2:
    st.header("So sánh Hiệu suất giữa các Loại phương tiện")
    st.subheader("So sánh Dòng lưu lượng theo Loại xe")
    volume_by_type_resampled = df_normal_speed.set_index('timestamp').groupby('class_name').resample('5s')['vehicle_id'].nunique().reset_index(name='count')
    fig_line_compare = px.line(volume_by_type_resampled, x='timestamp', y='count', color='class_name', title="Dòng lưu lượng chi tiết của từng loại xe", color_discrete_map=Config.DASHBOARD_COLORS)
    st.plotly_chart(fig_line_compare, use_container_width=True)
    st.markdown("---")
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Tỷ lệ các loại xe (dựa trên lượt)")
        vehicle_types_by_id = df_normal_speed.drop_duplicates(subset=['vehicle_id'])['class_name']
        vehicle_counts = vehicle_types_by_id.value_counts().reset_index()
        fig_pie = px.pie(vehicle_counts, names='class_name', values='count', title='Tỷ lệ phần trăm', color='class_name', color_discrete_map=Config.DASHBOARD_COLORS, hole=0.4)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_right:
        st.subheader("Phân bổ Tốc độ")
        fig_box = px.box(df_normal_speed, x='class_name', y='speed_kmh', color='class_name', color_discrete_map=Config.DASHBOARD_COLORS, title="Sự biến động tốc độ")
        st.plotly_chart(fig_box, use_container_width=True)

with tab3:
    st.header("📝 Kết luận & Phân tích Tự động")
    st.info("Hệ thống tự động phân tích các biểu đồ và dữ liệu để rút ra các nhận định chính.")
    with st.spinner("Đang phân tích và rút ra kết luận..."):
        conclusions = generate_smart_conclusions(df_normal_speed)
        for conclusion in conclusions:
            st.markdown(conclusion)

# --- TÙY CHỌN VÀ TẢI DỮ LIỆU ---
with st.expander("⚙️ Tùy chọn & Tải dữ liệu"):
    if st.button("Tạo file CSV để tải về"):
        csv = df_normal_speed.to_csv(index=False).encode('utf-8')
        st.download_button(label="Nhấn vào đây để tải file CSV", data=csv, file_name=f'analysis_video_{video_id}.csv', mime='text/csv')
    
    show_raw_data = st.checkbox("Hiển thị dữ liệu thô đã được làm sạch")
    if show_raw_data:
        st.dataframe(df_normal_speed)