"""Shared variant normalization: converts a VCF-style (1-based POS, REF, ALT)
into a minimal, SPDI-comparable (0-based position-of-first-difference,
deleted, inserted) tuple by trimming shared suffix then shared prefix bases.

Applying the SAME function to (a) VCF-style records (GIAB, bundle files,
which use an anchor base for indels) and (b) dbSNP's own SPDI deleted/
inserted fields reinterpreted as (pos0+1, deleted, inserted) makes both sides
directly comparable -- SPDI has no anchor base to begin with, so normalizing
it is a no-op (verified: the function is idempotent on already-minimal input).

Known limitation (documented, not silently assumed away): this is prefix/
suffix trimming only, not full contextual (reference-sequence-aware)
left/right-shifting within homopolymer or short-tandem-repeat runs. Two
tools can both report a "minimal" but differently-anchored representation of
the same indel inside a repeat (e.g. a 1bp deletion in a poly-A run can be
placed at several equivalent positions); such cases will not match here
unless the two sources happened to choose the same anchor. This affects a
minority of indels (short, low-complexity contexts) and is reported as a
limitation, not corrected via reference-sequence lookups in this pass.
"""


def normalize(pos1based, ref, alt):
    ref = list(ref)
    alt = list(alt)
    # trim shared suffix
    while ref and alt and ref[-1] == alt[-1] and (len(ref) > 1 and len(alt) > 1):
        ref.pop()
        alt.pop()
    # one more suffix char can be shared even down to length 1 on one side
    while ref and alt and ref[-1] == alt[-1]:
        ref.pop()
        alt.pop()
        if not ref or not alt:
            break
    # trim shared prefix
    prefix_len = 0
    while prefix_len < len(ref) and prefix_len < len(alt) and ref[prefix_len] == alt[prefix_len]:
        prefix_len += 1
    new_pos0 = (pos1based - 1) + prefix_len
    deleted = "".join(ref[prefix_len:])
    inserted = "".join(alt[prefix_len:])
    return new_pos0, deleted, inserted


if __name__ == "__main__":
    # self-tests against hand-worked examples
    cases = [
        # (pos1based, ref, alt) -> expected (pos0, deleted, inserted)
        ((100, "A", "G"), (99, "A", "G")),              # SNV, no anchor
        ((100, "AG", "A"), (100, "G", "")),              # 1bp deletion, anchor A
        ((100, "A", "AG"), (100, "", "G")),              # 1bp insertion, anchor A
        ((100, "CAG", "CG"), (100, "A", "")),             # deletion of middle base (0-based: C@99,A@100,G@101)
        ((100, "G", "G"), (99, "", "")),                   # degenerate (should not occur in real data)
    ]
    for (p, r, a), expected in cases:
        got = normalize(p, r, a)
        status = "OK" if got == expected else "FAIL"
        print(f"{status}: normalize({p},{r!r},{a!r}) = {got}  (expected {expected})")

    # idempotency check: SPDI-style input (no anchor) should pass through unchanged
    spdi_like = [(101, "G", ""), (100, "", "G"), (99, "A", "G")]
    for p, d, i in spdi_like:
        got = normalize(p, d, i)
        expected = (p - 1, d, i)
        status = "OK" if got == expected else "FAIL"
        print(f"{status}: normalize (SPDI passthrough) ({p},{d!r},{i!r}) = {got} (expected {expected})")
