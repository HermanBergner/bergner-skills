# Security checklist (diff review)

Read this when the diff touches an auth, input, IO, query, deserialization, or
crypto surface. It is an OWASP-framed checklist for *reviewing a diff* — not a
textbook. Assume OWASP knowledge; this is the "what to actually look for in the
changed lines, and what clears the ≥80 bar" cut.

## Contents

- How to surface a security finding
- OWASP Top 10 (2021), as diff checks
- Platform-specific surfaces (Authentik / OpenBao / FastAPI)

## How to surface a security finding

- Tie it to a concrete line in the diff and a concrete exploit path — "this
  builds SQL by f-string from `request.query`" beats "possible injection".
- A demonstrable hole on changed lines is 🔴 blocking (and usually ≥90).
- Vague "this could be more secure" with no path is a non-finding — drop it
  (SKILL.md §6 false positives).
- The runtime may not have `bandit`/`semgrep`/`pip-audit`. Reason from the diff,
  and recommend the authoritative scan rather than claiming you ran it.

## OWASP Top 10 (2021), as diff checks

- **A01 Broken Access Control** — a new/changed route or handler that mutates or
  reads sensitive data without an authorization check; an object reference
  (IDOR) that trusts a client-supplied id; a check that can be bypassed.
- **A02 Cryptographic Failures** — weak/again-rolled crypto, hardcoded keys/IVs,
  secrets in code or logs, TLS verification disabled, sensitive data stored or
  transmitted in clear.
- **A03 Injection** — SQL/command/LDAP/template built from untrusted input by
  concatenation; use bound parameters / safe APIs. Template injection (SSTI) via
  `render_template_string`-style calls on user input.
- **A04 Insecure Design** — a missing rate limit / lockout on an auth path; a
  trust boundary the change quietly crosses.
- **A05 Security Misconfiguration** — debug on, default creds, overly broad CORS,
  permissive bind, verbose errors leaking internals.
- **A06 Vulnerable Components** — a newly pinned dependency with a known CVE, or
  a downgrade; recommend `pip-audit`/`uv`'s audit for the lockfile.
- **A07 Identification/Auth Failures** — JWT `alg` not pinned, weak session
  handling, predictable tokens (`random` not `secrets`), missing auth on a
  mutating route.
- **A08 Software/Data Integrity** — insecure deserialization (`pickle`, unsafe
  `yaml.load`) of untrusted data; unsigned/unverified update or import path.
- **A09 Logging/Monitoring Failures** — secrets/PII written to logs; a
  security-relevant failure that is silently swallowed.
- **A10 SSRF** — a server-side fetch to a URL derived from user input without an
  allow-list.

## Platform-specific surfaces

- **Secrets belong in OpenBao**, never in a repo or a committed `.env`. A secret
  in the diff is an A02 + a leak (reference/secret-scanning.md) → 🔴.
- **Authentik / OIDC / JWT** — pin the algorithm; verify issuer/audience;
  enforce auth on routes that change state; don't log tokens.
- **FastAPI** — auth via a dependency on the protected route (not just the
  router include); Pydantic `extra="forbid"` where unexpected fields matter;
  don't return internals in error responses.
- **The change crosses the autonomous-coder trust boundary** (touches what an
  unattended agent could later run) — call it out explicitly; that is a
  first-class concern on this platform.
