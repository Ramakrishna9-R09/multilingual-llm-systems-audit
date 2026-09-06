# Part C - Decision memo: launch a gated prompt-only style control

**Recommendation: choose (c), prompt engineering only, for the three-week
launch.** Feature-flag it per language. Only Hindi and Kannada may be enabled
after human validation; leave the other four off until a qualified native
reviewer is available. Automated checks cannot certify natural register.

## Assumptions

- Staging runs the existing assistant without an external API; responses must
  preserve content and safety behavior.
- The Hindi/Kannada reviewer makes one blinded style/meaning/safety comparison
  in 90 seconds and is available for two weeks (20 hours).
- A 60-token style instruction is sufficient to test the control; measure its
  true count on the production model before launch.

## Back-of-the-envelope arithmetic

Create 200 realistic response situations per language: 1,200 prompts total.
For Hindi/Kannada, run four variants plus baseline (200 × 2 × 5 = 2,000
responses); run the winner through automated smoke checks elsewhere. Reviewer
capacity is 20 h × 60 / 1.5 = **800** comparisons: 80 duplicate calibration,
640 for 320 Hindi + 320 Kannada candidate-vs-baseline judgments, and 80
high-risk cases.

This uses **zero A100 training days** and no second model call. At 100,000
requests/day, a 60-token instruction adds 6 million input tokens/day. A
rewriter adds a sequential inference pass; synthetic SFT burns the window on
an artifact the available reviewer cannot validate in four languages. Keep the
28 A100-days as contingency.

## Success metric and gate

For Hindi and Kannada separately, the prompt must win at least **65%** of
blinded comparisons, have a 95% Wilson lower bound above 55%, and have no more
than **2% critical meaning, safety, or appropriateness failures**. The 80
duplicates need ≥80% within-reviewer agreement; never pool languages.

## Kill criterion

By the end of week 2, abandon it if either validated language has <60%
preference, >5% critical failures, or <70% duplicate agreement. Do not
silently move to synthetic SFT; it needs a reviewed data-quality gate. Keep
unreviewed languages off even if automated tests pass.

## First experiment - day 1

Write four concise prompts with positive register examples, prohibited
textbook markers, meaning preservation, and script constraints. Run baseline
plus variants on 100 fixed Hindi/Kannada situations; blind and randomize the
outputs. The reviewer scores casualness, meaning, and critical failures. Select
at most one per language for the 320-comparison gate.
