Now I have enough context to generate the discovery document. Let me create it:

FILENAME: implementation-plan-flow

**Objective**
Add a new workflow that generates implementation plans from discovery documents, following the same pattern as the discovery flow with questions, agent-based generation, and user approval.

**Context**
After completing a discovery document, users need to translate requirements into actionable implementation plans. Currently, the app only generates discovery.md files and creates empty plan.md placeholders. This feature bridges the gap between requirements and development by providing a structured planning workflow that mirrors the existing discovery process. The implementation plan will help development teams understand how to approach building the feature described in the discovery document.

**Assumptions**
- Users understand the distinction between discovery (what/why) and planning (approach/priorities)
- The planning workflow follows the same screen-based architecture as discovery (FeatureScreen → WizardScreen → DraftScreen pattern)
- Implementation planning questions focus on approach, priorities, and constraints rather than specific technologies
- Users may want to create plans for newly completed discoveries or revisit existing discovery documents
- The plan.md file structure and format will be defined by a new prompt template
- Users are comfortable with the existing feedback-for-regeneration editing model

**Constraints**
- Must integrate with existing .carta directory structure where each feature has discovery.md, plan.md, and implementation.md files
- Must follow the established screen-based architecture and handler patterns
- Must use the same Agent utility and tool-calling infrastructure as discovery flow
- Must maintain consistency with existing user interaction patterns (wizard Q&A, draft review, feedback cycles)
- Must handle the case where plan.md already exists with user confirmation before overwriting
- Must allow users to select from any existing discovery document in the .carta directory
- Planning questions must remain technology-agnostic and focus on approach rather than implementation details

**Acceptance Criteria**
- After completing a discovery document, users are prompted to start implementation planning with option to skip
- Users can manually trigger implementation planning from a menu or command
- Users can select any existing discovery document from the .carta directory to create a plan for
- System asks 2-5 clarifying questions about implementation approach, priorities, and constraints
- Questions follow the same format as discovery questions with options and impact statements
- Agent generates a draft implementation plan based on the discovery document and question answers
- Users can provide feedback to regenerate the plan multiple times before approval
- If plan.md already exists, users receive a confirmation prompt before overwriting
- Approved plans are saved to the correct .carta/{NNN}-{name}/plan.md file
- Users can restart the entire flow or exit after saving
- The workflow uses the same visual patterns and interactions as the discovery flow

**User Scenarios**
1. A product manager completes a discovery document for a new authentication feature. The app automatically prompts them to continue with implementation planning. They choose to proceed, answer questions about priorities and phasing, review the generated plan, provide feedback to adjust the rollout strategy, and approve the final plan for the development team.

2. A technical lead wants to create an implementation plan for a discovery document that was written two weeks ago. They manually trigger the planning flow, select the discovery document from a list of existing features in the .carta directory, answer questions about technical constraints and dependencies, and approve the generated plan.

3. A developer realizes the existing plan.md for a feature needs updating after requirements changed. They start the planning flow, select the existing discovery document, and when the plan is ready to save, they confirm they want to overwrite the existing plan.md file.

4. A team lead completes a discovery document but wants to defer planning until the next sprint. They skip the automatic prompt to create an implementation plan and exit the app. Later, they return and manually trigger planning for that discovery document.

**Edge Cases**
- User attempts to create a plan but no discovery documents exist in .carta directory
- Discovery document is malformed or missing required sections
- User provides feedback that contradicts the discovery document constraints
- Multiple users attempt to create plans for the same discovery document simultaneously
- User cancels the planning flow midway through questions or during draft review
- .carta directory structure is corrupted or missing expected files
- User provides empty or minimal feedback during refinement
- Plan.md file exists but is empty or corrupted when checking for overwrites

**Dependencies**
- Existing .carta directory structure with discovery.md files
- Existing Agent utility and tool-calling infrastructure
- Existing screen-based architecture (Screen, Handler, Widget patterns)
- Existing filename utilities for directory navigation and validation
- New prompt templates for planning questions (gather), plan generation (draft), and plan refinement (refine)

**Out of Scope**
- Editing plan.md files directly within the app
- Version control or history tracking for plan.md files
- Comparing multiple plan versions side-by-side
- Automatic synchronization between discovery.md changes and plan.md updates
- Generating implementation.md files (third phase of workflow)
- Collaborative multi-user planning sessions
- Exporting plans to external project management tools
- AI-suggested implementation technologies or architectures
- Automatic task breakdown or story point estimation
