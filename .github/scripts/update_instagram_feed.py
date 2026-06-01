#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROFILE = "dra.anacarolinaaugusto"
PROFILE_URL = "https://www.instagram.com/dra.anacarolinaaugusto?igsh=Z2U5OTNjMW5iOTMz"
API_URL = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={PROFILE}"
OUTPUT = Path("data/instagram-feed.json")


def fetch_profile():
    result = subprocess.run(
        [
            "curl",
            "-L",
            "--silent",
            API_URL,
            "-H",
            "User-Agent: Mozilla/5.0",
            "-H",
            "X-IG-App-ID: 936619743392459",
            "-H",
            "Accept: application/json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def build_feed(payload):
    user = payload["data"]["user"]
    edges = user["edge_owner_to_timeline_media"]["edges"][:4]
    posts = []

    for index, edge in enumerate(edges, start=1):
        node = edge["node"]
        shortcode = node["shortcode"]
        posts.append(
            {
                "shortcode": shortcode,
                "embed_url": f"https://www.instagram.com/p/{shortcode}/embed",
                "title": f"Post do Instagram da Dra. Ana Carolina Augusto {index}",
            }
        )

    return {
        "username": user["username"],
        "profile_url": PROFILE_URL,
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "posts": posts,
    }


def main():
    try:
        payload = fetch_profile()
    except (subprocess.CalledProcessError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
        print(f"Failed to update Instagram feed: {exc}", file=sys.stderr)
        return 1

    feed = build_feed(payload)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    if OUTPUT.exists():
        try:
            current = json.loads(OUTPUT.read_text())
        except json.JSONDecodeError:
            current = None
        if current and current.get("posts") == feed["posts"]:
            print("Instagram feed posts unchanged.")
            return 0

    OUTPUT.write_text(json.dumps(feed, ensure_ascii=True, indent=2) + "\n")
    print(f"Updated {OUTPUT} with {len(feed['posts'])} posts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
