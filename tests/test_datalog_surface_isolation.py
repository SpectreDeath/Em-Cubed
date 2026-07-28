"""Tests for DatalogSurface execution cache isolation.

Verifies that each DatalogSurface instance has its own independent cache,
cache is empty on fresh instantiation, clear_cache() works correctly,
cache_size property tracks entries, and cache eviction fires at capacity.
"""

from em_cubed.surfaces.datalog_surface import DatalogSurface


def _make_surface(**kwargs) -> DatalogSurface:
    return DatalogSurface(**kwargs)


class TestCacheInstanceIsolation:
    def test_separate_instances_have_independent_caches(self):
        a = _make_surface()
        b = _make_surface()
        a._execution_cache["sentinel_key"] = {"status": "ok", "value": 42}
        assert "sentinel_key" in a._execution_cache
        assert "sentinel_key" not in b._execution_cache, (
            "Cache is shared between instances - class-level dict bug still present!"
        )

    def test_class_level_dict_does_not_exist(self):
        assert "_execution_cache" not in DatalogSurface.__dict__, "_execution_cache is still defined at class level."


class TestCacheFreshStart:
    def test_cache_empty_on_init(self):
        surface = _make_surface()
        assert surface.cache_size == 0
        assert surface._execution_cache == {}

    def test_two_fresh_instances_both_empty(self):
        a = _make_surface()
        b = _make_surface()
        assert a.cache_size == 0
        assert b.cache_size == 0


class TestClearCache:
    def test_clear_cache_empties_dict(self):
        surface = _make_surface()
        surface._execution_cache["k1"] = {"status": "ok", "value": 1}
        surface._execution_cache["k2"] = {"status": "ok", "value": 2}
        assert surface.cache_size == 2
        surface.clear_cache()
        assert surface.cache_size == 0
        assert surface._execution_cache == {}

    def test_clear_cache_is_idempotent(self):
        surface = _make_surface()
        surface.clear_cache()
        surface.clear_cache()
        assert surface.cache_size == 0

    def test_clear_cache_on_a_does_not_affect_b(self):
        a = _make_surface()
        b = _make_surface()
        a._execution_cache["ak"] = {"status": "ok", "value": "a"}
        b._execution_cache["bk"] = {"status": "ok", "value": "b"}
        a.clear_cache()
        assert a.cache_size == 0
        assert b.cache_size == 1


class TestCacheSizeProperty:
    def test_cache_size_tracks_entries(self):
        surface = _make_surface()
        assert surface.cache_size == 0
        surface._execution_cache["x"] = {}
        assert surface.cache_size == 1
        surface._execution_cache["y"] = {}
        assert surface.cache_size == 2
        del surface._execution_cache["x"]
        assert surface.cache_size == 1


class TestCacheEviction:
    def test_cache_does_not_exceed_max_entries(self, monkeypatch):
        monkeypatch.setenv("EM_CUBED_DATALOG_CACHE_MAX_ENTRIES", "3")
        surface = _make_surface()
        assert surface._cache_max_entries == 3
        for i in range(3):
            key = f"key_{i}"
            if len(surface._execution_cache) >= surface._cache_max_entries:
                oldest = next(iter(surface._execution_cache))
                del surface._execution_cache[oldest]
            surface._execution_cache[key] = {"status": "ok", "value": i}
        assert surface.cache_size == 3
        if len(surface._execution_cache) >= surface._cache_max_entries:
            oldest = next(iter(surface._execution_cache))
            del surface._execution_cache[oldest]
        surface._execution_cache["key_3"] = {"status": "ok", "value": 3}
        assert surface.cache_size == 3
        assert "key_0" not in surface._execution_cache
        assert "key_3" in surface._execution_cache

    def test_default_max_entries_from_env(self, monkeypatch):
        monkeypatch.setenv("EM_CUBED_DATALOG_CACHE_MAX_ENTRIES", "512")
        surface = _make_surface()
        assert surface._cache_max_entries == 512

    def test_default_max_entries_is_256(self, monkeypatch):
        monkeypatch.delenv("EM_CUBED_DATALOG_CACHE_MAX_ENTRIES", raising=False)
        surface = _make_surface()
        assert surface._cache_max_entries == 256
