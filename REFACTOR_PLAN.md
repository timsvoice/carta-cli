# Carta-CLI Architecture Refactoring Plan

## Overview

Migrate Carta-CLI from a custom handler-based architecture to canonical Textual patterns (Screen-based navigation, custom widgets, message-based events).

**Current State:** Single app layout with handler state machine
**Target State:** Screen stack navigation with custom widgets and Textual messages

---

## Phase 1: Foundation & Entry Point

**Goal:** Establish proper project structure and entry point without changing behavior.

### Tasks

1. **Create `__main__.py`** (new file)
   - Move `main()` function from `app.py` to `__main__.py`
   - Standard CLI entry pattern: `python -m carta`

2. **Create directory structure**
   ```
   src/carta/app/
   ├── screens/          # (new)
   ├── widgets/          # (new)
   └── messages.py       # (new)
   ```

3. **Add global keybindings to CartaApp**
   - `BINDINGS` class attribute
   - `q` / `ctrl+c` → quit with confirmation
   - `?` → help screen (placeholder)

4. **Upgrade to SCSS** (optional)
   - Rename `styles.tcss` → `styles.scss`
   - Update `CSS_PATH` reference

### Files to Modify
- `src/carta/app/app.py` - Extract main(), add BINDINGS
- `src/carta/app/__main__.py` - New file

### Success Criteria
- [ ] `python -m carta` launches app
- [ ] `carta` CLI command still works
- [ ] Pressing `?` shows "Help coming soon" notification
- [ ] Pressing `q` triggers quit (or confirmation)

---

## Phase 2: Screen Infrastructure

**Goal:** Introduce Screen base classes and navigation patterns while keeping handlers functional.

### Tasks

1. **Create `BaseScreen` abstract class**
   - `src/carta/app/screens/base.py`
   - Common patterns: loading indicator, output writing
   - Abstract method stubs for subclasses

2. **Create `FeatureScreen`** (first screen migration)
   - `src/carta/app/screens/feature_screen.py`
   - Move `FeatureHandler` logic into screen
   - Use `compose()` to define screen-specific layout
   - Use `@work(thread=True)` instead of manual threading
   - Screen dismisses with `FeatureResult`

3. **Update CartaApp to use screen navigation**
   - `on_mount()` → `push_screen(FeatureScreen())`
   - Handle screen dismiss results
   - Remove handler infrastructure temporarily

4. **Define custom messages**
   - `src/carta/app/messages.py`
   - `AgentProgress(Message)` - tool call feedback
   - `AgentComplete(Message)` - agent finished

### Files to Modify
- `src/carta/app/app.py` - Screen navigation
- `src/carta/app/screens/__init__.py` - New
- `src/carta/app/screens/base.py` - New
- `src/carta/app/screens/feature_screen.py` - New (from handler)
- `src/carta/app/messages.py` - New

### Success Criteria
- [ ] App launches to FeatureScreen
- [ ] Feature description submission works
- [ ] Agent runs with `@work` decorator
- [ ] Loading indicator shows during agent work
- [ ] Screen dismisses with result on completion

---

## Phase 3: Complete Screen Migration

**Goal:** Convert remaining handlers to screens, establishing full screen-based workflow.

### Tasks

1. **Create `WizardScreen`**
   - `src/carta/app/screens/wizard_screen.py`
   - Receives questions from FeatureScreen result
   - Manages question navigation state
   - Dismisses with `WizardResult`

2. **Create `DraftScreen`**
   - `src/carta/app/screens/draft_screen.py`
   - Receives feature + answers from previous screens
   - Handles draft display, refinement cycle, approval
   - Dismisses with `DraftResult`

3. **Wire screen transitions in CartaApp**
   ```python
   def on_mount(self):
       self.push_screen(FeatureScreen(), callback=self._on_feature_done)

   def _on_feature_done(self, result: FeatureResult):
       if result.status == "success":
           self.push_screen(WizardScreen(result.questions), callback=self._on_wizard_done)
   ```

4. **Remove old handler infrastructure**
   - Delete `src/carta/app/handlers/` directory
   - Remove handler-related code from app.py

### Files to Modify
- `src/carta/app/screens/wizard_screen.py` - New (from handler)
- `src/carta/app/screens/draft_screen.py` - New (from handler)
- `src/carta/app/app.py` - Screen transition logic
- `src/carta/app/handlers/` - Delete entire directory

### Success Criteria
- [ ] Full workflow works: Feature → Wizard → Draft → Save
- [ ] Screen transitions use `push_screen()` with callbacks
- [ ] "Restart" creates fresh screen stack
- [ ] No handler code remains

---

## Phase 4: Custom Widget Extraction

**Goal:** Extract reusable widgets from screens for better composition and testability.

### Tasks

1. **Create `QuestionSelector` widget**
   - `src/carta/app/widgets/question_selector.py`
   - Extends `OptionList` or custom `Widget`
   - Displays question with numbered options
   - Shows progress bar
   - Emits `QuestionAnswered(Message)` on selection

2. **Create `DraftViewer` widget**
   - `src/carta/app/widgets/draft_viewer.py`
   - Displays markdown draft
   - Shows action options (approve/refine/restart)
   - Emits `DraftAction(Message)` on user choice

3. **Create `AgentOutput` widget**
   - `src/carta/app/widgets/agent_output.py`
   - Extends `RichLog`
   - Built-in token counter display
   - Methods for agent progress feedback

4. **Create `PromptInput` widget**
   - `src/carta/app/widgets/prompt_input.py`
   - Extends `TextArea` for multi-line input
   - Placeholder management
   - Emits `PromptSubmitted(Message)`

5. **Refactor screens to use widgets**
   - WizardScreen uses QuestionSelector
   - DraftScreen uses DraftViewer
   - All screens use AgentOutput + PromptInput

### Files to Create
- `src/carta/app/widgets/__init__.py`
- `src/carta/app/widgets/question_selector.py`
- `src/carta/app/widgets/draft_viewer.py`
- `src/carta/app/widgets/agent_output.py`
- `src/carta/app/widgets/prompt_input.py`

### Files to Modify
- `src/carta/app/screens/wizard_screen.py` - Use QuestionSelector
- `src/carta/app/screens/draft_screen.py` - Use DraftViewer
- `src/carta/app/screens/*.py` - Use AgentOutput, PromptInput

### Success Criteria
- [ ] Widgets are self-contained with their own styling
- [ ] Screens compose widgets via `compose()`
- [ ] Widget messages bubble up to screen handlers
- [ ] Full workflow still functional

---

## Phase 5: Modal Screens & Polish

**Goal:** Add modal overlays and reactive state for a polished UX.

### Tasks

1. **Create `HelpScreen` modal**
   - `src/carta/app/screens/modals/help_screen.py`
   - Extends `ModalScreen[None]`
   - Displays keybindings and workflow help
   - Dismisses on Escape or Enter

2. **Create `ConfirmQuitScreen` modal**
   - `src/carta/app/screens/modals/confirm_quit.py`
   - Extends `ModalScreen[bool]`
   - "Are you sure?" with Yes/No
   - Returns result to app for quit decision

3. **Add reactive theme support**
   - `theme: Reactive[str]` in CartaApp
   - `watch_theme()` method
   - `get_css_variables()` for dynamic theming

4. **Add screen-level keybindings**
   - Each screen defines relevant `BINDINGS`
   - WizardScreen: `p` for previous, `n` for next
   - DraftScreen: `a` for approve, `r` for refine

5. **Update styles**
   - Per-widget CSS classes
   - Screen-specific styling
   - Consistent color palette

### Files to Create
- `src/carta/app/screens/modals/__init__.py`
- `src/carta/app/screens/modals/help_screen.py`
- `src/carta/app/screens/modals/confirm_quit.py`

### Files to Modify
- `src/carta/app/app.py` - Reactive theme, modal handling
- `src/carta/app/screens/*.py` - Add BINDINGS
- `src/carta/app/styles.scss` - Enhanced styling

### Success Criteria
- [ ] `?` opens help modal from any screen
- [ ] `q` opens quit confirmation modal
- [ ] Escape dismisses modals
- [ ] Keybindings work per-screen
- [ ] Theme switching works (if implemented)

---

## Final Directory Structure

```
src/carta/
├── __init__.py
├── app/
│   ├── __init__.py
│   ├── __main__.py              # CLI entry point
│   ├── app.py                   # CartaApp class
│   ├── messages.py              # Custom Message classes
│   ├── styles.scss              # Global styles
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── base.py              # BaseScreen
│   │   ├── feature_screen.py    # Feature input
│   │   ├── wizard_screen.py     # Q&A wizard
│   │   ├── draft_screen.py      # Draft review
│   │   └── modals/
│   │       ├── __init__.py
│   │       ├── help_screen.py
│   │       └── confirm_quit.py
│   └── widgets/
│       ├── __init__.py
│       ├── question_selector.py
│       ├── draft_viewer.py
│       ├── agent_output.py
│       └── prompt_input.py
├── utils/                       # Unchanged
│   ├── agent.py
│   ├── cache.py
│   └── filename.py
└── prompts/                     # Unchanged
```

---

## Verification Strategy

### Per-Phase Testing
Each phase should pass these checks before proceeding:

1. **Manual smoke test:** Run `carta` and complete full workflow
2. **No regressions:** Feature → Wizard → Draft → Save works
3. **Clean exit:** App exits cleanly, no orphan threads

### End-to-End Test (Final)
1. Launch app: `carta`
2. Enter feature description
3. Answer all wizard questions
4. Review draft
5. Request refinement with feedback
6. Approve and save
7. Verify `.carta/NNN-feature-name/discovery.md` created
8. Press `q` → confirm quit
9. Restart flow with "new"

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking workflow during migration | Phase 2 keeps handlers until FeatureScreen proven |
| Threading regressions | `@work` decorator handles cancellation automatically |
| Lost state between screens | Pass state via screen constructor + dismiss result |
| Scope creep | Each phase is independently shippable |

---

## Notes

- Phases 1-3 are critical path (must complete in order)
- Phases 4-5 can be parallelized or deferred
- Each phase targets ~1-2 hours of implementation
- Handler logic is preserved; only the plumbing changes
