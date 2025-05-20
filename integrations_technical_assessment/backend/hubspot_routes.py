from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
import os
import httpx
import urllib.parse
import json

router = APIRouter()

# Store credentials in memory temporarily (replace with DB in prod)
user_credential_store = {}

# Set your credentials
HUBSPOT_CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID", "your_client_id")
HUBSPOT_CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET", "your_client_secret")
HUBSPOT_REDIRECT_URI = os.getenv(
    "HUBSPOT_REDIRECT_URI", "http://localhost:8000/integrations/hubspot/callback"
)


# Step 1: Redirect user to HubSpot's OAuth page
@router.post("/integrations/hubspot/authorize")
async def authorize(user_id: str = Form(...), org_id: str = Form(...)):
    scopes = "crm.objects.contacts.read crm.objects.deals.read"
    url = (
        f"https://app.hubspot.com/oauth/authorize?"
        f"client_id={HUBSPOT_CLIENT_ID}"
        f"&scope={urllib.parse.quote(scopes)}"
        f"&redirect_uri={urllib.parse.quote(HUBSPOT_REDIRECT_URI)}"
        f"&state={user_id}:{org_id}"
    )
    return JSONResponse(content=url)


# Step 2: OAuth callback
@router.get("/integrations/hubspot/callback")
async def oauth_callback(code: str, state: str):
    user_id, org_id = state.split(":")

    token_url = "https://api.hubapi.com/oauth/v1/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "client_id": HUBSPOT_CLIENT_ID,
        "client_secret": HUBSPOT_CLIENT_SECRET,
        "redirect_uri": HUBSPOT_REDIRECT_URI,
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(token_url, data=data, headers=headers)

    if token_resp.status_code != 200:
        return JSONResponse(status_code=400, content={"message": token_resp.text})

    token_data = token_resp.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return JSONResponse(status_code=500, content={"message": "Token not received"})

    # Store in memory
    user_credential_store[(user_id, org_id)] = {"access_token": access_token}

    return RedirectResponse(
        "http://localhost:3000"
    )  # ✅ Redirect back to your frontend


# Step 3: Frontend polls for credentials
@router.post("/integrations/hubspot/credentials")
async def get_credentials(user_id: str = Form(...), org_id: str = Form(...)):
    creds = user_credential_store.get((user_id, org_id))
    if not creds:
        return JSONResponse(
            status_code=404, content={"message": "No credentials found"}
        )
    return creds
