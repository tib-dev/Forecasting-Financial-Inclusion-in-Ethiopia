# Ethiopia Financial Inclusion - Unified Data Format v2

## Key Design Principle

**Don't force interpretation onto data.**

The previous version made a mistake: it assigned events to pillars (e.g., "Telebirr Launch" → USAGE). This is **biased** because:

- Telebirr affects both ACCESS and USAGE
- Fayda affects ACCESS, GENDER, and TRUST
- The pillar assignment is an **interpretation**, not a fact

## The Correct Approach

| Record Type   | `category` column                             | `pillar` column                            |
| ------------- | --------------------------------------------- | ------------------------------------------ |
| `observation` | (empty)                                       | **YES** - what dimension is measured       |
| `target`      | (empty)                                       | **YES** - what dimension is the goal       |
| `event`       | **Event type** (policy, product_launch, etc.) | **(empty)** - no pre-assignment            |
| `impact_link` | (empty)                                       | **YES** - pillar of the affected indicator |

---

## How It Works

### Events are neutral

```csv
EVT_0001,,event,product_launch,,Telebirr Launch,...
```

- `category` = what type of event (product_launch)
- `pillar` = empty (no pre-interpretation)

### Impact links capture effects

```csv
IMP_0001,EVT_0001,impact_link,,ACCESS,...,ACC_OWNERSHIP,direct,increase,high,15,12,...
IMP_0003,EVT_0001,impact_link,,USAGE,...,USG_P2P_COUNT,direct,increase,high,25,6,...
```

- One event → multiple impact_links
- Each impact_link has a pillar (derived from the affected indicator)

### Query: "What affects ACCESS?"

```python
# Get all impact_links that affect ACCESS indicators
access_impacts = df[
    (df['record_type'] == 'impact_link') &
    (df['pillar'] == 'ACCESS')
]

# Join to get event details
access_events = access_impacts.merge(
    df[df['record_type'] == 'event'],
    left_on='parent_id',
    right_on='record_id'
)
```

---

## Event Categories

| category         | Description          | Examples            |
| ---------------- | -------------------- | ------------------- |
| `product_launch` | New product/service  | Telebirr, M-Pesa    |
| `market_entry`   | New competitor       | Safaricom Ethiopia  |
| `policy`         | Government strategy  | NFIS-II             |
| `regulation`     | Regulatory directive | KYC rules           |
| `infrastructure` | System deployment    | Fayda, EthioPay     |
| `partnership`    | Integration          | M-Pesa + EthSwitch  |
| `milestone`      | Achievement          | P2P > ATM           |
| `economic`       | Macro shock          | FX reform           |
| `pricing`        | Price change         | Safaricom rate hike |

---

## Pillar Definitions (for observations only)

| pillar          | Measures                           |
| --------------- | ---------------------------------- |
| `ACCESS`        | Can people reach services?         |
| `USAGE`         | Are people using services?         |
| `AFFORDABILITY` | Can people afford services?        |
| `GENDER`        | Gender gaps                        |
| `QUALITY`       | Do services work reliably?         |
| `TRUST`         | Do people trust the system?        |
| `DEPTH`         | Beyond payments (savings, credit)? |

---

## Building the Models

### ACCESS Model

```python
# Target: ACCESS observations
Y = df[(df['record_type'] == 'observation') & (df['pillar'] == 'ACCESS')]

# Features: Events that affect ACCESS (via impact_links)
access_impacts = df[(df['record_type'] == 'impact_link') & (df['pillar'] == 'ACCESS')]

# Create event dummies from the events
events = df[df['record_type'] == 'event']
```

### USAGE Model

```python
# Target: USAGE observations
Y = df[(df['record_type'] == 'observation') & (df['pillar'] == 'USAGE')]

# Features: Events that affect USAGE (via impact_links)
usage_impacts = df[(df['record_type'] == 'impact_link') & (df['pillar'] == 'USAGE')]
```

---

## Data Entry Rules

### Adding an observation

```
record_type: observation
category: (leave empty)
pillar: ACCESS or USAGE or GENDER etc.
indicator_code: ACC_OWNERSHIP, USG_P2P_COUNT, etc.
```

### Adding an event

```
record_type: event
category: product_launch, policy, infrastructure, etc.
pillar: (leave empty - don't pre-assign!)
indicator: Event name
```

### Adding an impact link

```
record_type: impact_link
parent_id: The event ID (EVT_XXXX)
category: (leave empty)
pillar: The pillar of the affected indicator
related_indicator: The indicator code being affected
```

---

## Files

| File                           | Purpose                       |
| ------------------------------ | ----------------------------- |
| `ethiopia_fi_unified_data.csv` | The data (56 records)         |
| `reference_codes.csv`          | Valid codes for each field    |
| `SCHEMA_DESIGN.md`             | Detailed schema documentation |
