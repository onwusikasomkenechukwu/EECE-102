"""
Quantum Prototype Decision Analysis
Somkene Onwusika | EECE 102 - Transformational Technology Case Study

Decision: As a design engineer at a quantum hardware startup, choose the
sophistication level for a trapped-ion qubit control module prototype.

Options:
  A. Minimal   - 16 qubits, off-the-shelf FPGA control
  B. Mid-Tier  - 32 qubits, custom FPGA + partial ASIC integration
  C. Full-Spec - 50 qubits, fully custom ASIC control

This script:
  1. Defines a multi-attribute cost function
  2. Runs expected value analysis over the decision tree
  3. Performs sensitivity analysis on key uncertain parameters
  4. Offers an interactive mode for custom user inputs
"""

import numpy as np


# ---------------------------------------------------------------------------
# 1. Decision tree definition
# ---------------------------------------------------------------------------
# value in millions USD (net value after cost; positive = gain, negative = loss)
TREE = {
    "A_Minimal": {
        "dev_cost_m": 0.45,
        "outcomes": [
            ("Success",  0.70,  1.20),
            ("Failure",  0.30, -0.45),
        ],
    },
    "B_MidTier": {
        "dev_cost_m": 1.10,
        "outcomes": [
            ("Success",  0.55,  3.80),
            ("Partial",  0.30,  0.60),
            ("Failure",  0.15, -1.10),
        ],
    },
    "C_FullSpec": {
        "dev_cost_m": 2.80,
        "outcomes": [
            ("Success",  0.25,  9.50),
            ("Failure",  0.75, -2.80),
        ],
    },
}


def expected_value(option):
    return sum(p * v for _, p, v in TREE[option]["outcomes"])


def downside(option):
    return min(v for _, _, v in TREE[option]["outcomes"])


def upside(option):
    return max(v for _, _, v in TREE[option]["outcomes"])


def variance(option):
    ev = expected_value(option)
    return sum(p * (v - ev) ** 2 for _, p, v in TREE[option]["outcomes"])


# ---------------------------------------------------------------------------
# 2. Multi-attribute cost function
# ---------------------------------------------------------------------------
# Five attributes. Each scored 1 (bad) to 10 (good) for each option,
# then combined with user-adjustable weights. Higher composite = better.
ATTRIBUTES = ["financial_ev", "technical_risk", "schedule_risk",
              "strategic_fit", "team_readiness"]

# Scores are my engineering judgment given the startup's current state:
# small team, limited cryo infrastructure, 18-month runway.
SCORES = {
    "A_Minimal":  {"financial_ev": 4, "technical_risk": 9,
                   "schedule_risk": 9, "strategic_fit": 4, "team_readiness": 9},
    "B_MidTier":  {"financial_ev": 8, "technical_risk": 6,
                   "schedule_risk": 6, "strategic_fit": 8, "team_readiness": 6},
    "C_FullSpec": {"financial_ev": 5, "technical_risk": 2,
                   "schedule_risk": 2, "strategic_fit": 10, "team_readiness": 3},
}

DEFAULT_WEIGHTS = {
    "financial_ev":   0.30,
    "technical_risk": 0.25,
    "schedule_risk":  0.15,
    "strategic_fit":  0.20,
    "team_readiness": 0.10,
}


def cost_score(option, weights=None):
    """Weighted composite score. Higher is better."""
    w = weights or DEFAULT_WEIGHTS
    s = SCORES[option]
    return sum(w[a] * s[a] for a in ATTRIBUTES)


def opportunity_cost(option, weights=None):
    """Gap between this option and the best alternative composite score."""
    best = max(cost_score(o, weights) for o in TREE)
    return best - cost_score(option, weights)


# ---------------------------------------------------------------------------
# 3. Sensitivity analysis
# ---------------------------------------------------------------------------
def sensitivity_on_success_prob(option, deltas=(-0.2, -0.1, 0, 0.1, 0.2)):
    """Sweep the success probability and recompute EV. Re-normalizes others."""
    base = TREE[option]["outcomes"]
    rows = []
    base_success_p = base[0][1]
    for d in deltas:
        new_success = max(0.0, min(1.0, base_success_p + d))
        remaining = 1 - new_success
        old_other_total = 1 - base_success_p
        new_outcomes = [(base[0][0], new_success, base[0][2])]
        for name, p, v in base[1:]:
            scaled = (p / old_other_total) * remaining if old_other_total > 0 else 0
            new_outcomes.append((name, scaled, v))
        ev = sum(p * v for _, p, v in new_outcomes)
        rows.append((d, new_success, ev))
    return rows


def sensitivity_on_weights(option, attribute, deltas=(-0.15, -0.05, 0, 0.05, 0.15)):
    """Sweep a single attribute's weight (renormalizing the rest)."""
    rows = []
    for d in deltas:
        w = dict(DEFAULT_WEIGHTS)
        new_w = max(0.01, min(0.99, w[attribute] + d))
        other_sum = sum(v for k, v in w.items() if k != attribute)
        scale = (1 - new_w) / other_sum if other_sum > 0 else 0
        for k in w:
            w[k] = new_w if k == attribute else w[k] * scale
        rows.append((d, new_w, cost_score(option, w)))
    return rows


# ---------------------------------------------------------------------------
# 4. Reporting
# ---------------------------------------------------------------------------
def print_header(title):
    print("\n" + "=" * 68)
    print(f"  {title}")
    print("=" * 68)


def run_full_analysis():
    print_header("EXPECTED VALUE ANALYSIS")
    print(f"{'Option':<14}{'EV ($M)':<12}{'Upside':<12}{'Downside':<12}{'Std Dev':<10}")
    print("-" * 60)
    for opt in TREE:
        ev = expected_value(opt)
        print(f"{opt:<14}{ev:<12.3f}{upside(opt):<12.3f}"
              f"{downside(opt):<12.3f}{np.sqrt(variance(opt)):<10.3f}")

    print_header("COST FUNCTION (Composite Score, higher = better)")
    print(f"{'Option':<14}{'Score':<10}{'Opp. Cost':<12}")
    print("-" * 40)
    for opt in TREE:
        print(f"{opt:<14}{cost_score(opt):<10.2f}{opportunity_cost(opt):<12.2f}")

    print_header("SENSITIVITY: Success probability shift on Option B")
    print(f"{'Delta':<10}{'New P(Success)':<18}{'New EV ($M)':<15}")
    print("-" * 45)
    for d, p, ev in sensitivity_on_success_prob("B_MidTier"):
        print(f"{d:+.2f}     {p:<18.2f}{ev:<15.3f}")

    print_header("SENSITIVITY: Financial weight shift on Option B score")
    print(f"{'Delta':<10}{'New Weight':<14}{'New Score':<12}")
    print("-" * 40)
    for d, w, s in sensitivity_on_weights("B_MidTier", "financial_ev"):
        print(f"{d:+.2f}     {w:<14.2f}{s:<12.2f}")

    print_header("RECOMMENDATION")
    best = max(TREE, key=lambda o: (expected_value(o), cost_score(o)))
    print(f"Recommended option: {best}")
    print(f"  Expected value:   ${expected_value(best):.2f}M")
    print(f"  Composite score:  {cost_score(best):.2f}/10")
    print(f"  Opportunity cost: {opportunity_cost(best):.2f}")


# ---------------------------------------------------------------------------
# 5. Interactive decision program (additional credit)
# ---------------------------------------------------------------------------
def interactive():
    """Prompt the user for custom weights and re-evaluate all options."""
    print_header("INTERACTIVE MODE - enter your own attribute weights")
    print("Weights will be normalized to sum to 1.0.\n")
    raw = {}
    for a in ATTRIBUTES:
        while True:
            try:
                x = float(input(f"Weight for {a} (0-1) [{DEFAULT_WEIGHTS[a]}]: ") or DEFAULT_WEIGHTS[a])
                if 0 <= x <= 1:
                    raw[a] = x
                    break
            except ValueError:
                pass
            print("  please enter a number between 0 and 1")
    total = sum(raw.values()) or 1
    weights = {k: v / total for k, v in raw.items()}

    print("\nNormalized weights:")
    for k, v in weights.items():
        print(f"  {k:<16} {v:.3f}")

    print("\nResults with your weights:")
    print(f"{'Option':<14}{'Score':<10}{'EV ($M)':<12}{'Opp. Cost':<12}")
    print("-" * 50)
    ranked = sorted(TREE.keys(), key=lambda o: cost_score(o, weights), reverse=True)
    for opt in ranked:
        print(f"{opt:<14}{cost_score(opt, weights):<10.2f}"
              f"{expected_value(opt):<12.2f}{opportunity_cost(opt, weights):<12.2f}")
    print(f"\nYour recommendation: {ranked[0]}")


if __name__ == "__main__":
    run_full_analysis()
    print("\nRun interactive() in a Python shell for custom weight analysis.")
