from typing import Dict, Any

def get_macro_data(country: str = "United States") -> Dict[str, Any]:
    """Fetch macro economic data using tedata (TradingEconomics scraper)."""
    result = {}
    indicators = {
        "gdp_growth": "GDP Growth Rate",
        "cpi": "Inflation Rate",
        "unemployment": "Unemployment Rate",
        "interest_rate": "Interest Rate",
        "nfp": "Non Farm Payrolls",
        "us10y": "Government Bond 10Y",
    }
    try:
        import tedata as te
        for key, indicator_name in indicators.items():
            try:
                data = te.get_indicator(country, indicator_name)
                if data is not None:
                    # tedata returns various structures - handle flexibly
                    if hasattr(data, 'iloc'):
                        # DataFrame
                        latest = data.iloc[-1]
                        result[key] = {
                            "indicator": indicator_name,
                            "value": float(latest.get("Value", latest.get("value", 0)) if hasattr(latest, 'get') else latest),
                            "unit": str(data.columns.get("unit", "%") if hasattr(data, 'columns') else "%"),
                        }
                    elif isinstance(data, dict):
                        result[key] = {"indicator": indicator_name, **data}
                    else:
                        result[key] = {"indicator": indicator_name, "value": str(data)}
            except Exception as e:
                result[key] = {"indicator": indicator_name, "error": str(e)}
    except ImportError:
        result["error"] = "tedata not installed"
    except Exception as e:
        result["error"] = str(e)
    return result
