# hubspot.py

import json
import secrets
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
import base64
import requests
from .integration_item import IntegrationItem

from redis_client import add_key_value_redis, get_value_redis, delete_key_redis

# TODO: Replace with actual HubSpot client credentials
CLIENT_ID = "5c9e3bc5-3ad5-488b-ac7e-90da1ec80d58"
CLIENT_SECRET = "441b7692-bfd1-4193-aa22-189c0738720d"
encoded_client_id_secret = base64.b64encode(
    f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
).decode()

REDIRECT_URI = "http://localhost:8000/integrations/hubspot/oauth2callback"
AUTHORIZATION_URL = (
    f"https://app.hubspot.com/oauth/authorize"
    f"?client_id={CLIENT_ID}"
    f"&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fintegrations%2Fhubspot%2Foauth2callback"  # Ensure this matches your redirect URI
    # This string includes all the scopes you listed, URL-encoded
    f"&scope=crm.schemas.companies.write%20crm.schemas.contacts.write%20oauth%20crm.objects.contacts.write%20crm.objects.companies.write%20crm.objects.companies.read%20crm.schemas.contacts.read%20crm.objects.contacts.read%20crm.schemas.companies.read"
)


async def authorize_hubspot(user_id, org_id):
    state_data = {
        "state": secrets.token_urlsafe(32),
        "user_id": user_id,
        "org_id": org_id,
    }
    encoded_state = json.dumps(state_data)
    await add_key_value_redis(
        f"hubspot_state:{org_id}:{user_id}", encoded_state, expire=600
    )

    return f"{AUTHORIZATION_URL}&state={encoded_state}"


async def oauth2callback_hubspot(request: Request):
    if request.query_params.get("error"):
        raise HTTPException(status_code=400, detail=request.query_params.get("error"))
    code = request.query_params.get("code")
    encoded_state = request.query_params.get("state")
    state_data = json.loads(encoded_state)

    original_state = state_data.get("state")
    user_id = state_data.get("user_id")
    org_id = state_data.get("org_id")

    saved_state = await get_value_redis(f"hubspot_state:{org_id}:{user_id}")

    if not saved_state or original_state != json.loads(saved_state).get("state"):
        raise HTTPException(status_code=400, detail="State does not match.")

    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                "https://api.hubapi.com/oauth/v1/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            ),
            delete_key_redis(f"hubspot_state:{org_id}:{user_id}"),
        )

    await add_key_value_redis(
        f"hubspot_credentials:{org_id}:{user_id}",
        json.dumps(response.json()),
        expire=600,
    )

    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)


async def get_hubspot_credentials(user_id, org_id):
    credentials = await get_value_redis(f"hubspot_credentials:{org_id}:{user_id}")
    if not credentials:
        raise HTTPException(status_code=400, detail="No credentials found.")
    credentials = json.loads(credentials)
    await delete_key_redis(f"hubspot_credentials:{org_id}:{user_id}")

    return credentials


async def get_items_hubspot(credentials):
    credentials = json.loads(credentials)
    access_token = credentials.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=400, detail="No access token found in credentials."
        )

    # Example: Fetch contacts from HubSpot
    response = requests.get(
        "https://api.hubapi.com/crm/v3/objects/contacts",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to fetch HubSpot items."
        )

    items = response.json().get("results", [])
    integration_items = []
    for item in items:
        integration_items.append(
            IntegrationItem(
                id=item.get("id"),
                type="Contact",
                name=item.get("properties", {}).get("firstname", "")
                + " "
                + item.get("properties", {}).get("lastname", ""),
                creation_time=item.get("createdAt"),
                last_modified_time=item.get("updatedAt"),
            )
        )

    return integration_items


async def create_integration_item_metadata_object(response_json):
    # TODO
    pass
