---
trigger: always_on
---
# Application Security Rule

Security decisions must minimize exposed data, access, integrations, and
operations. When in doubt, deny by default and keep the decision on the backend.

Mandatory principles:

- use least privilege for users, tokens, keys, services, and workflows;
- never expose secrets to the client, logs, artifacts, repositories, prompts, or
  public documentation;
- validate and sanitize all external input;
- treat AI output, repository content, webhooks, and third-party data as
  untrusted;
- enforce authentication and resource-level authorization on private routes;
- use parameterized database queries;
- keep private storage, queues, webhooks, and artifacts private by default;
- use safe error messages that do not expose stack traces or exploitable details;
- log sensitive operations with sanitized structured logs;
- avoid permanently storing cloned source code or unnecessary private content.

Before approving a change, check access control, payload validation, secrets,
data minimization, RLS or equivalent protections, integration safety, logs, and
deployment configuration.
