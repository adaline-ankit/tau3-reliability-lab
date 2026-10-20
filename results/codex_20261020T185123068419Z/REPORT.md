# Codex model-run report

Actual model-generated conversations using saved ChatGPT login. Custom Codex transport; four authored text-retail tasks. These are not official leaderboard results.

Requested model: `gpt-5.6-luna`. CLI: `codex-cli 0.145.0`. Effort: `low`.

| Task | Trial | Native reward | DB match | Communication | Termination | Seconds |
|---|---:|---:|---|---:|---|---:|
| sample_01_cancel_pending | 0 | 1.0 | True | 1.0 | user_stop | 184.34 |
| sample_02_refuse_delivered | 0 | 1.0 | True | 1.0 | user_stop | 183.27 |
| sample_03_exchange_variant | 0 | 0.0 | True | 0.0 | user_stop | 235.85 |
| sample_04_partial_return | 0 | 1.0 | True | 1.0 | user_stop | 200.02 |

Attempted 4 of 4 planned task trials. Run complete: True.

Observed native outcome successes: 3/4. Includes all attempted trials; infrastructure failures count as failures.

Codex process calls: 41. Returned token counters: `{"cache_write_input_tokens": 0, "cached_input_tokens": 82432, "input_tokens": 395055, "output_tokens": 3055, "reasoning_output_tokens": 984}`.

Dollar cost is unavailable. Calls consume the user's Codex allowance. Sampling seed and temperature are not exposed by this adapter. One trial per authored task does not estimate consistency across repeated trials or general model performance. Native reward does not certify policy compliance. Agent/customer prompts, visible outputs, tool traces, prompt hashes and token counters are retained in results.json. No reasoning traces or authentication data are exported.
