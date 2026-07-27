Read docs/DESIGN_SYSTEM.md, api/app.py, and web/src/views/ — then check whether
/api/nodes already returns edges before adding an endpoint.

Build an Obsidian-style graph view under Browse > Graph: force-directed layout,
nodes colored by type (People/Teams/Processes/Tools/Decisions/Documents), sized by
edge count, click a node to open the existing NodeDrawer.

The graph must be ACL-projected — render only what the current principal can see,
and it should visibly shrink when I switch from ceo to contractor. That's the
demo, not decoration.

d3-force is fine to add. Use canvas, not SVG, above ~1000 nodes.

Plan first. Don't touch the retrieval or ACL code — this is a view over data that
already exists.

Two things before you send it:

Re-ingest first. You're at 28 nodes / 43 edges. That renders as a handful of dots, not the screenshot — and worse, the reviewer builds and tunes the layout against a graph too small to reveal any clustering problems.

The ACL line is the one that earns the grade. Anyone can prompt "build a graph view" and get d3-force. Requiring the graph to re-project per principal is a requirement only someone who knows this codebase would write, and it's demonstrable in one click during a demo