#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import os
import urllib.parse
import httpx
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "GitHub"
__module__ = "𝐆ɪᴛʜᴜʙ🐙"

__help__ = """
*Comprehensive GitHub Suite Module🐙*
(Ported from AshokShau/GithubBot)

*User & Organization:*  
❂ `/git [username]` (or `/user`) — View complete profile and stats of a GitHub user  
❂ `/org [org_name]` — View profile, description, and members of a GitHub organization  

*Repository Inspection:*  
❂ `/repo [owner/repo]` — Detailed overview of a repository (stars, forks, watchers, license)  
❂ `/commits [owner/repo]` — View recent commits with author, hash, and messages  
❂ `/releases [owner/repo]` — View latest releases, assets, tags, and changelogs  
❂ `/issues [owner/repo]` — List open issues of a repository  
❂ `/prs [owner/repo]` (or `/pulls`) — List open pull requests of a repository  
❂ `/branches [owner/repo]` — List active branches of a repository  
❂ `/contributors [owner/repo]` — Top contributors ranked by contribution count  

*Search:*  
❂ `/ghsearch [keyword]` — Search GitHub repositories with stars, forks, and links  
"""

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

def get_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


# 1. User Profile
@bot.on_message(filters.command(["git", "github", "user"]) & ~filters.forwarded)
async def github_user(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/git [username]` (e.g. `/git AshokShau`)"))

    username = m.command[1].strip().lstrip("@")
    status_msg = await m.reply_text(font("🔍 Fetching GitHub user data..."))

    url = f"https://api.github.com/users/{username}"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                name = data.get("name") or username
                bio = data.get("bio") or "No bio available."
                public_repos = data.get("public_repos", 0)
                followers = data.get("followers", 0)
                following = data.get("following", 0)
                company = data.get("company") or "None"
                location = data.get("location") or "Unknown"
                blog = data.get("blog") or "None"
                created_at = (data.get("created_at") or "").split("T")[0]
                avatar_url = data.get("avatar_url")
                profile_url = data.get("html_url")

                caption = (
                    f"🐙 **GitHub User:** [{name}]({profile_url})\n\n"
                    f"💬 **Bio:** `{bio}`\n"
                    f"📦 **Public Repos:** `{public_repos}`\n"
                    f"👥 **Followers:** `{followers}` | **Following:** `{following}`\n"
                    f"🏢 **Company:** `{company}`\n"
                    f"📍 **Location:** `{location}`\n"
                    f"🌐 **Website:** {blog}\n"
                    f"📅 **Joined:** `{created_at}`"
                )

                if avatar_url:
                    await m.reply_photo(photo=avatar_url, caption=caption)
                    await status_msg.delete()
                else:
                    await status_msg.edit_text(caption)
                return

        await status_msg.edit_text(font("❌ GitHub user not found!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


# 2. Organization Profile
@bot.on_message(filters.command(["org", "organization"]) & ~filters.forwarded)
async def github_org(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/org [org_name]` (e.g. `/org TheAloneTeam`)"))

    org_name = m.command[1].strip().lstrip("@")
    status_msg = await m.reply_text(font("🔍 Fetching GitHub organization data..."))

    url = f"https://api.github.com/orgs/{org_name}"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                name = data.get("name") or org_name
                desc = data.get("description") or "No description provided."
                public_repos = data.get("public_repos", 0)
                followers = data.get("followers", 0)
                blog = data.get("blog") or "None"
                location = data.get("location") or "Unknown"
                created_at = (data.get("created_at") or "").split("T")[0]
                avatar_url = data.get("avatar_url")
                html_url = data.get("html_url")

                caption = (
                    f"🏢 **GitHub Organization:** [{name}]({html_url})\n\n"
                    f"💬 **Description:** `{desc}`\n"
                    f"📦 **Public Repositories:** `{public_repos}`\n"
                    f"👥 **Followers:** `{followers}`\n"
                    f"📍 **Location:** `{location}`\n"
                    f"🌐 **Website:** {blog}\n"
                    f"📅 **Created:** `{created_at}`"
                )

                if avatar_url:
                    await m.reply_photo(photo=avatar_url, caption=caption)
                    await status_msg.delete()
                else:
                    await status_msg.edit_text(caption)
                return

        await status_msg.edit_text(font("❌ Organization not found!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


# 3. Repository Overview
@bot.on_message(filters.command(["repo", "repository"]) & ~filters.forwarded)
async def github_repo(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/repo [owner/repository]` (e.g. `/repo TheAloneTeam/MeowRoBot`)"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font("🔍 Fetching repository details..."))

    url = f"https://api.github.com/repos/{repo_path}"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                repo_name = data.get("full_name")
                desc = data.get("description") or "No description provided."
                stars = data.get("stargazers_count", 0)
                forks = data.get("forks_count", 0)
                watchers = data.get("watchers_count", 0)
                issues = data.get("open_issues_count", 0)
                lang = data.get("language") or "Unknown"
                default_branch = data.get("default_branch", "main")
                license_name = data.get("license", {}).get("name") if data.get("license") else "None"
                html_url = data.get("html_url")
                clone_url = data.get("clone_url")

                caption = (
                    f"📂 **Repository:** [{repo_name}]({html_url})\n\n"
                    f"📝 **Description:** `{desc}`\n"
                    f"⭐ **Stars:** `{stars}` | 🍴 **Forks:** `{forks}`\n"
                    f"👀 **Watchers:** `{watchers}` | 🐞 **Issues:** `{issues}`\n"
                    f"🌿 **Default Branch:** `{default_branch}`\n"
                    f"💻 **Language:** `{lang}`\n"
                    f"📜 **License:** `{license_name}`\n"
                    f"🔗 **Clone URL:** `{clone_url}`"
                )

                await status_msg.edit_text(caption)
                return

        await status_msg.edit_text(font("❌ Repository not found or is private!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


# 4. Recent Commits
@bot.on_message(filters.command(["commits", "commit"]) & ~filters.forwarded)
async def github_commits(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/commits [owner/repository]` (e.g. `/commits TheAloneTeam/MeowRoBot`)"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font("🔍 Fetching latest commits..."))

    url = f"https://api.github.com/repos/{repo_path}/commits?per_page=5"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                commits = resp.json()
                if not commits:
                    return await status_msg.edit_text(font("❌ No commits found in this repository."))

                text = f"📜 **Latest Commits for [{repo_path}](https://github.com/{repo_path}):**\n\n"
                for c in commits:
                    sha = c.get("sha", "")[:7]
                    html_url = c.get("html_url")
                    commit_info = c.get("commit", {})
                    author_name = commit_info.get("author", {}).get("name", "Unknown")
                    message = (commit_info.get("message") or "").split("\n")[0]
                    date_str = (commit_info.get("author", {}).get("date") or "").split("T")[0]

                    text += f"🔹 [`{sha}`]({html_url}) — **{message}**\n   👤 *{author_name}* on `{date_str}`\n\n"

                await status_msg.edit_text(text, disable_web_page_preview=True)
                return

        await status_msg.edit_text(font("❌ Repository not found or commits are unavailable!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


# 5. Releases & Changelogs
@bot.on_message(filters.command(["releases", "release"]) & ~filters.forwarded)
async def github_releases(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/releases [owner/repository]` (e.g. `/releases TheAloneTeam/MeowRoBot`)"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font("🔍 Fetching releases..."))

    url = f"https://api.github.com/repos/{repo_path}/releases?per_page=3"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                releases = resp.json()
                if not releases:
                    return await status_msg.edit_text(font("❌ No releases found for this repository."))

                text = f"🏷️ **Releases for [{repo_path}](https://github.com/{repo_path}):**\n\n"
                for rel in releases:
                    tag = rel.get("tag_name")
                    title = rel.get("name") or tag
                    pub_date = (rel.get("published_at") or "").split("T")[0]
                    html_url = rel.get("html_url")
                    tar_url = rel.get("tarball_url")
                    zip_url = rel.get("zipball_url")

                    text += (
                        f"📦 **[{title}]({html_url})** (`{tag}`)\n"
                        f"📅 **Date:** `{pub_date}`\n"
                        f"📥 [Source Code (zip)]({zip_url}) | [Source Code (tar)]({tar_url})\n\n"
                    )

                await status_msg.edit_text(text, disable_web_page_preview=True)
                return

        await status_msg.edit_text(font("❌ Repository not found or releases are private!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


# 6. Issues List
@bot.on_message(filters.command(["issues", "issue"]) & ~filters.forwarded)
async def github_issues(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/issues [owner/repository]` (e.g. `/issues TheAloneTeam/MeowRoBot`)"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font("🔍 Fetching open issues..."))

    url = f"https://api.github.com/repos/{repo_path}/issues?state=open&per_page=5"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                issues = resp.json()
                # Exclude pull requests (GitHub API returns PRs in issues endpoint unless filtered)
                pure_issues = [i for i in issues if "pull_request" not in i]
                if not pure_issues:
                    return await status_msg.edit_text(font("✨ No open issues in this repository!"))

                text = f"🐞 **Open Issues for [{repo_path}](https://github.com/{repo_path}):**\n\n"
                for iss in pure_issues[:5]:
                    num = iss.get("number")
                    title = iss.get("title")
                    user = iss.get("user", {}).get("login", "Unknown")
                    html_url = iss.get("html_url")
                    comments = iss.get("comments", 0)

                    text += f"🔹 [#{num}]({html_url}) — **{title}**\n   👤 By `{user}` | 💬 `{comments}` comments\n\n"

                await status_msg.edit_text(text, disable_web_page_preview=True)
                return

        await status_msg.edit_text(font("❌ Repository not found!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


# 7. Pull Requests List
@bot.on_message(filters.command(["prs", "pulls", "pullrequests"]) & ~filters.forwarded)
async def github_prs(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/prs [owner/repository]` (e.g. `/prs TheAloneTeam/MeowRoBot`)"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font("🔍 Fetching open pull requests..."))

    url = f"https://api.github.com/repos/{repo_path}/pulls?state=open&per_page=5"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                prs = resp.json()
                if not prs:
                    return await status_msg.edit_text(font("✨ No open pull requests in this repository!"))

                text = f"🔀 **Open Pull Requests for [{repo_path}](https://github.com/{repo_path}):**\n\n"
                for pr in prs:
                    num = pr.get("number")
                    title = pr.get("title")
                    user = pr.get("user", {}).get("login", "Unknown")
                    html_url = pr.get("html_url")
                    base = pr.get("base", {}).get("ref", "main")

                    text += f"🔹 [#{num}]({html_url}) — **{title}**\n   👤 By `{user}` into branch `{base}`\n\n"

                await status_msg.edit_text(text, disable_web_page_preview=True)
                return

        await status_msg.edit_text(font("❌ Repository not found!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


# 8. Contributors List
@bot.on_message(filters.command(["contributors", "contribs"]) & ~filters.forwarded)
async def github_contributors(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/contributors [owner/repository]` (e.g. `/contributors TheAloneTeam/MeowRoBot`)"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font("🔍 Fetching contributors..."))

    url = f"https://api.github.com/repos/{repo_path}/contributors?per_page=10"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                contribs = resp.json()
                if not contribs:
                    return await status_msg.edit_text(font("❌ No contributors found."))

                text = f"👥 **Top Contributors for [{repo_path}](https://github.com/{repo_path}):**\n\n"
                for idx, c in enumerate(contribs, 1):
                    login = c.get("login")
                    html_url = c.get("html_url")
                    commits = c.get("contributions", 0)

                    text += f"{idx}. [{login}]({html_url}) — `{commits}` commits\n"

                await status_msg.edit_text(text, disable_web_page_preview=True)
                return

        await status_msg.edit_text(font("❌ Repository not found!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


# 9. Branches List
@bot.on_message(filters.command(["branches", "branch"]) & ~filters.forwarded)
async def github_branches(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/branches [owner/repository]` (e.g. `/branches TheAloneTeam/MeowRoBot`)"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font("🔍 Fetching branches..."))

    url = f"https://api.github.com/repos/{repo_path}/branches?per_page=15"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                branches = resp.json()
                if not branches:
                    return await status_msg.edit_text(font("❌ No branches found."))

                text = f"🌿 **Branches for [{repo_path}](https://github.com/{repo_path}):**\n\n"
                for b in branches:
                    name = b.get("name")
                    commit_sha = b.get("commit", {}).get("sha", "")[:7]
                    text += f"🔹 `{name}` (`{commit_sha}`)\n"

                await status_msg.edit_text(text, disable_web_page_preview=True)
                return

        await status_msg.edit_text(font("❌ Repository not found!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


# 10. Repository Search
@bot.on_message(filters.command(["ghsearch", "searchrepo"]) & ~filters.forwarded)
async def github_search(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/ghsearch [search keywords]` (e.g. `/ghsearch telegram bot python`)"))

    query = m.text.split(None, 1)[1].strip()
    status_msg = await m.reply_text(font(f"🔍 Searching GitHub repositories for '{query}'..."))

    safe_q = urllib.parse.quote(query)
    url = f"https://api.github.com/search/repositories?q={safe_q}&sort=stars&order=desc&per_page=5"
    try:
        async with httpx.AsyncClient(timeout=12.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                total = data.get("total_count", 0)
                items = data.get("items", [])

                if not items:
                    return await status_msg.edit_text(font(f"❌ No repositories found matching '{query}'."))

                text = f"🔎 **GitHub Search Results for '{query}'** (Total: `{total}`):\n\n"
                for it in items:
                    full_name = it.get("full_name")
                    html_url = it.get("html_url")
                    stars = it.get("stargazers_count", 0)
                    forks = it.get("forks_count", 0)
                    lang = it.get("language") or "Code"
                    desc = (it.get("description") or "No description.")[:80]

                    text += (
                        f"📂 **[{full_name}]({html_url})**\n"
                        f"   ⭐ `{stars}` | 🍴 `{forks}` | 💻 `{lang}`\n"
                        f"   📝 *{desc}*\n\n"
                    )

                await status_msg.edit_text(text, disable_web_page_preview=True)
                return

        await status_msg.edit_text(font("❌ GitHub search API failed. Please try again later."))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))
