import pytest

@pytest.mark.asyncio
async def test_quorum_calculation():
    """Test quorum size calculation for 5-node cluster."""
    code = '''
n_nodes = 5
quorum = (n_nodes // 2) + 1
quorum == 3
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

@pytest.mark.asyncio
async def test_consensus_prolog_rule():
    """Test Prolog consensus validation rules."""
    code = '''
valid_quorum(Votes, Nodes) :-
    length(Votes, VCount),
    length(Nodes, NCount),
    QuorumSize is (NCount // 2) + 1,
    VCount >= QuorumSize.

?- valid_quorum([1,2,3], [a,b,c,d,e]).
'''
    from em_cubed.surfaces import PrologSurface
    surface = PrologSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

@pytest.mark.asyncio
async def test_consensus_hy_scoring():
    """Test Hy consensus confidence computation."""
    code = '''
(defn consensus-confidence [agreement-ratio total-nodes]
  (let [expected (/ total-nodes 2)]
    (/ agreement-ratio (+ expected 1))))

(consensus-confidence 0.8 5)
'''
    from em_cubed.surfaces import HySurface
    surface = HySurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"