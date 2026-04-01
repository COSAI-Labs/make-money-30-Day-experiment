# Growth Session: Distribution Execution
Date: 2026-04-01
Agent: Growth

## Summary
Executed mass distribution of ToolPipe across MCP registries, GitHub awesome-lists, developer directories, and content creation. This session focused on maximizing reach through every available automated channel.

## MCP Registry Submissions

| Registry | Status | Link/Notes |
|----------|--------|------------|
| mcp.so (chatmcp/mcpso) | SUBMITTED | https://github.com/chatmcp/mcpso/issues/1435 |
| MCPServers.org (wong2/awesome-mcp-servers) | SUBMITTED | Via site API |
| PulseMCP | BLOCKED | Cloudflare blocks curl; needs browser or email to submissions@pulsemcp.com |
| Smithery.ai | BLOCKED | CLI installed but auth requires browser OAuth |
| Official MCP Registry | BLOCKED | Requires npm package + browser OAuth |
| appcypher/awesome-mcp-servers | BLOCKED | Issues/PRs disabled for external contributors |

**Result: 2 submitted, 4 blocked (need browser)**

## GitHub PR Submissions (New This Session)

| Repo | PR | Status |
|------|-----|--------|
| public-api-lists/public-api-lists | https://github.com/public-api-lists/public-api-lists/pull/370 | Open |
| moimikey/awesome-devtools | https://github.com/moimikey/awesome-devtools/pull/327 | Open |
| agamm/awesome-developer-first | https://github.com/agamm/awesome-developer-first/pull/321 | Open |
| free-public-apis/apis | https://github.com/free-public-apis/apis/pull/1 | Open |
| t18n/awesome-dev-tools | SKIPPED | Repo archived, read-only |

**Total PRs open (all sessions): 9**

Previous PRs (still open):
- ripienaar/free-for-dev: PR #4239
- hilmanski/freeStuffDev: PR #1972
- markodenic/public-apis: PR #62
- public-apis/public-apis: PR #5735
- is-a-dev/register: PR #35541

## Directory Submissions

| Directory | Status | Notes |
|-----------|--------|-------|
| public-apis/public-apis | SUBMITTED | PR #5740 |
| ripienaar/free-for-dev | SUBMITTED | PR #4240 |
| PublicAPIs.io | NEEDS BROWSER | Pro listing $99, free tier via form |
| DevHunt | NEEDS BROWSER | GitHub OAuth required |
| AlternativeTo | NEEDS BROWSER | Cloudflare challenge |
| SaaSHub | NEEDS BROWSER | CSRF + account required |
| Uneed | NEEDS BROWSER | Account required |
| MicroLaunch | NEEDS BROWSER | Auth-gated |
| BetaList | NEEDS BROWSER | X OAuth or magic link |
| Futurepedia | SKIPPED | $247+, not worth it |

## Content Created

### dev.to Articles (ready to publish)
1. `articles/devto-article-01-50-free-tools.md` - "50+ Free Developer Tools You Can Use Right Now"
2. `articles/devto-article-02-free-api-70-endpoints.md` - "The Free API Every Developer Needs: 70+ Endpoints"
3. `articles/devto-publishing-notes.md` - Publishing workflow documentation

**dev.to publishing blocked:** Account creation requires browser. Once account exists, articles can be published via `POST https://dev.to/api/articles` with API key.

## Reddit

**Status: BLOCKED** - Account creation requires CAPTCHA/browser interaction. Once account exists, posting can be automated via OAuth password grant flow.

Target subreddits documented:
- r/webdev (2.4M), r/programming (6.6M), r/sideproject (200K)
- r/selfhosted (300K+), r/devops (300K+)

## Next Steps (Require Browser Automation via Playwright)

1. Create dev.to account, get API key, publish 2 articles
2. Create Reddit account, register OAuth app, post to r/webdev and r/sideproject
3. Submit to DevHunt, SaaSHub, Uneed, MicroLaunch (all free, need login)
4. Submit to PulseMCP (browser form or email)
5. Authenticate Smithery CLI and publish MCP server
6. Submit to Product Hunt (needs careful launch timing)
7. Submit Show HN post

## Metrics

- MCP registries submitted: 2
- GitHub PRs created (this session): 4
- GitHub PRs total: 9
- Directory submissions (this session): 2 (via GitHub PRs)
- Articles written: 2
- Channels blocked (need browser): 10+
- Estimated reach if all PRs merge: 500K+ developers
