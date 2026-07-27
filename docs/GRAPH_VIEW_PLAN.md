# Graph View Implementation Plan

## Current State
- **124 total nodes** (all Documents: Slack threads + Drive PDF)
- **637 edges** connecting documents
- **Node types**: Currently only Document; will expand to People/Teams/Processes/Tools/Decisions once M3 (entity resolution) is wired

## Vision (from docs/knowledgegraph.md)
Build an **Obsidian-style force-directed graph view** under Browse > Graph with:
- ✅ Nodes colored by type (People/Teams/Processes/Tools/Decisions/Documents)
- ✅ Nodes sized by edge count (degree)
- ✅ Click node → open existing NodeDrawer
- ✅ **ACL-projected**: render only what current principal can see
- ✅ Graph visibly shrinks when switching CEO → contractor (demo the ACL model)

## Critical Requirement
**The ACL line is the differentiator.** Anyone can add d3-force. Making it re-project per principal demonstrates understanding of the invariants (invariant 5 & 17: never filter on client, all data is ACL-projected by server).

## Implementation Plan

### Phase 1: API Prep ✅ (Already done)
**File**: `src/company_brain/api/app.py` line 608+

The `/api/nodes/{id}` endpoint **already returns relations** with proper ACL filtering:
- Returns only edges where both source AND target nodes are visible to the principal
- Status quo: CEO sees 637 edges, contractor would see fewer (ACL-filtered subset)
- This is the critical mechanism that makes per-principal graphs work

**Response shape** (already correct):
```typescript
{
  id: string
  type: string
  title: string
  body: string
  sensitivity: string
  relations: Array<{
    predicate: string
    subject?: string
    subject_title?: string
    object: string        // node ID
    object_title: string
    confidence: number
    provenance: string
    status: string       // "accepted" | "pending" | "declined"
  }>
}
```

**No API changes needed** — the filtering is already there!

### Phase 2: Graph Component (`web/src/views/GraphView.tsx`)
**Responsibilities**:
- Load all visible nodes + edges via `/api/nodes?type=all`
- Build adjacency graph for d3-force
- Render with canvas (performant at 1000+ nodes)
- Color nodes by type
- Size nodes by degree (in-degree + out-degree)
- Handle zoom, pan, click-to-open-drawer

**Key constraint**: Use only data the API returns. The principal's visible set is already filtered server-side.

### Phase 3: UI Integration
**Location**: `web/src/views/` (new file alongside AskView.tsx, BrowseView.tsx)

Add link in left sidebar Browse section:
```
Browse
  - Graph
  - People
  - Teams
  - Processes
  - Tools
  - Decisions
  - Documents
```

### Phase 4: ACL Demo
**How to show it works**:
1. Load as CEO (7 accessible refs) → graph shows all visible documents
2. Click principal switcher → contractor (1 accessible ref)
3. Graph re-renders, nodes/edges shrink to only contractor-visible documents
4. **This is the proof**: different graphs for different access levels

## Technical Decisions

### Library: d3-force
- ✅ Minimal external dependencies
- ✅ Canvas-based rendering (scalable)
- ✅ Force-directed naturally clusters related nodes
- ✅ Familiar to anyone who's seen Obsidian/Roam

### Canvas vs SVG
- Use canvas for 1000+ nodes (performance)
- SVG for <200 nodes (simpler)
- Threshold: check node count at load time

### Color Scheme (from DESIGN_SYSTEM)
```
Document → using lucide icon color or semantic token
People → blue (from token set)
Teams → purple
Processes → green
Tools → orange
Decisions → red
```

### Node Sizing
Linear scale: `size = 10 + (degree / max_degree) * 30`
- Minimum: 10px (isolated node)
- Maximum: 40px (hub node)

## Data Flow

```
1. User loads /browse/graph
   ↓
2. GraphView.tsx mounts
   ↓
3. Fetch /api/nodes (already ACL-filtered)
   ↓
4. Build d3-force simulation
   ↓
5. Render canvas with animated forces
   ↓
6. On click → open NodeDrawer for that node ID
   ↓
7. On principal change → re-fetch & re-render
```

## Success Criteria

- [ ] Graph renders all 124 nodes without lag
- [ ] Nodes are colored by type (even if only Document type for now)
- [ ] Nodes are sized by degree
- [ ] Click node → NodeDrawer opens with correct node
- [ ] Switch principal → graph visibly changes
  - CEO sees full graph (all accessible docs)
  - Contractor sees smaller graph (fewer docs)
- [ ] Pan/zoom works smoothly
- [ ] TypeScript strict mode passes
- [ ] Matches DESIGN_SYSTEM (semantic colors, spacing, lucide icons)

## Not in Scope (yet)

- Entity resolution wiring (M3) — will add People/Teams/Processes nodes later
- Search within graph view — future enhancement
- Export/save layouts — future enhancement
- Community detection/clustering labels — future enhancement

## Next Steps

1. **Confirm API returns edges** — check if `/api/nodes/{id}` needs extension
2. **Build GraphView component** — d3-force + canvas
3. **Integrate into Browse sidebar** — add Graph link
4. **Test ACL projection** — load as CEO, switch to contractor, verify graph shrinks
5. **Performance test** — ensure smooth at 1000+ nodes
