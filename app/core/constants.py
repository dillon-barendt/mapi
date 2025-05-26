# File: app/core/constants.py

APP_DESCRIPTION = """### What is this API?  
A toolkit for **parsing**, **generating**, and **diffing** row‑progression codes  
used in ticket‑marketplace seat maps.

* 🔍 Parse single codes or entire venues  
* 🆚 Diff partner updates before they break prod  
* 🛠️ Generate DSL strings from raw rows
"""
APP_DEFAULT_CORS_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

########################################################################################################################

VENUE_TAG_DESCRIPTION = (
    "Endpoints that build, diff, or compress entire venues.  \n"
    "Think of these as bulk counterparts to the `/parse` endpoint."
)

