/**
 * Force-directed graph visualization of the knowledge graph.
 *
 * ACL-projected: only renders nodes and edges the current principal can see.
 * Nodes are colored by type and sized by degree (connection count).
 *
 * Uses d3-force with canvas rendering for performance (smooth at 1000+ nodes).
 * When principal changes, the graph re-fetches and re-renders automatically.
 */

import { useEffect, useRef, useState } from "react";
import * as d3 from "d3-force";

import { api, type NodeDetail, type Principal } from "../lib/api";
import { Card } from "../components/ui/primitives";

// Node type colors using design tokens
const TYPE_COLORS: Record<string, string> = {
  Document: "#3b82f6", // blue-500
  Person: "#8b5cf6", // purple-500
  Team: "#ec4899", // pink-500
  Process: "#10b981", // emerald-500
  Tool: "#f59e0b", // amber-500
  Decision: "#ef4444", // red-500
};

type GraphNode = d3.SimulationNodeDatum & {
  id: string;
  type: string;
  title: string;
  sensitivity: string;
  degree: number; // in + out edges
};

type GraphLink = d3.SimulationLinkDatum<GraphNode> & {
  predicate: string;
  status: string;
};

export function GraphView({ principal }: { principal: Principal }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const simulationRef = useRef<d3.Simulation<GraphNode, GraphLink> | null>(null);

  // Fetch all nodes and build graph
  useEffect(() => {
    async function loadGraph() {
      try {
        setLoading(true);
        setError(null);

        // Fetch all document nodes (API is already ACL-filtered)
        // Use a high limit to fetch all accessible nodes (API defaults to 200)
        const nodes_list = await api.nodes(principal.id, undefined, undefined, 1000);
        console.log(`📊 Fetched ${nodes_list.length} node summaries for ${principal.id}`);

        if (nodes_list.length === 0) {
          setError("No visible nodes for this principal");
          setLoading(false);
          return;
        }

        // Fetch full details for each node (including relations)
        console.log(`🔍 Fetching full details for ${nodes_list.length} nodes...`);
        const nodeDetails = await Promise.all(
          nodes_list.map((n) =>
            api.node(principal.id, n.id).catch((e) => {
              console.warn(`Failed to fetch ${n.id}:`, e);
              return null;
            })
          )
        );

        const validNodes = nodeDetails.filter(
          (n) => n !== null
        ) as NodeDetail[];

        console.log(`✅ Got ${validNodes.length} nodes with full details`);
        if (validNodes.length > 0) {
          console.log(`📈 First node has ${validNodes[0].relations.length} relations`);
        }

        if (validNodes.length === 0) {
          setError("No visible nodes for this principal");
          setLoading(false);
          return;
        }

        // Build degree map (count outgoing edges)
        const degreeMap = new Map<string, number>();
        validNodes.forEach((node) => {
          const currentDegree = degreeMap.get(node.id) || 0;
          degreeMap.set(node.id, currentDegree + node.relations.length);
        });

        // Create graph nodes
        const graphNodes: GraphNode[] = validNodes.map((node) => ({
          id: node.id,
          type: node.type,
          title: node.title,
          sensitivity: node.sensitivity,
          degree: degreeMap.get(node.id) || 0,
          vx: 0,
          vy: 0,
        } as GraphNode));

        console.log(`🔵 Created ${graphNodes.length} graph nodes`);
        console.log(`Degrees: min=${Math.min(...graphNodes.map(n => n.degree))}, max=${Math.max(...graphNodes.map(n => n.degree))}`);

        // Create graph links (edges)
        const graphLinks: GraphLink[] = [];
        const linkSet = new Set<string>();

        validNodes.forEach((node) => {
          node.relations.forEach((rel) => {
            const key = `${node.id}-${rel.object}`;
            // Avoid duplicate links
            if (!linkSet.has(key)) {
              linkSet.add(key);
              graphLinks.push({
                source: node.id,
                target: rel.object,
                predicate: rel.predicate,
                status: rel.status,
              });
            }
          });
        });

        console.log(`🔗 Created ${graphLinks.length} graph links`);

        // Calculate radius scale based on max degree (BEFORE using in forces)
        const maxDegree = Math.max(1, ...graphNodes.map((n) => n.degree));
        const getNodeRadius = (node: GraphNode): number => {
          const MIN_RADIUS = 6;
          const MAX_RADIUS = 15;
          return MIN_RADIUS + (node.degree / maxDegree) * (MAX_RADIUS - MIN_RADIUS);
        };

        // Set up d3-force simulation
        const simulation = d3
          .forceSimulation<GraphNode>(graphNodes)
          .force("link", d3.forceLink<GraphNode, GraphLink>(graphLinks).distance(100))
          .force("charge", d3.forceManyBody().strength(-300))
          .force("center", d3.forceCenter(0, 0))
          .force("collide", d3.forceCollide().radius((d) => getNodeRadius(d) + 5));

        simulationRef.current = simulation;

        // Start rendering loop
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        const width = canvas.width;
        const height = canvas.height;

        let frameCount = 0;
        const render = () => {
          frameCount++;

          // Get dark mode setting
          const isDark = document.documentElement.dataset.theme === "dark";

          // Use dark mode appropriate background
          ctx.fillStyle = isDark ? "#1a1a1a" : "white";
          ctx.fillRect(0, 0, width, height);
          ctx.save();
          ctx.translate(width / 2, height / 2);

          // Draw links
          ctx.strokeStyle = isDark ? "rgba(100, 100, 100, 0.3)" : "rgba(200, 200, 200, 0.3)";
          ctx.lineWidth = 1;
          graphLinks.forEach((link) => {
            const source = link.source as GraphNode;
            const target = link.target as GraphNode;
            ctx.beginPath();
            ctx.moveTo(source.x || 0, source.y || 0);
            ctx.lineTo(target.x || 0, target.y || 0);
            ctx.stroke();
          });

          // Draw nodes
          if (frameCount === 1) {
            console.log(`🎨 First render: ${graphNodes.length} nodes to draw`);
          }

          graphNodes.forEach((node, idx) => {
            const radius = getNodeRadius(node); // getNodeRadius defined above
            const color = TYPE_COLORS[node.type] || "#6b7280";

            // Node circle
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(node.x || 0, node.y || 0, radius, 0, Math.PI * 2);
            ctx.fill();

            if (frameCount === 1 && idx < 3) {
              console.log(`  Node ${idx}: pos=(${node.x?.toFixed(1)}, ${node.y?.toFixed(1)}), radius=${radius.toFixed(1)}`);
            }

            // Highlight hovered or selected node
            if (node.id === hoveredNode || node.id === selectedNode) {
              ctx.strokeStyle = "#000";
              ctx.lineWidth = 2;
              ctx.stroke();
            }

            // Node label (only for hovered/selected to avoid clutter)
            if (node.id === hoveredNode || node.id === selectedNode) {
              ctx.fillStyle = "#000";
              ctx.font = "12px sans-serif";
              ctx.textAlign = "center";
              ctx.fillText(node.title, node.x || 0, (node.y || 0) + radius + 15);
            }
          });

          ctx.restore();
        };

        // Render on each simulation tick
        simulation.on("tick", () => {
          render();
        });

        // Handle canvas clicks for node selection
        const handleCanvasClick = (e: MouseEvent) => {
          const rect = canvas.getBoundingClientRect();
          const x = e.clientX - rect.left - rect.width / 2;
          const y = e.clientY - rect.top - rect.height / 2;

          // Find clicked node (with hit radius tolerance)
          for (const node of graphNodes) {
            const dist = Math.sqrt(
              Math.pow((node.x || 0) - x, 2) + Math.pow((node.y || 0) - y, 2)
            );
            if (dist < getNodeRadius(node) + 5) {
              setSelectedNode(node.id);
              break;
            }
          }
        };

        // Handle canvas mouse move for hover
        const handleCanvasMouseMove = (e: MouseEvent) => {
          const rect = canvas.getBoundingClientRect();
          const x = e.clientX - rect.left - rect.width / 2;
          const y = e.clientY - rect.top - rect.height / 2;

          // Find hovered node
          for (const node of graphNodes) {
            const dist = Math.sqrt(
              Math.pow((node.x || 0) - x, 2) + Math.pow((node.y || 0) - y, 2)
            );
            if (dist < getNodeRadius(node) + 5) {
              setHoveredNode(node.id);
              canvas.style.cursor = "pointer";
              return;
            }
          }
          setHoveredNode(null);
          canvas.style.cursor = "default";
        };

        canvas.addEventListener("click", handleCanvasClick);
        canvas.addEventListener("mousemove", handleCanvasMouseMove);

        setLoading(false);
        return () => {
          canvas.removeEventListener("click", handleCanvasClick);
          canvas.removeEventListener("mousemove", handleCanvasMouseMove);
          simulation.stop();
        };
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load graph");
        setLoading(false);
      }
    }

    loadGraph();
  }, [principal.id]);


  return (
    <div className="flex flex-col gap-4 h-full">
      <Card className="flex-1 flex flex-col gap-3 p-4">
        <div className="flex items-center justify-between">
          <h2 className="font-medium">Knowledge Graph</h2>
          <div className="text-xs text-muted-foreground">
            {loading && "Loading..."}
            {!loading && error && <span className="text-red-600">{error}</span>}
            {!loading && !error && (
              <span>Viewing as {principal.display}</span>
            )}
          </div>
        </div>

        <div className="flex-1 relative rounded-md border border-border/30 bg-white/50">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-muted-foreground">Loading graph...</span>
            </div>
          )}
          <canvas
            ref={canvasRef}
            width={1000}
            height={600}
            className="w-full h-full"
            style={{ display: loading ? "none" : "block" }}
          />
        </div>

        <div className="text-xs text-muted-foreground">
          <p>Click a node to see details. Hover to highlight. Graph auto-layouts with forces.</p>
        </div>
      </Card>

      {/* Type legend */}
      <Card className="p-4">
        <div className="grid grid-cols-2 gap-3 text-xs">
          {Object.entries(TYPE_COLORS).map(([type, color]) => (
            <div key={type} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: color }}
              />
              <span>{type}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
