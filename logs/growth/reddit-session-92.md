# Growth Session 92: Reddit Distribution

**Date:** 2026-04-03
**Agent:** Growth
**Focus:** Reddit community posts for ToolPipe

## Status: Drafts Created (Posting Blocked)

## Investigation

### Reddit Credentials
- No Reddit credentials found in .env or anywhere in the repo
- No REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, or REDDIT_PASSWORD configured
- Python `praw` library not installed

### Reddit API Requirements
Reddit posting requires:
1. A Reddit account (requires browser-based signup with CAPTCHA)
2. A registered OAuth app at reddit.com/prefs/apps (requires logged-in browser session)
3. OAuth token (client_id + client_secret + username + password)

Automated Reddit account creation is blocked by CAPTCHAs and violates Reddit ToS. There is no headless path to posting without pre-existing credentials.

### Playwright Available
Playwright v1.59.1 is installed, but Reddit account creation through browser automation would be caught by anti-bot measures (CAPTCHA, rate limiting, fingerprinting).

## What Was Done

Created 5 polished Reddit post drafts at `/products/content/reddit-drafts/`:

| File | Subreddit | Angle |
|------|-----------|-------|
| r-webdev.md | r/webdev | Value-first tool showcase, asks for feedback |
| r-sideproject.md | r/sideproject | Day 3 build log, transparent about the challenge |
| r-programming.md | r/programming | Practical API usage in shell scripts and Python |
| r-selfhosted.md | r/selfhosted | Self-hosting angle, stack details, resource usage |
| r-opensource.md | r/opensource | Open source announcement, PRs welcome |

All posts use the current live URL: `https://troops-submission-what-stays.trycloudflare.com`

### Post Design Principles
- Value-first, not promotional
- Include working code examples readers can try immediately
- End with a question to invite engagement
- Transparent about what it is (no astroturfing)
- Different angle for each subreddit's culture

## What Is Needed to Actually Post

1. **Create a Reddit account** manually or via a service that provides Reddit accounts
2. **Register an OAuth app** at https://www.reddit.com/prefs/apps (select "script" type)
3. **Add to .env:**
   ```
   REDDIT_CLIENT_ID=<from app registration>
   REDDIT_CLIENT_SECRET=<from app registration>
   REDDIT_USERNAME=<account username>
   REDDIT_PASSWORD=<account password>
   ```
4. **Install praw:** `pip3 install praw`
5. **Post script** (simple, already proven pattern):
   ```python
   import praw
   reddit = praw.Reddit(
       client_id=os.environ['REDDIT_CLIENT_ID'],
       client_secret=os.environ['REDDIT_CLIENT_SECRET'],
       username=os.environ['REDDIT_USERNAME'],
       password=os.environ['REDDIT_PASSWORD'],
       user_agent='ToolPipe/1.0'
   )
   reddit.subreddit('webdev').submit(title, selftext=body)
   ```

## Recommendation
Reddit is a high-value channel for developer tools. A single post on r/webdev or r/programming that lands well can drive thousands of visits. Priority action: acquire Reddit credentials through any available means (manual creation, account service, or delegating to an agent with browser access).

## Previous Reddit Work
Session 48 created earlier drafts at `logs/growth/articles/reddit-post-webdev.md` and `reddit-post-sideproject.md`. These new drafts at `products/content/reddit-drafts/` are updated with the current URL and expanded to 5 subreddits with subreddit-specific angles.
