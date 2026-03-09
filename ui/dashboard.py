"""
Passive View for the YouTube Analytics Dashboard using Streamlit.
Responsible only for rendering the UI based on a provided ViewModel.
"""

import os
import time
import threading
from datetime import date, timedelta
import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure
import streamlit as st

from models.dashboard_data import DashboardViewModel
from services.dashboard_provider import DashboardDataProvider
from database.connection import DatabaseManager
from database.repository import YoutubeRepository
from utils.paths import data_path
from config import AUTO_SHUTDOWN_TIMEOUT_SECONDS, DB_NAME

LAST_ACTIVITY_TIME = time.time()


class YoutubeDashboard:
    """
    Dashboard reproducing the Power BI layout with an auto-shutdown timer.
    Acts as a passive view consuming a pre-built DashboardViewModel.
    """

    def __init__(self, view_model: DashboardViewModel):
        """Initializes the dashboard with the pre-calculated view model."""
        self.view_model = view_model
        self._setup_auto_shutdown()

    def _setup_auto_shutdown(self) -> None:
        """Starts a background thread to kill the process after idleness."""
        if "watcher_started" not in st.session_state:
            def watcher() -> None:
                while True:
                    time.sleep(30)
                    elapsed = time.time() - LAST_ACTIVITY_TIME
                    if elapsed > AUTO_SHUTDOWN_TIMEOUT_SECONDS:
                        os._exit(0)

            thread = threading.Thread(target=watcher, daemon=True)
            thread.start()
            st.session_state.watcher_started = True

    def _update_activity(self) -> None:
        """Resets the global inactivity timer on every interaction."""
        global LAST_ACTIVITY_TIME
        LAST_ACTIVITY_TIME = time.time()

    def _format_value(self, value: float) -> str:
        """Formats numbers using 'mil' suffix only for values over 1000."""
        if abs(value) >= 1000:
            return f"{value / 1000:.1f} mil"
        return str(int(value))

    # --- UI RENDERING METHODS (High Abstraction) ---

    def render_header(self) -> None:
        """Renders title and top KPI cards."""
        col_title, col_kpi1, col_kpi2 = st.columns([4, 1, 1])

        with col_title:
            st.markdown("# YT Channel Report")

        stats_df = self.view_model.channel_stats
        if not stats_df.empty:
            with col_kpi1:
                total_views = stats_df.iloc[0]['total_views']
                st.metric("Total de views", self._format_value(total_views))
            with col_kpi2:
                top_sum = self.view_model.top_videos['views'].sum()
                st.metric("Top 10", self._format_value(top_sum))

    def render_top_content(self) -> None:
        """Renders the donut chart and the vertical metrics column."""
        col_donut, col_spacer, col_metrics = st.columns([2.5, 0.2, 1])

        with col_donut:
            st.write("**Top 10 videos por views**")
            v_df = self.view_model.top_videos
            if not v_df.empty:
                chart = self._build_donut_chart(v_df)
                st.plotly_chart(chart, width="stretch")

        with col_metrics:
            self._render_vertical_metrics()

    def _render_vertical_metrics(self) -> None:
        """Renders the monthly comparison KPIs using pre-calculated data."""
        if self.view_model.daily_metrics.empty:
            st.warning("No daily metrics available.")
            return

        curr_date = self.view_model.current_month_date
        prev_date = self.view_model.previous_month_date

        st.metric(
            f"Views ({curr_date.strftime('%B')})",
            self._format_value(self.view_model.current_month_views)
        )
        st.metric(
            f"Views ({prev_date.strftime('%B')})",
            self._format_value(self.view_model.previous_month_views)
        )
        st.metric(
            "Crecimiento Mensual %", 
            f"{self.view_model.monthly_growth_percentage * 100:.2f}%"
        )
        st.metric(
            "Promedio Vistas por Video", 
            self._format_value(self.view_model.average_views_per_video)
        )

    def render_history_section(self) -> None:
        """Renders the historical chart with a date range slider."""
        col_label, col_filter = st.columns([2, 1])
        daily_df = self.view_model.daily_metrics
        
        with col_label:
            st.write("**Histórico de views por Año, Trimestre y Mes**")
        
        if daily_df.empty:
            return

        with col_filter:
            min_date = daily_df['fetch_date'].min()
            max_allowed = max(min_date, date.today() - timedelta(days=2))
            
            date_range = st.select_slider(
                "Rango de fecha",
                options=pd.date_range(min_date, max_allowed).date,
                value=(min_date, max_allowed),
                label_visibility="collapsed"
            )

        filtered_df = daily_df[
            (daily_df['fetch_date'] >= date_range[0]) &
            (daily_df['fetch_date'] <= date_range[1])
        ]

        if not filtered_df.empty:
            chart = self._build_area_chart(filtered_df)
            st.plotly_chart(chart, width="stretch")

    # --- CHART BUILDERS & STYLING (Low Abstraction) ---

    def _build_donut_chart(self, df: pd.DataFrame) -> Figure:
        """Constructs and styles the Plotly donut chart."""
        fig = px.pie(
            df, values="views", names="title",
            hole=0.5, template="plotly_white"
        )
        fig.update_traces(
            textposition='outside',
            textinfo='value+percent',
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1),
            height=450,
            margin=dict(t=30, b=30, l=0, r=150)
        )
        return fig

    def _build_area_chart(self, df: pd.DataFrame) -> Figure:
        """Constructs and styles the Plotly area chart."""
        fig = px.area(
            df, x="fetch_date", y="views",
            template="plotly_white", markers=True
        )
        fig.update_traces(
            fillcolor="rgba(41, 182, 246, 0.2)",
            line_color="#29b6f6"
        )
        fig.update_layout(xaxis_title=None, yaxis_title=None, height=350)
        return fig

    def run(self) -> None:
        """Main orchestration for the dashboard view."""
        self._update_activity()
        
        self.render_header()
        st.divider()
        self.render_top_content()
        st.divider()
        self.render_history_section()


if __name__ == "__main__":
    st.set_page_config(
        page_title="YT Channel Report",
        page_icon="📊",
        layout="wide"
    )

    db_path = data_path(DB_NAME)
    db_manager = DatabaseManager(db_path)
    repository = YoutubeRepository(db_manager)
    
    provider = DashboardDataProvider(repository)
    dashboard_data = provider.build_view_model()
    
    app = YoutubeDashboard(dashboard_data)
    app.run()