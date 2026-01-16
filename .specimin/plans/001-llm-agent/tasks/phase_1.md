# Phase 1: Foundation

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
