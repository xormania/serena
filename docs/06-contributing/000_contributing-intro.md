# Contributing

**If you want to *use* Serena** — connect it to a coding agent, configure languages, work with
projects — [Usage](../02-usage/000_intro) is where to start. Nothing in this section is needed for
that.

This section is for working on Serena itself. The policy for a contribution — what can go
straight to a pull request and what wants an issue first — is set by
[CONTRIBUTING.md](https://github.com/oraios/serena/blob/main/CONTRIBUTING.md) at the repository
root; that file is the authority, and this section defers to it wherever they touch the same
ground. What this section carries is everything a policy file cannot: the day-to-day mechanics,
the conventions the code holds itself to, and a guided way into the source.

In the order a new contributor meets them:

1. **[The development loop](010_development-loop)** — the four commands that gate every change,
   how the tests are selected and skipped, what CI actually runs against a pull request, and the
   generated files that are regenerated rather than edited.
2. **[House style](020_house-style)** — the design, testing and docstring conventions, rendered
   from the project's own checked-in doctrine.
3. **[Adding language support](030_adding-a-language)** — the most common substantial
   contribution, mapped end to end.
4. **[FAQ](040_faq)** — the questions that keep arriving on the tracker, answered the way the
   maintainers answered them, with the threads linked.
5. **[Code Reference](code-reference/000_code-reference-intro)** — generated from the docstrings
   in `src/serena`, ordered the way you meet the package rather than alphabetically: readable
   forwards on a first pass, a lookup afterwards.
