from em_cubed.indexer import extract_fenced_block
import pathlib

content = pathlib.Path('skills/TIME_SERIES/time-series-forecaster/SKILL.md').read_text()
py = extract_fenced_block(content, 'python')
print('Python found:', py is not None)
if py:
    print('First 200 chars:', py[:200])

prolog = extract_fenced_block(content, 'prolog')
print('Prolog found:', prolog is not None)

hy = extract_fenced_block(content, 'hy')
print('Hy found:', hy is not None)
