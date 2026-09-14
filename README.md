# Secure AI Agent — IAM, RBAC, ABAC & Policy Enforcement
[![CI](https://github.com/Nabil-oussa/secure-ai-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Nabil-oussa/secure-ai-agent/actions/workflows/ci.yml)
A practical security laboratory exploring how to secure AI agents that interact with protected resources.

This project is built with **Python** and **smolagents** and progressively introduces security controls around an AI agent, from basic tool protection to externalized policy enforcement.

The project focuses on a fundamental security principle:

> **The LLM proposes. The agent orchestrates. The tool executes. The policy authorizes or denies.**

The LLM is **not** trusted as an authority for identity or authorization.

---

## 🎯 Objectives

The goal is to understand how traditional security principles can be applied to modern AI agent architectures.

The project progressively introduces:

* Tool-level security
* Path traversal protection
* RBAC — Role-Based Access Control
* Resource-based authorization
* Security audit logging
* ABAC — Attribute-Based Access Control
* Externalized security policies
* Security contexts
* Trusted runtime concepts
* Least-privilege authorization

---

## 🏗️ Architecture

The final architecture separates **intelligence**, **execution**, and **authorization**:

```text
                    ┌──────────────┐
                    │     LLM      │
                    │   Qwen etc.  │
                    └──────┬───────┘
                           │
                           │ proposes action
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

Authorization is based on four security dimensions:

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

The identity and security attributes are supplied by the runtime.

They must not be selected or modified by the LLM.

---

## 📚 Learning Progression

The repository intentionally shows the evolution of the security architecture.

### 01 — Basic Agent

**`basic_agent.py`**

Introduces a protected `read_file` tool.

The first security control prevents the agent from accessing files outside the authorized directory.

Path normalization is performed before authorization:

```python
Path(path).expanduser().resolve()
```

This prevents path traversal and similar-path bypasses.

---

### 02 — RBAC

**`rbac.py`**

Introduces identities and role-based permissions.

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

### 03 — RBAC + Identity

**`rbac_identity.py`**

Introduces an explicit agent identity and separates the identity from the authorization logic.

This step demonstrates why authorization decisions should be based on a security identity rather than on the requested operation alone.

---

### 04 — RBAC + Audit

**`rbac_audit.py`**

Introduces security audit logs.

Example:

```text
[AUDIT]
identity=file-reader
action=delete_file
resource=/tmp/agent-data/test.txt
decision=DENY
```

Authorization decisions can therefore be traced and investigated.

---

### 05 — Resource Authorization

**`rbac_resources.py`**

Authorization is extended to include the protected resource.

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

This introduces resource-level least privilege.

---

### 06 — ABAC

**`abac.py`**

Authorization is extended with contextual attributes.

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

A `file-admin` may have permission to perform an operation but still be denied if the contextual attributes do not satisfy the security policy.

---

### 07 — External Policy Enforcement

**`external_policy.py`**

The authorization policy is externalized into:

```text
policy.yaml
```

The application no longer contains the complete authorization policy.

This creates a clear separation:

```text
Application
     │
     ▼
PolicyEngine
     │
     ▼
policy.yaml
```

This approach is closer to a **Policy-as-Code** architecture.

---

## 🛡️ Security Context

The project introduces a dedicated `SecurityContext`:

```python
class SecurityContext:
    def __init__(self, identity, attributes):
        self.identity = identity
        self.attributes = attributes
```

The security context separates identity and authorization attributes from the implementation of individual tools.

Tools consume the security context but do not define their own security identity.

---

## 🔑 Trusted Runtime

The runtime is responsible for providing the security context:

```text
Trusted Runtime
       │
       ▼
SecurityContext
       │
       ▼
Agent / Tools
```

This represents an important security boundary.

The agent must not be able to arbitrarily change:

```text
identity = file-reader
```

into:

```text
identity = file-admin
```

Simply asking the LLM to:

> "Act as an administrator"

must never grant additional privileges.

> **Authentication and authorization must remain outside the control of the LLM.**

The current implementation is a pedagogical simulation of a trusted runtime. A production implementation would typically obtain identity from an external identity provider or workload identity mechanism.

---

## 🧪 Security Tests

The project includes automated tests covering:

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

The current test suite contains **15 tests**.

Run the complete test suite with:

```bash
PYTHONPATH=. ./venv/bin/pytest -q
```

Expected result:

```text
15 passed
```

---

## 📁 Project Structure

```text
secure-ai-agent/
│
├── README.md
├── .gitignore
├── requirements.txt
│
├── basic_agent.py
├── rbac.py
├── rbac_identity.py
├── rbac_audit.py
├── rbac_resources.py
├── abac.py
├── external_policy.py
│
├── policy.yaml
├── policy_engine.py
├── security_context.py
├── runtime.py
│
└── tests/
    ├── test_policy_engine.py
    └── test_tools.py
```

---

## 🧰 Technologies

* Python 3.12+
* [smolagents](https://github.com/huggingface/smolagents)
* Hugging Face Inference
* Qwen
* pytest
* YAML
* RBAC
* ABAC
* Policy Enforcement
* Security Context
* Audit Logging

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/Nabil-oussa/secure-ai-agent.git
cd secure-ai-agent
```

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## 🧪 Running the Tests

Run the complete test suite:

```bash
PYTHONPATH=. pytest -q
```

Or, when using the project's virtual environment directly:

```bash
PYTHONPATH=. ./venv/bin/pytest -q
```

Run the tool-level test manually:

```bash
PYTHONPATH=. python tests/test_tools.py
```

---

## 🤖 Running the Agent

The final implementation is available in:

```text
external_policy.py
```

The agent can be launched with:

```bash
python external_policy.py
```

The LLM-based execution requires an available Hugging Face inference provider and the appropriate credentials or access configuration.

> The automated security tests do not require LLM inference.

This distinction is intentional: **authorization logic should remain testable independently of the LLM.**

---

## 🔒 Security Principles Demonstrated

The project demonstrates several core security principles:

### Least Privilege

Agents receive only the permissions required for their role and resource scope.

### Defense in Depth

Security is enforced at multiple levels:

```text
Tool
 ↓
Path validation
 ↓
Identity
 ↓
Action
 ↓
Resource
 ↓
Attributes
 ↓
Policy
```

### Separation of Duties

The LLM is responsible for reasoning and proposing actions.

The policy layer is responsible for authorization.

The tool is responsible for executing the authorized operation.

### Fail Closed

If an identity, action, resource, or required attribute does not satisfy the policy, the operation is denied.

### Auditability

Authorization decisions are logged with:

```text
identity
action
resource
attributes
decision
```

---

## ⚠️ Current Limitations

This project is an educational security laboratory and should not be considered a production-ready authorization framework.

Current limitations include:

* The trusted runtime is simulated locally.
* Identity is currently configured by the runtime rather than obtained from a real Identity Provider.
* The policy engine is intentionally lightweight.
* Audit logs are currently written to stdout.
* No persistent audit backend is implemented.
* No cryptographic identity verification is implemented.
* No real OAuth2/OIDC or workload identity integration exists yet.
* LLM inference depends on an external inference provider.

These limitations are intentional and define the next stages of the project.

---

## 🔭 Roadmap

Possible future improvements include:

### Identity & IAM

* Trusted Identity Provider
* JWT-based identity
* OAuth2 / OIDC
* Short-lived credentials
* Workload identity
* Service-to-service authorization

### Policy & Authorization

* Policy versioning
* Policy decision logging
* Policy-as-Code
* Open Policy Agent (OPA)
* Risk-based authorization
* Dynamic policy evaluation

### AI Security

* Prompt injection resistance
* Tool poisoning protection
* Tool-level rate limiting
* Human-in-the-loop approval
* Agent-to-agent authorization
* MCP security
* Agent identity
* Agent capability control

### Cloud Security

* Kubernetes service identities
* Cloud IAM integration
* Secrets management
* KMS integration

### Cryptography

* PKI
* mTLS
* Certificate lifecycle management
* Post-Quantum Cryptography
* Hybrid classical/PQC authentication

---

## 🎓 Learning Goal

This project is part of a practical learning path toward:

```text
Agentic AI Security
        ↓
       IAM
        ↓
       PKI
        ↓
       KMS
        ↓
 Cloud Security
        ↓
Post-Quantum Cryptography
```

The main objective is to understand how traditional security principles such as **least privilege, identity, authorization, policy enforcement and auditability** can be applied to modern AI agent architectures.

---

## 📌 Status

**Educational / Experimental**

The project is actively evolving as a practical laboratory for:

**AI Security · IAM · Policy Enforcement · QA · Cloud Security · PKI · KMS · Post-Quantum Cryptography**
