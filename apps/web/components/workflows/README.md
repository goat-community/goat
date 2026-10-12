# Workflows Feature - Implementation Guide

> **Status**: Phase 5 - Execution Engine (In Progress)  
> **Last Updated**: February 2, 2026  
> **Related Features**: Layouts, GenericTool/Toolbox, Windmill

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Model](#data-model)
4. [UI Specifications](#ui-specifications)
5. [Execution Logic](#execution-logic)
6. [API Endpoints](#api-endpoints)
7. [Implementation Phases](#implementation-phases)
8. [File Structure](#file-structure)
9. [Design Decisions](#design-decisions)
10. [Future Considerations](#future-considerations)

---

## Overview

Workflows allow users to chain multiple tools (processes) together in a visual DAG (Directed Acyclic Graph) editor. Users can drag and drop tools, connect them, configure parameters, and execute them sequentially.

### Key Features

- Visual workflow editor using ReactFlow (@xyflow/react - already installed)
- Drag-and-drop tools from a sidebar palette
- Connect tool outputs to tool inputs via edges
- Configure tool parameters in a side panel
- Execute workflows: "Run Node" or "Run to Here"
- Auto-save workflow changes
- Project layers displayed as read-only reference

### Similar To

- **Layouts**: Same project-scoped CRUD pattern, auto-save, similar panel structure
- **GenericTool**: Reuse OGC process descriptions for tool configuration forms

---

## Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WORKFLOW EDITOR                                 │
│  ┌─────────────┐    ┌─────────────────────────────┐    ┌─────────────────┐  │
│  │   Config    │    │      ReactFlow Canvas       │    │     Nodes       │  │
│  │   Panel     │    │                             │    │     Panel       │  │
│  │             │    │  [Dataset] ──▶ [Tool] ──▶ [Tool]                   │  │
│  │ • Workflows │    │                             │    │ • Import        │  │
│  │ • Layers    │    │                             │    │ • Accessibility │  │
│  │   (view)    │    │                             │    │ • Geoanalysis   │  │
│  └─────────────┘    └─────────────────────────────┘    └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ (on Run)
                              ┌───────────────┐
                              │   Core API    │
                              │ /execute      │
                              └───────────────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │   Windmill    │
                              │ workflow_runner│
                              │ (@task per node)│
                              └───────────────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │   Poll Status │
                              │ (every 2 sec) │
                              └───────────────┘
```

### Why Windmill "Workflows as Code"

1. **Browser-Independent**: Users can close browser, workflow continues running
2. **Single Source of Truth**: Windmill stores all job state (no duplicate in our DB)
3. **Real-Time Progress**: `workflow_as_code_status` shows which node is running
4. **Existing Infrastructure**: Reuse same tools, same job polling, same UI patterns
5. **Per-Step Tracking**: Each `@task` is a tracked sub-job in Windmill

### Key Components

| Component       | Location                             | Purpose                                       |
| --------------- | ------------------------------------ | --------------------------------------------- |
| Workflow Editor | `apps/web/components/workflows/`     | ReactFlow-based visual editor                 |
| Workflow API    | `apps/core/endpoints/v2/workflow.py` | CRUD + execute endpoint                       |
| Workflow Runner | `goatlib/tools/workflow_runner.py`   | Windmill script that orchestrates execution   |
| Job Polling     | `apps/web/hooks/jobs/JobStatus.tsx`  | Existing pattern for tracking running jobs    |
| Processes API   | `apps/processes/`                    | Proxies to Windmill for job submission/status |

---

## Data Model

### Backend (PostgreSQL)

**Table: `customer.workflow`**

| Column          | Type        | Description                         |
| --------------- | ----------- | ----------------------------------- |
| `id`            | UUID        | Primary key                         |
| `project_id`    | UUID        | FK to `project.id` (CASCADE delete) |
| `name`          | TEXT        | Workflow name                       |
| `description`   | TEXT        | Optional description                |
| `is_default`    | BOOLEAN     | Default workflow for project        |
| `config`        | JSONB       | ReactFlow nodes, edges, viewport    |
| `thumbnail_url` | TEXT        | Preview image URL                   |
| `created_at`    | TIMESTAMPTZ | Creation timestamp                  |
| `updated_at`    | TIMESTAMPTZ | Last update timestamp               |

**Pydantic Schemas** (`apps/core/src/core/schemas/workflow.py`):

```python
class WorkflowBase(BaseModel):
    name: str
    description: str | None = None
    is_default: bool = False
    config: dict  # WorkflowConfig JSON

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_default: bool | None = None
    config: dict | None = None

class WorkflowRead(WorkflowBase):
    id: UUID
    project_id: UUID
    thumbnail_url: str | None
    created_at: datetime
    updated_at: datetime
```

### Frontend (TypeScript/Zod)

**File: `apps/web/lib/validations/workflow.ts`**

```typescript
import * as z from "zod";

// Node status during execution
export const nodeStatusSchema = z.enum([
  "idle",
  "pending",
  "running", 
  "completed",
  "error",
]);

// Dataset node - references a layer by UUID
export const datasetNodeDataSchema = z.object({
  type: z.literal("dataset"),
  label: z.string(),
  layerId: z.string().uuid().optional(),    // Layer UUID (from project, explorer, or catalog)
  layerName: z.string().optional(),
  geometryType: z.string().optional(),
  filter: z.record(z.unknown()).optional(), // Workflow filter (independent from layer's CQL)
});

// Tool node - represents a process
export const toolNodeDataSchema = z.object({
  type: z.literal("tool"),
  processId: z.string(),                    // e.g., "buffer", "catchment_area"
  label: z.string(),
  config: z.record(z.unknown()),            // Tool parameters (excluding layer inputs)
  status: nodeStatusSchema.optional(),
  outputLayerId: z.string().uuid().optional(),  // Result layer UUID after execution (temporary, not added to project)
  jobId: z.string().optional(),             // Windmill job ID during execution
  error: z.string().optional(),
});

// Workflow node (ReactFlow compatible)
export const workflowNodeSchema = z.object({
  id: z.string(),
  type: z.enum(["dataset", "tool"]),
  position: z.object({ x: z.number(), y: z.number() }),
  data: z.union([datasetNodeDataSchema, toolNodeDataSchema]),
  width: z.number().optional(),
  height: z.number().optional(),
  selected: z.boolean().optional(),
});

// Workflow edge (ReactFlow compatible)  
export const workflowEdgeSchema = z.object({
  id: z.string(),
  source: z.string(),              // Source node ID
  target: z.string(),              // Target node ID
  sourceHandle: z.string().optional(), // Output handle ID
  targetHandle: z.string().optional(), // Input handle ID (e.g., "input_layer_id")
});

// Full workflow configuration
export const workflowConfigSchema = z.object({
  nodes: z.array(workflowNodeSchema),
  edges: z.array(workflowEdgeSchema),
  viewport: z.object({
    x: z.number(),
    y: z.number(),
    zoom: z.number(),
  }).optional(),
});

// Workflow entity
export const workflowSchema = z.object({
  id: z.string().uuid(),
  project_id: z.string().uuid(),
  name: z.string(),
  description: z.string().nullable(),
  is_default: z.boolean(),
  config: workflowConfigSchema,
  thumbnail_url: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type NodeStatus = z.infer<typeof nodeStatusSchema>;
export type DatasetNodeData = z.infer<typeof datasetNodeDataSchema>;
export type ToolNodeData = z.infer<typeof toolNodeDataSchema>;
export type WorkflowNode = z.infer<typeof workflowNodeSchema>;
export type WorkflowEdge = z.infer<typeof workflowEdgeSchema>;
export type WorkflowConfig = z.infer<typeof workflowConfigSchema>;
export type Workflow = z.infer<typeof workflowSchema>;
```

---

## UI Specifications

### Layout Structure (3-Panel)

Based on mockups, the workflow editor has three panels:

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Header: [Map] [Workflows*] [Layouts] [Dashboards]      [Share] [Save]   │
├────────────────┬───────────────────────────────────┬─────────────────────┤
│                │                                   │                     │
│  LEFT PANEL    │         CANVAS                    │    RIGHT PANEL      │
│  (280px)       │         (flex)                    │    (320px)          │
│                │                                   │                     │
│  ┌───────────┐ │  ┌─────────────────────────────┐  │  ┌───────────────┐  │
│  │Workflows  │ │  │ Toolbar:                    │  │  │ NODES | HIST  │  │
│  │+ Add      │ │  │ [🗑][📋][🔍][⊞][☁][⬇]      │  │  ├───────────────┤  │
│  │           │ │  │ [▶ RUN NODE] [▶▶ RUN TO HERE]│ │  │ Search        │  │
│  │• Blank    │ │  └─────────────────────────────┘  │  ├───────────────┤  │
│  │  Workflow │ │                                   │  │ Import        │  │
│  │           │ │      [Dataset] ──▶ [Tool]        │  │  + Add Dataset│  │
│  ├───────────┤ │                    │             │  ├───────────────┤  │
│  │Layers     │ │                    ▼             │  │ Accessibility │  │
│  │(read-only)│ │               [Output]           │  │  • Catchment  │  │
│  │           │ │                                   │  │  • Heatmap    │  │
│  │ Group 1   │ │                                   │  ├───────────────┤  │
│  │  • Layer  │ │  ┌─────────────────────────────┐  │  │ Geoanalysis   │  │
│  │  • Layer  │ │  │ + / - / Fit                 │  │  │ Geoprocessing │  │
│  │ Group 2   │ │  └─────────────────────────────┘  │  │ Data Mgmt     │  │
│  │  • Layer  │ │  [Show table] [Show map]          │  └───────────────┘  │
│  └───────────┘ │                                   │                     │
└────────────────┴───────────────────────────────────┴─────────────────────┘
```

### Left Panel: WorkflowsConfigPanel

**Sections:**

1. **Workflows List** (collapsible)
   - "+ Add Workflow" button → Creates blank workflow immediately (no template picker)
   - List of workflows with context menu (rename, duplicate, delete)
   - Selected workflow highlighted

2. **Layers** (collapsible, read-only)
   - Shows project layer tree (groups + layers)
   - Filter icons visible but non-interactive
   - Purpose: Reference for users to see available data

### Center: WorkflowCanvas

**Toolbar** (top of canvas):

| Icon           | Action      | Description                                 |
| -------------- | ----------- | ------------------------------------------- |
| 🗑              | Delete      | Delete selected node(s)                     |
| 📋              | Duplicate   | Duplicate selected node(s)                  |
| 🔍              | Filter      | Open filter panel for selected dataset node |
| ⊞              | Auto-layout | Arrange nodes automatically                 |
| ☁              | Save        | Manual save (auto-save enabled)             |
| ⬇              | Export      | Export workflow as JSON                     |
| ▶ RUN NODE     | Execute     | Run only the selected node                  |
| ▶▶ RUN TO HERE | Execute     | Run from start up to selected node          |

**Canvas Features:**

- ReactFlow canvas with zoom/pan
- Custom node types: `DatasetNode`, `ToolNode`
- Connection validation (geometry type compatibility)
- Minimap (optional)
- Background grid/dots

**Bottom Bar:**

- [Show table] - Show data table for selected node's output
- [Show map] - Toggle map view in a split pane

### Right Panel: WorkflowsNodesPanel

**Tabs:** NODES | HISTORY

**NODES Tab:**

- Search input
- Categorized blocks (same as toolbox):
  - **Import**: + Add Dataset (creates DatasetNode)
  - **Accessibility Indicators**: Catchment area, Heatmap variations, PT tools
  - **Data Management**: Join & Group
  - **Geoanalysis**: Buffer, aggregate, etc.
  - **Geoprocessing**: Clip, intersect, dissolve, etc.

**HISTORY Tab:**

- List of workflow executions
- Timestamp, status, duration

### Node Selection Panel (Replaces Right Panel)

When a node is selected, the right panel transforms:

**For Tool Nodes:**

```
┌─────────────────────────────────┐
│ < Catchment Area                │ (back button + title)
├─────────────────────────────────┤
│ [TOOL] [RESULT]                 │ (tabs)
├─────────────────────────────────┤
│ Description text...             │
├─────────────────────────────────┤
│ ⚙ Configuration                 │
│                                 │
│ [TIME] [DISTANCE]               │ (mode toggle)
│                                 │
│ Travel time limit (Min)         │
│ [15 min                      ]  │
│                                 │
│ Travel speed (Km/h)             │
│ [5 km/h                      ]  │
│                                 │
│ Number of breaks (Steps)        │
│ [5                           ]  │
│                                 │
│ ... more fields                 │
└─────────────────────────────────┘
```

**For Dataset Nodes:**

```
┌─────────────────────────────────┐
│ < Berliner Bezirksgrenzen       │
├─────────────────────────────────┤
│ [TOOL] [RESULT]                 │
├─────────────────────────────────┤
│ Dataset details                 │
│                                 │
│ Name                            │
│ xxxxxxxxx                       │
│                                 │
│ Source                          │
│ [dropdown or display]           │
│                                 │
│ Type                            │
│ Feature                         │
├─────────────────────────────────┤
│ 🔍 Filter                [🔵]   │
│                                 │
│ Filter 1                  ...   │
│ If [Field ▼] [Operator ▼] [Val] │
│                                 │
│ Filter 2                  ...   │
│ And [Field ▼] [Operator ▼] [Val]│
│                                 │
│ [+ Add Expression]              │
│ [Clear filter]                  │
└─────────────────────────────────┘
```

### Node Appearance

**Dataset Node:**

```
┌─────────────────────────────────┐
│ ≡  Berliner Bezirksgrenzen    ○ │ (drag handle, title, output handle)
└─────────────────────────────────┘
```

**Tool Node (Collapsed):**

```
┌─────────────────────────────────────────┐
│ ○  🏔 Catchment area                  ○ │
│    ─────────────────────────────        │
│    Routing type: Walk                   │
│    Travel time limit (Min): 15          │
│    Travel speed (Km/h): 5               │
│    Steps: 5                             │
│    Catchment area shape: Polygon        │
│    Polygon Difference: Enabled          │
└─────────────────────────────────────────┘
```

- Left handle(s): Input connections
- Right handle: Output connection
- Status indicator: Border color (idle=gray, running=blue, completed=green, error=red)
- Collapsed view shows key parameter summary

---

## Execution Architecture

> **Updated**: February 2, 2026

### Design Principles

1. **Browser-Independent Execution**: Users may close their browser during long-running workflows (even a single buffer on large datasets can take minutes)
2. **No Duplicate State**: Use Windmill as the single source of truth for job status
3. **Real-Time Progress**: Show which node is currently running via polling
4. **Temporary Results**: Tool outputs are temporary until explicitly saved

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER CLICKS "RUN"                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Frontend:                                                                  │
│  1. POST /api/v2/projects/{id}/workflows/{id}/execute                      │
│  2. Receive { job_id: "xxx" }                                              │
│  3. Poll GET /jobs/{job_id} every 2 seconds (same as existing tools)       │
│  4. Update node statuses based on workflow_as_code_status                   │
│  5. On completion, extract per-node results                                 │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Backend (Core API):                                                        │
│  1. Receive workflow execution request                                      │
│  2. Load workflow config (nodes, edges)                                     │
│  3. Delete old temporary layers (cleanup previous run)                      │
│  4. Submit workflow_runner script to Windmill                               │
│  5. Return { job_id } to frontend                                           │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Windmill (workflow_runner script):                                         │
│  1. Receive { nodes, edges, user_id, project_id, workflow_id }             │
│  2. Topologically sort nodes                                                │
│  3. For each tool node, run as @task (tracked by Windmill)                  │
│  4. Pass results between nodes (outputLayerId → next input)                 │
│  5. Return all node results on completion                                   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  User Closes Browser, Returns Later:                                        │
│  1. Load workflow page                                                      │
│  2. Query Windmill for jobs with args.workflow_id = this workflow           │
│  3. If running job exists, resume polling                                   │
│  4. If completed, populate node statuses from job results                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Windmill "Workflows as Code" Approach

Instead of OpenFlow JSON, we use a **single Python script with `@task` decorators**. Each `@task` becomes a tracked sub-job that Windmill monitors.

**File: `packages/python/goatlib/src/goatlib/tools/workflow_runner.py`**

```python
from wmill import task
import wmill

@task()
def run_tool(node_id: str, process_id: str, inputs: dict) -> dict:
    """Run a single tool and return its result with node_id."""
    result = wmill.run_script(f"f/goat/tools/{process_id}", args=inputs)
    return {"node_id": node_id, **result}


def topological_sort(nodes: list, edges: list) -> list:
    """Return nodes in execution order (datasets first, then tools by dependency)."""
    # ... implementation ...
    pass


def build_inputs(node: dict, edges: list, all_nodes: list, results: dict) -> dict:
    """Build input dict for a tool node from its config and predecessor outputs."""
    inputs = {**node["data"]["config"]}
    
    for edge in edges:
        if edge["target"] != node["id"]:
            continue
        
        source_node = next(n for n in all_nodes if n["id"] == edge["source"])
        target_handle = edge.get("targetHandle", "input_layer_id")
        
        if source_node["data"]["type"] == "dataset":
            # Direct layer reference
            inputs[target_handle] = source_node["data"]["layerId"]
            # Include filter if present
            if source_node["data"].get("filter"):
                filter_key = target_handle.replace("_id", "_filter")
                inputs[filter_key] = source_node["data"]["filter"]
        else:
            # Reference previous tool's output
            prev_result = results.get(source_node["id"])
            if prev_result:
                inputs[target_handle] = prev_result["layer_id"]
    
    return inputs


def main(
    user_id: str,
    project_id: str,
    workflow_id: str,
    folder_id: str,
    nodes: list[dict],
    edges: list[dict],
) -> dict:
    """Execute a workflow: run all tool nodes in topological order."""
    
    # Sort nodes by dependency
    sorted_nodes = topological_sort(nodes, edges)
    
    # Track results per node
    results = {}
    
    # Execute each tool node
    for node in sorted_nodes:
        if node["data"]["type"] != "tool":
            continue
        
        # Build inputs from config + predecessor outputs
        inputs = build_inputs(node, edges, nodes, results)
        inputs["user_id"] = user_id
        inputs["project_id"] = project_id
        inputs["folder_id"] = folder_id
        inputs["temporary"] = True  # Don't add to project layer list
        inputs["result_layer_name"] = node["data"].get("label", "Workflow Result")
        
        # Run as @task - Windmill tracks this as a sub-job
        result = run_tool(
            node_id=node["id"],
            process_id=node["data"]["processId"],
            inputs=inputs
        )
        
        results[node["id"]] = result
    
    return results
```

### Real-Time Progress Tracking

Windmill provides `workflow_as_code_status` in job responses:

```json
{
  "jobID": "abc-123",
  "status": "running",
  "workflow_as_code_status": {
    "scheduled": ["run_tool_node1", "run_tool_node2"],
    "running": ["run_tool_node1"],
    "completed": []
  }
}
```

**Frontend polling** (every 2 seconds, same as existing tools):

```typescript
// Use existing useJobStatus pattern
const { jobs } = useJobs({ read: false });

// Extract workflow_as_code_status for the current workflow job
const workflowJob = jobs?.find(j => j.args?.workflow_id === workflowId);
if (workflowJob?.workflow_as_code_status) {
  const { running, completed } = workflowJob.workflow_as_code_status;
  
  // Update node statuses in UI
  nodes.forEach(node => {
    if (completed.includes(`run_tool_${node.id}`)) {
      updateNodeStatus(node.id, "completed");
    } else if (running.includes(`run_tool_${node.id}`)) {
      updateNodeStatus(node.id, "running");
    }
  });
}
```

### Temporary Layers & Save Behavior

**Problem**: Currently, all tool outputs are automatically added to the project's layer list.

**Solution**: Add `temporary` flag to tool execution.

**Backend Changes**:

1. **`goatlib/tools/schemas.py`** - Add `temporary` field:
   ```python
   class ToolInputBase(BaseModel):
       # ... existing fields ...
       temporary: bool = Field(
           default=False,
           description="If True, result layer is temporary (not added to project layer list)"
       )
   ```

2. **`goatlib/tools/base.py`** - Skip `add_to_project()` when temporary:
   ```python
   async def _create_db_records(self, ...):
       # ... create layer metadata (always needed to view results) ...
       
       # Only add to project if NOT temporary
       layer_project_id = None
       if params.project_id and not getattr(params, 'temporary', False):
           layer_project_id = await self.db_service.add_to_project(...)
       
       return {"folder_id": folder_id, "layer_project_id": layer_project_id}
   ```

3. **`customer.layer`** table - Add `is_temporary` column:
   ```sql
   ALTER TABLE customer.layer ADD COLUMN is_temporary BOOLEAN DEFAULT FALSE;
   ```

4. **Finalize endpoint** - Convert temporary to permanent:
   ```
   POST /api/v2/layers/{layer_id}/finalize?project_id={project_id}
   ```
   - Sets `is_temporary = false`
   - Calls `add_to_project()` to add to layer list
   - Returns `layer_project_id`

**Frontend "Save" Button**:

When user clicks "Save" on a completed tool node:
```typescript
async function saveNodeResult(node: WorkflowNode, projectId: string) {
  if (node.data.outputLayerId) {
    await finalizeLayer(node.data.outputLayerId, projectId);
    // Refresh project layers
    mutateProjectLayers();
  }
}
```

### Cleanup Strategy

**When to delete old temporary layers:**

1. **On new workflow run**: Delete all temporary layers from the previous run of this workflow
2. **Scheduled cleanup** (optional): Background job to delete temp layers older than 24 hours

**Implementation**:

```python
# In workflow execute endpoint
async def execute_workflow(workflow_id: str, user_id: str, ...):
    # Query Windmill for previous completed jobs of this workflow
    previous_jobs = await windmill_client.list_jobs_filtered(
        user_id=user_id,
        script_path_start="f/goat/workflow_runner",
        success=True,
    )
    
    # Find jobs for this specific workflow
    for job in previous_jobs:
        if job.get("args", {}).get("workflow_id") == workflow_id:
            # Delete temporary layers from previous run
            for node_id, result in job.get("result", {}).items():
                layer_id = result.get("layer_id")
                if layer_id:
                    await delete_temporary_layer(layer_id)
    
    # Submit new execution
    job_id = await windmill_client.run_script_async(...)
    return {"job_id": job_id}
```

### Handling Disconnected Subgraphs

Workflows can have multiple disconnected chains:

```
Subgraph 1: [Dataset A] → [Buffer]
Subgraph 2: [Dataset B] → [Join] → [Join]
                         ↑
              [Dataset C] ┘        ↑
              [Dataset D] ─────────┘
```

**Solution**: Execute all as a single Windmill job, sequential order.

The topological sort handles disconnected components by processing them in order. Windmill's "Workflows as Code" doesn't require connections between tasks.

### Database Changes

**Minimal changes required:**

| Table            | Change                    | Description                      |
| ---------------- | ------------------------- | -------------------------------- |
| `customer.layer` | Add `is_temporary` column | Track temporary workflow results |

**No changes needed to `customer.workflow`** - Windmill stores all job state!

### Querying Workflow Jobs

```python
# List all workflow jobs for a user
async def list_workflow_jobs(user_id: str):
    return await windmill_client.list_jobs_filtered(
        user_id=user_id,
        script_path_start="f/goat/workflow_runner",
    )

# List jobs for a specific workflow
async def list_jobs_for_workflow(user_id: str, workflow_id: str):
    jobs = await windmill_client.list_jobs_filtered(
        user_id=user_id,
        script_path_start="f/goat/workflow_runner",
    )
    return [j for j in jobs if j.get("args", {}).get("workflow_id") == workflow_id]

# Get latest job for a workflow
async def get_latest_workflow_job(user_id: str, workflow_id: str):
    jobs = await list_jobs_for_workflow(user_id, workflow_id)
    return jobs[0] if jobs else None  # Jobs are ordered by created_at DESC
```

### "Save to Project" Node (Future)

In the future, "Save" will be a node type:

```
[Dataset] → [Buffer] → [Save to Project]
```

**Implementation**: Create a Windmill script `f/goat/save_to_project`:

```python
def main(layer_id: str, project_id: str, user_id: str, layer_name: str | None = None):
    """Finalize a temporary layer and add to project."""
    # 1. Update layer: is_temporary = false
    # 2. Call add_to_project()
    # 3. Return layer_project_id
```

This can be called like any other tool in the workflow runner.

### Summary

| Component               | Location                           | Purpose                                       |
| ----------------------- | ---------------------------------- | --------------------------------------------- |
| **Workflow Runner**     | `goatlib/tools/workflow_runner.py` | Orchestrates workflow execution in Windmill   |
| **Temporary Flag**      | `goatlib/tools/schemas.py`         | `temporary: bool` field on `ToolInputBase`    |
| **Skip Add to Project** | `goatlib/tools/base.py`            | Don't add to layer list when `temporary=True` |
| **Finalize Endpoint**   | `core/endpoints/v2/layer.py`       | `POST /layers/{id}/finalize`                  |
| **Frontend Polling**    | `hooks/jobs/JobStatus.tsx`         | Existing pattern, extend for workflows        |
| **Node Status Updates** | `components/workflows/`            | Read `workflow_as_code_status` from job       |

### Migration Notes

This architecture is designed for incremental implementation:

1. **Phase 1**: Add `temporary` flag + skip `add_to_project()` in BaseToolRunner
2. **Phase 2**: Create `workflow_runner.py` and sync to Windmill
3. **Phase 3**: Create execute endpoint in Core API
4. **Phase 4**: Frontend polling and node status updates
5. **Phase 5**: Finalize endpoint and "Save" button
6. **Phase 6**: Cleanup of old temporary layers

---

## Execution Modes (Simplified)

For MVP, we support a single "Run Workflow" button that executes all tool nodes.

Future enhancements:
- **Run Node**: Execute only selected node (requires upstream to be complete)
- **Run to Here**: Execute from start up to selected node

### Output Layer Management

- **Temporary by default**: All workflow results are temporary (not in layer list)
- **Explicit Save**: User clicks "Save" to add a result to the project
- **Cleanup on Re-run**: Previous temporary results deleted when workflow runs again
- **Naming**: `{NodeLabel}` (workflow name visible in layer metadata)

---

## API Endpoints

### Core API Routes

**Base URL**: `/api/v2/projects/{project_id}/workflow`

| Method | Endpoint                   | Description                    |
| ------ | -------------------------- | ------------------------------ |
| GET    | `/`                        | List all workflows for project |
| GET    | `/{workflow_id}`           | Get specific workflow          |
| POST   | `/`                        | Create workflow                |
| PUT    | `/{workflow_id}`           | Update workflow                |
| DELETE | `/{workflow_id}`           | Delete workflow                |
| POST   | `/{workflow_id}/duplicate` | Duplicate workflow             |

### Frontend API Hooks

**File: `apps/web/lib/api/workflows.ts`**

```typescript
// Hooks
export const useWorkflows = (projectId?: string) => { ... };
export const useWorkflow = (projectId?: string, workflowId?: string) => { ... };

// Mutations
export const createWorkflow = async (projectId: string, workflow: WorkflowCreate) => { ... };
export const updateWorkflow = async (projectId: string, workflowId: string, workflow: WorkflowUpdate) => { ... };
export const deleteWorkflow = async (projectId: string, workflowId: string) => { ... };
export const duplicateWorkflow = async (projectId: string, workflowId: string, newName?: string) => { ... };
```

---

## Implementation Phases

### Phase 1: Data Layer (Backend + Types) - 1 week ✅ DONE

- [x] Create `Workflow` SQLAlchemy model (`apps/core/src/core/db/models/workflow.py`)
- [x] Create Alembic migration
- [x] Create Pydantic schemas (`apps/core/src/core/schemas/workflow.py`)
- [x] Create CRUD class (`apps/core/src/core/crud/crud_workflow.py`)
- [x] Create API endpoints (`apps/core/src/core/endpoints/v2/workflow.py`)
- [x] Register routes in `apps/core/src/core/endpoints/v2/router.py`
- [x] Create Zod validations (`apps/web/lib/validations/workflow.ts`)
- [x] Create API hooks (`apps/web/lib/api/workflows.ts`)

### Phase 2: UI Shell - 1 week ✅ DONE

- [x] Add "Workflows" to header toggle (`apps/web/components/header/Header.tsx`)
- [x] Create `WorkflowsLayout.tsx` main component
- [x] Create `WorkflowsConfigPanel.tsx` (left panel - workflow list + layers)
- [x] Create `WorkflowsNodesPanel.tsx` (right panel - tool blocks)
- [x] Wire up mode switch in `apps/web/app/map/[projectId]/page.tsx`

### Phase 3: ReactFlow Canvas - 2 weeks ✅ DONE

- [x] Create `WorkflowCanvas.tsx` with ReactFlow setup
- [x] Create `DatasetNode.tsx` custom node component
- [x] Create `ToolNode.tsx` custom node component
- [x] Implement edge connection logic with validation
- [x] Implement node drag-and-drop from palette
- [x] Create canvas toolbar (delete, duplicate, auto-layout)
- [x] Implement auto-save on config changes

### Phase 4: Node Configuration - 2 weeks ✅ DONE

- [x] Create `DatasetNodeSettings.tsx` (layer selector + filter)
- [x] Create `ToolNodeSettings.tsx` (reuse OGC process form rendering)
- [x] Integrate with existing `ProcessedInputField.tsx` components
- [x] Handle geometry type constraints for connections
- [x] Show parameter summary on collapsed tool nodes

### Phase 5: Execution Engine - 2 weeks 🔄 IN PROGRESS

**Backend Changes:**

- [ ] Add `temporary` field to `ToolInputBase` in `goatlib/tools/schemas.py`
- [ ] Modify `BaseToolRunner._create_db_records()` to skip `add_to_project()` when `temporary=True`
- [ ] Add `is_temporary` column to `customer.layer` table (Alembic migration)
- [ ] Create `workflow_runner.py` in `goatlib/tools/`
- [ ] Sync `workflow_runner` to Windmill via `python -m goatlib.tools.sync_windmill`
- [ ] Add execute endpoint: `POST /projects/{id}/workflows/{id}/execute`
- [ ] Add finalize endpoint: `POST /layers/{id}/finalize`

**Frontend Changes:**

- [ ] Create `useWorkflowExecution` hook
- [ ] Add "Run Workflow" button to toolbar
- [ ] Extend job polling to read `workflow_as_code_status`
- [ ] Update node statuses based on running/completed tasks
- [ ] Add "Save" button to tool node details panel
- [ ] Handle job completion and populate `outputLayerId` on nodes

### Phase 6: Polish - 1 week

- [ ] Add i18n translations for workflow execution states
- [ ] Add keyboard shortcuts
- [ ] Add undo/redo support
- [ ] Add copy/paste nodes
- [ ] Add minimap
- [ ] Performance optimization
- [ ] Cleanup strategy for old temporary layers

---

## File Structure

```
apps/web/components/workflows/
├── README.md                          # This file
├── WorkflowsLayout.tsx                # Main container
├── index.ts                           # Exports
├── panels/
│   ├── WorkflowsConfigPanel.tsx       # Left: workflow list + layers
│   ├── WorkflowsNodesPanel.tsx        # Right: tool blocks palette
│   ├── DatasetNodeSettings.tsx        # Dataset configuration panel
│   ├── ToolNodeSettings.tsx           # Tool configuration panel
│   └── WorkflowDataPanel.tsx          # Bottom: table/map view
├── canvas/
│   ├── WorkflowCanvas.tsx             # ReactFlow canvas wrapper
│   └── WorkflowToolbar.tsx            # Canvas toolbar
├── nodes/
│   ├── DatasetNode.tsx                # Dataset/layer node
│   ├── ToolNode.tsx                   # Tool/process node
│   ├── TextAnnotationNode.tsx         # Text annotation node
│   └── index.ts                       # Node type registry
└── edges/
    └── index.ts                       # Edge type registry
```

```
apps/core/src/core/
├── db/models/workflow.py              # SQLAlchemy model
├── schemas/workflow.py                # Pydantic schemas
├── crud/crud_workflow.py              # CRUD operations
└── endpoints/v2/workflow.py           # API routes (CRUD + execute)
```

```
apps/web/lib/
├── validations/workflow.ts            # Zod schemas
├── api/workflows.ts                   # API hooks
└── store/workflow/
    ├── slice.ts                       # Redux slice for workflow state
    └── selectors.ts                   # Redux selectors
```

```
packages/python/goatlib/src/goatlib/tools/
├── workflow_runner.py                 # NEW: Windmill workflow orchestrator
├── save_to_project.py                 # NEW: Finalize temporary layer
├── schemas.py                         # Add 'temporary' field
└── base.py                            # Skip add_to_project() when temporary
```

---

## Design Decisions

### 1. Auto-save

**Decision**: Yes, auto-save on every change (debounced)

**Rationale**: Consistent with layouts, prevents data loss

**Implementation**: Debounced `updateWorkflow` call on config changes

### 2. Execution Backend

**Decision**: Windmill "Workflows as Code" (`@task` decorators)

**Rationale**: 
- Users may close browser during long-running workflows
- Windmill handles all job tracking, progress, and state
- No need to store execution state in our database
- Same polling pattern as existing tools

**Alternatives Considered**:
- Frontend orchestration (rejected: browser close breaks execution)
- Windmill OpenFlow (more complex, not needed for MVP)

### 3. Job State Storage

**Decision**: Use Windmill as single source of truth (no `last_job_id` in DB)

**Rationale**:
- Query Windmill for jobs with `args.workflow_id = this_workflow`
- Existing job polling infrastructure works unchanged
- No duplicate state to keep in sync

### 4. Temporary Layers

**Decision**: Tool outputs are temporary until explicitly saved

**Rationale**:
- Prevents cluttering project with intermediate results
- User controls what gets added to layer list
- Easy cleanup on re-run

**Implementation**: 
- `temporary: true` flag on tool inputs
- `is_temporary` column on layer table
- "Save" button calls finalize endpoint

### 5. Progress Tracking

**Decision**: Poll every 2 seconds (same as existing tools)

**Rationale**:
- Simple, proven pattern
- Windmill provides `workflow_as_code_status` in job response
- No WebSocket/SSE complexity needed

### 6. Cleanup Strategy

**Decision**: Delete old temporary layers when starting new run

**Rationale**:
- Simple mental model: "Run" replaces previous results
- No orphaned layers accumulating
- Layers that were "Saved" are NOT deleted (not temporary anymore)

### 7. Disconnected Subgraphs

**Decision**: Execute all in single Windmill job, sequential order

**Rationale**:
- Simpler implementation
- Resource-friendly (not competing for workers)
- Can optimize with parallel execution later

### 8. "Save to Project" Node (Future)

**Decision**: Will be a first-class node type, not just a button

**Rationale**:
- Explicit in workflow graph
- Can be placed anywhere in the chain
- Consistent with other node types

---

## Future Considerations

### Planned Enhancements

1. **"Save to Project" Node**: Explicit node type for saving results (not just a button)
2. **Run Node / Run to Here**: Execute partial workflows for debugging
3. **Parallel Execution**: Run independent branches concurrently using Windmill's `branchall`
4. **Scheduled Execution**: Cron-based workflow runs via Windmill schedules
5. **Workflow Templates Gallery**: Predefined workflows for common use cases
6. **Version History**: Track workflow changes over time

### Potential Enhancements

1. **Workflow Sharing**: Share workflows between projects/users
2. **Conditional Logic**: Branch based on intermediate results
3. **Loop Nodes**: Iterate over feature collections
4. **External Data Sources**: Fetch data from APIs as input
5. **Notifications**: Alert on completion/failure (email, Slack)
6. **Export/Import**: Share workflows as JSON files

### OpenFlow Migration (Optional)

If we need more advanced Windmill features (complex branching, approval steps), we could:

1. Generate Windmill OpenFlow JSON from ReactFlow graph
2. Submit as native Windmill Flow instead of "Workflows as Code"
3. Use `flow_status` instead of `workflow_as_code_status` for progress

Current "Workflows as Code" approach is simpler and sufficient for MVP.

---

## References

### Related Code

- **Layouts Pattern**: `apps/web/components/reports/ReportsLayout.tsx`
- **GenericTool**: `apps/web/components/map/panels/toolbox/generic/GenericTool.tsx`
- **OGC Utils**: `apps/web/lib/utils/ogc-utils.ts`
- **Processes API**: `apps/processes/src/processes/routers/processes.py`
- **Tool Registry**: `packages/python/goatlib/src/goatlib/tools/registry.py`

### External Dependencies

- **ReactFlow**: `@xyflow/react` (v12.10.0) - Already installed
- **dnd-kit**: `@dnd-kit/core` - Already installed (used for drag-drop)

### i18n Keys

Already added:
- `"workflows": "Workflows"` (en, de)

Need to add:
- Tool names (reuse from toolbox)
- UI labels for workflow editor
- Status messages
- Error messages
