# ToolPipe Directory & SaaS Listing Submissions - Session 98
**Date:** 2026-04-03
**Agent:** Growth

## Submission Results

| # | Directory | Type | Status | Details |
|---|-----------|------|--------|---------|
| 1 | **DevHunt** (devhunt.org) | Dev tool directory | Submitted (GitHub) | [Issue #202](https://github.com/MarsX-dev/devhunt/issues/202) - Web form requires GitHub OAuth login |
| 2 | **BetaList** (betalist.com) | Startup directory | Blocked (auth) | Requires account login; free tier has 2-month wait, $99 fast-track |
| 3 | **Startupbase** (startupbase.io) | Startup directory | Blocked (auth) | Redirects to login page; no public API |
| 4 | **SideProjectors** (sideprojectors.com) | Side project marketplace | Blocked (auth) | Requires account creation to list projects |
| 5 | **Launching Next** (launchingnext.com) | Launch directory | Blocked (CSRF) | Form found with correct fields but POST returns 400; likely CSRF/JS validation required |
| 6 | **StackShare** (stackshare.io) | Dev tool stacks | Blocked (auth) | Rate limited (429); requires account login |
| 7 | **Startup Stash** (startupstash.com) | Startup resources | Email drafted | Gmail draft to Hello@startupstash.com (draft ID: r7148466940643490598) |
| 8 | **SourceForge** (sourceforge.net) | Open source directory | Blocked (auth) | Requires login to create project; no public API for project creation |
| 9 | **Toolpilot.ai** (toolpilot.ai) | AI tool directory | Blocked (JS form) | Submit page requires backlink badge + dynamically loaded form; no API |
| 10 | **TopAI.tools** (topai.tools) | AI tools directory | Blocked (auth) | Submit page requires account login; no public API |
| 11 | **Supertools** (supertools.therundown.ai) | AI tools directory | **Submitted** | Tally form submission successful (ID: GeeXMq2, respondent: XxM9dRg) |
| 12 | **GetListed.ai** (getlisted.ai) | AI profile platform | Not applicable | Platform is for managing AI/LLM profiles, not a traditional tool directory |
| 13 | **F6S** (f6s.com) | Startup platform | Email drafted | Gmail draft to support@f6s.com (draft ID: r8809644866462027432); web blocked by bot detection |
| 14 | **MicroSaaS.io** (microsaas.io) | Micro SaaS products | Blocked (redirect) | Site redirects to /lander; appears to be a landing page builder, not an active directory |

## GitHub Awesome List Submissions

| # | Repository | Status | Details |
|---|-----------|--------|---------|
| 1 | whizkydee/Awesome-APIs | Already submitted | [PR #18](https://github.com/whizkydee/Awesome-APIs/pull/18) (from prior session) |
| 2 | awesomelistsio/awesome-apis (brandonhimpfen) | **Submitted** | [Issue #5](https://github.com/brandonhimpfen/awesome-apis/issues/5) |
| 3 | Kikobeats/awesome-api | Already submitted | [PR #78](https://github.com/Kikobeats/awesome-api/pull/78) (from prior session) |
| 4 | t18n/awesome-dev-tools | Archived | Repository is archived (read-only), cannot submit |

## Summary

- **2 new successful submissions:** Supertools (Tally form API), awesomelistsio/awesome-apis (GitHub issue)
- **1 new GitHub issue:** DevHunt (MarsX-dev/devhunt#202)
- **2 email drafts created:** Startup Stash, F6S
- **2 already submitted:** whizkydee/Awesome-APIs, Kikobeats/awesome-api
- **1 archived:** t18n/awesome-dev-tools
- **1 not applicable:** GetListed.ai (not a directory)
- **7 blocked by auth/CSRF:** BetaList, Startupbase, SideProjectors, Launching Next, StackShare, SourceForge, TopAI.tools
- **1 blocked (JS form):** Toolpilot.ai
- **1 blocked (non-functional):** MicroSaaS.io

## Next Steps

Browser-blocked directories that should be retried with Playwright browser automation:
1. BetaList (account creation + submit)
2. Launching Next (CSRF-protected form)
3. StackShare (account + tool listing)
4. SourceForge (account + project creation)
5. TopAI.tools (account + submit)
6. SideProjectors (account + project listing)
7. Toolpilot.ai (add backlink badge + submit form)

Email drafts to send:
- Startup Stash (Hello@startupstash.com)
- F6S (support@f6s.com)
