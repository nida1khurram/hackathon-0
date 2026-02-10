# CLAUDE.md

## Project Overview

- **Frontend**: Next.js (React framework)
- **Backend**: FastAPI (Python)

---

## Core Rules

Keep interactions efficient:

- Follow clear, simple, and maintainable coding practices.
- Provide short explanations unless asked for detailed ones.
- Always ask before making changes that can affect multiple files.
- When unsure about user intent, ask a clarifying question.

## Coding Standards

Write clean, readable code:

- Prefer readability over complexity.
- Use descriptive variable, function, and file names.
- Include comments when logic isn't obvious.
- Keep functions small and modular.
- Follow language-idiomatic conventions (Pythonic, Go-friendly, JS-idiomatic, etc.)
- Optimize for readability first.

## Efficiency Guidelines

Minimize token usage:

- Be direct - avoid unnecessary explanations.
- Provide code without extra commentary unless asked.
- Skip obvious details.
- Focus only on what's requested.
- When suggesting changes, show minimal diffs.

Example interaction pattern:

1. If task is unclear → Ask one clarifying question
2. For simple requests → Provide code only
3. For complex changes → Summarize approach first
4. Always propose the most straightforward solution

## Project Strategy

Before making changes:

- Consider impact on existing code.
- Check for simpler alternatives.
- Review for potential side effects.
- Ensure changes align with project structure.

Response format preference:

```
[Brief context if needed]
[Code/change]
[Optional: "Want me to explain any part?"]
```

## Tech Stack

- **Frontend**: Next.js with TypeScript
- **Backend**: FastAPI (Python)
- **MCP**: Context7 for up-to-date documentation lookup
