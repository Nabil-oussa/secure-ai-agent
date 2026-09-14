# Secure AI Agent — IAM, RBAC, ABAC & Policy Enforcement

A practical security lab exploring how to secure AI agents that can interact with protected resources.

This project is built with **Python** and **smolagents** and progressively introduces security controls around an AI agent:

```text
LLM
 ↓
CodeAgent
 ↓
Tool
 ↓
SecurityContext
 ↓
PolicyEngine
 ↓
policy.yaml
 ↓
ALLOW / DENY
 ↓
Protected Resource
```

## 🎯 Objectives

The goal is to understand how security mechanisms can be integrated into an AI agent architecture.

The project progressively implements:

* Tool-level security
* Path traversal protection
* RBAC — Role-Based Access Control
* Resource-based authorization
* Security audit logs
* ABAC — Attribute-Based Access Control
* Externalized security policies
* Security Context
* Trusted Runtime

The central security principle is:

> **The LLM proposes. The agent orchestrates. The tool executes. The policy authorizes or denies.**

The LLM must never be trusted as the authority for identity or authorization.

---

## 🏗️ Architecture

The final architecture separates intelligence, execution and authorization:

```text
                    ┌──────────────┐
                    │     LLM      │
                    │   Qwen etc.  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  CodeAgent   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │     Tool     │
                    │ read / delete│
                    └──────┬───────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │  SecurityContext   │
                 │                    │
                 │ identity           │
                 │ attributes         │
                 └─────────┬──────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ PolicyEngine │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  policy.yaml │
                    └──────┬───────┘
                           │
                     ┌─────┴─────┐
                     ▼           ▼
                   ALLOW        DENY
                     │
                     ▼
              Protected Resource
```

---

## 🔐 Security Model

Authorization is based on:

```text
Identity + Action + Resource + Attributes
                         │
                         ▼
                    Policy Engine
                         │
                    ALLOW / DENY
```

Example security context:

```python
{
    "identity": "file-reader",
    "attributes": {
        "environment": "development",
        "department": "security",
        "risk_level": "low"
    }
}
```

The identity is supplied by the trusted runtime and is not selected by the LLM.

---

## 📚 Learning Progression

### 01 — Basic Agent

`01_basic_agent.py`

Introduces a protected `read_file` tool.

The first security control prevents the agent from accessing files outside the authorized directory.

Path normalization is performed before authorization:

```python
Path(path).expanduser().resolve()
```

This protects against path traversal and similar-path bypasses.

---

### 02 — RBAC

`02_rbac.py`

Introduces identities and permissions.

Example:

```text
file-reader
 └── read_file

file-admin
 ├── read_file
 └── delete_file
```

Authorization becomes dependent on the identity of the agent.

---

### 03 — RBAC + Audit

`03_rbac_audit.py`

Introduces security audit logs.

Example:

```text
[AUDIT]
identity=file-reader
action=delete_file
resource=/tmp/agent-data/test.txt
decision=DENY
```

Every authorization decision can therefore be traced.

---

### 04 — Resource Authorization

`04_rbac_resources.py`

Authorization is no longer limited to the action.

It also considers the protected resource.

For example:

```text
file-reader
 ├── read_file → /tmp/agent-data
 └── read_file → /tmp/public

file-admin
 ├── read_file   → /tmp/agent-data
 ├── read_file   → /tmp/public
 └── delete_file → /tmp/agent-data
```

This implements a basic least-privilege model.

---

### 05 — ABAC

`05_abac.py`

Authorization is extended with attributes.

The decision becomes:

```text
Identity
   +
Action
   +
Resource
   +
Attributes
   ↓
ALLOW / DENY
```

Example:

```yaml
environment: development
department: security
risk_level: low
```

A `file-admin` may therefore have the required permission but still be denied if the contextual attributes do not satisfy the policy.

---

### 06 — External Policy

`06_external_policy.py`

The authorization policy is externalized into:

```text
policy.yaml
```

The application no longer contains the complete authorization policy.

This creates a clearer separation:

```text
Application
     │
     ▼
PolicyEngine
     │
     ▼
policy.yaml
```

---

## 🛡️ Security Context

The project introduces a dedicated `SecurityContext`:

```python
class SecurityContext:
    def __init__(self, identity, attributes):
        self.identity = identity
        self.attributes = attributes
```

This separates security information from the tools themselves.

The tools consume the security context but do not define their own authorization policy.

---

## 🔑 Trusted Runtime

The runtime is responsible for creating the security context:

```text
Trusted Runtime
       │
       ▼
SecurityContext
       │
       ▼
Agent / Tools
```

This is an important security boundary.

The agent must not be able to arbitrarily change:

```text
identity = file-reader
```

into:

```text
identity = file-admin
```

Simply asking the LLM to "act as an administrator" must never grant additional privileges.

---

## 🧪 Security Tests

The project includes tests covering:

* Authorized file access
* Unauthorized file access
* Path traversal
* Similar-path bypass
* Unknown identities
* Unknown actions
* Empty identities
* Missing attributes
* Incorrect environment
* Incorrect department
* High-risk operations
* Unauthorized deletion
* Resource boundary enforcement

Example:

```python
assert not policy_engine.is_allowed(
    "file-reader",
    "delete_file",
    "/tmp/agent-data/test.txt",
    {
        "environment": "development",
        "department": "security",
        "risk_level": "low",
    },
)
```

---

## 🧰 Technologies

* Python
* smolagents
* Hugging Face Inference API
* Qwen
* pytest
* YAML
* RBAC
* ABAC
* Policy Enforcement
* Security Context
* Audit Logging

---

## 🚀 Running the Tests

Create the virtual environment and install the dependencies.

Then run:

```bash
pytest -v
```

For the direct tool tests:

```bash
python test_tools.py
```

The LLM-based agent can be launched with:

```bash
python 06_external_policy.py
```

> LLM inference requires an available Hugging Face inference provider and valid credentials where required.

---

## 🔭 Future Improvements

Possible next steps:

* Trusted Identity Provider
* JWT-based identity
* OAuth2 / OIDC
* Short-lived credentials
* Policy versioning
* Policy decision logging
* Policy-as-Code
* Open Policy Agent (OPA)
* Kubernetes service identities
* Tool-level rate limiting
* Risk-based authorization
* Human-in-the-loop approval
* Prompt injection resistance
* Agent-to-agent authorization
* MCP security
* KMS integration
* PKI / mTLS
* Post-Quantum Cryptography

---

## 🎓 Learning Goal

This project is part of a practical learning path toward:

**Agentic AI Security → IAM → PKI → KMS → Cloud Security → Post-Quantum Cryptography**

The main objective is to understand how traditional security principles such as **least privilege, identity, authorization, policy enforcement and auditability** can be applied to modern AI agent architectures.
