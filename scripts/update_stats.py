#!/usr/bin/env python3
"""Refresh README badges from public, owned, non-fork GitHub repositories."""

import argparse
import json
import os
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


START = "<!-- STATS-START -->"
END = "<!-- STATS-END -->"


def github_get(path, token):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-profile-stats",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"https://api.github.com{path}", headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def count(value):
    if type(value) is not int or value < 0:
        raise ValueError("GitHub returned an invalid statistic")
    return value


def fetch_stats(owner, token=""):
    profile = github_get(f"/users/{owner}", token)
    followers = count(profile["followers"])
    repositories = {}
    page = 1
    while True:
        batch = github_get(
            f"/users/{owner}/repos?type=owner&sort=full_name&direction=asc&per_page=100&page={page}",
            token,
        )
        if not isinstance(batch, list):
            raise ValueError("GitHub returned an invalid repository list")
        for repo in batch:
            # Explicit filtering also prevents a local token's private data from
            # becoming part of the public badges.
            if (
                repo["private"] is False
                and repo["fork"] is False
                and repo["owner"]["login"].casefold() == owner.casefold()
            ):
                repositories[repo["id"]] = count(repo["stargazers_count"])
        if len(batch) < 100:
            break
        page += 1
    return sum(repositories.values()), followers, len(repositories)


def compact(number):
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}".removesuffix(".0") + "m"
    if number >= 1_000:
        return f"{number / 1_000:.1f}".removesuffix(".0") + "k"
    return str(number)


def stats_block(owner, stars, followers, repos):
    profile = f"https://github.com/{owner}"
    badges = [
        ("Total Stars", compact(stars), "FFD93D", profile),
        ("Followers", compact(followers), "4C8BF5", profile + "?tab=followers"),
        ("Public Repos", str(repos), "2EA44F", profile + "?tab=repositories"),
    ]
    lines = [START]
    for label, value, color, target in badges:
        image = (
            f"https://img.shields.io/badge/{quote(label, safe='')}-{value}-{color}"
            "?style=flat&logo=github&logoColor=white"
        )
        lines.append(f"[![{label}]({image})]({target})")
    lines.append(END)
    return "\n".join(lines)


def replace_stats(content, replacement):
    if content.count(START) != 1 or content.count(END) != 1:
        raise ValueError("README must contain exactly one STATS-START/END pair")
    start = content.index(START)
    end = content.index(END)
    if end < start:
        raise ValueError("README statistics markers are reversed")
    return content[:start] + replacement + content[end + len(END):]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--owner",
        default=os.environ.get("PROFILE_OWNER")
        or os.environ.get("GITHUB_REPOSITORY_OWNER")
        or "belalee-ai",
    )
    parser.add_argument("--readme", type=Path, default=Path("README.md"))
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", args.owner):
        parser.error("owner must be a GitHub username")
    content = args.readme.read_text(encoding="utf-8")
    # Check the markers before requesting data. Failures leave README untouched.
    replace_stats(content, START + "\n" + END)
    stats = fetch_stats(args.owner, os.environ.get("GITHUB_TOKEN", ""))
    updated = replace_stats(content, stats_block(args.owner, *stats))
    if updated == content:
        print("Profile statistics are unchanged.")
        return
    args.readme.write_text(updated, encoding="utf-8")
    print(f"Updated public stats: stars={stats[0]}, followers={stats[1]}, repos={stats[2]}")


if __name__ == "__main__":
    try:
        main()
    except (HTTPError, URLError, OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"Cannot update profile statistics: {error}") from None
