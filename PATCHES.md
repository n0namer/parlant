# MNNZ Fork Patch Inventory

This file tracks **local changes to upstream-owned behavior/files** that must be considered during every upstream upgrade.

## Current inventory

**No accepted upstream-core patches yet.**

Current MNNZ work should prefer adapters/extensions and external integration code. Documentation/governance files added by the fork are not counted as upstream-core product patches, but they are part of the durable fork overlay.

## Patch record template

Copy this section for every unavoidable upstream-core patch:

```md
### MNNZ-PATCH-XXX — short name

- Status: LOCAL_PATCH_STILL_REQUIRED | LOCAL_PATCH_NEEDS_REBASE | UPSTREAM_FIXED | SEMANTIC_CONFLICT | PATCH_OBSOLETE
- Purpose:
- Owner:
- Introduced fork SHA:
- Upstream baseline SHA:
- Paths/symbols:
- Acceptance tests:
- Security/safety implications:
- Upstream issue/PR:
- Removal condition:
- Latest semantic-overlap review:
  - upstream candidate SHA:
  - textual overlap: yes/no
  - semantic overlap: yes/no/unknown
  - reason:
  - action:
```

## Rules

- Do not hide a core patch inside an unrelated commit.
- Do not replay a patch into a new upstream baseline until it is classified.
- If upstream fixes the need, classify `UPSTREAM_FIXED` and prove the acceptance test before removing our patch.
- If semantic overlap is unknown for a material patch, upgrade promotion is blocked.
- A conflict-free rebase is not sufficient evidence.
