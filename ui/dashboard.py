import os
import sys
import time
import sqlite3
import threading
from pathlib import Path
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.paths import data_path

st.set_page_config(
    page_title="YT Channel Report",
    page_icon="📊",
    layout="wide"
)

# Global variable to track activity across threads and reruns
LAST_ACTIVITY_TIME = time.time()


class YoutubeDashboard:
    """
    Dashboard reproducing the Power BI layout with an auto-shutdown timer.
    """

    def __init__(self, db_path: str):
        """
        Initializes the dashboard and starts the inactivity watcher.
        """
        self.db_path = db_path
        self._setup_auto_shutdown()

    def _setup_auto_shutdown(self):
        """
        Starts a background thread to kill the process after 10m of idleness.
        """
        if "watcher_started" not in st.session_state:
            def watcher():
                timeout = 300
                while True:
                    time.sleep(30)
                    elapsed = time.time() - LAST_ACTIVITY_TIME
                    if elapsed > timeout:
                        os._exit(0)

            thread = threading.Thread(target=watcher, daemon=True)
            thread.start()
            st.session_state.watcher_started = True

    def _update_activity(self):
        """
        Resets the global inactivity timer on every interaction.
        """
        global LAST_ACTIVITY_TIME
        LAST_ACTIVITY_TIME = time.time()

    def _get_connection(self):
        """
        Internal helper for database connection.
        """
        return sqlite3.connect(self.db_path)

    def load_channel_stats(self) -> pd.DataFrame:
        """
        Fetches the latest channel overview metrics.
        """
        query = "SELECT * FROM channel_stats LIMIT 1"
        with self._get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def load_daily_metrics(self) -> pd.DataFrame:
        """
        Fetches daily views and handles date parsing.
        """
        query = "SELECT * FROM daily_metrics ORDER BY fetch_date"
        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn)
            df['fetch_date'] = pd.to_datetime(df['fetch_date']).dt.date
            return df

    def load_video_metrics(self) -> pd.DataFrame:
        """
        Fetches high-performing video data.
        """
        query = "SELECT * FROM video_metrics ORDER BY views DESC LIMIT 10"
        with self._get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def format_value(self, value: float) -> str:
        """
        Formats numbers using 'mil' suffix only for values over 1000.
        """
        if abs(value) >= 1000:
            return f"{value / 1000:.1f} mil"
        return str(int(value))

    def render_header(self, stats: pd.DataFrame):
        """
        Renders title and top KPI cards in the main header.
        """
        col_title, col_kpi1, col_kpi2 = st.columns([4, 1, 1])

        with col_title:
            st.markdown("# YT Channel Report")

        if not stats.empty:
            row = stats.iloc[0]
            with col_kpi1:
                st.metric(
                    "Total de views",
                    self.format_value(row['total_views'])
                )
            with col_kpi2:
                top_sum = self.load_video_metrics()['views'].sum()
                st.metric("Top 10", self.format_value(top_sum))

    def render_top_content(self, daily_df: pd.DataFrame):
        """
        Renders the donut chart and the vertical metrics column.
        """
        col_donut, col_spacer, col_metrics = st.columns([2.5, 0.2, 1])

        with col_donut:
            st.write("**Top 10 videos por views**")
            v_df = self.load_video_metrics()
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
            self._render_vertical_metrics(daily_df)

    def _render_vertical_metrics(self, df: pd.DataFrame):
        """
        Renders monthly comparison metrics in a single vertical column.
        """
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
        st.metric("Crecimiento Mensual %", f"{growth:.2f}")

        st_df = self.load_channel_stats()
        if not st_df.empty:
            avg = st_df.iloc[0]['total_views'] / max(st_df.iloc[0]['total_videos'], 1)
            st.metric("Promedio Vistas por Video", self.format_value(avg))

    def render_history_section(self, daily_df: pd.DataFrame):
        """
        Renders the historical chart with its integrated date filter.
        """
        col_label, col_filter = st.columns([2, 1])
        
        with col_label:
            st.write("**Histórico de views por Año, Trimestre y Mes**")
        
        with col_filter:
            min_d = daily_df['fetch_date'].min() if not daily_df.empty else date.today()
            max_allowed = date.today() - timedelta(days=2)
            
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

    def run(self):
        """
        Main orchestration for the dashboard view.
        """
        self._update_activity()
        daily_df = self.load_daily_metrics()
        stats = self.load_channel_stats()
        
        self.render_header(stats)
        st.divider()
        self.render_top_content(daily_df)
        st.divider()
        self.render_history_section(daily_df)


if __name__ == "__main__":
    app = YoutubeDashboard(data_path("youtube_stats.db"))
    app.run()