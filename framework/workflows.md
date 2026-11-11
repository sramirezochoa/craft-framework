# Workflows

**FRAMEWORK-OWNED — do not edit.**
**HUMAN-FACING — agents should not read this file.** A flowchart's meaning
sits in an edge list that has to be traversed; for an agent the same facts are
faster and less ambiguous as the ordered steps in
[working-guide.md](working-guide.md) and the criteria in
[definition-of-done.md](definition-of-done.md). Diagrams are here because
people read structure better as a picture.

The same process, drawn. Mermaid, so it is plain text, diffable, and rendered
by GitHub and most IDEs.

**Nothing here is normative.** These diagrams show *flow* and gate *names*
only — no exit criteria, which live in `definition-of-done.md` alone. Where a
diagram and that file disagree, that file wins.

The gates, by name:

<!-- BEGIN GENERATED: gates-names — from definition-of-done.md, do not edit by hand -->

- **Gate 0** — Understanding confirmed
- **Gate 1** — Change spec approved
- **Gate 2** — Plan approved
- **Gate 3** — Tests red for the right reason
- **Gate 4** — Implementation complete
- **Gate 5** — Review passed
- **Gate 6** — Change folded back (Definition of Done)

*Generated from [definition-of-done.md](definition-of-done.md), the single source of truth for the gate model.*

<!-- END GENERATED -->

---

## 1. The full track

New or altered behaviour. Every arrow out of a gate needs a human.

```mermaid
flowchart TD
    Start([Request arrives]) --> READ[Read capability doc + code<br/>Restate current behaviour]
    READ --> G0{{"Gate 0 — understanding confirmed"}}
    G0 -.->|wrong| READ

    G0 -->|owner agrees| SPEC[Write change.md<br/>current vs desired · AC-n]
    SPEC --> G1{{"Gate 1 — change spec approved"}}
    G1 -.->|too big| SPLIT[Split into<br/>smaller changes] -.-> SPEC

    G1 -->|approved| PLAN[Write plan.md + tasks.md<br/>approach · contracts · risks · ADRs]
    PLAN --> G2{{"Gate 2 — plan approved"}}

    G2 -->|approved| TEST[Write failing tests + eval cases<br/>one per AC-n]
    TEST --> G3{{"Gate 3 — red for the right reason"}}
    G3 -.->|typo or<br/>compile error| TEST

    G3 -->|behaviour genuinely<br/>missing| IMPL[Implement one task]
    IMPL --> VERIFY[["bash scripts/verify.sh"]]
    VERIFY -.->|red| IMPL
    VERIFY -->|green| MORE{Tasks left?}
    MORE -->|yes| IMPL

    MORE -->|no| G4{{"Gate 4 — implementation complete"}}
    G4 --> REVIEW[Apply review checklist]
    REVIEW --> G5{{"Gate 5 — review passed · CI green"}}
    G5 -.->|changes requested| IMPL

    G5 -->|approved| FOLD[Update capability docs<br/>accept ADRs · publish contracts]
    FOLD --> G6{{"Gate 6 — capability doc reflects reality"}}
    G6 --> Done([Done])

    classDef gate fill:#fff3cd,stroke:#997404,color:#5c4504
    classDef work fill:#e7f1ff,stroke:#2a5db0,color:#17315c
    classDef danger fill:#ffe5e5,stroke:#b02a2a,color:#5c1717
    class G0,G1,G2,G3,G4,G5 gate
    class READ,SPEC,PLAN,TEST,IMPL,REVIEW,FOLD work
    class G6 danger
```

Gate 6 is marked differently on purpose. It is the one that gets skipped, and
skipping it turns every capability document into fiction.

---

## 2. Which track?

```mermaid
flowchart TD
    Q([Work arrives]) --> NEW{Does a user-visible<br/>behaviour change?}

    NEW -->|no| DOC{Is the capability doc<br/>wrong about<br/>current behaviour?}
    DOC -->|yes| LIGHTDOC[LIGHT TRACK<br/>+ correct the doc<br/>as part of the fix]
    DOC -->|no| LIGHT[LIGHT TRACK<br/>test + fix + verify]

    NEW -->|yes| EXISTS{Does a capability doc<br/>exist for this area?}
    EXISTS -->|yes| FULL[FULL TRACK<br/>amend the capability]
    EXISTS -->|no, and the<br/>code exists| ADOPT[ADOPTION<br/>write the capability doc<br/>as part of the change]
    EXISTS -->|no, and it is<br/>genuinely new| GREEN[FULL TRACK<br/>create the capability]

    ADOPT --> FULL

    classDef light fill:#e6f4ea,stroke:#1e7e34,color:#0f3d1a
    classDef full fill:#e7f1ff,stroke:#2a5db0,color:#17315c
    classDef adopt fill:#f3e8ff,stroke:#6b3fa0,color:#33205c
    class LIGHT,LIGHTDOC light
    class FULL,GREEN full
    class ADOPT adopt
```

The owner chooses. The cost of the full track on a small change is an hour; the
cost of the light track on a real behaviour change is an undocumented system.

---

## 3. How the artifacts relate

```mermaid
flowchart LR
    subgraph living ["docs/capabilities/ — living, always current"]
        CAP["order-cancellation.md<br/><i>what the system does today</i>"]
    end

    subgraph work ["docs/changes/ — time-ordered, archived"]
        CH1["011-...<br/>merged"]
        CH2["012-...<br/>merged"]
        CH3["013-...<br/>in progress"]
    end

    subgraph why ["docs/adr/ — append-only"]
        ADR["0008-outbox-for-events.md"]
    end

    subgraph proof ["evals/ + tests — executable"]
        EV["AC-3-....yaml"]
        TS["CancelTest"]
    end

    CH1 -->|folded back<br/>at gate 6| CAP
    CH2 -->|folded back<br/>at gate 6| CAP
    CH3 -.->|will fold back| CAP

    CAP -->|change log row<br/>points back| CH2
    CH2 -->|produced| ADR
    ADR -->|constrains<br/>future changes| CH3

    CH2 -->|acceptance criteria<br/>become| EV
    CH2 -->|acceptance criteria<br/>become| TS
    EV -->|prove| CAP
    TS -->|prove| CAP

    classDef cap fill:#e6f4ea,stroke:#1e7e34,color:#0f3d1a
    classDef chg fill:#e7f1ff,stroke:#2a5db0,color:#17315c
    classDef adr fill:#f3e8ff,stroke:#6b3fa0,color:#33205c
    classDef ex fill:#fff3cd,stroke:#997404,color:#5c4504
    class CAP cap
    class CH1,CH2,CH3 chg
    class ADR adr
    class EV,TS ex
```

Four nouns, four questions:

| Artifact | Answers | Lifecycle |
|---|---|---|
| Capability | What does it do **now**? | Living — amended forever |
| Change | What changed, and why? | Archived once merged |
| ADR | Why this approach over the alternatives? | Append-only; superseded, never edited |
| Test / eval | Does it actually do it? | Runs on every commit |

---

## 4. Who does what

```mermaid
sequenceDiagram
    actor Owner
    actor Reviewer
    participant Agent
    participant Repo as Repository
    participant CI

    Owner->>Agent: "allow cancelling after shipment"
    Agent->>Repo: read capability doc + code
    Agent->>Owner: "today it works like this — correct?"
    Owner-->>Agent: gate 0 ✓

    Agent->>Repo: write change.md
    Agent->>Reviewer: request review
    Reviewer-->>Agent: gate 1 ✓

    Agent->>Repo: write plan.md + tasks.md
    Agent->>Reviewer: request review
    Reviewer-->>Agent: gate 2 ✓

    loop one task at a time
        Agent->>Repo: failing test, then code
        Agent->>CI: bash scripts/verify.sh
        CI-->>Agent: green
    end

    Agent->>Reviewer: PR with DoD checklist
    Reviewer->>Repo: apply review checklist
    Reviewer-->>Agent: gate 5 ✓

    Agent->>Repo: fold change into capability doc
    Reviewer-->>Owner: gate 6 ✓ — done
```

The agent is always the **author**, never the reviewer of its own work. A
separate agent session with fresh context makes a reasonable second reviewer —
it has not talked itself into the approach — but never the final one.

---

## 5. Brownfield: the fold-back loop

What makes this framework work on code that already exists.

```mermaid
flowchart TD
    REQ([Change request on<br/>existing behaviour]) --> READ[Read the capability doc]
    READ --> CODE[Read the code]
    CODE --> CMP{Do they agree?}

    CMP -->|no| FIX[The doc is a bug.<br/>Correct it as part<br/>of this change]
    FIX --> DELTA
    CMP -->|yes| DELTA[State the delta:<br/>current → desired<br/>+ what must NOT change]

    DELTA --> REG[Existing tests and evals<br/>become the regression net]
    REG --> BUILD[Build the change]
    BUILD --> CHECK{All existing<br/>cases still green?}

    CHECK -->|no| DECIDE{Was this change<br/>declared in the spec?}
    DECIDE -->|no| STOP[/"STOP — unapproved<br/>behaviour change"/]
    DECIDE -->|yes| BUILD
    STOP --> DELTA

    CHECK -->|yes| FOLD[Fold into the capability doc]
    FOLD --> TRUE([Doc describes<br/>reality again])

    classDef stop fill:#ffe5e5,stroke:#b02a2a,color:#5c1717
    classDef good fill:#e6f4ea,stroke:#1e7e34,color:#0f3d1a
    class STOP stop
    class TRUE,FOLD good
```

---

## 6. Adoption: an existing codebase

```mermaid
flowchart TD
    START([Existing codebase]) --> P1

    subgraph P1 [Phase 1 — orientation, about an hour]
        OV[Write docs/overview.md] --> INV[List capability NAMES only<br/>in docs/capabilities/README.md]
        INV --> VER[Point verify at whatever<br/>tests exist today]
        VER --> ADR0[ADR recording<br/>the starting state]
    end

    P1 --> WAIT{{"Stop here.<br/>Do NOT back-write<br/>documentation."}}

    WAIT --> TOUCH([A change touches<br/>an undocumented area])

    subgraph P2 [Phase 2 — lazy, ongoing]
        TOUCH --> RD[Read that code thoroughly]
        RD --> WRITE[Write the capability doc<br/>describing behaviour AS IT IS<br/>including the parts you dislike]
        WRITE --> CONF[Owner confirms accuracy]
        CONF --> NOW[Now run the normal<br/>full track]
    end

    P2 --> MORE([Next change])
    MORE -.-> TOUCH

    classDef warn fill:#fff3cd,stroke:#997404,color:#5c4504
    class WAIT warn
```

Documenting everything up front is weeks of work producing documents nobody
reads, drifting from the day they are written. After a few months of lazy
adoption the areas you actually work on are documented, and the dormant ones
cost you nothing.

---

## 7. Ownership and upgrade

```mermaid
flowchart LR
    subgraph repo [Your project repository]
        direction TB
        subgraph fw ["framework/ — framework-owned"]
            FWD[process docs<br/>templates<br/>skills<br/>scripts<br/>VERSION]
        end
        subgraph proj ["everything else — yours"]
            PD[docs/overview.md<br/>docs/amendments.md<br/>docs/architecture.md<br/>docs/capabilities/<br/>docs/changes/<br/>docs/adr/<br/>src/ test/ evals/<br/>scripts/project/<br/>.github/actions/setup/]
        end
    end

    UP[["framework/upgrade.sh"]] -->|"rm -rf framework/<br/>then copy"| FWD
    UP -.->|never touched| PD

    FWD -->|reads| PD

    classDef f fill:#e7f1ff,stroke:#2a5db0,color:#17315c
    classDef p fill:#e6f4ea,stroke:#1e7e34,color:#0f3d1a
    class FWD f
    class PD p
```

Where the framework needs project-specific content it **reads a file you own**
rather than containing it:

| Framework file | Reads your |
|---|---|
| `framework/constitution.md` | `docs/amendments.md` |
| `framework/craft.py` | `scripts/project/verify-impl.sh` |
| generated CI workflow | `.github/actions/setup/action.yml` |
| `AGENTS.md` | `docs/overview.md` |

`verify` warns when a framework-owned file has been edited locally, and names
the project-owned file the content belonged in.
