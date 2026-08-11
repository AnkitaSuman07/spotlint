
# spotlint

### Static analysis for agentic software.

spotlint is a local-first static analyzer for Python applications that use **AI agents, LLMs, tools, and agentic workflows**.

Agentic applications introduce execution patterns that traditional linters and static-analysis tools were not designed to reason about: repeated agent execution, tool reachability, uncontrolled execution paths, and missing execution boundaries.

spotlint Beta provides an initial, deterministic analysis layer for identifying these patterns during development and CI.

> ⚠️ **spotlint is currently in beta.** Findings are experimental and should not be interpreted as proof that an application is secure or safe.

---

## Why spotlint?

Traditional static analysis is built around conventional software constructs:

```text
Source Code
    │
    ▼
AST / CFG
    │
    ▼
Rules
    │
    ▼
Findings
```

Agentic applications introduce additional execution semantics:

```text
                    Agent
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
         LLM         Tools       Memory
                      │
               ┌──────┼──────┐
               ▼      ▼      ▼
              API    SQL   Files
```

An agent may dynamically decide:

* which tool to call
* how many times to call it
* which execution path to follow
* whether to invoke another agent
* which external capability to access

spotlint's goal is to make potentially risky execution patterns visible **before the application runs**.

---

# Beta Philosophy

spotlint Beta follows four principles.

### Local-first

Analysis runs locally against the developer's source code.

### No source upload

spotlint does not require source code to be sent to a spotlint server.

### No LLM required

The beta analyzer uses deterministic static analysis. An LLM is not required to generate findings.

### CI-friendly

spotlint is designed to work locally and in automated development pipelines.

---

# Current Status

| Capability                   | Beta |
| ---------------------------- | ---- |
| Python analysis              | ✅    |
| AST-based analysis           | ✅    |
| Agent/tool pattern detection | ✅    |
| Deterministic analysis       | ✅    |
| Local execution              | ✅    |
| Text output                  | ✅    |
| JSON output                  | ✅    |
| SARIF output                 | ✅    |
| CLI                          | ✅    |
| LLM required                 | ❌    |
| Cloud service required       | ❌    |

**Version:** `0.1.0-beta`

**Status:** Experimental developer release

---

# Installation

Clone the repository:

```bash
git clone <repository-url>
cd spotlint
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Install spotlint:

```bash
pip install -e ".[dev]"
```

Verify the installation:

```bash
spotlint --help
```

---

# Quick Start

Scan a Python file:

```bash
spotlint check test_agent.py
```

Scan a project:

```bash
spotlint check .
```

Example:

```text
sp001 HIGH
  test_agent.py:5:5

  Unbounded agent/tool execution loop detected.

  Evidence:
    while True:

  Why:
    An unconditional loop contains agent or tool
    execution without a statically visible bound.

  Recommendation:
    Add an iteration limit, timeout, cancellation
    condition, or explicit execution boundary.
```

---

# Example

Given:

```python
def run_agent():
    while True:
        agent.run()
        execute_tool("search")
```

spotlint may report:

```text
sp001 HIGH
  test_agent.py:2:5

  Unbounded agent/tool execution loop detected.

  Evidence:
    while True:

  Recommendation:
    Add an execution limit, timeout, cancellation
    condition, or explicit termination policy.
```

The purpose is not to claim that the code is definitely vulnerable.

The purpose is to highlight an execution pattern that deserves developer review.

---

# Beta Rules

spotlint Beta contains five initial experimental rules.

The rules are intentionally conservative in scope. They will evolve as we collect real-world examples and measure false positives and false negatives.

---

## sp001 — Unbounded Agent Execution

**Severity:** HIGH

Detects unconditional loops containing patterns associated with agent or tool execution.

Example:

```python
while True:
    agent.run()
```

Potential concerns include:

* runaway execution
* unexpected API usage
* excessive token consumption
* resource exhaustion
* workflows that are difficult to terminate

A bounded execution model is preferable:

```python
for _ in range(MAX_STEPS):
    agent.run()
```

Or use an explicit timeout, deadline, cancellation mechanism, or execution budget.

---

## sp002 — Uncontrolled Tool Invocation

**Severity:** HIGH

Identifies tool invocation patterns without an obvious local failure boundary.

Example:

```python
result = execute_tool(user_input)
```

Tool execution can fail because of:

* network failures
* invalid input
* authorization failures
* service errors
* timeouts
* malformed responses

Where appropriate, applications should establish explicit failure handling:

```python
try:
    result = execute_tool(user_input)
except ToolError as exc:
    handle_tool_failure(exc)
```

> This rule is a static signal, not proof that error handling is absent from the complete runtime path.

---

## sp003 — Dangerous Tool Reachability

**Severity:** HIGH

Identifies patterns associated with high-impact capabilities.

Examples include operations involving:

```text
SQL
Shell / command execution
Filesystem writes
Filesystem deletion
External network access
```

For example:

```python
execute_sql(query)
```

or:

```python
run_command(command)
```

These capabilities can be legitimate and necessary.

spotlint's goal is to make them visible for review rather than automatically declaring them unsafe.

A future version will provide more precise capability and policy analysis.

---

## sp004 — Cascading Agent Execution

**Severity:** HIGH

Identifies patterns involving multiple agent executions within a workflow or function.

Example:

```python
def workflow():
    agent.run()
    agent.run()
```

Multiple agent calls are not inherently unsafe.

The beta rule is intended as an initial signal for workflows that may involve cascading or repeated agent execution.

Future versions will use richer call-graph and control-flow analysis to distinguish simple sequential calls from actual recursive or cyclic execution paths.

---

## sp005 — Missing Execution Boundary

**Severity:** MEDIUM

Identifies agent execution where an explicit execution boundary is not statically visible.

Example:

```python
agent.run()
```

Execution boundaries may include:

```text
Maximum steps
Maximum iterations
Timeout
Deadline
Cancellation
Recursion depth
Execution budget
```

For example:

```python
agent.run(
    max_steps=10,
    timeout=30,
)
```

The beta implementation provides an initial static signal. Framework-specific analysis will improve the precision of this rule over time.

---

# CLI

## Basic scan

```bash
spotlint check .
```

## Scan one file

```bash
spotlint check test_agent.py
```

## Select a rule

```bash
spotlint check . --rule sp001
```

Multiple rules:

```bash
spotlint check . --rule sp001,sp003
```

## Severity filtering

```bash
spotlint check . --severity HIGH
```

Supported severities:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

# Output Formats

## Terminal

Default output:

```bash
spotlint check .
```

Designed for developers running spotlint locally.

---

## JSON

```bash
spotlint check . --format json
```

JSON is intended for automation and integration with other development tools.

Example structure:

```json
{
  "version": "0.1",
  "findings": [
    {
      "rule_id": "sp001",
      "severity": "HIGH",
      "message": "Unbounded agent/tool execution loop detected."
    }
  ]
}
```

---

## SARIF

```bash
spotlint check . --format sarif --output spotlint.sarif
```

SARIF is intended for integration with code-scanning and CI systems.

---

# Exit Codes

spotlint is designed to work in CI/CD pipelines.

```text
0   No findings at or above the configured severity
1   Findings detected
2   spotlint execution/configuration error
```

Example:

```bash
spotlint check . --severity HIGH
```

This allows a pipeline to enforce a policy such as:

```text
                 Pull Request
                       │
                       ▼
                  spotlint
                       │
              ┌────────┴────────┐
              ▼                 ▼
             PASS              FAIL
              │                 │
              ▼                 ▼
           Continue          Review
```

---

# Architecture

The current beta intentionally keeps the analysis pipeline simple:

```text
Python Source
      │
      ▼
 Python AST
      │
      ▼
Analysis Context
      │
      ▼
  Rule Engine
      │
      ▼
   Findings
      │
 ┌────┼────┐
 ▼    ▼    ▼
Text JSON SARIF
```

The architecture is designed to evolve toward deeper semantic analysis without requiring a complete rewrite.

The longer-term direction is:

```text
Source
  │
  ▼
AST
  │
  ▼
Symbol / Call Analysis
  │
  ▼
Control Flow
  │
  ▼
Agent Semantics
  │
  ▼
Capability Analysis
  │
  ▼
Policy Analysis
```

---

# Design Principles

## Deterministic analysis

The same source should produce the same result.

spotlint Beta does not depend on an LLM to determine whether a finding should be reported.

---

## Evidence-based findings

A finding should identify:

```text
Rule
Severity
File
Location
Evidence
Explanation
Recommendation
```

spotlint should avoid vague messages such as:

```text
"This code might be dangerous."
```

Instead, findings should explain **why the code was flagged**.

---

## Minimize false positives

Static-analysis tools are only useful when developers trust their findings.

spotlint therefore treats precision as a core product metric.

Each rule should have:

* positive fixtures
* negative fixtures
* edge cases
* false-positive analysis

---

## Framework-aware over time

The initial beta intentionally avoids depending on a single agent framework.

Future versions may add semantic support for ecosystems such as:

* LangGraph
* LangChain
* MCP-based applications
* OpenAI agent patterns
* custom agent frameworks

Framework integrations should extend spotlint's analysis model rather than define it.

---

# What spotlint Does Not Do

spotlint Beta does **not**:

* execute your application
* execute your agent
* simulate an LLM
* guarantee application security
* prove an agent is safe
* replace conventional SAST
* replace dependency scanning
* replace code review
* understand every Python framework
* determine whether an LLM response is factually correct

A clean spotlint scan means only that the implemented beta rules did not identify the patterns they are designed to detect.

---

# Testing

Run the test suite:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Rule tests should contain both positive and negative cases.

Example:

```text
tests/
├── test_sp001.py
├── test_sp002.py
├── test_sp003.py
├── test_sp004.py
└── test_sp005.py
```

A rule is not considered reliable simply because it detects a positive example.

It must also avoid flagging legitimate code unnecessarily.

---

# Repository Structure

```text
spotlint/
│
├── README.md
├── LICENSE
├── pyproject.toml
│
├── src/
│   └── spotlint/
│       │
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       │
│       ├── analysis/
│       │   ├── __init__.py
│       │   └── engine.py
│       │
│       ├── model/
│       │   ├── __init__.py
│       │   ├── context.py
│       │   └── finding.py
│       │
│       ├── rules/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── helpers.py
│       │   ├── registry.py
│       │   ├── sp001.py
│       │   ├── sp002.py
│       │   ├── sp003.py
│       │   ├── sp004.py
│       │   └── sp005.py
│       │
│       └── reporters/
│           ├── __init__.py
│           ├── text.py
│           ├── json.py
│           └── sarif.py
│
└── tests/
```

---

# Roadmap

spotlint Beta is focused on validating the core idea:

> Can static analysis provide useful, actionable signals for agentic software?

The roadmap will evolve based on developer feedback.

### Near term

```text
Improve rule precision
Improve Python analysis
Expand test corpus
Measure false positives
Improve CLI experience
Improve CI integration
```

### Future

```text
Call-graph analysis
Control-flow analysis
Framework-aware analysis
Agent execution modeling
Capability discovery
Policy analysis
```

One potential long-term direction is an **Agent Capability Graph** that can answer:

> What capabilities are reachable from this agent?

For example:

```text
Agent
 │
 ├── LLM
 │
 ├── Tool
 │    ├── HTTP
 │    ├── SQL
 │    └── Filesystem
 │
 └── Memory
```

This is a future direction, not a capability claim for the current beta.

---

# Contributing

spotlint is currently in beta and feedback is especially valuable.

Useful contributions include:

* real-world agent examples
* false-positive reports
* false-negative reports
* rule improvements
* test fixtures
* framework examples
* performance benchmarks
* documentation improvements

When proposing a rule, provide:

1. Rule ID
2. Problem statement
3. Positive example
4. Negative example
5. Expected severity
6. Explanation
7. Recommendation
8. False-positive considerations

---

# Reporting Issues

When reporting an issue, include:

```text
spotlint version:
Python version:
Operating system:
Rule:
Input pattern:
Expected result:
Actual result:
```

Please remove:

* API keys
* passwords
* tokens
* credentials
* proprietary source code
* personal information

before submitting examples.

---

# Security

If you believe you have discovered a security issue in spotlint itself, please follow the repository's security reporting process rather than publicly posting sensitive details.

A dedicated `SECURITY.md` should be added before the first stable release.

---

# License

Apache License 2.0.

See `LICENSE` for the full license text.

---

# Project Status

**spotlint `v0.1.0-beta`**

Experimental developer release.

The goal of this beta is not to claim that agentic software can already be completely analyzed.

The goal is to establish whether **static analysis can become a useful engineering layer for agentic software**.

> **Understand the flow before you run the agent.**
