# Example prompts: turn your account data into clear pictures

Copy a prompt into your connected Claude, VS Code or ChatGPT client. The agent reads data through Jainam MCP Agent; **your AI client creates the chart**, if its rendering or code tools support it. The MCP server supplies data and prompt templates, not an embedded chart viewer. If a client cannot draw charts, ask for a chart-ready table or a local report instead.

## Start with these three

### 1. Sector-wise donut chart

```text
Fetch my CNC holdings once using Jainam tools. Show my portfolio sector-wise as a
colorful donut chart, using current market value for slice sizes. Put total market
value in the center, and show each sector's INR value and percentage in the legend.

Use sector classifications only if the returned data includes them or I provide a
sector-mapping file with a named source/date. Otherwise ask for that mapping; do
not guess sectors from company names. Keep unmapped holdings as “Unclassified”
and display the percentage classified. Label missing valuation separately.

Add a table below the chart and state the snapshot time. Do not place any orders.
```

### 2. Investment-wise pie chart

```text
Show my stock-wise investment allocation as a pie chart using quantity × average
acquisition cost, not current market value. Fetch my CNC holdings once. First
verify which fields represent settled quantity, average cost and cost basis.
Do not add overlapping pledged/unsettled quantities.

Show the top 8 holdings individually and combine the rest as “Other”. Label the
legend with stock name, invested INR and percentage. Add total invested capital,
a table of every holding and any holdings excluded because cost is unavailable.
Call the chart “Allocation by acquisition cost”; do not label it current exposure.
```

### 3. Market-value donut chart

```text
Create a clean, professional donut chart of my holdings by current market value.
Use the broker's market-value field where authoritative; otherwise calculate
quantity × mark price only if quantity units and price timestamps are clear.
Show the top 10 positions plus Other, with total valued holdings in the center.
Use distinct, readable colors, a clear legend and INR/percentage labels.

Show valued-holdings coverage, missing marks, snapshot time and the underlying
table. If no reliable current marks exist, say so instead of using invented prices.
```

## More visual requests

### Compare invested capital versus current value

```text
Create two side-by-side donut charts for my CNC holdings: allocation by acquisition
cost and allocation by current market value. Keep identical stock colors across
both charts. Show the same top 8 stocks plus Other, and show both INR totals.
Use only holdings with sufficient fields for the comparison, disclose exclusions,
and add a table showing the percentage-point change in each holding's weight.
Explain that this compares one snapshot, not time-weighted investment performance.
```

### A complete holdings dashboard

```text
Build a visual holdings report with four KPI cards: invested capital, market value,
unrealized P&L and unrealized return percentage, each with data-coverage notes.
Then show a stock-allocation donut, signed P&L bars and a detailed holdings table.

Separate positive and negative P&L visually, but include +/- signs so meaning does
not rely only on color. Add a sector donut only if a sourced sector mapping exists.
Use INR, readable labels, a restrained color palette and the actual snapshot time.
Fetch each needed Jainam snapshot once and reuse it for every view. Keep it read-only.
```

### Sector versus investment size

```text
Using my holdings and a sourced sector mapping, make a treemap where each rectangle
is a stock, its area is current market value and its group is sector. Use a diverging
color scale for unrealized return only where cost and market value are both known.
Keep missing-return values neutral and show Unclassified separately. Provide a
sector-wise table and explain concentration without recommending trades.
If a treemap is unsupported, use grouped horizontal bars instead.
```

### Largest holdings and concentration

```text
Show my ten largest holdings as a horizontal market-value bar chart. Calculate the
largest-position share and top-5 concentration using the same valued-holdings
denominator. Add the total excluded market value if known, or say that it is unknown.
Do not present incomplete valuation as the complete portfolio. Give three factual
observations about concentration, not instructions to buy or sell.
```

### Open positions: profit and loss

```text
Read my existing positions once. Show a diverging horizontal bar chart of
broker-reported unrealized P&L by instrument, centered at zero. Separate realized
and unrealized P&L in KPI cards; do not add fields that overlap.

For futures/options, verify whether quantity means lots or units and whether a
contract multiplier has already been applied. If unclear, use labelled broker P&L
only and omit derived exposure. Include exchange, expiry, product, currency and
snapshot time in a table. Never close or change a position.
```

### Positions by exchange or product

```text
Create a donut chart showing the count of my open positions by exchange, and a
second chart by product type. Make clear that these slices represent position
counts, not invested capital, margin or maximum loss. Exclude closed/zero-quantity
positions after verifying the schema, and show an exceptions table for ambiguous
records. Do not sum rupee notional across options and futures without valid units.
```

### Trade activity: where did I trade most?

```text
Analyze my returned trade book. State the actual date range it covers. Deduplicate
by exchange trade ID if present and count partial fills as fills. Show a donut
chart of traded turnover by symbol and an hourly bar chart of fill counts in IST.

Call turnover trading activity, not invested capital or profit. Show fill count,
unique order count and completed round trips separately, with unknowns explicit.
Do not infer realized P&L from unmatched buy and sell cash flows.
```

### Realized-profit analysis, when the data supports it

```text
Create a realized-profit report for the date range actually available in my trade
book. Use broker-reported realized P&L if supplied and explain its definition.
Only reconstruct FIFO P&L when opening inventory, complete fills, contract units,
corporate actions and charges are known; otherwise explain what is missing.

Where valid, show signed P&L bars by symbol and a chronological cumulative-realized
P&L line chart. Label it realized P&L, not an equity curve or total portfolio return.
Do not invent win rate, profit factor, drawdown or net profit when their inputs
cannot be established. Show gross results and charges separately.
```

### Orders versus executed trades

```text
Fetch the order book and trade book once each. Show the number of orders by current
state as a donut chart and reconcile their filled quantities against trade fills.
Cancelled or pending orders must not count as executed trades. Treat partial fills
correctly and do not double-count repeated updates of the same order.
Show at most three ambiguous orders for follow-up history checks. Label different
fetch times and explain that these two books are not an atomic snapshot.
```

### Historical candlestick chart

```text
Help me confirm the exact instrument, exchange, expiry, token, date range and
broker-supported resolution. Then fetch historical candles for at most 31 days.
Show a candlestick chart with volume below it only if those fields are returned.
Use Unix milliseconds for the request, label the display timezone, sort and
deduplicate timestamps, and identify gaps and any still-forming candle.
Do not invent missing candles or imply this is a live streaming chart.
```

### A report I can open locally

```text
Using the already fetched, sanitized holdings snapshot, create a self-contained
HTML report with inline charts, a stock-allocation donut, KPI cards and an
accessible table. Use no remote scripts, external assets, analytics or API calls.
Include no user ID, PAN, contact information, session tokens or other credentials.

Ask where I want to save the private report before writing a file, if your client
supports file creation. Keep the report local and do not upload it. If file tools
are unavailable, provide the report content or a chart-ready table instead.
```

## Make every result more useful

Append this to any prompt:

```text
Before charting, list the available fields and confirm the chart's metric and
units. Fetch each required endpoint once, reuse the snapshot and do calculations
in the client's code tool if available. Do not repeatedly poll. Do not use external
web enrichment without asking me. Distinguish zero from unavailable. Every chart
must show a title, metric, units, denominator, coverage and snapshot time, with a
table fallback. Keep credentials and personal identifiers out of the report.
```

A model can make arithmetic or classification errors. Compare totals with the source table; a polished chart is not proof of accuracy. This library describes analysis requests, not financial advice or promised client capabilities.

## Reusable MCP prompt templates

The server also exposes `holdings_dashboard`, `positions_review`, `trade_journal_review`, `account_reconciliation` and `historical_chart` through MCP's prompt capability. Clients that support prompt discovery can select these directly; other clients can use the text above. A prompt template does not run an API call or execute a trade by itself.
