# Candlestick Pattern Analyzer — Cangjie Edition
# Orchestrates Python encoding, Prolog sequence generation, QuickJS matching

import std.math.*

func main() {
    let input = context["candle_input"] as CandleInput;
    println("Cangjie Candlestick Analyzer Starting...");

    // Python: Encode OHLC candles to pattern types
    let encoded_result = perform EmCubed.call_surface("python", "
class CandlestickEncoder:
    def encode_candle(self, open_price, high, low, close):
        body = abs(close - open_price)
        range_total = high - low
        is_bullish = close > open_price
        is_bearish = close < open_price

        if body < 0.1 * range_total and is_bullish:
            return 'hammer'
        elif body < 0.1 * range_total and is_bearish:
            return 'hanging_man'
        elif is_bullish and close > open_price + 0.9 * range_total:
            return 'bullish_maribozu'
        elif is_bearish and close < open_price - 0.9 * range_total:
            return 'bearish_maribozu'
        elif is_bullish:
            return 'bullish'
        elif is_bearish:
            return 'bearish'
        else:
            return 'doji'

    def encode_sequence(self, candles):
        return [self.encode_candle(**c) for c in candles]

encoder = CandlestickEncoder()
sequence = encoder.encode_sequence(input.candles)
{'sequence': sequence}
    ");

    let sequence = encoded_result.get("sequence", List<String>());

    // Prolog: Generate valid pattern permutations
    let prolog_patterns = perform EmCubed.call_surface("prolog", "
bullish_pattern(hammer).
bullish_pattern(bullish_maribozu).
bullish_pattern(bullish).

bearish_pattern(hanging_man).
bearish_pattern(bearish_maribozu).
bearish_pattern(bearish).

valid_pattern_sequence([A, B]) :- bullish_pattern(A), bullish_pattern(B).
valid_pattern_sequence([A, B]) :- bearish_pattern(A), bearish_pattern(B).

match_candlestick_signal([hammer, bullish_maribozu], strong_buy).
match_candlestick_signal([bullish, bullish], buy).
match_candlestick_signal([hanging_man, bearish_maribozu], strong_sell).
match_candlestick_signal([bearish, bearish], sell).

length(sequence, L), L >= 1.
    ");

    // QuickJS: Fast sequence matching
    let match_result = perform EmCubed.call_surface("quickjs", "
function matchPattern(sequence) {
    const signalMap = {
        'hammer_bullish_maribozu': 'strong_buy',
        'bullish_bullish': 'buy',
        'hanging_man_bearish_maribozu': 'strong_sell',
        'bearish_bearish': 'sell',
        'doji_bullish': 'neutral_to_buy',
        'doji_bearish': 'neutral_to_sell'
    };
    
    const key = sequence.slice(0, 2).join('_');
    const signal = signalMap[key] || 'neutral';
    
    const counts = {};
    for (const p of sequence) {
        counts[p] = (counts[p] || 0) + 1;
    }
    
    const total = sequence.length;
    const dominant = Object.keys(counts).reduce((a, b) => 
        counts[a] > counts[b] ? a : b
    );
    
    return { signal: signal, dominant: dominant, counts: counts };
}

const seq = input.sequence;
matchPattern(seq)
    ");

    return CandleOutput {
        encoded_sequence: sequence,
        signal: match_result.get("signal", "neutral"),
        dominant_pattern: match_result.get("dominant", "neutral"),
        pattern_counts: match_result.get("counts", Map<String, Int32>()),
        validation_passed: prolog_patterns.get("status") == "ok"
    };
}

struct CandleInput {
    candles: List<Map<String, Float64>>;
}

struct CandleOutput {
    encoded_sequence: List<String>;
    signal: String;
    dominant_pattern: String;
    pattern_counts: Map<String, Int32>;
    validation_passed: Bool;
}

## Testing

### Unit Tests

```python
import pytest
from em_cubed.surfaces import PythonSurface

@pytest.mark.asyncio
async def test_candlestick_encoding():
    """Test candlestick pattern encoding."""
    surface = PythonSurface()
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
encoder.encode_candle(100, 110, 99, 109) == "bullish_maribozu"
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
    assert result["value"] == True
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_candlestick_cangjie_edition():
    """Test candlestick skill in registry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "TECHNICAL_ANALYSIS" / "candlestick-pattern-analyzer"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: candlestick-pattern-analyzer\nDomain: TECHNICAL_ANALYSIS')
        (skills_dir / "SKILL_CANGJIE.md").write_text('# CA\nfunc main() {}')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("candlestick", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Analyzing OHLC Sequence

```python
from em_cubed import get_skill

skill = get_skill("candlestick-pattern-analyzer")
candle_input = {
    "candle_input": {
        "candles": [
            {"open_price": 100, "high": 110, "low": 99, "close": 109},
            {"open_price": 109, "high": 115, "low": 108, "close": 114}
        ]
    }
}
result = skill.execute(candle_input)
print("Signal:", result["signal"], "Dominant:", result["dominant_pattern"])
```