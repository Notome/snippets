import asyncio
import aiohttp
import pandas as pd
import json
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8000/callback"
PLAYLIST_ID = os.getenv("SPOTIFY_PLAYLIST_ID", "3ak3WgqfQeBcFggDPXsBhp")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

access_token = ""
CACHE_FILE = "existing_ids.json"
SAVE_FILE = "notfoud.xlsx"

async def refresh_access_token(refresh_token):
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as r:
            if r.status == 200:
                token_data = await r.json()
                return token_data["access_token"]
            else:
                raise Exception(f"Failed to refresh access token: {r.status} {await r.text()}")


async def api_call(method, url, params=None, payload=None):
    global access_token
    max_attempts = 5

    for attempt in range(max_attempts):
        headers = {"Authorization": f"Bearer {access_token}"}
        if payload is not None:
            headers["Content-Type"] = "application/json"

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=headers, params=params, json=payload
            ) as resp:
                if resp.status in (200, 201):
                    if "application/json" in resp.headers.get("Content-Type", ""):
                        return await resp.json()
                    return await resp.text()

                elif resp.status == 204:
                    return {}

                elif resp.status == 401:
                    print("Access token expired, refreshing...")
                    access_token = await refresh_access_token(REFRESH_TOKEN)
                    continue  # retry immediately without backoff

                elif resp.status == 429:
                    retry_after = int(resp.headers.get("Retry-After", 1)) + 1
                    print(f"Rate limited, sleeping {retry_after}s...")
                    await asyncio.sleep(retry_after)
                    continue

                else:
                    print(f"API error {resp.status}: {await resp.text()}")
                    return None

        backoff = 2 ** (attempt + 1)
        print(f"Retrying after {backoff}s...")
        await asyncio.sleep(backoff)

    print("Max retries exceeded")
    return None


async def get_track_by_name(track_name, artist):
    url = "https://api.spotify.com/v1/search"
    params = {
        "q": f"track:{track_name} artist:{artist}",
        "type": "track",
        "limit": 1,
    }
    result = await api_call("GET", url, params=params)
    await asyncio.sleep(0.2)
    return result


async def get_playlist_track_ids():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))

    existing = set()
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/items"
    params = {"fields": "items(track(id)),next", "limit": 100}

    data = await api_call("GET", url, params=params)
    while data:
        for item in data.get("items", []):
            track = item.get("track")
            if track and track.get("id"):
                existing.add(track["id"])
        next_url = data.get("next")
        if not next_url:
            break
        data = await api_call("GET", next_url)
        await asyncio.sleep(0.2)

    with open(CACHE_FILE, "w") as f:
        json.dump(list(existing), f)
    return existing


def save_progress(df, existing_ids):
    df.to_excel(SAVE_FILE, index=False)
    with open(CACHE_FILE, "w") as f:
        json.dump(list(existing_ids), f)
    print("Progress saved ✅")


async def main():
    global access_token
    access_token = await refresh_access_token(REFRESH_TOKEN)
    print("Access token refreshed ✅")

    existing_ids = await get_playlist_track_ids()
    print(f"Playlist has {len(existing_ids)} existing tracks")

    df = pd.read_excel(SAVE_FILE)

    df.columns = [c.strip() for c in df.columns]
    if "Track Name" in df.columns and "song_name" not in df.columns:
        df.rename(columns={"Track Name": "song_name"}, inplace=True)
    if "Artist Name(s)" in df.columns and "artist_name1" not in df.columns:
        df.rename(columns={"Artist Name(s)": "artist_name1"}, inplace=True)

    if "track_id" not in df.columns:
        df["track_id"] = pd.NA
    if "added" not in df.columns:
        df["added"] = False

    batch = []
    batch_indices = []
    BATCH_SIZE = 100
    total = len(df)

    for index, row in df.iterrows():
        if row.get("added") is True:
            continue

        track_id = row.get("track_id")

        if pd.isna(track_id) or track_id == "":
            song = str(row.get("song_name", "")).strip()
            artist = str(row.get("artist_name1", "")).strip()

            if not song:
                continue

            print(f"[{index+1}/{total}] Searching: {song} — {artist}")
            result = await get_track_by_name(song, artist)

            if result and result.get("tracks") and result["tracks"]["items"]:
                track = result["tracks"]["items"][0]
                track_id = track["id"]
                df.at[index, "track_id"] = track_id
                print(f"  Found: {track['name']} by {track['artists'][0]['name']}")
            else:
                print(f"  Not found: {song} — {artist}")
                continue

        if pd.notna(track_id) and str(track_id) not in existing_ids:
            batch.append(f"spotify:track:{track_id}")
            batch_indices.append(index)

        if len(batch) == BATCH_SIZE or (index == total - 1 and batch):
            print(f"Adding {len(batch)} tracks to playlist...")
            url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/items"
            res = await api_call("POST", url, payload={"uris": batch})

            if res is not None and (isinstance(res, dict) and "snapshot_id" in res or res == {}):
                print(f"  Added successfully ✅  snapshot_id: {res.get('snapshot_id', 'N/A')}")
                for uri in batch:
                    existing_ids.add(uri.split(":")[-1])
                for i in batch_indices:
                    df.at[i, "added"] = True
                save_progress(df, existing_ids)
            else:
                print("  Failed to add batch ❌")

            await asyncio.sleep(0.3)
            batch = []
            batch_indices = []

    save_progress(df, existing_ids)
    added_count = df["added"].sum()
    print(f"\nDone! {added_count} tracks added to playlist.")


if __name__ == "__main__":
    asyncio.run(main())