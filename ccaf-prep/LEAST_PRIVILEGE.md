# Least privilege at the tool interface — scope tools so misuse is impossible, not discouraged

> When an agent misuses a broad, general-purpose tool (using a "fetch any URL" tool to run ad-hoc web
> searches), the deepest fix is to **narrow the tool's capability at its interface** so the misuse
> can't happen — not to *ask* it to stop, *filter* the bad cases, or *remove* a capability it
> legitimately needs. A D2 (tool design) pattern; the tool-design instance of the
> deterministic-by-construction axis in [`DISTRACTOR_HEURISTIC.md`](./DISTRACTOR_HEURISTIC.md).

## The principle: least privilege

Give each tool the **narrowest capability that does its job.** A tool that can do more than the task
requires is one the agent *will* eventually misuse — the broader the surface, the more off-label
behavior leaks in. The fix that holds is to **redesign the tool's contract** so the unwanted behavior is
structurally impossible (the tool can't express it), following the principle of least privilege.
"Constrain capability at the interface level" beats every fix that leaves the broad capability in place
and then tries to police it.

## The ladder of fixes (weakest → strongest)

For "a general-purpose tool is being misused for a different job":

| Fix | What it does | Why it's weaker |
|---|---|---|
| **Tell it to stop** (prompt) | Add an instruction: "use this only for X, not Y" | *Discourages*, doesn't prevent — probabilistic; the model can still do Y (distractor #2: prompt where determinism is needed). |
| **Patch the bad cases** (blocklist) | Filter/deny calls matching known-bad targets | *Leaky + maintenance-heavy* — a denylist is never complete (new bad targets slip through); treats the symptom, not the capability. |
| **Remove the tool** (over-correct) | Take the capability away and route it elsewhere | Throws out a capability the agent *legitimately needs*, and often **mixes concerns** by handing the job to the wrong component. |
| **Scope the tool** (least privilege) ✅ | Replace the broad tool with a purpose-specific one whose **inputs are validated** to the intended use | *Makes misuse impossible by construction* — the narrow contract can't express the off-label behavior. The root-cause fix. |

## "Validates inputs" — what that actually means

The strong fix replaces a do-anything tool with one whose **contract only accepts valid inputs for its
single purpose and rejects the rest.** For a document-loading tool, "validate the input points to a
document" means the tool checks the target really *is* a document — by file type / extension, by the
response content-type, or against an allowlist of document sources — and **refuses anything that isn't**
(a search-results page, an arbitrary web page). So the intuition is right: the tool confirms the target
*is a document*, which is exactly what makes it impossible to repurpose for fetching non-document pages.
**The validation is the enforcement** — it's what turns "please don't" into "can't."

## The discriminator

When a broad tool is being misused, ask: **does the fix leave the broad capability in place and police
it (prompt, blocklist, remove-and-reroute), or does it narrow the capability so misuse can't be
expressed?** The structural fix — a purpose-scoped tool with validated inputs — wins. Same family as
"deterministic gate beats prompt" (Axis B in `DISTRACTOR_HEURISTIC.md`), applied to *tool design*: the
guarantee lives in the tool's **contract**, not in an instruction or a filter.

## Don't confuse it with "route it to the right agent"

Re-routing the job to the correct component (e.g. [`HUB_AND_SPOKE.md`](./HUB_AND_SPOKE.md)) is the right
move *when the job belongs to another agent.* Here it's a trap: removing the URL-loading capability and
rerouting it would strip a capability the document agent **legitimately needs** (loading document URLs)
and hand it to an agent built for a different job (web search). The thing to constrain is the **tool's
scope**, not the routing.
