# 🍬 Nassau Candy Distributor — Profitability Dashboard

A Streamlit analytics dashboard that transforms raw order data into
product-level profitability intelligence for Nassau Candy Distributor.

---

## 📊 Dashboard Modules

| Tab | Description |
|-----|-------------|
| **Product Profitability** | Margin leaderboard, profit contribution, sales vs margin matrix |
| **Division Performance** | Revenue vs profit by division, region breakdown, margin distribution |
| **Cost & Margin Diagnostics** | Cost-sales scatter, waterfall chart, risk flag table |
| **Profit Concentration (Pareto)** | 80/20 analysis, US state map, treemap, dependency risk |

### Sidebar Filters
- 📅 Order date range selector
- 🏭 Division multi-select
- 🌎 Region multi-select
- 📈 Minimum gross margin threshold slider
- 🔍 Product name search

---

## 📐 KPIs Tracked

| KPI | Formula |
|-----|---------|
| Gross Margin (%) | Gross Profit ÷ Sales × 100 |
| Profit per Unit | Gross Profit ÷ Units |
| Revenue Contribution | Product Sales ÷ Total Sales |
| Profit Contribution | Product Profit ÷ Total Profit |
| Cost Ratio (%) | Cost ÷ Sales × 100 |

---

## 🧹 Data Cleaning Applied

- Removed rows where Sales ≤ 0 or Units = 0
- Dropped records with null Gross Profit
- Parsed Order Date and Ship Date (dd-mm-yyyy format)
- Stripped whitespace from Product Name

---

## 🏭 Factory Reference

| Factory | Latitude | Longitude |
|---------|----------|-----------|
| Lot's O' Nuts | 32.88 | -111.77 |
| Wicked Choccy's | 32.08 | -81.09 |
| Sugar Shack | 48.12 | -96.18 |
| Secret Factory | 41.45 | -90.57 |
| The Other Factory | 35.12 | -89.97 |

---

## 👤 Author

Built as part of the Nassau Candy Distributor Profitability Analysis project.
