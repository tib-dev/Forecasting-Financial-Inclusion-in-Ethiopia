# Forecasting Financial Inclusion in Ethiopia

**Modeling, Explaining, and Forecasting Access and Usage of Digital Financial Services**
An end-to-end data science system for analyzing Ethiopia’s financial inclusion trajectory using time series analysis, event impact modeling, and scenario-based forecasting.

This project builds a **policy-grade financial inclusion analytics and forecasting system** that transforms sparse survey data, operational indicators, and national events into forward-looking insights for regulators, development finance institutions, and fintech operators.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Business Context](#business-context)
- [Objectives](#objectives)
- [Global Findex Framework](#global-findex-framework)
- [Data & Features](#data--features)
- [Unified Data Model](#unified-data-model)
- [Project Structure](#project-structure)
- [System Architecture](#system-architecture)
- [Analytical Pipeline](#analytical-pipeline)
- [Event Impact Modeling](#event-impact-modeling)
- [Forecasting Approach](#forecasting-approach)
- [Dashboard](#dashboard)
- [Engineering Practices](#engineering-practices)
- [Setup & Installation](#setup--installation)
- [Running the Project](#running-the-project)
- [Technologies Used](#technologies-used)
- [Author](#author)

---

## Project Overview

This project implements a **full financial inclusion research and forecasting workflow**, similar to what is used by central banks, multilateral institutions, and fintech strategy teams.

The system covers the complete lifecycle:

- Ingesting and unifying heterogeneous financial inclusion data
- Enriching sparse survey data with operational and infrastructure indicators
- Modeling how policies, product launches, and infrastructure investments affect outcomes
- Forecasting financial inclusion under multiple scenarios
- Visualizing trends, event impacts, and projections through an interactive dashboard

This is a **decision-support and policy analysis system**, not a simple trend extrapolation exercise.

---

## Business Context

Ethiopia is undergoing rapid digital financial transformation:

- Telebirr launched in 2021 and surpassed 54M registered users
- M-Pesa entered in 2023 with rapid adoption
- Interoperable P2P digital transfers now exceed ATM withdrawals

Yet, according to the **Global Findex 2024**, only **49% of adults** have a financial account, up just **3 percentage points since 2021**.

Stakeholders need to understand:

- What truly drives financial inclusion in Ethiopia
- Why massive digital payment growth has not translated into proportional account ownership
- How future policies and investments may change outcomes

This project answers those questions quantitatively.

---

## Objectives

- Build a unified, extensible financial inclusion dataset
- Analyze Ethiopia’s inclusion trajectory across Access and Usage dimensions
- Quantify the impact of events such as policy reforms and product launches
- Forecast financial inclusion outcomes for 2025–2027
- Communicate insights clearly to technical and non-technical stakeholders

---

## Global Findex Framework

The project follows the **World Bank Global Findex** definitions:

### Access — Account Ownership

Share of adults (15+) with an account at a financial institution or who used mobile money in the past 12 months.

### Usage — Digital Payments

Share of adults who made or received a digital payment in the past 12 months.

These indicators are slow-moving, survey-based, and measured every three years, creating unique modeling challenges.

---

## Data & Features

### Core Indicators

| Indicator           | Description                    |
| ------------------- | ------------------------------ |
| ACC_OWNERSHIP       | Account ownership rate         |
| ACC_MM_ACCOUNT      | Mobile money account ownership |
| USG_DIGITAL_PAYMENT | Digital payment usage rate     |

### Supporting Indicators

- Mobile penetration and smartphone adoption
- 4G population coverage
- Agent and merchant density
- Digital transaction volumes
- ATM and bank branch density

### Event Data

- Product launches (Telebirr, M-Pesa)
- Policy and regulatory changes (NBE directives)
- Infrastructure milestones (interoperability, digital ID rollout)
- Market entries and ecosystem shifts

---

## Unified Data Model

All data follows a **single unified schema** with a `record_type` field:

| record_type | Description                                         |
| ----------- | --------------------------------------------------- |
| observation | Measured values from surveys, operators, or reports |
| event       | Policies, launches, infrastructure investments      |
| impact_link | Modeled relationships between events and indicators |
| target      | Official policy targets (e.g., NFIS goals)          |

**Key design principle**
Events are _not_ pre-assigned to Access or Usage. Their effects are modeled explicitly through `impact_link` records, avoiding analytical bias.

---

## Project Structure

```text
forecasting-financial-inclusion-ethiopia/
├── data/
│   ├── raw/                        # Original source files
│   ├── processed/                  # Unified & enriched datasets
│   └── reference/                  # Reference codes & schema docs
├── notebooks/
│   ├── data_enrichment.ipynb
│   ├── eda.ipynb
│   ├── event_impact.ipynb
│   └── forecasting.ipynb
├── dashboard/
│   └── app.py                      # Streamlit application
├── reports/
│   ├── figures/
│   └── summary_insights.md
├── src/
│   └── fi_forecasting/
│       ├── data/                   # Loaders & validators
│       ├── enrichment/             # Feature & proxy indicators
│       ├── modeling/               # Event & regression models
│       ├── forecasting/            # Scenario-based forecasts
│       └── utils/
├── data_enrichment_log.md
├── README.md
└── pyproject.toml
```

## System Architecture

``text

```text
┌──────────────────────────┐
│ Global Findex & Reports │
│ Operator & Infra Data │
└───────────┬──────────────┘
│
▼
┌──────────────────────────┐
│ Unified Data Ingestion │
│ & Enrichment Layer │
└───────────┬──────────────┘
│
▼
┌──────────────────────────┐
│ Exploratory Analysis │
│ & Market Diagnostics │
└───────────┬──────────────┘
│
▼
┌──────────────────────────┐
│ Event Impact Modeling │
│ (Interventions & Lags) │
└───────────┬──────────────┘
│
▼
┌──────────────────────────┐
│ Forecasting Engine │
│ - Baseline Trend │
│ - Event-Augmented │
│ - Scenarios │
└───────────┬──────────────┘
│
▼
┌──────────────────────────┐
│ Interactive Dashboard │
│ & Policy Insights │
└──────────────────────────┘
```

```

## Analytical Pipeline

- Load and validate unified dataset
- Enrich with infrastructure and proxy indicators
- Perform exploratory data analysis
- Map events to indicators via impact links
- Estimate event effects with lag structures
- Generate baseline and scenario forecasts
- Visualize trends, impacts, and projections

## Event Impact Modeling

- Events are modeled as intervention variables with:

* Direction (positive / negative)
* Magnitude (low / medium / high)
* Lag (months)
* Evidence basis (local data or comparable countries)

- This allows the model to explain why:

* Mobile money usage surged
* Account ownership growth slowed
* Infrastructure improvements lead usage before access

## Forecasting Approach

- Given limited survey points:

* Trend regression for structural baseline
* Event-augmented adjustments
* Scenario analysis (optimistic, base, pessimistic)
* Explicit uncertainty bounds
* Forecast horizon:
* 2025–2027

- Outputs are probabilistic and policy-relevant, not point predictions.

## Dashboard

- Built with Streamlit, the dashboard includes:

* Key financial inclusion metrics
* Interactive time-series exploration
* Event timeline overlays
* Forecasts with confidence intervals
* Progress toward national inclusion targets
* Scenario selector for policy analysis

## Engineering Practices

- Unified schema for heterogeneous data
- Explicit causal assumptions via impact links
- Transparent documentation of uncertainty
- Modular, reproducible notebooks
- Separation of analysis, modeling, and visualization

## Setup & Installation

## Running the Project

## Technologies Used

## Author
```
