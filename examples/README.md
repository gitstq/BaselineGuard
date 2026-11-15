# Examples

## `custom-rules.json`

A ready-to-use **extend** rule set. It overrides one built-in rule (`css-nesting`
becomes forbidden) and adds one project-specific rule. Try it:

```bash
PYTHONPATH=src python3 -m baselineguard rules validate examples/custom-rules.json
PYTHONPATH=src python3 -m baselineguard scan tests/fixtures --rules examples/custom-rules.json
PYTHONPATH=src python3 -m baselineguard rules list --rules examples/custom-rules.json --status deprecated
```

Set `"mode": "replace"` if you want to ship only your own rules and ignore the
41 built-in ones.

### Required fields for each rule

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | lowercase slug, unique |
| `name` | string | human readable |
| `category` | string | `css` / `markup` / `script` / `api` (informational) |
| `status` | string | `widely` / `newly` / `limited` / `deprecated` |
| `baseline_year` | int or null | required for `widely` / `newly`; null for `limited` / `deprecated` |
| `applies_to` | array | subset of `css`, `markup`, `script` |
| `patterns` | array of regex | Python `re` syntax; escape backslashes in JSON |
| `suggestion` | string | actionable guidance shown in reports and agent context |
| `reference` | string | documentation URL |

## Fixtures used by the demo and tests

`tests/fixtures/` contains a tiny HTML/CSS/JS sample that deliberately mixes
widely available features, newly available features and deprecated tags. It is
also what `scripts/demo.sh` scans, so every demo command is reproducible offline.
