from datetime import datetime
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import EconomicEvent
from src.lib.logger import get_logger

logger = get_logger(__name__)

async def fetch_calendar_events(db: AsyncSession, start_date=None, end_date=None):
    """Fetch events using ecocal and persist to DB with exact mapping."""
    try:
        from ecocal import Calendar
        logger.info("Starting refined ecocal ingestion: %s to %s", start_date, end_date)
        
        # We use 1 thread to be extremely careful with fxstreet rate limits
        ec = Calendar(
            startHorizon=start_date, 
            endHorizon=end_date, 
            withDetails=True, 
            nbThreads=1, 
            preBuildCalendar=True
        )
        
        # Use detailedCalendar if available, otherwise fallback to simple calendar
        df = None
        if hasattr(ec, 'detailedCalendar') and ec.detailedCalendar is not None and len(ec.detailedCalendar) > 0:
            df = ec.detailedCalendar
            logger.info("Using detailedCalendar with %d rows", len(df))
        elif hasattr(ec, 'calendar') and ec.calendar is not None and len(ec.calendar) > 0:
            df = ec.calendar
            logger.info("Using basic calendar with %d rows (details not available)", len(df))
        
        if df is None or len(df) == 0:
            logger.warning("No data found even after successful ecocal execution")
            return []

        count = 0
        for _, row in df.iterrows():
            try:
                # Exact mapping from ecocal Detailed DataFrame
                title = row.get('Name') or row.get('name') or row.get('Title') or 'Unknown'
                country = row.get('Currency') or row.get('countryCode') or 'GLOBAL'
                importance = str(row.get('Impact') or row.get('Importance') or 'low').lower()
                
                # Time parsing
                time_val = row.get('dateUtc') or row.get('Date') or row.get('Start')
                if pd.notnull(time_val):
                    if isinstance(time_val, str):
                        try:
                            # Handle formats like "03/07/2026 08:00:00" or ISO
                            if '/' in time_val:
                                time_val = datetime.strptime(time_val, "%m/%d/%Y %H:%M:%S")
                            else:
                                time_val = datetime.fromisoformat(time_val.replace('Z', '+00:00'))
                        except:
                            time_val = datetime.utcnow()
                else:
                    time_val = datetime.utcnow()

                new_event = EconomicEvent(
                    provider="ecocal_detailed",
                    title=str(title),
                    country=str(country),
                    importance=importance,
                    time_utc=time_val,
                    actual_value=float(row.get('actual')) if pd.notnull(row.get('actual')) and str(row.get('actual')).replace('.','',1).isdigit() else None,
                    forecast_value=float(row.get('consensus')) if pd.notnull(row.get('consensus')) and str(row.get('consensus')).replace('.','',1).isdigit() else None,
                    previous_value=float(row.get('previous')) if pd.notnull(row.get('previous')) and str(row.get('previous')).replace('.','',1).isdigit() else None,
                    unit=str(row.get('unit') or '')
                )
                db.add(new_event)
                count += 1
            except Exception as ex:
                logger.debug("Row mapping error: %s", ex)
        
        await db.commit()
        logger.info("Final persistence: %d rows saved", count)
        return [{"title": "Ingested", "count": count}]
        
    except Exception as e:
        logger.error("Critical ecocal worker error: %s", e)
        return []
