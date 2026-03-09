"""
Passive View for the YouTube Analytics Dashboard using Streamlit.
Responsible only for rendering the UI based on a provided ViewModel.
"""

import os
import time
import threading
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st

# Project dependencies
from models.dashboard_data import DashboardViewModel
from services.dashboard_provider import DashboardDataProvider
from database.connection import DatabaseManager
from database.repository import YoutubeRepository
from utils.paths import data_path

# Global constants for activity tracking
AUTO_SHUTDOWN_TIMEOUT_SECONDS = 300
LAST_ACTIVITY_TIME = time.time()


class YoutubeDashboard:
    """
    Dashboard reproducing the Power BI layout with an auto-shutdown timer.
    Acts as a passive view consuming a pre-built DashboardViewModel.
    """

    def __init__(self, view_model: DashboardViewModel):
        """
        Initializes the dashboard with the required data object.

        Args:
            view_model: Data Transfer Object containing all pre-fetched DataFrames.
        """
        self.view_model = view_model
        self._setup_auto_shutdown()

    def _setup_auto_shutdown(self) -> None:
        """
        Starts a background thread to kill the process after idleness.
        """
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
        """
        Resets the global inactivity timer on every interaction.
        """
        global LAST_ACTIVITY_TIME
        LAST_ACTIVITY_TIME = time.time()

    def format_value(self, value: float) -> str:
        """
        Formats numbers using 'mil' suffix only for values over 1000.
        """
        if abs(value) >= 1000:
            return f"{value / 1000:.1f} mil"
        return str(int(value))

    def render_header(self) -> None:
        """
        Renders title and top KPI cards in the main header.
        """
        stats_df = self.view_model.channel_stats
        col_title, col_kpi1, col_kpi2 = st.columns([4, 1, 1])

        with col_title:
            st.markdown("# YT Channel Report")

        if not stats_df.empty:
            row = stats_df.iloc[0]
            with col_kpi1:
                st.metric(
                    "Total de views",
                    self.format_value(row['total_views'])
                )
            with col_kpi2:
                top_sum = self.view_model.top_videos['views'].sum()
                st.metric("Top 10", self.format_value(top_sum))

    def render_top_content(self) -> None:
        """
        Renders the donut chart and the vertical metrics column.
        """
        col_donut, col_spacer, col_metrics = st.columns([2.5, 0.2, 1])

        with col_donut:
            st.write("**Top 10 videos por views**")
            v_df = self.view_model.top_videos
            
            if not v_df.empty:
                fig = px.pie(
                    v_df, values="views", names="title",
                    hole=0.5, template="plotly_white"
                )
                fig.update_traces(
                    textposition='outside',
                    textinfo='value+percent',
                    marker=dict(line=dict(color='#FFFFFF', width=2))
                )
                fig.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.1
                    ),
                    height=450,
                    margin=dict(t=30, b=30, l=0, r=150)
                )
                st.plotly_chart(fig, width="stretch")

        with col_metrics:
            self._render_vertical_metrics()

    def _render_vertical_metrics(self) -> None:
        """
        Renders monthly comparison metrics in a single vertical column.
        """
        df = self.view_model.daily_metrics.copy()
        if df.empty:
            st.warning("No daily metrics available.")
            return

        limit_date = date.today() - timedelta(days=2)
        curr_m, curr_y = limit_date.month, limit_date.year
        prev_date = limit_date.replace(day=1) - timedelta(days=1)
        prev_m, prev_y = prev_date.month, prev_date.year

        df['month'] = pd.to_datetime(df['fetch_date']).dt.month
        df['year'] = pd.to_datetime(df['fetch_date']).dt.year

        v_curr = df[(df['month'] == curr_m) & (df['year'] == curr_y)]['views'].sum()
        v_prev = df[(df['month'] == prev_m) & (df['year'] == prev_y)]['views'].sum()

        st.metric(
            f"Views ({datetime(2000, curr_m, 1).strftime('%B')})",
            self.format_value(v_curr)
        )
        st.metric(
            f"Views ({datetime(2000, prev_m, 1).strftime('%B')})",
            self.format_value(v_prev)
        )
        
        growth = (v_curr - v_prev) / v_prev if v_prev > 0 else 0
        st.metric("Crecimiento Mensual %", f"{growth * 100:.2f}%")

        st_df = self.view_model.channel_stats
        if not st_df.empty:
            avg = st_df.iloc[0]['total_views'] / max(st_df.iloc[0]['total_videos'], 1)
            st.metric("Promedio Vistas por Video", self.format_value(avg))

    def render_history_section(self) -> None:
        """
        Renders the historical chart with its integrated date filter.
        """
        col_label, col_filter = st.columns([2, 1])
        daily_df = self.view_model.daily_metrics
        
        with col_label:
            st.write("**Histórico de views por Año, Trimestre y Mes**")
        
        if daily_df.empty:
            return

        with col_filter:
            min_d = daily_df['fetch_date'].min()
            max_allowed = date.today() - timedelta(days=2)
            
            # Fallback if dates are invalid
            if min_d > max_allowed:
                max_allowed = min_d

            date_range = st.select_slider(
                "Rango de fecha",
                options=pd.date_range(min_d, max_allowed).date,
                value=(min_d, max_allowed),
                label_visibility="collapsed"
            )

        filtered_df = daily_df[
            (daily_df['fetch_date'] >= date_range[0]) &
            (daily_df['fetch_date'] <= date_range[1])
        ]

        if not filtered_df.empty:
            fig = px.area(
                filtered_df, x="fetch_date", y="views",
                template="plotly_white", markers=True
            )
            fig.update_traces(
                fillcolor="rgba(41, 182, 246, 0.2)",
                line_color="#29b6f6"
            )
            fig.update_layout(xaxis_title=None, yaxis_title=None, height=350)
            st.plotly_chart(fig, width="stretch")

    def run(self) -> None:
        """
        Main orchestration for the dashboard view.
        """
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

    db_path = data_path("youtube_stats.db")
    db_manager = DatabaseManager(db_path)
    repository = YoutubeRepository(db_manager)
    
    provider = DashboardDataProvider(repository)
    dashboard_data = provider.build_view_model()
    
    app = YoutubeDashboard(dashboard_data)
    app.run()