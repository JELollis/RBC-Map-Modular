<!--
Thanks for contributing to the RBC Community Map (modular build)!
Fill in the sections below. Delete any that don't apply.
-->

## Summary

<!-- What does this PR do, and why? One or two sentences is fine. -->

## Type of change

<!-- Put an "x" in the boxes that apply. -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that changes existing behavior)
- [ ] Refactor / modularization (no functional change)
- [ ] Documentation / assets only
- [ ] Build, packaging, or CI

## Related issues

<!-- e.g. "Closes #12", "Relates to #7". Leave blank if none. -->

## Changes

<!-- Bullet the notable changes. Mention any new/removed modules or dependencies. -->

-

## Testing

<!--
How did you verify this? The app is a PySide6 desktop client, so note whether
you launched it and what you exercised.
-->

- [ ] `python main.py` launches without errors
- [ ] Affected screens/dialogs behave as expected
- [ ] Existing sessions/database migrate cleanly (if schema changed)
- [ ] Ran on: <!-- Windows / macOS / Linux + Python version -->

## Screenshots

<!-- For UI changes, add before/after screenshots. Otherwise delete this section. -->

## Checklist

- [ ] Code follows the module layout (flat imports via `from imports import *`; new components live in their own module)
- [ ] No secrets, credentials, or personal session data committed (`sessions/`, `logs/` stay ignored)
- [ ] `VERSION_NUMBER` bumped if this is a release
- [ ] Docs / README updated if behavior or setup changed
