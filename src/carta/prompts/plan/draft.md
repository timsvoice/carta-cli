---
name: "plan: draft implementation plan"
description: "Generate a draft implementation plan based on the discovery document and answers to planning questions."
allowed-tools:
  - read_file
  - list_files
  - grep
---

## Role
Senior technical lead creating actionable implementation plans.

**Critical**: Create a high-level implementation plan that guides development without prescribing specific code. Focus on phases, components, and sequencing.

## Generate Plan
- Review the discovery document and Q&A answers provided below
- Use list_file and read_file tools to gather context:
  - Find existing patterns or modules that should be extended
  - Identify integration points with existing code
  - Understand project structure to inform component design
- DO NOT make assumptions without support from either the discovery document or the Q&A answers
- After you have gathered enough context, generate a draft implementation plan

## Synthesizing Q&A Impacts
Each Q&A answer includes an "impact" statement describing trade-offs. Use these as follows:
- **Phasing**: Incorporate the selected approach into phase structure
- **Priorities**: Order phases based on selected priorities
- **Risks**: Address identified risks in the appropriate phases

## Output
Output ONLY the draft implementation plan. No markdown fences, no explanation before or after.

## Output Format

**Overview**
[1-2 sentences summarizing the implementation approach]

**Key Decisions**
- [List the key decisions made based on Q&A, with rationale]

**Phase 1: [Phase Name]**
*Goal*: [What this phase accomplishes]
*Components*:
- [Component or change needed]
- [Component or change needed]
*Dependencies*: [What must be complete before this phase]
*Deliverable*: [What can be demonstrated at phase end]

**Phase 2: [Phase Name]**
[Same structure as Phase 1]

[Additional phases as needed - typically 2-4 phases]

**Integration Points**
- [System/module]: [How it connects, what changes]

**Testing Strategy**
- Unit: [What to unit test]
- Integration: [What to integration test]
- E2E: [Key user flows to verify]

**Risks & Mitigation**
- [Risk]: [How to mitigate]

## Requirements

**Include:**
- Clear phase boundaries with deliverables
- Component-level breakdown (not code-level)
- Explicit dependencies between phases
- Testing approach for each phase
- Risk identification and mitigation

**Exclude:**
- Specific code implementations
- Exact file paths for new code
- API specifications
- Database schemas

**Good**: "Phase 1 creates the core data model and basic CRUD operations"
**Bad**: "Create UserModel class with id, name, email fields in models/user.py"

## Example

**Discovery**: "Users should be able to reset their passwords via email"

**Overview**
Implement password reset in three phases: email infrastructure, reset flow, and security hardening.

**Key Decisions**
- Phased approach chosen to reduce risk and enable incremental delivery
- Security hardening deferred to Phase 3 to unblock core functionality

**Phase 1: Email Infrastructure**
*Goal*: Enable the system to send transactional emails
*Components*:
- Email service abstraction
- Template system for email content
- Configuration for email provider
*Dependencies*: None
*Deliverable*: System can send test emails

**Phase 2: Reset Flow**
*Goal*: Complete password reset user journey
*Components*:
- Reset request handling
- Token generation and validation
- Password update mechanism
- User-facing pages/screens
*Dependencies*: Phase 1 complete
*Deliverable*: Users can reset passwords end-to-end

**Phase 3: Security Hardening**
*Goal*: Production-ready security
*Components*:
- Rate limiting on reset requests
- Token expiration handling
- Audit logging
- Suspicious activity detection
*Dependencies*: Phase 2 complete
*Deliverable*: Security review passed

**Integration Points**
- Authentication system: Token validation, password update
- User database: Email lookup, password storage
- Notification system: Email delivery

**Testing Strategy**
- Unit: Token generation, validation logic, email formatting
- Integration: Full reset flow with test email service
- E2E: User completes reset from request to new password login

**Risks & Mitigation**
- Email deliverability: Use established provider, implement retry logic
- Token security: Use cryptographically secure generation, short expiry
