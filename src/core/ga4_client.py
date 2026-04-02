import os
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

_PROPERTY_ID = os.getenv("GOOGLE_ANALYTICS_PROPERTY_ID", "")
_SA_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Dimension, Metric, FilterExpression,
        Filter,
    )
    from google.oauth2 import service_account
    _GA4_AVAILABLE = True
except ImportError:
    _GA4_AVAILABLE = False
    logger.warning("google-analytics-data not installed — GA4 disabled")


def _date_range(days: int = 30):
    end = date.today()
    start = end - timedelta(days=days)
    return DateRange(start_date=str(start), end_date=str(end))


class GA4Client:
    def __init__(self):
        self.connected = False
        self._client = None
        self._property = f"properties/{_PROPERTY_ID}" if _PROPERTY_ID else None

        if not _GA4_AVAILABLE or not _PROPERTY_ID or not _SA_JSON:
            return

        try:
            creds = service_account.Credentials.from_service_account_file(
                _SA_JSON,
                scopes=["https://www.googleapis.com/auth/analytics.readonly"],
            )
            self._client = BetaAnalyticsDataClient(credentials=creds)
            self.connected = True
        except Exception as e:
            logger.warning("GA4 init failed: %s", e)

    def get_status(self) -> dict:
        return {"connected": self.connected}

    def get_seo_metrics(self) -> dict | None:
        """Return organic search metrics for last 30 days."""
        if not self.connected:
            return None
        try:
            # Daily organic sessions trend
            trend_req = RunReportRequest(
                property=self._property,
                date_ranges=[_date_range(30)],
                dimensions=[Dimension(name="date")],
                metrics=[Metric(name="sessions"), Metric(name="newUsers")],
                dimension_filter=FilterExpression(
                    filter=Filter(
                        field_name="sessionDefaultChannelGrouping",
                        string_filter=Filter.StringFilter(value="Organic Search"),
                    )
                ),
                order_bys=[{"dimension": {"dimension_name": "date"}}],
            )
            trend_resp = self._client.run_report(trend_req)

            # Top landing pages
            pages_req = RunReportRequest(
                property=self._property,
                date_ranges=[_date_range(30)],
                dimensions=[Dimension(name="landingPage")],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="engagementRate"),
                    Metric(name="bounceRate"),
                ],
                dimension_filter=FilterExpression(
                    filter=Filter(
                        field_name="sessionDefaultChannelGrouping",
                        string_filter=Filter.StringFilter(value="Organic Search"),
                    )
                ),
                limit=10,
                order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}],
            )
            pages_resp = self._client.run_report(pages_req)

            # Summary metrics
            summary_req = RunReportRequest(
                property=self._property,
                date_ranges=[_date_range(30)],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="newUsers"),
                    Metric(name="engagementRate"),
                    Metric(name="bounceRate"),
                ],
                dimension_filter=FilterExpression(
                    filter=Filter(
                        field_name="sessionDefaultChannelGrouping",
                        string_filter=Filter.StringFilter(value="Organic Search"),
                    )
                ),
            )
            summary_resp = self._client.run_report(summary_req)

            summary = {}
            if summary_resp.rows:
                vals = [v.value for v in summary_resp.rows[0].metric_values]
                summary = {
                    "sessions": int(vals[0]),
                    "new_users": int(vals[1]),
                    "engagement_rate": round(float(vals[2]) * 100, 1),
                    "bounce_rate": round(float(vals[3]) * 100, 1),
                }

            trend = [
                {
                    "date": row.dimension_values[0].value,
                    "sessions": int(row.metric_values[0].value),
                    "new_users": int(row.metric_values[1].value),
                }
                for row in trend_resp.rows
            ]

            pages = [
                {
                    "page": row.dimension_values[0].value,
                    "sessions": int(row.metric_values[0].value),
                    "engagement_rate": round(float(row.metric_values[1].value) * 100, 1),
                    "bounce_rate": round(float(row.metric_values[2].value) * 100, 1),
                }
                for row in pages_resp.rows
            ]

            return {"summary": summary, "trend": trend, "top_pages": pages}
        except Exception as e:
            logger.warning("GA4 SEO metrics failed: %s", e)
            return None

    def get_sem_metrics(self) -> dict | None:
        """Return paid search metrics for last 30 days."""
        if not self.connected:
            return None
        try:
            summary_req = RunReportRequest(
                property=self._property,
                date_ranges=[_date_range(30)],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="conversions"),
                    Metric(name="engagementRate"),
                ],
                dimension_filter=FilterExpression(
                    filter=Filter(
                        field_name="sessionDefaultChannelGrouping",
                        string_filter=Filter.StringFilter(value="Paid Search"),
                    )
                ),
            )
            summary_resp = self._client.run_report(summary_req)

            trend_req = RunReportRequest(
                property=self._property,
                date_ranges=[_date_range(30)],
                dimensions=[Dimension(name="date")],
                metrics=[Metric(name="sessions"), Metric(name="conversions")],
                dimension_filter=FilterExpression(
                    filter=Filter(
                        field_name="sessionDefaultChannelGrouping",
                        string_filter=Filter.StringFilter(value="Paid Search"),
                    )
                ),
                order_bys=[{"dimension": {"dimension_name": "date"}}],
            )
            trend_resp = self._client.run_report(trend_req)

            summary = {}
            if summary_resp.rows:
                vals = [v.value for v in summary_resp.rows[0].metric_values]
                summary = {
                    "sessions": int(vals[0]),
                    "conversions": int(float(vals[1])),
                    "engagement_rate": round(float(vals[2]) * 100, 1),
                }

            trend = [
                {
                    "date": row.dimension_values[0].value,
                    "sessions": int(row.metric_values[0].value),
                    "conversions": int(float(row.metric_values[1].value)),
                }
                for row in trend_resp.rows
            ]

            return {"summary": summary, "trend": trend}
        except Exception as e:
            logger.warning("GA4 SEM metrics failed: %s", e)
            return None
