import io
import contextlib
from datetime import datetime
import zoneinfo

def get_current_time(timezone: str = "UTC") -> str:
    """
    Get the current time and date in the specified timezone.
    
    Args:
        timezone: The IANA timezone name (e.g., "UTC", "America/New_York"). Defaults to "UTC".
            
    Returns:
        The current date and time formatted as a string, or an error message if the timezone is invalid.
    """
    try:
        tz = zoneinfo.ZoneInfo(timezone)
    except Exception as e:
        return f"Error: Invalid timezone '{timezone}'. {e}"
        
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M:%S %Z%z")

def execute_python(code: str) -> str:
    """
    Executes the provided Python code and captures standard output.
    
    Args:
        code: The Python code string to execute.
        
    Returns:
        The captured standard output (printed output) or the string representation of any Exception raised.
    """
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        try:
            exec(code, {})
        except Exception as e:
            return str(e)
    return f.getvalue()
