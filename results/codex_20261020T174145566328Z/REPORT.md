# Codex model-run report

Actual model-generated conversations using saved ChatGPT login. Custom Codex transport; four authored text-retail tasks. These are not official leaderboard results.

Requested model: `gpt-5.6-luna`. CLI: `codex-cli 0.145.0`. Effort: `low`.

| Task | Trial | Native reward | Termination | Seconds |
|---|---:|---:|---|---:|
| sample_02_refuse_delivered | 0 | 1 | user_stop | 123.91 |
| sample_03_exchange_variant | 0 | 0 | user_stop | 160.38 |
| sample_04_partial_return | 0 | 0 | user_stop | 139.63 |

Attempted 3 of 3 planned task trials. Run complete: True.

Observed native outcome successes: 1/3. Includes all attempted trials; infrastructure failures count as failures.

Codex process calls: 22. Returned token counters: `{"cache_write_input_tokens": 0, "cached_input_tokens": 29440, "input_tokens": 207560, "output_tokens": 1840, "reasoning_output_tokens": 641}`.

Dollar cost is unavailable. Calls consume the user's Codex allowance. Sampling seed and temperature are not exposed by this adapter. One trial per authored task does not estimate consistency across repeated trials or general model performance. Native reward does not certify policy compliance. Agent/customer prompts, visible outputs, tool traces, prompt hashes and token counters are retained in results.json. No reasoning traces or authentication data are exported.
