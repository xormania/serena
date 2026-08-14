# API Reference

Serena's interface is its tools. This section documents them one by one: what each does,
what it takes, and which of those are required.

**If you are using Serena through an agent**, you do not need this — the agent reads these
same descriptions itself, and [Usage](../02-usage/000_intro) is where to start. This is for
anyone who needs the interface exactly: writing or debugging an MCP client, checking what a
tool will accept before calling it, or working out why an agent chose the arguments it did.

For a shorter view — every tool and one line about it — see [Tools](../01-about/035_tools).
This section describes the interface; the Python that implements it is a separate matter.

## Where this comes from

Each page is generated from the tool registry, using the two things the MCP server itself
sends to a client: the parameter schema built by `get_apply_fn_metadata_from_cls`, and the
docstring that `serena.mcp` parses for the tool's description and each parameter's text.

That is the point of generating it. The reference cannot describe a parameter the server
does not accept, or omit one it does, because it is reading the same definition the server
transmits. What you see here is what your client is told.

## What is not here yet

Every tool returns a string, and about half of them do not yet describe what that string
contains. Where a tool documents its return value it is shown; where it does not, nothing
is invented to fill the space. The gap is visible on purpose, and it is being worked
through — the tools whose returns are undocumented are exactly the ones this page will
grow a *Returns* line for.
