---
description: Hybrid-Agile development instructions for backlog, epics, and user stories management
applyTo: 'docs/agile/**'
---

# Hybrid-Agile Development Instructions

## Overview

This document defines the Hybrid-Agile approach for managing product backlog, epics, and user stories in the Loan Application Processing System project. The methodology combines traditional Business Requirements Documents (BRD) and Functional Specification Documents (FSD) with iterative Agile execution through Epics and User Stories.

---

## Core Principles

- **Index-Based Organization:** Backlog serves as the master index for all epics and user stories
- **Epic Separation:** Each epic resides in its own dedicated folder for organization and clarity
- **User Story Isolation:** Each user story exists as an independent markdown file for maintainability
- **Traceability:** All stories trace back to BRD and FSD requirements
- **Iterative Delivery:** Stories grouped into epics, executed in sprints
- **Lightweight Format:** Markdown files, no heavy tools required
- **Testability:** Clear acceptance criteria guide development and QA

---

## Directory Structure

```
docs/agile/
├── README.md                          # Backlog Index (Master Reference)
├── backlog.md                         # Backlog Overview & Prioritization
│
├── epics/
│   ├── 001-Application-Submission/
│   │   ├── epic.md
│   │   ├── US-1-1.md                 # User Story files
│   │   ├── US-1-2.md
│   │   └── ...
│   │
│   ├── 002-Identity-Verification/
│   │   ├── epic.md
│   │   ├── US-2-1.md
│   │   ├── US-2-2.md
│   │   └── ...
│   │
│   ├── 003-Document-Management/
│   │   ├── epic.md
│   │   └── ...
│   │
│   └── 00X-[Epic-Name]/
│       ├── epic.md
│       └── US-X-Y.md
│
└── retired/                            # Archived/deprecated stories
    └── [archived stories]
```

---

## 1. Backlog Index Structure

### 1.1 `docs/agile/backlog.md` (Master Index)

The **backlog.md** file serves as the centralized index and is the single source of truth for all backlog items.

**Contents:**

```markdown
# Product Backlog - Loan Application Processing System

**Last Updated:** [DATE]
**Total Epics:** [COUNT]
**Total User Stories:** [COUNT]
**Sprint Cadence:** 2-week sprints

## Backlog Status Summary

| Metric | Value |
|--------|-------|
| Active Epics | X |
| Planned User Stories | Y |
| In Progress | Z |
| Completed | N |
| Upcoming Sprint | Sprint XX |

## Epic Index (Organized by Priority)

### P0 (Critical) - MVP Delivery

| Epic ID | Epic Name | Stories | Status | Sprint |
|---------|-----------|---------|--------|--------|
| [E-001] | [Link to epic.md] | [Count] | [Status] | [Sprint] |
| [E-002] | [Link to epic.md] | [Count] | [Status] | [Sprint] |

### P1 (High) - Q1 Release

| Epic ID | Epic Name | Stories | Status | Sprint |
|---------|-----------|---------|--------|--------|
| [E-XXX] | [Link to epic.md] | [Count] | [Status] | [Sprint] |

### P2 (Medium) - Future Phases

| Epic ID | Epic Name | Stories | Status | Sprint |
|---------|-----------|---------|--------|--------|
| [E-XXX] | [Link to epic.md] | [Count] | [Status] | [Sprint] |

### P3 (Low) - Backlog

| Epic ID | Epic Name | Stories | Status | Sprint |
|---------|-----------|---------|--------|--------|
| [E-XXX] | [Link to epic.md] | [Count] | [Status] | [Sprint] |

## User Story Index (by Epic)

### Epic: E-001 - [Epic Name]
- [Link to US-1-1.md] - [Story Title] (P0, S, Ready)
- [Link to US-1-2.md] - [Story Title] (P1, M, Ready)
- [Link to US-1-3.md] - [Story Title] (P1, L, Blocked)

### Epic: E-002 - [Epic Name]
- [Link to US-2-1.md] - [Story Title] (P0, M, Ready)
- [Link to US-2-2.md] - [Story Title] (P1, M, Draft)

## Capacity Planning

**Sprint Velocity (Average):** [Points/Sprint]
**Team Size:** [Members]
**Sprint Length:** 2 weeks

## Release Planning

| Release | Target Date | Epics Included | Stories |
|---------|------------|-----------------|---------|
| MVP v1.0 | [Date] | E-001, E-002, ... | XX |
| v1.1 | [Date] | E-XXX | YY |

## Notes & Dependencies

- [Key dependencies across epics]
- [Regulatory/compliance blockers]
- [Technical constraints]
```

---

## 2. Epic Structure

### 2.1 Epic Folder Organization

Each Epic gets its own folder: `docs/agile/epics/XXX-[Epic-Name]/`

**Folder Contents:**
- `epic.md` - Epic definition and metadata
- `US-X-1.md`, `US-X-2.md`, etc. - Individual user story files

### 2.2 Epic File: `epic.md`

**Filename:** `epic.md` (always consistent naming)

**Location:** `docs/agile/epics/XXX-[Epic-Name]/epic.md`

**Content Template:**

```markdown
# Epic: [Epic Name]

**Epic ID:** E-XXX
**Priority:** P0 / P1 / P2 / P3
**Status:** Not Started / In Progress / Completed / On Hold
**Target Sprint(s):** Sprint [XX] - Sprint [YY]
**Related BRD:** [Link to BRD section, e.g., BR-1.1, BR-1.2]
**Related FSD:** [Link to FSD section, e.g., Feature 3.1, Process 2.1]

---

## Epic Overview

**Business Goal:**
[High-level business objective this epic achieves]

**User Story:**
As a [user role], I want [capability], so that [business value]

**Success Criteria:**
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

---

## Scope

### What's Included
- [Feature/capability 1]
- [Feature/capability 2]
- [Feature/capability 3]

### What's Excluded
- [Out of scope item 1]
- [Out of scope item 2]

---

## User Stories

| Story ID | Title | Points | Status |
|----------|-------|--------|--------|
| [US-X-1] | [Story Title] | [5] | [Not Started] |
| [US-X-2] | [Story Title] | [3] | [In Progress] |
| [US-X-3] | [Story Title] | [8] | [Ready] |

**Total Story Points:** [SUM]

**Story Details:** See individual US-X-Y.md files

---

## Dependencies

### Internal Dependencies
- Epic E-XXX must be completed before this epic can start
- Feature Y depends on completion of Feature X

### External Dependencies
- Third-party API integration required: [Service name]
- Regulatory approval needed before: [Feature]

---

## Acceptance Criteria (Epic Level)

For the epic to be considered complete:
- [ ] All user stories meet acceptance criteria
- [ ] Integration testing passed
- [ ] Compliance review completed (if applicable)
- [ ] Stakeholder sign-off obtained
- [ ] Documentation updated
- [ ] Training materials prepared (if needed)

---

## Technical Notes

- [Architecture impacts]
- [Database schema changes]
- [API changes]
- [Integration points]
- [Performance considerations]

---

## Timeline

**Estimated Duration:** [X weeks]
**Start Date:** [Date]
**Target Completion:** [Date]
**Review Frequency:** Weekly standup

---

## Metrics & Reporting

**Velocity Prediction:** [X story points/sprint]
**Risk Level:** Low / Medium / High
**Key Blockers:** [None / List items]

---

## Notes

[Additional context, decisions, assumptions]

**Last Updated:** [DATE]
**Epic Owner:** [Name]
**Product Owner Review:** [Approved/Pending]
```

---

## 3. User Story Structure

### 3.1 User Story File Organization

**Naming Convention:** `US-X-Y.md`
- `X` = Epic number (001, 002, 003, etc.)
- `Y` = Story number within epic (1, 2, 3, etc.)

**Examples:**
- `US-1-1.md` - First story in Epic 1
- `US-1-5.md` - Fifth story in Epic 1
- `US-2-1.md` - First story in Epic 2

**Location:** `docs/agile/epics/XXX-[Epic-Name]/US-X-Y.md`

### 3.2 User Story File Template

**Filename:** `US-X-Y.md`

**Content Template:**

```markdown
# User Story: [Story Title]

**Story ID:** US-X-Y
**Epic:** [Link to epic.md] (E-XXX: Epic Name)
**Priority:** P0 / P1 / P2 / P3
**Status:** Not Started / In Progress / In Review / Done / Blocked
**Story Points:** [1/2/3/5/8/13]
**Sprint:** Sprint [XX] / Backlog
**Related BRD:** [BR-X.X]
**Related FSD:** [Feature X.X / Use Case X.X / Process X.X]

---

## User Story

**As a** [user role/persona]
**I want** [specific action/feature]
**So that** [business value/benefit]

---

## Acceptance Criteria

Clear, testable conditions that define when the story is complete:

- [ ] **Scenario 1:** [Given context] When [action] Then [expected result]
- [ ] **Scenario 2:** [Given context] When [action] Then [expected result]
- [ ] **Scenario 3:** [Given context] When [action] Then [expected result]
- [ ] **Criteria 4:** [Testable criterion]
- [ ] **Criteria 5:** [Testable criterion]

### Definition of Done

This story is complete when:
- [ ] Code written and peer-reviewed
- [ ] Unit tests written and passing (>80% coverage)
- [ ] Integration tests passing
- [ ] Acceptance criteria verified
- [ ] Code merged to main branch
- [ ] Documentation updated
- [ ] Ready for demo/review

---

## Tasks & Technical Details

### Development Tasks
1. [Specific task 1] - [Estimated effort: X hours]
2. [Specific task 2] - [Estimated effort: X hours]
3. [Specific task 3] - [Estimated effort: X hours]

### Technical Considerations
- **Architecture Impacts:** [None / Describe impacts]
- **Database Changes:** [Schema updates, migrations]
- **API Changes:** [Endpoints, parameters]
- **Performance:** [Target response times, considerations]
- **Security:** [Security implications, data protection]
- **Browser/Platform Support:** [Compatibility requirements]

---

## Implementation Details

### Front-End (if applicable)
- **Components/Pages:** [List affected components]
- **State Management:** [Redux / Context / Local state]
- **UI/UX:** [Mockup link / Figma reference]
- **Design System:** [Components to use]

### Back-End (if applicable)
- **Endpoints:** [New/modified API endpoints]
- **Database:** [Tables/collections affected]
- **Business Logic:** [Core logic implementation]
- **External Integrations:** [Third-party APIs]

### Data Requirements

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| [Field] | [Type] | Yes/No | [Rule] |
| [Field] | [Type] | Yes/No | [Rule] |

---

## Testing Strategy

### Unit Tests
- [Test case 1]
- [Test case 2]

### Integration Tests
- [Integration test 1]
- [Integration test 2]

### Manual Testing Scenarios
- [Manual test scenario 1]
- [Manual test scenario 2]

### Acceptance Test Checklist
- [ ] Acceptance criterion 1 verified
- [ ] Acceptance criterion 2 verified
- [ ] Edge cases tested
- [ ] Error handling verified

---

## Dependencies & Blockers

### Internal Dependencies
- This story depends on: [US-X-Y, US-X-Z]
- This story blocks: [US-X-A, US-X-B]

### External Dependencies
- [Third-party service dependency]
- [API availability requirement]

### Known Blockers
- [Current blocker 1]
- [Current blocker 2]

**Blocker Resolution:** [Action plan to unblock]

---

## Compliance & Regulatory

**Regulatory Requirement:** [If applicable, reference BRD/FSD regulation]
- [Compliance aspect 1]
- [Compliance aspect 2]

**Audit Trail:** [Document logging/tracking needs]

---

## Documentation

### User Documentation
- [ ] User guide section to be created
- [ ] FAQ entry needed
- [ ] In-app help text

### Technical Documentation
- [ ] API documentation updated
- [ ] Architecture diagram updated
- [ ] Code comments/inline documentation
- [ ] Deployment notes

---

## Estimation & Effort

**Story Points:** [1/2/3/5/8/13]
**Estimated Hours:** [Dev hours + QA hours]
**Complexity:** Low / Medium / High
**Risk Level:** Low / Medium / High

### Estimation Breakdown
- Frontend: [X hours]
- Backend: [X hours]
- Testing: [X hours]
- Documentation: [X hours]
- **Total:** [X hours]

---

## Acceptance & Sign-Off

**Product Owner:** [Name] - [ ] Approved
**Stakeholder Review:** [Date] - [Status]
**QA Lead:** [Name] - [ ] Verified

---

## Notes & Comments

[Additional context, assumptions, edge cases, design decisions]

---

## Related Stories

- [Related story 1]
- [Related story 2]
- [Predecessor story]
- [Follow-up story]

---

**Created:** [DATE]
**Last Updated:** [DATE]
**Assignee:** [Developer Name]
**Reviewer:** [Lead Developer Name]
```

---

## 4. Backlog Management Workflow

### 4.1 Creating a New Epic

1. **Define the Epic** following the Epic template in Section 2.2
2. **Create folder** `docs/agile/epics/XXX-[Epic-Name]/`
3. **Create epic.md** in the folder with all required sections
4. **Identify related stories** from BRD/FSD requirements
5. **Update backlog.md** index with new epic entry
6. **Obtain Product Owner approval** before sprint assignment

### 4.2 Creating New User Stories

1. **Extract story from Epic** scope and BRD/FSD requirements
2. **Write user story** using the template in Section 3.2
3. **Save as file** `docs/agile/epics/XXX-[Epic-Name]/US-X-Y.md`
4. **Link in epic.md** user story index table
5. **Link in backlog.md** epic's story list
6. **Estimate story points** following your team's Fibonacci scale (1, 2, 3, 5, 8, 13)
7. **Mark status** as "Ready" for sprint planning

### 4.3 Sprint Planning Process

1. **Review backlog.md** for prioritized stories
2. **Select stories** for upcoming sprint
3. **Update status** in each story file to "In Progress"
4. **Update sprint number** in story files
5. **Assign developers** and reviewers
6. **Calculate total velocity** (sum of story points)
7. **Communicate sprint plan** to team

### 4.4 Sprint Execution

- **Daily Standup:** Reference status in story files
- **Update Status:** Change story status as progress occurs (In Progress → In Review → Done)
- **Track Blockers:** Document in the Dependencies & Blockers section
- **Communicate Changes:** Update backlog.md weekly

### 4.5 Sprint Review & Retrospective

1. **Demo completed stories** (status = "Done")
2. **Verify acceptance criteria** met
3. **Obtain Product Owner sign-off**
4. **Update backlog.md** with completion metrics
5. **Archive completed stories** (keep in original locations with Done status)
6. **Plan next sprint** based on velocity and priorities

---

## 5. Naming & Conventions

### 5.1 Epic Naming

- **Format:** `XXX-[Epic-Name]`
- **XXX:** Sequential number (001, 002, 003, etc.)
- **Epic-Name:** Kebab-case, descriptive (e.g., `Application-Submission`, `Identity-Verification`)
- **Example:** `001-Application-Submission`, `005-AML-Compliance-Screening`

### 5.2 User Story Naming

- **Format:** `US-X-Y`
- **X:** Epic number (1-digit or zero-padded)
- **Y:** Story sequence within epic
- **Example:** `US-1-1`, `US-2-5`, `US-10-3`

### 5.3 File Naming

- **Epic folder:** `docs/agile/epics/001-Application-Submission/`
- **Epic file:** Always named `epic.md`
- **Story files:** `US-1-1.md`, `US-1-2.md`, etc.
- **No spaces in folder names**, use hyphens for word separation

### 5.4 Priority Levels

- **P0 (Critical):** MVP features, regulatory requirements, deal-breakers
- **P1 (High):** Important features, significant user value, target release
- **P2 (Medium):** Nice-to-have features, competitive advantage, future phases
- **P3 (Low):** Polish, enhancements, technical debt, backlog items

### 5.5 Status Values

- **Not Started:** Story created but not yet begun
- **In Progress:** Developer actively working on story
- **In Review:** Code complete, awaiting review/testing
- **Done:** All acceptance criteria met, Product Owner signed off
- **Blocked:** Cannot proceed, waiting on dependency or blocker
- **Cancelled:** No longer needed or deferred indefinitely
- **On Hold:** Temporarily paused, will resume later

---

## 6. Traceability Matrix

### 6.1 Linking to Requirements

Every user story must trace back to BRD/FSD:

**In Story File (header):**
```markdown
**Related BRD:** BR-1.1, BR-1.2
**Related FSD:** Feature 3.1, Use Case 3.1.1, Business Process 2.1
```

**Why This Matters:**
- Ensures requirements are implemented
- Supports regulatory traceability
- Facilitates impact analysis for changes
- Enables requirements verification

### 6.2 Bi-Directional Traceability

**Forward Traceability (BRD → Stories):**
- Every BRD requirement should be covered by one or more user stories

**Backward Traceability (Stories → BRD):**
- Every user story should reference the BRD/FSD requirement it addresses

**Verification:**
- Run periodic audits to ensure all BRD items are covered
- Run audits to ensure all stories reference requirements

---

## 7. Definition of Done (Team Level)

Stories are considered complete when ALL of these criteria are met:

### Development Complete
- [ ] Code written following coding standards
- [ ] Code peer-reviewed and approved
- [ ] All unit tests written and passing (≥80% coverage)
- [ ] All integration tests passing
- [ ] No TODO comments in code
- [ ] Code merged to main/develop branch

### Testing Complete
- [ ] All acceptance criteria verified (manual or automated)
- [ ] Edge cases and error scenarios tested
- [ ] Cross-browser testing completed (if applicable)
- [ ] Performance testing completed (if applicable)
- [ ] Security review completed (if applicable)
- [ ] QA sign-off obtained

### Documentation Complete
- [ ] Code comments added for complex logic
- [ ] API documentation updated (if applicable)
- [ ] User documentation updated
- [ ] Help text/tooltips added (if applicable)
- [ ] Architecture documentation updated (if needed)

### Business Complete
- [ ] Product Owner verified acceptance criteria
- [ ] Stakeholder sign-off obtained
- [ ] Release notes prepared
- [ ] Training materials created (if needed)

### Compliance Complete (if applicable)
- [ ] Regulatory requirements verified
- [ ] Compliance checklist completed
- [ ] Audit trail logged
- [ ] Data protection verified

---

## 8. Sprint Planning Template

### 8.1 Sprint Planning Checklist

**Before Sprint Planning:**
- [ ] Backlog.md is updated and prioritized
- [ ] Top 20-30 stories are refined with acceptance criteria
- [ ] Estimated story points assigned to prioritized stories
- [ ] Epic dependencies identified
- [ ] Blockers documented
- [ ] Product Owner available for questions

**During Sprint Planning:**
- [ ] Team commits to sprint goal
- [ ] Stories selected based on velocity and priority
- [ ] Tasks identified for each story
- [ ] Assignments made to developers
- [ ] Dependencies and risks discussed
- [ ] Sprint goal documented

**After Sprint Planning:**
- [ ] Backlog.md updated with sprint assignments
- [ ] User story files updated with sprint number
- [ ] Status changed to "Ready" or "In Progress"
- [ ] Team has kickoff meeting
- [ ] Sprint board created/updated

---

## 9. Quality Standards

### 9.1 User Story Quality Checklist

Before marking a story as "Ready" for sprint:

- [ ] Story title is clear and specific
- [ ] User story follows format: "As a... I want... So that..."
- [ ] Acceptance criteria are testable and measurable
- [ ] Acceptance criteria use "Given-When-Then" format where applicable
- [ ] Story is independent (can be delivered without other stories)
- [ ] Story is negotiable (details can be refined during sprint)
- [ ] Story is valuable (clear business value stated)
- [ ] Story is estimable (team can estimate story points)
- [ ] Story is small (can be completed in one sprint)
- [ ] Story is testable (acceptance criteria define how to verify)
- [ ] Dependencies are clearly identified
- [ ] Related BRD/FSD requirements are linked
- [ ] Technical considerations documented
- [ ] Acceptance criteria for "Definition of Done" included

### 9.2 Epic Quality Checklist

Before assigning stories to sprint:

- [ ] Epic aligns with BRD/FSD business requirements
- [ ] Epic goal is clear and specific
- [ ] Success criteria for epic defined
- [ ] All related user stories identified and prioritized
- [ ] Epic dependencies documented
- [ ] Estimated total story points for epic
- [ ] Target sprint(s) or timeline identified
- [ ] Product Owner approval obtained
- [ ] Regulatory/compliance implications documented (if applicable)

---

## 10. Backlog Maintenance

### 10.1 Backlog Grooming (Weekly)

**Every Week, Product Owner should:**
1. Review current backlog.md status
2. Refine top 20-30 stories with acceptance criteria
3. Re-prioritize based on new feedback/changes
4. Identify and resolve blockers
5. Update epic.md with story count and status
6. Update any completed story status to "Done"

### 10.2 Backlog Health Checks (Monthly)

1. **Completeness:** Are all BRD/FSD requirements represented as stories?
2. **Traceability:** Do all stories link to BRD/FSD requirements?
3. **Prioritization:** Are stories prioritized by business value?
4. **Estimation:** Are story points realistic based on velocity?
5. **Status Accuracy:** Are story statuses current?
6. **Dependencies:** Are all dependencies documented?

### 10.3 Archival & Cleanup (End of Sprint)

- Move completed stories to `docs/agile/retired/` folder (optional, keep in place with Done status)
- Archive cancelled stories with cancellation reason
- Clean up any duplicate or obsolete stories
- Update backlog.md with sprint metrics

---

## 11. Deliverables & Artifacts

### 11.1 Required Artifacts

| Artifact | Location | Purpose | Update Frequency |
|----------|----------|---------|------------------|
| backlog.md | docs/agile/ | Master index of all work | Weekly |
| epic.md | docs/agile/epics/XXX-*/epic.md | Epic definition & scope | As needed |
| US-X-Y.md | docs/agile/epics/XXX-*/US-X-Y.md | User story details | As needed |
| Epic folders | docs/agile/epics/ | Organize stories by epic | Sprint planning |

### 11.2 Sprint Reporting

**At Sprint End, Update:**
1. backlog.md with sprint metrics
2. All story statuses to reflect actual status
3. Epic.md with story completion count
4. Release planning timeline if affected

### 11.3 Release Documentation

**For Each Release, Create:**
1. Release notes document listing completed features
2. User release summary
3. Technical release notes (breaking changes, etc.)
4. Training materials (if applicable)

---

## 12. Tools & Technology Stack

### 12.1 What We Use

- **Markdown** for all documentation (version control friendly)
- **Git** for backlog version control and history
- **GitHub/GitLab** for collaboration and reviews
- **Text Editor** (VS Code, etc.) for editing backlog files
- **Project Board** (GitHub Projects, Jira, etc.) - optional for visual tracking

### 12.2 What We Don't Use

- **Heavy project management tools** (not required)
- **Database-driven backlog systems** (markdown is sufficient)
- **Complex custom workflows** (keep it simple)

### 12.3 Integration with Developer Tools

- Story files reference in code commits: "Fixes US-1-1"
- Pull requests link to story: "Closes #US-1-1" (if using GitHub issues)
- CI/CD pipeline can read backlog.md for status
- Test reports can reference user stories

---

## 13. Governance & Approval

### 13.1 Approval Workflow

**For New Epics:**
1. Draft by Product Owner/Business Analyst
2. Review by Development Lead (technical feasibility)
3. Review by Compliance (if regulatory implications)
4. Final approval by Product Owner

**For New User Stories:**
1. Draft by Product Owner
2. Review by Development Lead (during backlog grooming)
3. Refinement with team (during sprint planning)
4. Approval by Product Owner (story is ready to commit)

### 13.2 Roles & Responsibilities

| Role | Responsibility |
|------|-----------------|
| **Product Owner** | Backlog prioritization, story approval, acceptance |
| **Development Lead** | Technical feasibility, estimation, dependencies |
| **Scrum Master** | Process facilitation, blocker resolution, metrics |
| **Development Team** | Story implementation, quality, documentation |
| **QA Lead** | Acceptance criteria verification, testing |
| **Compliance Officer** | Regulatory requirement verification (if applicable) |

---

## 14. Change Management

### 14.1 Handling Scope Changes

**If story scope changes mid-sprint:**
1. Stop work immediately
2. Document change request
3. Re-estimate story points
4. Discuss with Product Owner and team
5. Options: Revise story, split story, defer to next sprint
6. Update story file with new acceptance criteria
7. Get team re-confirmation of commitment

**If BRD/FSD requirements change:**
1. Create change request with business justification
2. Assess impact on existing stories/epics
3. Update affected user stories
4. Update backlog.md dependencies
5. Obtain approvals and re-plan if necessary

### 14.2 Story Versioning

- Keep story history in markdown (add "Last Updated" field)
- Use Git commit history for version tracking
- Never delete historical information, mark as "Archived" instead
- Add change notes when significant changes made

---

## 15. Communication & Transparency

### 15.1 Backlog Communication

**Weekly:**
- Update backlog.md with latest status
- Share backlog summary with stakeholders
- Communicate blockers and risks

**Sprint Cadence:**
- Sprint planning: Stories selected and committed
- Daily standup: Reference current story status
- Sprint review: Demo completed stories (Done status)
- Sprint retro: Discuss process improvements

### 15.2 Stakeholder Updates

**For Executives:**
- Release backlog.md to show priorities and timeline
- Highlight P0/P1 epics and completion status
- Communicate risks and dependencies

**For Development Team:**
- Share sprint plan with user stories
- Make individual story files easily accessible
- Discuss acceptance criteria and technical approach

---

## 16. Examples & Templates

### 16.1 Sample Epic Structure

```
docs/agile/epics/001-Application-Submission/
├── epic.md
├── US-1-1.md (Applicant creates account)
├── US-1-2.md (Applicant selects loan product)
├── US-1-3.md (Applicant completes application form)
├── US-1-4.md (Applicant saves draft application)
├── US-1-5.md (Applicant submits application)
└── US-1-6.md (System validates application)
```

### 16.2 Sample Backlog Index Entry

```markdown
## Epic: E-001 - Application Submission
**Priority:** P0 | **Status:** In Progress | **Sprint:** Sprint 1-2
**Stories:** 6 | **Points:** 34 | **BRD Ref:** BR-1.1, BR-1.2, BR-1.3, BR-1.4

| Story ID | Title | Points | Status |
|----------|-------|--------|--------|
| [US-1-1](epics/001-Application-Submission/US-1-1.md) | Applicant account creation | 3 | Done |
| [US-1-2](epics/001-Application-Submission/US-1-2.md) | Loan product selection | 2 | In Progress |
| [US-1-3](epics/001-Application-Submission/US-1-3.md) | Application form completion | 8 | Ready |
```

---

## 17. When to Use This Framework

Use this Hybrid-Agile approach when:

✅ **DO USE:**
- Large products with multiple features and phases
- Teams requiring transparency and traceability
- Projects with regulatory/compliance requirements
- Multi-team coordination needed
- Version control and change history important
- Lightweight tooling preferred
- Git-based workflow established

❌ **AVOID IF:**
- Very small team with single story at a time
- Project requires heavy real-time dashboarding
- Team prefers visual board-based workflows exclusively
- No Git infrastructure available

---

## 18. Troubleshooting

### Issue: Stories are too large

**Solution:**
- Break story into smaller stories (smaller point values)
- Create parent story linking to sub-stories
- Estimate sub-stories separately
- Plan to deliver parent story across multiple sprints

### Issue: Backlog.md is becoming too large

**Solution:**
- Move completed epics to `docs/agile/retired/backlog-archive.md`
- Create quarterly backlog summaries
- Use backlog.md for current sprint + 2-3 future sprints only
- Archive historical backlog separately

### Issue: Stories missing traceability to BRD/FSD

**Solution:**
- Conduct backlog audit quarterly
- Create traceability matrix (BRD → Stories)
- Update stories to reference requirements
- Add missing stories for uncovered requirements

### Issue: Story status not being updated

**Solution:**
- Add story status check to daily standup
- Make status updates part of Definition of Done
- Automate status updates where possible (CI/CD integration)
- Review backlog weekly to catch stale stories

---

## 19. Quick Reference

### Quick Checklist for New Stories

```markdown
- [ ] Story title clear and specific
- [ ] User story formatted correctly (As a... I want... So that...)
- [ ] Acceptance criteria written (5-10 criteria, testable)
- [ ] Story points estimated
- [ ] BRD/FSD requirements linked
- [ ] Dependencies identified
- [ ] Technical approach documented
- [ ] Definition of Done included
- [ ] Product Owner approval obtained
- [ ] File saved as US-X-Y.md in correct epic folder
- [ ] Story linked in backlog.md
```

### Quick Checklist for Sprint Planning

```markdown
- [ ] Backlog.md prioritized and reviewed
- [ ] Top 20-30 stories refined and estimated
- [ ] Team velocity calculated
- [ ] Sprint goal defined
- [ ] Stories selected for sprint
- [ ] Total story points < team velocity
- [ ] All dependencies resolvable within sprint
- [ ] Blockers identified and planned
- [ ] Stories assigned to developers
- [ ] Story files updated with sprint number
- [ ] Sprint kickoff meeting scheduled
```

---

## References

- **BRD:** `/docs/BRD/Loan_Application_BRD.md`
- **FSD:** `/docs/FSD/Loan_Application_FSD.md`
- **Product Owner Prompt:** `/.github/prompts/product-owner.prompt.md`
- **FSD Instructions:** `/.github/instructions/fsd.instructions.md`

---

**Document Version:** 1.0
**Last Updated:** November 17, 2025
**Next Review:** Quarterly or upon major project changes
**Document Owner:** Agile Coach / Scrum Master
