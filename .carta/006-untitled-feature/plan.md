# Implementation Plan: Implementation Plan Flow

## Technical Context
- **Existing**: Python 3.11+, Textual TUI framework, OpenRouter/LM Studio LLM backend
- **Detected**: Screen-based navigation with typed results, Agent utility with tools, `.carta/` directory structure
- **Decisions**: New dedicated plan screens, HomeScreen + post-discovery prompt entry, numbered selection input, modal overwrite confirmation, phased plan structure

## Decision Exploration

| Decision | Selected | Rationale |
|----------|----------|-----------|
| Screen Architecture | Parallel plan screens | Clean separation allows plan-specific customization without polluting discovery screens with conditionals |
| Entry Point | HomeScreen + post-discovery | Supports all user scenarios: new users see menu, discovery completers get natural flow |
| Selection UX | Numbered text input | Matches existing wizard pattern, simpler to implement, adequate for typical feature counts |
| Overwrite Handling | Modal confirmation | Consistent with existing ConfirmQuitScreen pattern, emphasizes destructive action |
| Plan Structure | Phased approach | Clear timeline with phases, tasks, and dependencies provides actionable guidance |

## Solution Architecture

The implementation adds a planning workflow parallel to discovery, with a new HomeScreen as the app's entry point. When the app launches, users see a menu offering "Start Discovery" or "Create Plan" options. After completing a discovery document, users receive a prompt asking whether to continue with planning.

The planning flow consists of three dedicated screens: `PlanSelectScreen` for choosing an existing discovery document, `PlanWizardScreen` for answering implementation-focused questions, and `PlanDraftScreen` for reviewing and refining the generated plan. These screens follow the same patterns as their discovery counterparts but with plan-specific prompts and logic.

The plan generation agent reads the selected discovery.md file, asks clarifying questions about approach and priorities, then generates a phased implementation plan. If a plan.md already exists for the selected feature, a modal confirmation dialog appears before overwriting.

## Technology Decisions

- Textual Screen class with typed results for all new screens
- Existing Agent utility with `file_read`, `list_files`, `grep` tools for plan generation
- New prompt templates under `src/carta/prompts/plan/` directory
- Reuse existing widgets (PromptInput, AgentOutput) via AgentScreenMixin
- New ConfirmOverwriteScreen modal following ConfirmQuitScreen pattern

## Component Modifications

1. **CartaApp** (`src/carta/app/app.py`): Replace direct `_start_discovery_flow()` call with `HomeScreen` push; add planning flow callbacks; add post-discovery prompt logic
2. **types.py** (`src/carta/app/types.py`): Add `HomeResult`, `PlanSelectResult`, `PlanWizardResult`, `PlanDraftResult` dataclasses
3. **messages.py** (`src/carta/app/messages.py`): Add `FeatureSelected` message for plan selection
4. **DraftScreen** (`src/carta/app/screens/draft_screen.py`): After successful save, dismiss with flag indicating plan prompt should appear

## New Components

1. **HomeScreen** (`src/carta/app/screens/home_screen.py`): Entry menu with numbered options for discovery vs planning
2. **PlanSelectScreen** (`src/carta/app/screens/plan_select_screen.py`): Lists `.carta/` features, accepts numbered input to select discovery document
3. **PlanWizardScreen** (`src/carta/app/screens/plan_wizard_screen.py`): Q&A for implementation approach questions
4. **PlanDraftScreen** (`src/carta/app/screens/plan_draft_screen.py`): Display and refine generated plan with approval/feedback cycle
5. **ConfirmOverwriteScreen** (`src/carta/app/screens/modals/confirm_overwrite.py`): Modal confirmation for existing plan.md
6. **gather.md** (`src/carta/prompts/plan/gather.md`): Prompt for generating planning questions
7. **draft.md** (`src/carta/prompts/plan/draft.md`): Prompt for generating phased implementation plan
8. **refine.md** (`src/carta/prompts/plan/refine.md`): Prompt for refining plan based on feedback

## Task Sequence

### Phase 1: Foundation
1. Create `HomeResult` and plan-related result types in `types.py`
2. Create `HomeScreen` with discovery/plan menu options
3. Update `CartaApp.on_mount()` to push `HomeScreen` instead of `FeatureScreen`
4. Add `_on_home_done()` callback to route to discovery or planning flow

**Dependencies**: None

### Phase 2: Plan Selection
5. Create `FeatureSelected` message in `messages.py`
6. Create `PlanSelectScreen` that lists `.carta/` directories with discovery.md files
7. Add `_start_plan_flow()` method to `CartaApp`
8. Add `_on_plan_select_done()` callback

**Dependencies**: Phase 1

### Phase 3: Plan Prompts
9. Create `src/carta/prompts/plan/` directory structure
10. Create `gather.md` prompt for implementation questions (focus on phases, priorities, risks)
11. Create `draft.md` prompt for phased plan generation
12. Create `refine.md` prompt for plan refinement

**Dependencies**: None (can run parallel to Phase 2)

### Phase 4: Plan Generation Screens
13. Create `PlanWizardScreen` (mirrors WizardScreen with plan context)
14. Create `PlanDraftScreen` (mirrors DraftScreen, saves to plan.md)
15. Add `_on_plan_wizard_done()` and `_on_plan_draft_done()` callbacks to `CartaApp`

**Dependencies**: Phase 2, Phase 3

### Phase 5: Overwrite Protection
16. Create `ConfirmOverwriteScreen` modal
17. Add overwrite check logic to `PlanDraftScreen` before saving
18. Integrate modal callback to proceed or cancel save

**Dependencies**: Phase 4

### Phase 6: Post-Discovery Integration
19. Modify `DraftResult` to include `prompt_for_plan: bool` flag
20. Update `DraftScreen` to set flag after successful discovery save
21. Update `_on_draft_done()` to show plan prompt when flag is set
22. Add transition from post-discovery prompt to `PlanSelectScreen` (pre-selecting the just-completed feature)

**Dependencies**: Phase 4

## Integration Points

- **Agent utility**: Plan screens use same `Agent` class with identical tool set; no changes needed
- **Filename utilities**: Reuse `get_next_sequence_number()` and directory scanning for feature listing
- **Styles**: New screens inherit from existing `styles.tcss`; may need minor additions for home menu
- **Widgets**: `AgentScreenMixin`, `PromptInput`, `AgentOutput` reused without modification

## Testing Strategy

- **Unit**: Result dataclass construction, feature directory scanning, plan.md existence checking
- **Integration**: Screen transitions (Home→Select→Wizard→Draft), callback routing, file save operations
- **E2E**: Complete planning flow from home screen, post-discovery prompt flow, overwrite confirmation flow
- **Edge**: No features exist in `.carta/`, malformed discovery.md, empty feedback during refinement

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Screen duplication leads to maintenance burden | Extract shared logic into mixins; consider future refactor to parameterized screens |
| Plan prompts produce low-quality output | Iterate on prompt engineering; include examples in prompt templates |
| Users confused by two entry points | Clear labeling in HomeScreen; help text explaining discovery vs planning |
| Feature selection awkward with many items | Accept numbered input pattern for now; note fuzzy search as future enhancement |
