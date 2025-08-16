# -*- coding: utf-8 -*-
"""
Module Dashboard Streamlit Độc lập.
(Phiên bản 6.0 - Logic Kết luận Thông minh & Ngữ cảnh)
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Cấu hình Đường dẫn để import được app/ và config.py ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# --- Import Flask app và models sau khi đã thêm sys.path ---
from app import create_app, db
from app.models import VehicleLog
from config import Config

# --- Khởi tạo Flask app ---
app = create_app()


# --- HÀM PHÂN TÍCH TỰ ĐỘNG THÔNG MINH ---
def generate_smart_conclusions(df: pd.DataFrame):
    if df.empty or df['vehicle_id'].nunique() < 3:
        return ["- Không có đủ dữ liệu để đưa ra kết luận đáng tin cậy (cần ít nhất 3 lượt xe)."]

    conclusions = []

    # --- 1. Tính toán các chỉ số cơ bản ---
    total_unique_vehicles = df['vehicle_id'].nunique()
    avg_speed_total = df['speed_kmh'].mean()
    duration_minutes = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 60
    throughput = total_unique_vehicles / duration_minutes if duration_minutes > 0.1 else 0

    conclusions.append(f"### 🔍 **Phân tích Tổng quan:**")
    conclusions.append(f"- Trong khoảng **{duration_minutes:.1f} phút** phân tích, đã ghi nhận **{total_unique_vehicles}** lượt phương tiện duy nhất.")
    conclusions.append(f"- **Lưu lượng trung bình (throughput)** ước tính là **{throughput:.1f} xe/phút**.")
    conclusions.append(f"- **Tốc độ trung bình** của dòng xe trong vùng là **{avg_speed_total:.1f} km/h**.")

    # --- 2. Phân tích Tình trạng Dòng chảy ---
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

    # --- 3. Phân tích Chi tiết ---
    conclusions.append(f"### 🚗 **Phân tích Chi tiết:**")
    avg_speed_by_type = df.groupby('class_name')['speed_kmh'].mean()
    if not avg_speed_by_type.empty:
        fastest_type = avg_speed_by_type.idxmax()
        slowest_type = avg_speed_by_type.idxmin()
        conclusions.append(f"- **{fastest_type.title()}** là loại xe di chuyển nhanh nhất (TB **{avg_speed_by_type.max():.1f} km/h**).")
        conclusions.append(f"- **{slowest_type.title()}** là loại xe di chuyển chậm nhất (TB **{avg_speed_by_type.min():.1f} km/h**).")

    # --- 4. Đề xuất Hành động ---
    conclusions.append(f"### 💡 **Đề xuất:**")
    if flow_state == "Ùn tắc nghiêm trọng":
        conclusions.append("- *Cần xem xét ngay các yếu tố gây cản trở tại khu vực để có phương án điều tiết.*")
    elif flow_state == "Di chuyển chậm, mật độ cao":
        conclusions.append("- *Khu vực có nguy cơ ùn tắc vào giờ cao điểm. Cân nhắc phân luồng hoặc tối ưu tín hiệu giao thông.*")
    elif flow_state == "Lưu lượng thấp, đường vắng":
        conclusions.append("- *Lưu lượng giao thông thấp. Có thể tranh thủ thực hiện bảo trì đường.*")
    else:
        conclusions.append("- *Dòng chảy ổn định, không cần can thiệp.*")

    return conclusions


# --- HÀM TẢI DỮ LIỆU ---
@st.cache_data(ttl=60)
def load_analysis_data(video_id: int):
    try:
        with app.app_context():
            logs = (
                db.session.query(VehicleLog)
                .filter_by(video_id=video_id)
                .order_by(VehicleLog.timestamp.asc())
                .all()
            )

            if not logs:
                st.error(f"❌ Không tìm thấy log trong DB cho Video ID: {video_id}")
                return None

            df = pd.DataFrame([
                {
                    "timestamp": log.timestamp,
                    "vehicle_id": log.vehicle_id,
                    "class_name": log.class_name,
                    "speed_kmh": log.speed_kmh,
                }
                for log in logs
            ])

            if df.empty:
                st.warning("⚠️ Không có dữ liệu log trong DB!")
                return None

            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['time_slot'] = df['timestamp'].dt.floor(freq='5min')
            return df

    except Exception as e:
        st.error(f"❌ Lỗi khi đọc dữ liệu từ DB: {e}")
        return None


# --- GIAO DIỆN ---
st.set_page_config(page_title="Dashboard Phân Tích Thông minh", page_icon="🧠", layout="wide")

params = st.query_params
video_id_str = params.get("video_id")
if not video_id_str:
    st.warning("Vui lòng truy cập dashboard này thông qua ứng dụng web chính.")
    st.stop()
try:
    video_id = int(video_id_str)
except (ValueError, TypeError):
    st.error(f"Video ID '{video_id_str}' không hợp lệ.")
    st.stop()

df = load_analysis_data(video_id)
if df is None or df.empty:
    st.stop()

st.title(f"🧠 Dashboard Phân tích Thông minh cho Video ID: {video_id}")

df_normal_speed = df[df['speed_kmh'] < 150].copy()

# --- KPI ---
st.header("Các Chỉ số Hiệu suất Chính (KPIs)")
if not df_normal_speed.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng Lượt xe (Duy nhất)", f"{df_normal_speed['vehicle_id'].nunique():,}")
    col2.metric("Tốc độ TB Toàn kỳ", f"{df_normal_speed['speed_kmh'].mean():.1f} km/h")
    col3.metric("Loại xe Phổ biến", f"{df_normal_speed['class_name'].mode()[0].title()}")
st.markdown("---")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📈 Theo thời gian", "📊 So sánh & Phân bổ", "📝 Kết luận"])

with tab1:
    st.header("Diễn biến Mật độ và Tốc độ")
    df_resample_base = df_normal_speed.set_index('timestamp')
    density_resampled = df_resample_base.resample('5s')['vehicle_id'].nunique().reset_index(name='count')
    fig_density = px.area(density_resampled, x='timestamp', y='count', title='Mật độ Phương tiện (xe/5 giây)')
    st.plotly_chart(fig_density, use_container_width=True)

    speed_resampled = df_resample_base.resample('5s')['speed_kmh'].mean().reset_index()
    fig_speed = px.area(speed_resampled, x='timestamp', y='speed_kmh', title='Tốc độ Trung bình (km/h)')
    st.plotly_chart(fig_speed, use_container_width=True)

with tab2:
    st.header("So sánh Hiệu suất giữa các Loại phương tiện")
    volume_by_type_resampled = df_normal_speed.set_index('timestamp').groupby('class_name').resample('5s')['vehicle_id'].nunique().reset_index(name='count')
    fig_line_compare = px.line(volume_by_type_resampled, x='timestamp', y='count', color='class_name', title="Dòng lưu lượng chi tiết", color_discrete_map=Config.DASHBOARD_COLORS)
    st.plotly_chart(fig_line_compare, use_container_width=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Tỷ lệ các loại xe")
        vehicle_types_by_id = df_normal_speed.drop_duplicates(subset=['vehicle_id'])['class_name']
        vehicle_counts = vehicle_types_by_id.value_counts().reset_index()
        fig_pie = px.pie(vehicle_counts, names='class_name', values='count', title='Tỷ lệ phần trăm', color='class_name', color_discrete_map=Config.DASHBOARD_COLORS, hole=0.4)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_right:
        st.subheader("Phân bổ Tốc độ")
        fig_box = px.box(df_normal_speed, x='class_name', y='speed_kmh', color='class_name', color_discrete_map=Config.DASHBOARD_COLORS)
        st.plotly_chart(fig_box, use_container_width=True)

with tab3:
    st.header("📝 Kết luận Tự động")
    with st.spinner("Đang phân tích..."):
        conclusions = generate_smart_conclusions(df_normal_speed)
        for conclusion in conclusions:
            st.markdown(conclusion)

# --- Tùy chọn tải dữ liệu ---
with st.expander("⚙️ Tải dữ liệu"):
    if st.button("Tạo file CSV"):
        csv = df_normal_speed.to_csv(index=False).encode('utf-8')
        st.download_button(label="Tải CSV", data=csv, file_name=f'analysis_video_{video_id}.csv', mime='text/csv')

    if st.checkbox("Hiển thị dữ liệu thô"):
        st.dataframe(df_normal_speed)
