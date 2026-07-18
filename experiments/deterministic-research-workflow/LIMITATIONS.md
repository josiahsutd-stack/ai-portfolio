# Limitations

- Uses local synthetic/demo markdown documents only.
- Does not browse the live web.
- Planner behavior is deterministic and rule-based.
- Tool outputs are small summaries, not deep research synthesis.
- Human approval is represented as a required checkpoint, not an interactive review queue.
- SQLite traces are local development artifacts, not production observability.
- The implementation executes a fixed local workflow; it does not establish open-ended research capability.

## Unsupported Inferences

- Do not infer that this workflow can safely operate external tools.
- Do not infer production reliability from the local trace evaluator.
- Do not infer report factuality beyond retrieved local documents.
- Do not infer multi-user memory, authentication, or access controls.
