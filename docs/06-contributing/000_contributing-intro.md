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

1. **[Getting started](010_getting-started)** — from a fresh clone to a verified change: the
   environment, the four commands that gate every commit, how the tests are selected and
   skipped, what CI runs against a pull request, and the files that are generated rather than
   edited.
2. **[Using Serena on Serena](015_using-serena)** — keep your daily server on current
   `main`, run a specific branch when testing calls for it, and let the diagnostics tools
   tell you what each edit did.
3. **[House style](020_house-style)** — the design, testing and docstring conventions, rendered
   from the project's own checked-in doctrine.
4. **[Adding language support](030_adding-a-language)** — the most common substantial
   contribution, mapped end to end.
5. **[Scripts](035_scripts)** — the map of `scripts/`: demos that run tools without an
   agent attached, the generators, and the introspection utilities.
6. **[FAQ](040_faq)** — the questions that keep arriving on the tracker, answered the way the
   maintainers answered them, with the threads linked.
7. **[Code Reference](code-reference/000_code-reference-intro)** — generated from the docstrings
   in `src/serena`, ordered the way you meet the package rather than alphabetically: readable
   forwards on a first pass, a lookup afterwards.
