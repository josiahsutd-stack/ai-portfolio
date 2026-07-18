# Limitations

## Language Coverage

- Deterministic regular expressions and a small programme-feature dictionary only.
- Unrecognized wording remains in the message log but does not enter the ledger.
- Number words, coreference, negation beyond documented forms, temporal reasoning, implied decisions, attachments, tables, images, and speech transcripts are not handled.

## Requirement Semantics

- Conflicts require the same normalized key; semantically related requirements with different keys may escape detection.
- Units are recognized only for the implemented fields, and no jurisdiction-specific conversion or validation is performed.
- Completeness checks are category presence checks, not project-type or regulatory adequacy review.

## Authority And Audit

- Roles are selected in the interface and are not authenticated.
- SQLite events are append-only through the application API but are not tamper-evident or digitally signed.
- The bundled role matrix is illustrative and cannot establish contractual authority.

## Specification Output

- The output is a coordination draft, not a professional specification, contract document, tender package, employer's requirement, scope of work, or authority submission.
- No product standards, code clauses, drawings, BIM models, schedules, or cost plans are incorporated.
- Human review is mandatory before any project use.

## Evaluation

- Five synthetic fixtures were authored around the implemented grammar.
- Perfect fixture scores indicate deterministic regression consistency only.
- The separate 33-case language stress set is also manually labeled and not blinded or independently labeled; it retains 2 number-word misses.
- Real-project performance, stakeholder acceptance, security, and workflow impact remain untested.
