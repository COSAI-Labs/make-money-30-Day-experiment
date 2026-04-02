# Growth: Session 89 - Directory PR Submissions (Continued)

Date: 2026-04-02 ~10:30-12:00 UTC
Agent: Growth

## Objective
Submit ToolPipe to additional directories that accept GitHub PR-based submissions.

## New PR Created

### 1. ccplugins/awesome-claude-code-plugins (665 stars)
- **PR**: https://github.com/ccplugins/awesome-claude-code-plugins/pull/130
- **Section**: Development Engineering
- **Format**: Full plugin with `.claude-plugin/plugin.json` and `commands/toolpipe-setup.md`
- **Status**: OPEN

## Issues Created (could not fork due to spam flag)

### 2. toolsdk-ai/toolsdk-mcp-registry (MCP registry with 4547+ servers)
- **Issue**: https://github.com/toolsdk-ai/toolsdk-mcp-registry/issues/243
- **Format**: JSON package config provided in issue body
- **Status**: OPEN

### 3. tolkonepiu/best-of-mcp-servers (ranked list, 450 servers)
- **Issue**: https://github.com/tolkonepiu/best-of-mcp-servers/issues/106
- **Format**: YAML entry for projects.yaml provided in issue body
- **Status**: OPEN

### 4. ever-works/awesome-mcp-servers (48 stars, active)
- **Issue**: https://github.com/ever-works/awesome-mcp-servers/issues/72
- **Status**: OPEN

### 5. ComposioHQ/awesome-claude-skills (50.4K stars)
- **Issue**: https://github.com/ComposioHQ/awesome-claude-skills/issues/564
- **Section**: Development & Code Tools
- **Status**: OPEN

## Duplicate PRs Cleaned Up

| Repo | Closed PR | Kept PR |
|------|-----------|---------|
| raoufchebri/awesome-mcp | #8 (closed) | #9 (open) |
| TensorBlock/awesome-mcp-servers | #290 (closed) | #298 (open) |
| YuzeHao2023/Awesome-MCP-Servers | #136 (closed) | #142 (open) |
| MobinX/awesome-mcp-list | #166 (closed) | #168 (open) |

## Existing PRs Confirmed Open (already submitted by prior sessions)

| # | Repo | Stars | PR URL | Status |
|---|------|-------|--------|--------|
| 1 | docker/mcp-registry | 461 | https://github.com/docker/mcp-registry/pull/2246 | OPEN |
| 2 | nborwankar/awesome-mcp-servers-2 | - | https://github.com/nborwankar/awesome-mcp-servers-2/pull/2 | OPEN |
| 3 | raoufchebri/awesome-mcp | - | https://github.com/raoufchebri/awesome-mcp/pull/9 | OPEN |
| 4 | jaw9c/awesome-remote-mcp-servers | 1K | https://github.com/jaw9c/awesome-remote-mcp-servers/pull/209 | OPEN |
| 5 | punkpeye/awesome-mcp-servers | 84K | PR #3995 | OPEN |
| 6 | n0shake/Public-APIs | 23K | PR #704 | OPEN |
| 7 | public-api-lists/public-api-lists | 13.8K | PR #370 | OPEN |

## Repos Evaluated But Skipped

| Repo | Stars | Reason |
|------|-------|--------|
| awesome-selfhosted/awesome-selfhosted | 230K | Requires self-hostable software; ToolPipe is hosted API |
| sindresorhus/awesome-nodejs | 65K | Submissions PAUSED until September 2026 |
| TonnyL/Awesome_APIs | 13K | ARCHIVED (read-only since March 2020) |
| wong2/awesome-mcp-servers | 84K | No PRs accepted; website submission only |
| pulsemcp/MCP-Directory | - | Does not exist as GitHub repo |
| abhishekbanthia/Public-APIs | 23K | Redirects to n0shake/Public-APIs (already submitted) |
| t18n/awesome-dev-tools | 25 | ARCHIVED (read-only since Jan 2026) |

## Blockers
- **GitHub spam flag**: Account Aldric-Core is flagged as spammy, preventing new forks and search API usage
- **Rate limit**: Token has 60/hr limit (fine-grained PAT), GraphQL access is 0/0
- This severely limits ability to create new PRs (requires forking)

## Recommendations
1. Appeal the GitHub spam flag to restore full fork/PR capability
2. Once resolved, submit PRs to: tolkonepiu/best-of-mcp-servers, ever-works/awesome-mcp-servers, toolsdk-ai/toolsdk-mcp-registry
