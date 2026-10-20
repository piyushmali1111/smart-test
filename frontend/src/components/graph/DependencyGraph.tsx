import React, { useMemo, useCallback } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import dagre from 'dagre';
import { GraphNodeComponent } from './GraphNode';
import type { GraphResponse, AffectedResponse } from '../../api/types';
import { useScenarioStore } from '../../store/useScenarioStore';

interface DependencyGraphProps {
  graphData: GraphResponse;
  affectedData: AffectedResponse;
  onNodeClick?: (id: string, shiftKey: boolean) => void;
}

const nodeTypes = {
  customNode: GraphNodeComponent,
};

export const DependencyGraph: React.FC<DependencyGraphProps> = ({
  graphData,
  affectedData,
  onNodeClick,
}) => {
  const { changedIds, toggleChanged } = useScenarioStore();

  const affectedMap = useMemo(() => {
    const map = new Map<string, number>();
    for (const a of affectedData.affected) {
      map.set(a.id, a.distance);
    }
    return map;
  }, [affectedData.affected]);

  const cycleNodeSet = useMemo(() => {
    const set = new Set<string>();
    for (const group of affectedData.sccGroups) {
      for (const id of group) {
        set.add(id);
      }
    }
    return set;
  }, [affectedData.sccGroups]);

  // Compute Dagre auto layout
  const { initialNodes, initialEdges } = useMemo(() => {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));
    dagreGraph.setGraph({ rankdir: 'LR', nodesep: 50, ranksep: 120 });

    const nodeWidth = 170;
    const nodeHeight = 65;

    graphData.nodes.forEach((node) => {
      dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
    });

    graphData.edges.forEach((edge) => {
      dagreGraph.setEdge(edge.source, edge.target);
    });

    dagre.layout(dagreGraph);

    const nodes: Node[] = graphData.nodes.map((node) => {
      const pos = dagreGraph.node(node.id);
      const isChanged = changedIds.includes(node.id);
      const isAffected = affectedMap.has(node.id);
      const distance = affectedMap.get(node.id);

      let status: 'changed' | 'affected' | 'unaffected' = 'unaffected';
      if (isChanged) status = 'changed';
      else if (isAffected) status = 'affected';

      return {
        id: node.id,
        type: 'customNode',
        position: {
          x: pos ? pos.x - nodeWidth / 2 : 0,
          y: pos ? pos.y - nodeHeight / 2 : 0,
        },
        data: {
          label: node.label,
          file: node.file,
          kind: node.kind,
          status,
          distance,
          inCycle: cycleNodeSet.has(node.id),
        },
      };
    });

    const edges: Edge[] = graphData.edges.map((edge, idx) => {
      const sourceAffected = affectedMap.has(edge.source) || changedIds.includes(edge.source);
      const targetAffected = affectedMap.has(edge.target);
      const isHot = sourceAffected && targetAffected;

      return {
        id: `e-${edge.source}-${edge.target}-${idx}`,
        source: edge.source,
        target: edge.target,
        animated: isHot,
        style: {
          stroke: isHot ? 'var(--warn)' : 'rgba(148, 163, 184, 0.35)',
          strokeWidth: isHot ? 2 : 1,
        },
      };
    });

    return { initialNodes: nodes, initialEdges: edges };
  }, [graphData, affectedMap, changedIds, cycleNodeSet]);

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      if (onNodeClick) {
        onNodeClick(node.id, false);
      } else {
        toggleChanged(node.id, false);
      }
    },
    [onNodeClick, toggleChanged]
  );

  return (
    <div className="relative h-full w-full rounded-panel overflow-hidden bg-bg-3 border border-border">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        onNodeClick={handleNodeClick}
        fitView
        minZoom={0.2}
        maxZoom={1.8}
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={24}
          size={1}
          color="rgba(148, 163, 255, 0.12)"
        />

        <Controls
          showInteractive={false}
          className="!bg-bg-2 !border-border !rounded-panel overflow-hidden [&>button]:!bg-bg-3 [&>button]:!border-border [&>button]:!text-text-muted [&>button:hover]:!bg-bg-4 [&>button:hover]:!text-brand"
        />

        <MiniMap
          nodeColor={(node) => {
            const data = node.data as any;
            if (data?.status === 'changed') return 'var(--danger)';
            if (data?.status === 'affected') return 'var(--warn)';
            return 'var(--slate)';
          }}
          className="!bg-bg-1/90 !border !border-border !rounded-panel overflow-hidden"
          maskColor="rgba(11, 16, 32, 0.7)"
          zoomable
          pannable
        />
      </ReactFlow>
    </div>
  );
};
