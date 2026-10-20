# Codex model-run report

Actual model-generated conversations using saved ChatGPT login. Custom Codex transport; four authored text-retail tasks. These are not official leaderboard results.

Requested model: `gpt-5.6-luna`. CLI: `codex-cli 0.145.0`. Effort: `low`.

| Task | Trial | Native reward | Termination | Seconds |
|---|---:|---:|---|---:|
| sample_01_cancel_pending | 0 | 0 | user_stop | 124.04 |

Attempted 1 of 1 planned task trials. Run complete: True.

Observed native outcome successes: 0/1. Includes all attempted trials; infrastructure failures count as failures.

Codex process calls: 7. Returned token counters: `{"cache_write_input_tokens": 0, "cached_input_tokens": 5888, "input_tokens": 65041, "output_tokens": 473, "reasoning_output_tokens": 130}`.

Dollar cost is unavailable. Calls consume the user's Codex allowance. Sampling seed and temperature are not exposed by this adapter. One trial per authored task does not estimate consistency across repeated trials or general model performance. Native reward does not certify policy compliance. Agent/customer prompts, visible outputs, tool traces, prompt hashes and token counters are retained in results.json. No reasoning traces or authentication data are exported.
