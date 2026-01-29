# Elia - Textual TUI Architecture Report

## Executive Summary

Elia is a well-structured Textual application demonstrating canonical patterns for TUI development. The architecture follows a clear separation: **App** → **Screens** → **Widgets**, with CSS-based styling and event-driven communication.

---

## 1. App Layer

**Class:** `Elia(App[None])` in `elia_chat/app.py`

```
App Configuration:
├── CSS_PATH        → External SCSS file
├── BINDINGS        → Global keybindings (quit, help)
├── theme: Reactive → Dynamic theme switching
└── on_mount()      → Pushes HomeScreen, applies theme
```

**Entry Point:** `__main__.py` uses Click CLI, instantiates `Elia()` and calls `.run()`

---

## 2. Screen Layer

| Screen | Type | Purpose |
|--------|------|---------|
| `HomeScreen` | `Screen[None]` | Main hub - chat list, prompt input |
| `ChatScreen` | `Screen[None]` | Active chat interface |
| `HelpScreen` | `ModalScreen[None]` | Help overlay |
| `RenameChat` | `ModalScreen[str]` | Input modal |
| `ChatDetails` | `ModalScreen[None]` | Metadata display |
| `OptionsModal` | `ModalScreen[RuntimeConfig]` | Settings |

**Navigation Pattern:** Stack-based via `push_screen()` / `pop_screen()`

---

## 3. Widget Composition

```
HomeScreen
├── AppHeader (Widget)
├── HomePromptInput (TextArea subclass)
├── ChatList (OptionList subclass)
├── Welcome (Static subclass)
└── Footer

ChatScreen
├── Chat (Widget) ─────────────────────┐
│   ├── ResponseStatus (Vertical)      │
│   ├── ChatHeader (Widget)            │
│   ├── VerticalScroll                 │ Container
│   │   └── Chatbox[] (Widget)         │
│   └── ChatPromptInput (TextArea)     │
└── Footer ────────────────────────────┘
```

---

## 4. Class Inheritance Map

```
textual.app.App ────────────────→ Elia

textual.screen.Screen ──────────→ HomeScreen, ChatScreen
textual.screen.ModalScreen ─────→ HelpScreen, RenameChat, ChatDetails, OptionsModal

textual.widget.Widget ──────────→ Chat, Chatbox, ChatHeader, AppHeader
textual.widgets.Static ─────────→ TitleStatic, Welcome
textual.widgets.TextArea ───────→ PromptInput → HomePromptInput, ChatPromptInput
textual.widgets.OptionList ─────→ ChatList
textual.containers.Vertical ────→ ResponseStatus
```

---

## 5. File Organization

```
elia_chat/
├── app.py                 # App(Elia)
├── __main__.py            # CLI entry
├── elia.scss              # Global styles
├── screens/               # All Screen subclasses
│   ├── home_screen.py
│   ├── chat_screen.py
│   └── *.py (modals)
└── widgets/               # All Widget subclasses
    ├── chat.py
    ├── chatbox.py
    └── *.py
```

---

## 6. Key Architectural Patterns

| Pattern | Implementation |
|---------|----------------|
| **Reactive State** | `@reactive` decorator, `watch_*` methods |
| **Event System** | Custom `Message` subclasses, `@on` decorators |
| **Signal Pub/Sub** | `Signal[T]` for cross-widget config updates |
| **Async Workers** | `@work(thread=True)` for LLM streaming |
| **CSS Theming** | Single SCSS file + dynamic `get_css_variables()` |
| **Composition** | `compose()` method yields child widgets |

---

## 7. Event Flow Example

```
User types → PromptInput
         ↓
    PromptSubmitted (Message)
         ↓
    ChatScreen handles via @on
         ↓
    Chat.stream_agent_response() (worker thread)
         ↓
    AgentResponseComplete (Message)
         ↓
    ChatScreen saves to DB
```

---

This architecture demonstrates Textual best practices: clear screen/widget separation, CSS-driven styling, reactive state, and message-based component communication.
