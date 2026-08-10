# JWT refresh-token plan

## OBJECTIVE

Add refresh-token behavior without weakening the existing access-token boundary.

## SCOPE

Name exact auth handlers, token services, persistence paths, and exclusive Backend Worker ownership.

## INPUT EVIDENCE

Record current authentication flow, token claims, persistence behavior, and relevant checks.

## REQUIRED BEHAVIOR

Define issuance, rotation, revocation, expiry, replay handling, and error behavior.

## CONSTRAINTS

Preserve repository conventions, compatibility requirements, and least privilege.

## MUST PRESERVE

Preserve current access-token validation and authorization boundaries.

## MUST NOT CHANGE

Do not broaden unrelated endpoints, dependencies, infrastructure, or external state.

## ACCEPTANCE CRITERIA

Trace each requirement to the final diff and objective validation evidence.

## ESCALATION CONDITIONS

Stop for ambiguous token semantics, missing migration authority, or an unsafe trust-boundary change.

## EXPECTED OUTPUT

Return decisions, changed files, checks, security findings, missing evidence, and final verdict.
