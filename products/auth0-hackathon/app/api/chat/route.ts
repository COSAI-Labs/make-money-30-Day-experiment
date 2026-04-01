import { NextRequest, NextResponse } from 'next/server'
import { getSession } from '@auth0/nextjs-auth0'

const TOOLPIPE_API = process.env.TOOLPIPE_API_URL || 'https://assessing-scoop-authorities-sheet.trycloudflare.com'

// Define available tools
const TOOLS = [
  { name: 'format_json', desc: 'Format and beautify JSON data', endpoint: '/json/format', method: 'POST' },
  { name: 'validate_json', desc: 'Validate JSON syntax', endpoint: '/json/validate', method: 'POST' },
  { name: 'generate_qr', desc: 'Generate a QR code', endpoint: '/qr/generate', method: 'GET', params: ['data', 'size'] },
  { name: 'generate_uuid', desc: 'Generate a UUID', endpoint: '/uuid/generate', method: 'GET' },
  { name: 'generate_hash', desc: 'Generate hash (MD5, SHA-256, etc.)', endpoint: '/hash/generate', method: 'POST' },
  { name: 'dns_lookup', desc: 'Look up DNS records', endpoint: '/dns/lookup', method: 'GET', params: ['domain'] },
  { name: 'generate_password', desc: 'Generate a secure password', endpoint: '/password/generate', method: 'GET' },
  { name: 'text_analyze', desc: 'Analyze text (word count, readability)', endpoint: '/text/analyze', method: 'POST' },
  { name: 'base64_encode', desc: 'Encode text to Base64', endpoint: '/base64/encode', method: 'POST' },
  { name: 'base64_decode', desc: 'Decode Base64 to text', endpoint: '/base64/decode', method: 'POST' },
  { name: 'markdown_to_html', desc: 'Convert Markdown to HTML', endpoint: '/markdown/to-html', method: 'POST' },
  { name: 'url_encode', desc: 'URL encode text', endpoint: '/url/encode', method: 'POST' },
  { name: 'jwt_decode', desc: 'Decode a JWT token', endpoint: '/jwt/decode', method: 'POST' },
  { name: 'whois_lookup', desc: 'WHOIS domain lookup', endpoint: '/whois/lookup', method: 'GET', params: ['domain'] },
  { name: 'github_repos', desc: 'List user GitHub repos (via Token Vault)', endpoint: 'GITHUB', method: 'VAULT' },
  { name: 'github_profile', desc: 'Get GitHub profile info (via Token Vault)', endpoint: 'GITHUB_PROFILE', method: 'VAULT' },
]

async function callToolPipe(endpoint: string, method: string, body?: any, params?: Record<string, string>) {
  let url = `${TOOLPIPE_API}${endpoint}`
  if (params) {
    const qs = new URLSearchParams(params).toString()
    url += `?${qs}`
  }

  const opts: RequestInit = { method, headers: { 'Content-Type': 'application/json' } }
  if (body && method === 'POST') {
    opts.body = JSON.stringify(body)
  }

  const res = await fetch(url, opts)
  return res.json()
}

async function callGitHub(path: string, token: string) {
  const res = await fetch(`https://api.github.com${path}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'DevAgent/1.0',
    },
  })
  return res.json()
}

export async function POST(req: NextRequest) {
  const { messages } = await req.json()
  const session = await getSession()
  const userMessage = messages[messages.length - 1]?.content || ''

  // Simple intent detection and tool routing
  const lowerMsg = userMessage.toLowerCase()
  let response = ''

  try {
    if (lowerMsg.includes('json') && (lowerMsg.includes('format') || lowerMsg.includes('beautif'))) {
      // Extract JSON from the message
      const jsonMatch = userMessage.match(/[{[][\s\S]*[}\]]/);
      if (jsonMatch) {
        const result = await callToolPipe('/json/format', 'POST', { json: jsonMatch[0], indent: 2 })
        response = `Here's your formatted JSON:\n\n\`\`\`json\n${result.formatted || result.result || JSON.stringify(result, null, 2)}\n\`\`\``
      } else {
        response = 'Please provide JSON data to format. For example: `Format this JSON: {"name":"test"}`'
      }
    } else if (lowerMsg.includes('qr')) {
      const urlMatch = userMessage.match(/https?:\/\/[^\s]+/) || userMessage.match(/(?:for|code)\s+(.+?)$/i)
      const data = urlMatch ? urlMatch[0] : 'https://toolpipe.dev'
      response = `Here's your QR code:\n\n![QR Code](${TOOLPIPE_API}/qr/generate?data=${encodeURIComponent(data)}&size=200)\n\nDirect link: ${TOOLPIPE_API}/qr/generate?data=${encodeURIComponent(data)}`
    } else if (lowerMsg.includes('uuid')) {
      const result = await callToolPipe('/uuid/generate', 'GET')
      response = `Generated UUID: \`${result.uuid}\``
    } else if (lowerMsg.includes('dns') || lowerMsg.includes('lookup')) {
      const domainMatch = userMessage.match(/(?:for|of|lookup)\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i)
      if (domainMatch) {
        const result = await callToolPipe('/dns/lookup', 'GET', null, { domain: domainMatch[1] })
        response = `DNS records for **${domainMatch[1]}**:\n\n\`\`\`json\n${JSON.stringify(result, null, 2)}\n\`\`\``
      } else {
        response = 'Please specify a domain. For example: `Look up DNS for google.com`'
      }
    } else if (lowerMsg.includes('password')) {
      const result = await callToolPipe('/password/generate', 'GET')
      response = `Generated secure password: \`${result.password || result.result}\``
    } else if (lowerMsg.includes('hash')) {
      const textMatch = userMessage.match(/hash\s+(?:of\s+)?["']?(.+?)["']?\s*$/i)
      const text = textMatch ? textMatch[1] : userMessage
      const result = await callToolPipe('/hash/generate', 'POST', { text, algorithm: 'sha256' })
      response = `SHA-256 hash: \`${result.hash || result.result}\``
    } else if (lowerMsg.includes('base64')) {
      if (lowerMsg.includes('decode')) {
        const b64Match = userMessage.match(/decode\s+(.+)/i)
        if (b64Match) {
          const result = await callToolPipe('/base64/decode', 'POST', { data: b64Match[1].trim() })
          response = `Decoded: \`${result.decoded || result.result}\``
        }
      } else {
        const textMatch = userMessage.match(/encode\s+(.+)/i)
        if (textMatch) {
          const result = await callToolPipe('/base64/encode', 'POST', { data: textMatch[1].trim() })
          response = `Base64: \`${result.encoded || result.result}\``
        }
      }
    } else if ((lowerMsg.includes('github') || lowerMsg.includes('repo')) && session?.accessToken) {
      // Use Auth0 Token Vault to get GitHub token
      // In production, this would use the Token Vault SDK
      response = `I can see you're authenticated as **${session.user?.name}**. To access your GitHub repos, I use Auth0 Token Vault to securely retrieve your GitHub access token without ever seeing your raw credentials.\n\nAvailable tools: ${TOOLS.map(t => `\`${t.name}\``).join(', ')}`
    } else if (lowerMsg.includes('help') || lowerMsg.includes('what can')) {
      response = `I'm DevAgent, your AI-powered developer assistant. I can help with:\n\n` +
        TOOLS.map(t => `- **${t.name}**: ${t.desc}`).join('\n') +
        `\n\nJust describe what you need in natural language!`
    } else {
      // Default: try to be helpful
      response = `I can help with that! Here are some things I can do:\n\n` +
        `- **Format JSON**: "Format this JSON: {...}"\n` +
        `- **Generate QR code**: "Generate a QR code for https://..."\n` +
        `- **DNS lookup**: "Look up DNS for example.com"\n` +
        `- **Generate password**: "Generate a secure password"\n` +
        `- **Generate UUID**: "Generate a UUID"\n` +
        `- **Hash text**: "Hash hello world"\n` +
        `- **GitHub access**: "List my GitHub repos" (requires login)\n\n` +
        `Type \`help\` for the full list of tools.`
    }
  } catch (error: any) {
    response = `Error calling tool: ${error.message}. Please try again.`
  }

  if (!response) {
    response = 'I wasn\'t able to process that request. Try asking me to format JSON, generate a QR code, look up DNS, or generate a password.'
  }

  return NextResponse.json({ content: response })
}
