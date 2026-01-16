# Phase 2: Tool System

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
