# Implementation Tasks: LLM Agent

**Overview**: Internal LLM agent module with OpenRouter API integration and tool execution capabilities.
**Total Tasks**: 54 | **Phases**: 3 | **Estimated Completion**: Medium complexity

---

## Phase 1: Foundation
**Dependencies**: None
**Parallel Opportunities**: 2

- [ ] T001 [P] Add httpx dependency to pyproject.toml (R01)
- [ ] T002 [P] Create agent module skeleton with logging setup in src/carta/agent.py (R09)
- [ ] T003 Write test for missing API key raising ConfigurationError in tests/test_agent.py (R08)
- [ ] T004 Run test and confirm RED (ConfigurationError not defined)
- [ ] T005 Implement API key loading with ConfigurationError in src/carta/agent.py (R08)
- [ ] T006 Run test and confirm GREEN
- [ ] T007 Write test for basic prompt returning structured response in tests/test_agent.py (R01, R06)
- [ ] T008 Run test and confirm RED (run() not implemented)
- [ ] T009 Implement run() with OpenRouter API call in src/carta/agent.py (R01)
- [ ] T010 Run test and confirm GREEN
- [ ] T011 Write test for custom model and parameters (temperature, max_tokens) in tests/test_agent.py (R02)
- [ ] T012 Run test and confirm RED (parameters not passed)
- [ ] T013 Add model and LLM parameter support to run() in src/carta/agent.py (R02)
- [ ] T014 Run test and confirm GREEN
- [ ] T015 Write test for retry on 429/5xx with exponential backoff in tests/test_agent.py (R07)
- [ ] T016 Run test and confirm RED (retry not implemented)
- [ ] T017 Implement retry logic with exponential backoff (1s, 2s, 4s) in src/carta/agent.py (R07)
- [ ] T018 Run test and confirm GREEN

---

## Phase 2: Tool System
**Dependencies**: Phase 1 complete
**Parallel Opportunities**: 3

- [ ] T019 [P] Define tool schemas (file_read, file_write, shell_exec) in src/carta/agent.py (R03, R04, R05)
- [ ] T020 [P] Implement allowlist validation (ls, cat, grep, find) in src/carta/agent.py (R05)
- [ ] T021 [P] Implement working directory restriction in src/carta/agent.py (R03, R04, R05)
- [ ] T022 Write test for file_read tool execution in tests/test_agent.py (R03)
- [ ] T023 Run test and confirm RED (tool execution not implemented)
- [ ] T024 Implement file_read tool executor in src/carta/agent.py (R03)
- [ ] T025 Run test and confirm GREEN
- [ ] T026 Write test for file_write tool execution in tests/test_agent.py (R04)
- [ ] T027 Run test and confirm RED
- [ ] T028 Implement file_write tool executor in src/carta/agent.py (R04)
- [ ] T029 Run test and confirm GREEN
- [ ] T030 Write test for shell_exec with allowlist enforcement in tests/test_agent.py (R05)
- [ ] T031 Run test and confirm RED
- [ ] T032 Implement shell_exec tool executor with allowlist in src/carta/agent.py (R05)
- [ ] T033 Run test and confirm GREEN
- [ ] T034 Write test for tool loop (model requests tool → execute → return to model) in tests/test_agent.py (R01)
- [ ] T035 Run test and confirm RED
- [ ] T036 Implement tool execution loop in run() in src/carta/agent.py (R01)
- [ ] T037 Run test and confirm GREEN

---

## Phase 3: Integration & Polish
**Dependencies**: Phase 2 complete
**Parallel Opportunities**: 2

- [ ] T038 Write test for path traversal rejection in tests/test_agent.py (R03, R04)
- [ ] T039 Run test and confirm RED
- [ ] T040 Add path traversal validation to file tools in src/carta/agent.py (R03, R04)
- [ ] T041 Run test and confirm GREEN
- [ ] T042 Write test for disallowed shell command rejection in tests/test_agent.py (R05)
- [ ] T043 Run test and confirm RED
- [ ] T044 Add disallowed command error handling in src/carta/agent.py (R05)
- [ ] T045 Run test and confirm GREEN
- [ ] T046 [P] Write test for token usage logging in tests/test_agent.py (R09)
- [ ] T047 [P] Write test for cost estimate in response in tests/test_agent.py (R06)
- [ ] T048 Run tests and confirm RED
- [ ] T049 Implement token/cost logging and response fields in src/carta/agent.py (R06, R09)
- [ ] T050 Run tests and confirm GREEN
- [ ] T051 Write test for network timeout handling in tests/test_agent.py (R07)
- [ ] T052 Run test and confirm RED
- [ ] T053 Add timeout configuration and error handling in src/carta/agent.py (R07)
- [ ] T054 Run test and confirm GREEN

---

## Spec Requirement Mapping
- R01: Tasks T007-T010, T034-T037
- R02: Tasks T011-T014
- R03: Tasks T019, T021-T025, T038-T041
- R04: Tasks T019, T021, T026-T029, T038-T041
- R05: Tasks T019-T021, T030-T033, T042-T045
- R06: Tasks T007, T047, T049
- R07: Tasks T015-T018, T051-T054
- R08: Tasks T003-T006
- R09: Tasks T002, T046, T049

---

## Critical Dependencies
- T001 (httpx) blocks all API-related tasks
- T005 (API key loading) blocks T009 (run implementation)
- T019-T021 (tool schemas/validation) block T024, T028, T032 (tool executors)
- T036 (tool loop) required before Phase 3 edge case tests

---

## Notes
- Default model: `openai/gpt-4o-mini` when not specified
- Shell allowlist: `ls`, `cat`, `grep`, `find` (read-only)
- All file/shell operations restricted to working directory
- Mock httpx in tests to avoid real API calls
- Cost estimate derived from token count x model pricing (may need OpenRouter pricing lookup)
