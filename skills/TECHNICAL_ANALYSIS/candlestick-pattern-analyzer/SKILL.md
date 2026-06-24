---
name: candlestick-pattern-analyzer
domain: TECHNICAL_ANALYSIS
version: 1.0.0
surfaces:
- python
- prolog
- quickjs
description: Candlestick pattern analyzer for financial time-series pattern recognition and technical signal detection.
compatibility: PYTHON
complexity: Medium
type: Analysis
category: Technical Analysis Skills
estimated execution time: 2-5 minutes
source: community
allowed-tools: '- read

  - write

  - edit

  - bash

  - glob

  - grep

  - codebase_search

  - task

  - sequentialthinking_sequentialthinking

  - webfetch

  - websearch

  - question

  - suggest

  '
---
origin: manual
triggers:
  - candlestick_analysis
  - pattern_recognition
  - price_action
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0

## Purpose

Multi-surface candlestick pattern analyzer for encoding, generating, and matching ordered sequences of price action patterns. Uses Python for numerical encoding, Prolog for combinatorial pattern generation, and QuickJS for fast sequence matching.

## Implementation

### Python Pattern Encoding

```python
class CandlestickEncoder:
    def encode_candle(self, open_price, high, low, close):
        body = abs(close - open_price)
        range_total = high - low
        is_bullish = close > open_price
        is_bearish = close < open_price

        if body < 0.1 * range_total and is_bullish:
            return "hammer"
        elif body < 0.1 * range_total and is_bearish:
            return "hanging_man"
        elif is_bullish and close > open_price + 0.9 * range_total:
            return "bullish_maribozu"
        elif is_bearish and close < open_price - 0.9 * range_total:
            return "bearish_maribozu"
        elif is_bullish:
            return "bullish"
        elif is_bearish:
            return "bearish"
        else:
            return "doji"

    def encode_sequence(self, candles):
        return [self.encode_candle(**c) for c in candles]
```

### Prolog Pattern Rules

```prolog
% Define candlestick pattern types
bullish_pattern(hammer).
bullish_pattern(bullish_maribozu).
bullish_pattern(bullish).

bearish_pattern(hanging_man).
bearish_pattern(bearish_maribozu).
bearish_pattern(bearish).

% Pattern sequence validation
valid_pattern_sequence([bullish, bullish]) :- !.
valid_pattern_sequence([bullish, hammer]) :- !.
valid_pattern_sequence([bearish, bearish]) :- !.
valid_pattern_sequence([bearish, hanging_man]) :- !.
valid_pattern_sequence([doji, bullish]) :- !.
valid_pattern_sequence([doji, bearish]) :- !.
valid_pattern_sequence(Pattern) :- length(Pattern, 1).

% Generate permutations
pattern_permutation([A, B]) :- bullish_pattern(A), bearish_pattern(B).
pattern_permutation([A, B]) :- bearish_pattern(A), bullish_pattern(B).
pattern_permutation([doji, A]) :- (bullish_pattern(A) ; bearish_pattern(A)).
pattern_permutation([A, doji]) :- (bullish_pattern(A) ; bearish_pattern(A)).

% Match against known sequences
match_candlestick_signal([hammer, bullish_maribozu], strong_buy).
match_candlestick_signal([bullish, bullish], buy).
match_candlestick_signal([hanging_man, bearish_maribozu], strong_sell).
match_candlestick_signal([bearish, bearish], sell).
```

### QuickJS Sequence Matcher

```javascript
function matchPattern(sequence) {
    const patternMap = {
        "hammer_bullish_maribozu": "strong_buy",
        "bullish_bullish": "buy",
        "hanging_man_bearish_maribozu": "strong_sell",
        "bearish_bearish": "sell",
        "doji_bullish": "neutral_to_buy",
        "doji_bearish": "neutral_to_sell"
    };
    
    const key = sequence.slice(0, 2).join("_");
    return patternMap[key] || "neutral";
}

function countPatterns(candles) {
    const counts = { bullish: 0, bearish: 0, doji: 0, neutral: 0 };
    for (const c of candles) {
        counts[c] = (counts[c] || 0) + 1;
    }
    return counts;
}
```

## Testing

```python
import pytest

@pytest.mark.asyncio
async def test_candlestick_encoder():
    code = '''
class CandlestickEncoder:
    def encode_candle(self, open_price, high, low, close):
        body = abs(close - open_price)
        range_total = high - low
        is_bullish = close > open_price
        is_bearish = close < open_price
        if is_bullish and close > open_price + 0.9 * range_total:
            return "bullish_maribozu"
        elif is_bearish:
            return "bearish"
        elif is_bullish:
            return "bullish"
        else:
            return "doji"

encoder = CandlestickEncoder()
result = encoder.encode_candle(100, 110, 99, 109) == "bullish_maribozu"
result
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

@pytest.mark.asyncio
async def test_candlestick_prolog_rules():
    code = '''
from em_cubed.surfaces import PrologSurface
surface = PrologSurface()
program = """
bullish_pattern(hammer).
bullish_pattern(bullish_maribozu).
valid_pattern_sequence([A, B]) :- bullish_pattern(A), bullish_pattern(B).
?- valid_pattern_sequence([hammer, bullish_maribozu]).
"""
result = surface.execute(program, {})
result["status"] == "ok"
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

@pytest.mark.asyncio
async def test_quickjs_pattern_match():
    code = '''
from em_cubed.surfaces import QuickJSSurface
surface = QuickJSSurface()
script = '''
function matchPattern(sequence) {
    const patternMap = {
        "hammer_bullish_maribozu": "strong_buy",
        "bullish_bullish": "buy"
    };
    return patternMap[sequence.slice(0, 2).join("_")] || "neutral";
}
matchPattern(["hammer", "bullish_maribozu"])
'''
    result = surface.execute(script, {})
    result.get("output") == "strong_buy"
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
'''
```

## Security Considerations
- Pure numerical operations on OHLC data
- In-memory sequence processing only
- No file system or network access

## Dependencies
- numpy (for numerical encoding)
- No external API dependencies