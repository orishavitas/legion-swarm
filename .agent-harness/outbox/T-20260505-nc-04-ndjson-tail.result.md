# Result: T-20260505-nc-04-ndjson-tail
task_id: T-20260505-nc-04-ndjson-tail
completed_at: 2026-05-12T00:02:00+03:00
NEXUS_VERIFICATION: PASSED

## Summary
Implemented `legion/ndjson_tail.py` with `MultiTailer` class. Maintains per-source byte offsets, detects truncation, skips malformed JSON lines, injects `repo` key. All 5 tests pass.

## Acceptance Criteria
- [x] `python -m pytest tests/test_legion_ndjson_tail.py -v` → 5 passed
- [x] Truncation resets offsets correctly
- [x] Malformed JSON lines skipped without raising
- [x] All changes committed on branch `task/T-20260505-nc-04-ndjson-tail`

## Verification Commands Run
```
python -m pytest tests/test_legion_ndjson_tail.py -v
# 5 passed in 0.05s
```

## Files Changed
- `legion/ndjson_tail.py` (new)
- `tests/test_legion_ndjson_tail.py` (new)
