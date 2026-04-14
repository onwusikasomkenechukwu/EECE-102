# Quantum Decision Analysis

A decision support script for evaluating prototype sophistication levels on a trapped-ion qubit control module. Built as part of an EECE 102 Transformational Technology case study at Howard University.

The script takes a design engineer's perspective at a mid-stage quantum hardware startup and quantifies the tradeoff between three prototype options: a minimal 16-qubit FPGA build, a mid-tier 32-qubit FPGA + partial ASIC build, and a full-spec 50-qubit custom ASIC build.

## What it does

- Computes expected value, upside, downside, and standard deviation for each option from a decision tree
- Evaluates a five-attribute weighted cost function (financial EV, technical risk, schedule risk, strategic fit, team readiness)
- Calculates opportunity cost as the gap between each option and the top-ranked alternative
- Runs sensitivity analysis on success probability and attribute weights
- Offers an interactive mode where the user enters custom weights and gets a re-ranked recommendation

## Requirements

- Python 3.8 or later
- NumPy

Install NumPy if you don't have it:

```bash
pip install numpy
```

## Usage

Run the full analysis from the command line:

```bash
python quantum_decision.py
```

This prints the expected value table, composite scores, both sensitivity sweeps, and the final recommendation.

### Interactive mode

For custom weights, open a Python shell in the same directory:

```python
>>> from quantum_decision import interactive
>>> interactive()
```

The program will prompt for a weight between 0 and 1 for each of the five attributes. Press Enter to accept the default. Weights are normalized automatically so they sum to 1.0, and the three options are re-ranked based on your priorities.

## Structure

| Function | Purpose |
|---|---|
| `expected_value(option)` | EV across the decision tree branches |
| `upside(option)` / `downside(option)` | Best and worst case net value |
| `variance(option)` | Variance of outcomes (std dev is its square root) |
| `cost_score(option, weights)` | Weighted composite score, higher is better |
| `opportunity_cost(option, weights)` | Gap from the best option |
| `sensitivity_on_success_prob(option)` | Sweeps success probability and recomputes EV |
| `sensitivity_on_weights(option, attribute)` | Sweeps one attribute's weight and recomputes score |
| `run_full_analysis()` | Prints all tables at once |
| `interactive()` | Prompts for custom weights and re-ranks |

## Customization

The decision tree and attribute scores are defined as dictionaries at the top of the file. To evaluate a different decision, edit:

- `TREE` — add or modify options, their dev costs, and outcome probabilities
- `SCORES` — rate each option 1 to 10 on the five attributes
- `DEFAULT_WEIGHTS` — change the default attribute weights (must sum to 1.0)

The scoring logic will pick up the changes automatically. No other edits needed.

## Sample output

```
====================================================================
  EXPECTED VALUE ANALYSIS
====================================================================
Option        EV ($M)     Upside      Downside    Std Dev
------------------------------------------------------------
A_Minimal     0.705       1.200       -0.450      0.756
B_MidTier     2.105       3.800       -1.100      1.949
C_FullSpec    0.275       9.500       -2.800      5.326

====================================================================
  RECOMMENDATION
====================================================================
Recommended option: B_MidTier
  Expected value:   $2.10M
  Composite score:  7.00/10
  Opportunity cost: 0.00
```

## Extending with an LLM backend

The `interactive()` function can be replaced with an Anthropic API call that parses a natural-language description of the user's priorities into a weight dictionary, then feeds it into `cost_score()`. The underlying scoring logic stays identical — only the input layer changes. This turns the script from a one-off case study into a general-purpose decision support tool.

## Author

Somkene Onwusika
EECE 102 — Transformational Technology Case Study
Howard University, April 2026
