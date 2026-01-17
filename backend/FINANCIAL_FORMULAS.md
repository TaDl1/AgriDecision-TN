# AgriDecision Financial Engine - Formulas & Variables

## Crop Input Types Classification

### Seeds (seeds_kg)
- Chickpeas, Lentils, Wheat, Fava Beans, Green Peas
- Potato, Onion, Garlic, Carrots, Spinach
- Zucchini (packet), Okra, Watermelon

### Seedlings (seedlings)
- Tomato (100 seedlings option)
- Pepper (100 seedlings option)

### Sapling (sapling)
- Olive, Almond, Citrus, Grape
- Artichoke (crowns/root divisions)

## Financial Calculation Formulas

### 1. Input Cost Calculation
```
Total_Input_Cost = Input_Quantity × Cost_Per_Unit
```
**Example**: 1 kg wheat seeds × 5 TND/kg = 5 TND

### 2. Expected Yield Range (Interval-based)
```
Min_Yield = Input_Quantity × Yield_Min_Multiplier
Max_Yield = Input_Quantity × Yield_Max_Multiplier
```
**Example**: 1 kg wheat seeds
- Min: 1 × 20 = 20 kg
- Max: 1 × 40 = 40 kg

### 3. Expected Revenue Range
```
Min_Revenue = Min_Yield × Market_Price_Per_Kg
Max_Revenue = Max_Yield × Market_Price_Per_Kg
```
**Example**: Wheat with market price 1.5 TND/kg
- Min: 20 kg × 1.5 = 30 TND
- Max: 40 kg × 1.5 = 60 TND

### 4. Expected Profit Range
```
Min_Profit = Min_Revenue - Total_Input_Cost
Max_Profit = Max_Revenue - Total_Input_Cost
```
**Example**: 
- Min: 30 - 5 = 25 TND
- Max: 60 - 5 = 55 TND

### 5. ROI (Return on Investment) Range
```
Min_ROI = (Min_Profit / Total_Input_Cost) × 100%
Max_ROI = (Max_Profit / Total_Input_Cost) × 100%
```
**Example**:
- Min: (25 / 5) × 100% = 500%
- Max: (55 / 5) × 100% = 1100%

## Analytics - Money Saved Calculation (Risk Avoidance)

When a farmer follows "WAIT" or "NOT_RECOMMENDED" advice:

```
Saved_Amount = Input_Quantity × Cost_Per_Unit
```

**Interval Display**:
```
Total_Saved_Min = Σ(avoided_decisions) Saved_Amount
Total_Saved_Max = Total_Saved_Min (same, as cost is fixed)
```

**Display**: "You saved X TND by avoiding Y risky decisions"

## Analytics - Potential Gains (If Planted Successfully)

For successful plantings, calculate actual vs expected:

```
Actual_Yield = recorded_yield_kg (from Outcome table)
Expected_Yield_Range = [Input_Quantity × Yield_Min, Input_Quantity × Yield_Max]

Performance_Ratio = Actual_Yield / ((Yield_Min + Yield_Max) / 2)
```

**Display**: "Your wheat yielded 35kg (within expected 20-40kg range)"

## Crop-Specific Examples

### Wheat (seeds_kg)
- Input: 1 kg seeds @ 5 TND/kg
- Yield: 20-40 kg
- Market: 1.5 TND/kg
- Revenue: 30-60 TND
- Profit: 25-55 TND

### Tomato (seedlings)
- Input: 100 seedlings @ 0.5 TND/seedling = 50 TND
- Yield: 300-800 kg (3-8 kg per seedling)
- Market: 2 TND/kg
- Revenue: 600-1600 TND
- Profit: 550-1550 TND

### Olive (sapling)
- Input: 1 tree @ 50 TND
- Yield: 20-40 kg/year (annual)
- Market: 3 TND/kg
- Revenue: 60-120 TND/year
- Profit: 10-70 TND (first year), then 60-120 TND/year

### Citrus (sapling)
- Input: 1 tree @ 60 TND
- Yield: 50-150 kg/year
- Market: 2 TND/kg
- Revenue: 100-300 TND/year
- Profit: 40-240 TND (first year), then 100-300 TND/year

## UI Display Patterns

### Dashboard Modal (Get Advice)
```
"Estimated Harvest: 20-40 kg"
"Potential Revenue: 30-60 TND"
"Expected Profit: 25-55 TND"
```

### Analytics (Money Saved)
```
"You saved between 150-150 TND by avoiding 5 risky decisions"
(or simplified: "You saved 150 TND...")
```

### Analytics (Performance)
```
"Your crops generated 450-780 TND in revenue this season"
"Average yield performance: 85% of optimal range"
```
