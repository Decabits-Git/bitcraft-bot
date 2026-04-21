import asyncio
import requests
import threading
import time

_rate_lock = threading.Lock()
_SECONDS_PER_REQUEST = 0.24
_last_request = 0.0

'''
Function - _throttle
Inputs   - N/A
Outputs  - N/A
Purpose  - Prevent bot from hitting BitJita rate limit (currently 250/min)
'''
async def _throttle():
    global _last_request

    with _rate_lock:
        current_time = time.monotonic()
        time_to_sleep = _SECONDS_PER_REQUEST - (current_time - _last_request)
        _last_request = max(_last_request + _SECONDS_PER_REQUEST, time.monotonic())

    if time_to_sleep > 0:
        await asyncio.sleep(time_to_sleep)

'''
Function - get
Inputs   -            [str]  url     : the URL to send the HTTP request to
           (Optional) [dict] params  : optional parameters to append to the URL
           (Optional) [dict] headers : optional HTTP headers to submit with the request
Outputs  - [dict] response : the JSON response from the BitJita endpoint
Purpose  - Send HTTP GET request to the desired URL and validate the response
'''
async def get(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
) -> dict | None:
    
    await _throttle()

    try:
        response = requests.get(
            url=url,
            params=params,
            headers=headers,
            timeout=30,
        )

        if response.status_code == 200:
            return response.json()
    except requests.RequestException as e:
        print("HTTP Error:", e)

    return None
