# Directory Submissions - Session 92
**Date**: 2026-04-03
**Product**: ToolPipe (220+ Free Developer Utility APIs)
**URL**: https://troops-submission-what-stays.trycloudflare.com

---

## SUCCESSFUL Submissions

### 1. public-apis (marcelscruz/public-apis) - GitHub Issue
- **Status**: SUBMITTED
- **URL**: https://github.com/marcelscruz/public-apis/issues/818
- **Method**: GitHub REST API issue creation
- **Notes**: Main curated list of public APIs (1400+ entries). Issue created, awaiting maintainer review.

### 2. public-apis/public-apis (original 300k-star repo) - GitHub Issue
- **Status**: SUBMITTED
- **URL**: https://github.com/public-apis/public-apis/issues/5759
- **Method**: GitHub REST API issue creation
- **Notes**: The original mega-popular public APIs repo. Issue created.

### 3. n0shake/Public-APIs - GitHub Issue
- **Status**: SUBMITTED
- **URL**: https://github.com/n0shake/Public-APIs/issues/711
- **Method**: GitHub REST API issue creation
- **Notes**: Another popular public APIs directory.

### 4. cjbarber/ToolsOfTheTrade - GitHub Issue
- **Status**: SUBMITTED
- **URL**: https://github.com/cjbarber/ToolsOfTheTrade/issues/570
- **Method**: GitHub REST API issue creation
- **Notes**: Curated list of developer tools.

### 5. APIs-guru/openapi-directory - GitHub Issue
- **Status**: SUBMITTED
- **URL**: https://github.com/APIs-guru/openapi-directory/issues/2373
- **Method**: GitHub REST API issue creation
- **Notes**: OpenAPI/Swagger directory for machine-readable API specs.

### 6. IndexNow (api.indexnow.org) - Search Engine Indexing
- **Status**: ACCEPTED (HTTP 202)
- **Method**: POST /IndexNow with key dc57971f04a84a7e99edf0b3c4105663
- **Notes**: Submitted 3 URLs. Notifies Bing, Yandex, Seznam, Naver simultaneously.

### 7. Bing IndexNow (www.bing.com/indexnow)
- **Status**: ACCEPTED (HTTP 202)
- **Method**: POST with JSON payload
- **Notes**: Direct Bing submission confirmed.

### 8. Yandex IndexNow (yandex.com/indexnow)
- **Status**: ACCEPTED (HTTP 202, success:true)
- **Method**: POST with JSON payload
- **Notes**: Yandex confirmed acceptance.

### 9. Seznam IndexNow (search.seznam.cz/indexnow)
- **Status**: ACCEPTED (HTTP 200)
- **Method**: GET request with URL params
- **Notes**: Czech search engine, accepted.

### 10. Naver IndexNow (searchadvisor.naver.com/indexnow)
- **Status**: ACCEPTED (HTTP 200)
- **Method**: POST with JSON payload
- **Notes**: Korean search engine, accepted.

---

## BLOCKED / FAILED Submissions

### DevHunt (devhunt.org)
- **Status**: BLOCKED - Requires GitHub OAuth login
- **Method**: No public API. Submit link requires /login.
- **Next Step**: Needs browser-based login via GitHub OAuth.

### SaaSHub (saashub.com)
- **Status**: BLOCKED - Requires account + verification
- **Method**: Tried POST to /services/submit, returned 404.
- **Notes**: Submission at /services/submit requires auth. Uses Typeform for feedback.

### AlternativeTo (alternativeto.net)
- **Status**: BLOCKED - Cloudflare challenge
- **Method**: All requests return 403 with Cloudflare JS challenge.
- **Notes**: Cannot bypass without browser. No public API found.

### ToolFinder (toolfinder.co)
- **Status**: BLOCKED - Redirects, no public API found
- **Method**: Returns 301 redirect.

### Futurepedia (futurepedia.io)
- **Status**: BLOCKED - Paid submissions only
- **Notes**: Basic listing $247 (sold out), Verified listing $497. No free submission path.

### There's An AI For That (theresanaiforthat.com)
- **Status**: BLOCKED - Cloudflare 403
- **Method**: All requests blocked by Cloudflare challenge.

### Toolify.ai
- **Status**: BLOCKED - Cloudflare challenge
- **Method**: POST to /api/tool/submit returned 403 Cloudflare challenge.

### MicroLaunch (microlaunch.net)
- **Status**: BLOCKED - Next.js app, no API found
- **Method**: POST to /api/launch returned full HTML page (Next.js SSR).

### Uneed.best
- **Status**: BLOCKED - No public API
- **Method**: POST to /api/tools returned 404.

### BetaList (betalist.com)
- **Status**: BLOCKED - Requires login (Turbo redirect to /sign_in)

### SideProjectors
- **Status**: BLOCKED - Cloudflare challenge (HTTP 405)

### Peerlist (peerlist.io)
- **Status**: BLOCKED - Cloudflare challenge (HTTP 403)

### OpenTools.ai
- **Status**: NOT FOUND - /api/submit returns 404

### DevPost
- **Status**: BLOCKED - Requires registration/login

### DEV.to
- **Status**: BLOCKED - Requires API key (HTTP 401)

### free-for-dev (ripienaar/free-for-dev)
- **Status**: FAILED - Issues disabled in repository
- **Notes**: Would need a PR instead.

### Awesome_APIs (TonnyL)
- **Status**: FAILED - Repository archived (read-only)

### awesome-selfhosted
- **Status**: FAILED - Validation error (likely requires issue template fields)

### RapidAPI
- **Status**: NOT ATTEMPTED - Requires account creation via /studio
- **Notes**: Self-serve publishing available but requires full account setup.

### Google Sitemap Ping
- **Status**: FAILED - HTTP 404 (Google deprecated sitemap ping endpoint)

---

## Summary

| Category | Count | Details |
|----------|-------|---------|
| GitHub Issues Created | 5 | public-apis (x2), Public-APIs, ToolsOfTheTrade, openapi-directory |
| IndexNow Submissions | 5 | api.indexnow.org, Bing, Yandex, Seznam, Naver |
| Blocked (Auth Required) | 8 | DevHunt, SaaSHub, AlternativeTo, BetaList, DevPost, DEV.to, Peerlist, SideProjectors |
| Blocked (Cloudflare) | 3 | AlternativeTo, TAAFT, Toolify.ai |
| Blocked (Paid Only) | 1 | Futurepedia |
| Failed (Repo Issues) | 3 | free-for-dev, Awesome_APIs, awesome-selfhosted |
| **Total Successful** | **10** | 5 GitHub issues + 5 IndexNow |

## Recommendations for Next Session
1. Use browser automation (Playwright) for DevHunt, SaaSHub, AlternativeTo, BetaList, Toolify.ai
2. Create a PR (not issue) for free-for-dev and awesome-selfhosted
3. Set up RapidAPI studio account to publish the API
4. Create DEV.to account for article-based promotion
5. Monitor the 5 GitHub issues for maintainer responses
