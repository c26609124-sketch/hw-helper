# Claude Code Development Guidelines

This document contains important guidelines for maintaining the Homework Helper AI codebase when working with Claude Code (or similar AI assistants).

## Badge Requirements for Update Changelogs

### Critical Rule: Badge Consistency

**Every badge type used in `version.json` changelog entries MUST exist in the `BADGE_COLORS` dictionary in `ui.py`.**

### Available Badge Types

The following badge types are currently supported (defined in `ui.py` line 1045):

| Badge Type | Color | Hex Code | Usage |
|------------|-------|----------|-------|
| `NEW` | Blue | `#1a73e8` | New features or additions |
| `FIX` | Green | `#34a853` | Bug fixes and corrections |
| `CRITICAL` | Red | `#ea4335` | Critical fixes or security issues |
| `UPDATE` | Yellow | `#fbbc04` | General updates or improvements |
| `SECURITY` | Orange | `#ff6b35` | Security-related changes |
| `COMPLETE` | Purple | `#9c27b0` | Completed features or milestones |
| `HOTFIX` | Bright Orange | `#f39c12` | Emergency hotfixes |
| `UX` | Teal | `#1abc9c` | User experience improvements |
| `TECHNICAL` | Gray | `#607d8b` | Technical notes or internal changes |
| `REMOVED` | Gray | `#9e9e9e` | Removed features or deprecations |
| `NOTE` | Indigo | `#5c6bc0` | Important notes and clarifications |

### How to Use Badges in Changelogs

Badges should be used as prefixes in changelog entries:

```json
{
  "version": "1.0.61",
  "date": "2025-11-12",
  "changes": [
    "NEW: Added dark mode support",
    "FIX: Fixed login button not responding",
    "CRITICAL: Security patch for authentication",
    "REMOVED: Deprecated legacy API endpoints"
  ]
}
```

### Adding New Badge Types

If you need to add a new badge type:

1. **Add to BADGE_COLORS dictionary** (ui.py, line 1045):
   ```python
   BADGE_COLORS = {
       # ... existing badges ...
       'YOURBADGE': '#hexcode',  # Brief description
   }
   ```

2. **Update this documentation** to list the new badge type

3. **Test the badge** by creating a changelog entry and viewing it in the update modal

### Why This Matters

The update modal parses changelog entries and creates visual badges for each prefix. If a changelog uses a badge type that doesn't exist in `BADGE_COLORS`, it will cause an error:

```python
badge_frame = ctk.CTkFrame(
    parent,
    fg_color=self.BADGE_COLORS[badge_type],  # KeyError if badge_type not in dict!
    # ...
)
```

## Module Import Guidelines

### Edmentum Components

All Edmentum question type components are imported at the top of `ui.py` (lines 43-51):

```python
from lib.edmentum import (
    EdmentumQuestionRenderer,
    EdmentumMultipleChoice,
    EdmentumMatchedPairs,
    EdmentumFillBlank,
    EdmentumHotSpot,
    EdmentumHotText,
    EdmentumOrdering
)
```

**DO NOT** add inline imports like `from edmentum_components import ...` in function bodies. These components are already imported at the top and should be referenced directly.

### Component Availability Check

Before using Edmentum components, check `EDMENTUM_RENDERER_AVAILABLE`:

```python
if EDMENTUM_RENDERER_AVAILABLE:
    component = EdmentumFillBlank(...)
```

This flag is automatically set to `False` if the import fails, ensuring graceful degradation.

## Print Statement Guidelines

### Always Use flush=True for Debugging Output

When adding print statements for debugging or status messages, **always** use `flush=True`:

```python
print(f"✓ Loaded version: {version}", flush=True)
print(f"⚠️ Error occurred: {error}", flush=True)
```

**Why?** On Windows systems, buffered output may not appear immediately in the console, making debugging difficult. `flush=True` forces immediate output.

## Version Loading

Version loading happens **synchronously** during app initialization (ui.py line 1370):

```python
# Load version synchronously (before any threads that might need it)
self.current_version = self._load_version()
```

**DO NOT** move version loading into daemon threads or background tasks. Version information must be available immediately and should produce visible console output for debugging.

## Error Reporting Configuration

Error reporting is configured via `config.json`:

```json
{
    "error_reporting": {
        "enabled": true,
        "endpoint": "https://api.slckr.xyz/api/report"
    }
}
```

Status is logged on startup for debugging:
```
📋 Error reporting: ENABLED
   Endpoint: https://api.slckr.xyz/api/report
```

## Common Pitfalls to Avoid

1. **Badge Mismatch**: Adding changelog entries with badges not in `BADGE_COLORS`
2. **Inline Imports**: Importing Edmentum components inside functions instead of using top-level imports
3. **Unbuffered Output**: Using `print()` without `flush=True` for Windows compatibility
4. **Threading Version Loading**: Loading version in daemon threads where errors are invisible

## Testing Checklist for Updates

Before committing version updates, verify:

- [ ] All badges in changelog exist in `BADGE_COLORS`
- [ ] No new inline `from edmentum_components import ...` statements
- [ ] All debugging print statements use `flush=True`
- [ ] Version loading happens synchronously, not in threads
- [ ] Error reporting status visible in console output

---

**Last Updated**: v1.0.66 (2025-11-13)
