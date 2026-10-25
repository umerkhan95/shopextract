# P5 concrete reusable components

| Component | Actual consumers / ownership | Contract and lifecycle |
| --- | --- | --- |
| _cli_core CoreGroup/CoreCommand/CliFailure/make_response | every CLI operation/discovery command | Central config/error/output; protocol serve exemption precedes ambient settings; remove obsolete phase guard only, preserve Click validation |
| _cli_data.read_json_file/bounded_tree | goal, profiles, operator, session loaders |1MiB/depth64/100000nodes/duplicate and nonfinite rejection before side effects, exact native codecs remain authoritative |
| _cli_categories.runtime_file | maintenance --category-config | Native immutable CategoryRuntimeConfig (native unversioned), persisted native policy digest; engine reconstructs same policy |
| MaintenanceStore.create/status/report/evidence/request_cancel/list_jobs | maintenance command family | One explicit db path; store closed finally; invalid create checked natively before opening. Add only list_jobs bounded ordered IDs/status, no job state machine duplicate |
| MaintenanceEngine.run/resume/retry_unknown/cancel/close | maintenance run/resume/retry/cancel | Single instance per invocation; use native locks, two attempts, unknown outcome and budgets; native cleanup plus independent deadline observation |
| native Goal/Budgets/CategoryProfile/FieldRule dataclasses | maintenance loaders/config schemas | Closed field/type load, then native semantic validation; investigator/callback protocols excluded from CLI |
| ToolRuntime.bootstrap/call/aclose, ToolConfig/Limits/CaptureGrant | tools call/serve and maintenance engine | Native session ownership/origins/handles/resource limits. Same session used for all steps; await aclose finally, no handle made durable |
| tools.contracts.schema/validate and TOOL_NAMES | tools schemas, schema native inventory, session step validation | Static8 tool schemas; versioned native envelopes retained; helper operations compose poll/page only, not new public tools |
| tools.mcp_server.serve | tools serve | Genuine official SDK adapter, protocol stdout and native cleanup. Optional import lazy, actionable install error |
| importlib.resources + package JSON files | schema list/show; installed callers | Package-safe resources, JSON Schema metadata; no runtime construction/help callback. Native tool schemas generated, not duplicated |
| Click Command/Option/Argument declarations | capabilities | Read real nested grammar/arity/choices/defaults/output flags; no speculative command count parity |

Shared total_deadline used maintenance and tools-session bounded tasks: wait with timer, cancel/drain task if timer fires, raise timeout regardless of consumed cancellation. Caller finally closes engine/runtime/store. Whole result bound uses actual encoded make_response bytes, no preview/truncation. All errors safe static text/native code only. No generic workflow framework, native adapter change, duplicate durable/session engine or arbitrary callable loader.
