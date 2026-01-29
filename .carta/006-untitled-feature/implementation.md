# Implementation Tasks: Implementation Plan Flow

**Overview**: Add a planning workflow parallel to discovery with HomeScreen entry point, plan selection, wizard Q&A, and draft generation with overwrite protection.
**Total Tasks**: 52 | **Phases**: 6 | **Parallel Opportunities**: 12

---

## Phase 1: Foundation
**Dependencies**: None
**Parallel Opportunities**: 2

- [ ] T001 Write test for HomeResult dataclass expecting status field in tests/app/test_types.py (R01)
- [ ] T002 Run test and confirm RED (HomeResult undefined)
- [ ] T003 Add HomeResult dataclass to src/carta/app/types.py (R01)
- [ ] T004 Run test and confirm GREEN
- [ ] T005 [P] Write test for PlanSelectResult dataclass expecting feature_path field in tests/app/test_types.py (R01)
- [ ] T006 [P] Write test for PlanWizardResult dataclass expecting answers field in tests/app/test_types.py (R01)
- [ ] T007 Run tests and confirm RED (dataclasses undefined)
- [ ] T008 Add PlanSelectResult, PlanWizardResult, PlanDraftResult dataclasses to src/carta/app/types.py (R01)
- [ ] T009 Run tests and confirm GREEN
- [ ] T010 Create HomeScreen with numbered menu options in src/carta/app/screens/home_screen.py (R02)
- [ ] T011 Update screens __init__.py to export HomeScreen in src/carta/app/screens/__init__.py (R02)
- [ ] T012 Update CartaApp.on_mount() to push HomeScreen instead of FeatureScreen in src/carta/app/app.py (R02)
- [ ] T013 Add _on_home_done() callback with routing logic to src/carta/app/app.py (R02)
- [ ] T014 Verify app launches with HomeScreen showing discovery/plan options

---

## Phase 2: Plan Selection
**Dependencies**: Phase 1 complete
**Parallel Opportunities**: 1

- [ ] T015 Add FeatureSelected message to src/carta/app/messages.py (R03)
- [ ] T016 Write test for list_feature_directories utility expecting list of paths in tests/utils/test_filename.py (R04)
- [ ] T017 Run test and confirm RED (function undefined)
- [ ] T018 Add list_feature_directories() function to src/carta/utils/filename.py (R04)
- [ ] T019 Run test and confirm GREEN
- [ ] T020 Create PlanSelectScreen with numbered feature list in src/carta/app/screens/plan_select_screen.py (R04)
- [ ] T021 Update screens __init__.py to export PlanSelectScreen (R04)
- [ ] T022 Add _start_plan_flow() method to CartaApp in src/carta/app/app.py (R04)
- [ ] T023 Add _on_plan_select_done() callback to CartaApp in src/carta/app/app.py (R04)
- [ ] T024 Verify plan selection flow shows features and accepts numbered input

---

## Phase 3: Plan Prompts
**Dependencies**: None (parallel to Phase 2)
**Parallel Opportunities**: 3

- [ ] T025 [P] Create src/carta/prompts/plan/ directory structure
- [ ] T026 [P] Create gather.md prompt for implementation questions in src/carta/prompts/plan/gather.md (R05)
- [ ] T027 [P] Create draft.md prompt for phased plan generation in src/carta/prompts/plan/draft.md (R05)
- [ ] T028 [P] Create refine.md prompt for plan refinement in src/carta/prompts/plan/refine.md (R05)
- [ ] T029 Verify prompts load without errors via Agent utility

---

## Phase 4: Plan Generation Screens
**Dependencies**: Phase 2, Phase 3 complete
**Parallel Opportunities**: 2

- [ ] T030 Create PlanWizardScreen mirroring WizardScreen in src/carta/app/screens/plan_wizard_screen.py (R06)
- [ ] T031 Update screens __init__.py to export PlanWizardScreen (R06)
- [ ] T032 Add _on_plan_wizard_done() callback to CartaApp in src/carta/app/app.py (R06)
- [ ] T033 [P] Create PlanDraftScreen mirroring DraftScreen in src/carta/app/screens/plan_draft_screen.py (R07)
- [ ] T034 [P] Update screens __init__.py to export PlanDraftScreen (R07)
- [ ] T035 Add _on_plan_draft_done() callback to CartaApp in src/carta/app/app.py (R07)
- [ ] T036 Update PlanDraftScreen._save_draft() to write plan.md instead of creating new directory (R07)
- [ ] T037 Verify complete plan generation flow from selection through approval

---

## Phase 5: Overwrite Protection
**Dependencies**: Phase 4 complete
**Parallel Opportunities**: 0

- [ ] T038 Create ConfirmOverwriteScreen modal in src/carta/app/screens/modals/confirm_overwrite.py (R08)
- [ ] T039 Update modals __init__.py to export ConfirmOverwriteScreen (R08)
- [ ] T040 Write test for plan_exists() utility expecting boolean in tests/utils/test_filename.py (R08)
- [ ] T041 Run test and confirm RED (function undefined)
- [ ] T042 Add plan_exists() function to src/carta/utils/filename.py (R08)
- [ ] T043 Run test and confirm GREEN
- [ ] T044 Add overwrite check logic to PlanDraftScreen._save_draft() in src/carta/app/screens/plan_draft_screen.py (R08)
- [ ] T045 Integrate ConfirmOverwriteScreen callback to proceed or cancel save (R08)
- [ ] T046 Verify overwrite confirmation appears when plan.md exists

---

## Phase 6: Post-Discovery Integration
**Dependencies**: Phase 4 complete
**Parallel Opportunities**: 2

- [ ] T047 [P] Modify DraftResult to include prompt_for_plan and feature_path fields in src/carta/app/types.py (R09)
- [ ] T048 [P] Update DraftScreen._save_draft() to set prompt_for_plan=True after successful save in src/carta/app/screens/draft_screen.py (R09)
- [ ] T049 Create ConfirmPlanPromptScreen modal for post-discovery prompt in src/carta/app/screens/modals/confirm_plan_prompt.py (R09)
- [ ] T050 Update modals __init__.py to export ConfirmPlanPromptScreen (R09)
- [ ] T051 Update _on_draft_done() to show plan prompt when flag is set in src/carta/app/app.py (R09)
- [ ] T052 Add transition from post-discovery prompt to PlanSelectScreen with pre-selected feature in src/carta/app/app.py (R09)

---

## Spec Requirement Mapping
- R01 (Result types): Tasks T001-T009
- R02 (HomeScreen entry): Tasks T010-T014
- R03 (Messages): Task T015
- R04 (Plan selection): Tasks T016-T024
- R05 (Plan prompts): Tasks T025-T029
- R06 (PlanWizardScreen): Tasks T030-T032
- R07 (PlanDraftScreen): Tasks T033-T037
- R08 (Overwrite protection): Tasks T038-T046
- R09 (Post-discovery integration): Tasks T047-T052

---

## Critical Dependencies
- Phase 1 must complete before Phase 2 (HomeScreen routing needed)
- Phase 2 and Phase 3 can run in parallel
- Phase 4 requires both Phase 2 and Phase 3
- Phase 5 and Phase 6 can run in parallel after Phase 4

---

## Notes
- PlanWizardScreen receives discovery.md content instead of feature description
- PlanDraftScreen writes to existing feature directory's plan.md, not creating new directory
- HomeScreen uses same numbered input pattern as WizardScreen for consistency
- Plan prompts focus on implementation approach (phases, priorities, risks) vs discovery prompts (requirements, scope)
