# Cost-Effectiveness Frontier Protocol

**Objective.** Compute the cost per run for each of the 8 cells, plot quality vs. cost,
and identify the Pareto-optimal conditions (the "cost-effectiveness frontier"). This
answers: "which condition gives the best quality for a given cost?"

---

## 1. Cost computation

### Step 1: Define provider pricing

For each provider (gpt, claude, gemini, kimi, qwen), define the pricing:

| Provider | Input price ($/1M tokens) | Output price ($/1M tokens) |
|----------|---------------------------|----------------------------|
| gpt | X.XX | X.XX |
| claude | X.XX | X.XX |
| gemini | X.XX | X.XX |
| kimi | X.XX | X.XX |
| qwen | X.XX | X.XX |

**Source:** provider websites (OpenAI, Anthropic, Google, Moonshot, Alibaba). Note the date
(pricing may change).

### Step 2: Compute cost per run

For each run, compute:

```
cost = (input_tokens × input_price + output_tokens × output_price) / 1,000,000
```

**Example:**
- Input tokens: 250
- Output tokens: 500
- Input price: $2.50 / 1M tokens
- Output price: $10.00 / 1M tokens
- Cost = (250 × 2.50 + 500 × 10.00) / 1,000,000 = $0.005625

### Step 3: Aggregate by cell

For each of the 8 cells, compute:
- **Mean cost per run:** average cost across all runs in the cell.
- **Mean quality per run:** average judge score across all runs in the cell.
- **Standard deviation:** for both cost and quality.

**Output:** a table with 8 rows (one per cell), columns: cell, mean_cost, mean_quality, sd_cost, sd_quality.

## 2. Visualization

### Step 1: Scatter plot

- **X-axis:** mean cost per run (in dollars).
- **Y-axis:** mean quality per run (judge score, 1–5 or 0–100).
- **Points:** 8 points (one per cell), labeled with cell name (e.g., "C-S-N", "F-T-P").
- **Error bars:** ±1 SD for both cost and quality.

### Step 2: Pareto frontier

- **Identify Pareto-optimal points:** a cell is Pareto-optimal if no other cell has both
  lower cost and higher quality.
- **Draw the frontier:** connect the Pareto-optimal points with a line (or curve).
- **Label the frontier:** "Cost-effectiveness frontier."

### Step 3: Interpretation

- **Cells on the frontier:** best tradeoffs (you can't improve quality without increasing cost,
  or reduce cost without decreasing quality).
- **Cells below the frontier:** dominated (there's a better option).
- **Cells above the frontier:** impossible (by definition).

### Step 4: Additional visualizations (optional)

- **Cost-effectiveness ratio:** quality / cost (higher is better). Plot as a bar chart.
- **Incremental cost-effectiveness ratio (ICER):** for each cell, compute the additional cost
  per unit of quality gained relative to the cheapest cell. Plot as a table or bar chart.

## 3. Reporting

### In the paper

> "We computed the cost-effectiveness frontier for the 8 experimental conditions (Figure X).
> The frontier connects the Pareto-optimal conditions: C-T-P (cheap team + persona, $0.012/run,
> quality = 3.8) and F-S-N (frontier solo, $0.045/run, quality = 4.2). C-T-P achieves 90% of
> F-S-N's quality at 27% of the cost, supporting the orchestration economics thesis: structure
> can substitute for model tier."

### In the supplementary materials

- **Table:** mean cost, mean quality, SD for all 8 cells.
- **Figure:** scatter plot with Pareto frontier.
- **Code:** R/Python script for computing cost and generating the plot.

---

## Task for the coder

1. **Define provider pricing:** create a JSON file with input/output prices for each provider.
2. **Compute cost per run:** for each run in the pilot (or main run), compute cost using the formula above.
3. **Aggregate by cell:** compute mean cost, mean quality, SD for each of the 8 cells.
4. **Generate the scatter plot:** use matplotlib (Python) or ggplot2 (R).
5. **Identify Pareto-optimal points:** cells that are not dominated by any other cell.
6. **Draw the Pareto frontier:** connect the Pareto-optimal points.
7. **Save outputs:**
   - `provider_pricing.json` (input/output prices per provider).
   - `cost_per_run.csv` (per-run cost, quality, tokens).
   - `cell_summary.csv` (mean cost, mean quality, SD per cell).
   - `cost_effectiveness_scatter.png` (and `.pdf`).
   - `pareto_frontier.csv` (list of Pareto-optimal cells).
   - `cost_effectiveness.py` (or `.R`) (script for computing and plotting).

## Acceptance criteria

- [ ] Provider pricing is defined and saved.
- [ ] Cost per run is computed for all runs.
- [ ] Cell summary (mean cost, mean quality, SD) is computed for all 8 cells.
- [ ] Scatter plot is generated with error bars.
- [ ] Pareto-optimal points are identified.
- [ ] Pareto frontier is drawn.
- [ ] All outputs are saved in the specified formats.

## Definition of Done

The cost-effectiveness analysis is complete. The experimenter can write in the paper: "We
computed the cost-effectiveness frontier (Figure X). C-T-P is on the frontier: it achieves
X% of F-S-N's quality at Y% of the cost."
