"""PyArrow zero-copy shared memory substrate for high-throughput polyglot data exchange."""

from typing import Any

import structlog

logger = structlog.get_logger()

try:
    import pyarrow as pa
    from pyarrow import ipc

    _PYARROW_AVAILABLE = True
except ImportError:
    pa = None  # type: ignore[assignment]
    ipc = None  # type: ignore[assignment]
    _PYARROW_AVAILABLE = False


class ArrowSharedSubstrate:
    """Zero-copy Arrow memory substrate manager across execution surfaces."""

    def __init__(self):
        self._table_store: dict[str, Any] = {}
        logger.info("ArrowSharedSubstrate initialized", pyarrow_available=_PYARROW_AVAILABLE)

    @property
    def available(self) -> bool:
        return _PYARROW_AVAILABLE

    def register_table(self, name: str, data: Any) -> bool:
        """Register a dataset as an Arrow Table in the substrate.

        Args:
            name: Table identifier
            data: Data payload (Arrow Table, RecordBatch, pandas DataFrame, list of dicts, or dict of lists)

        Returns:
            True if registration succeeded
        """
        if not _PYARROW_AVAILABLE:
            # Fallback to raw dict storage
            self._table_store[name] = data
            return True

        try:
            if isinstance(data, pa.Table):
                arrow_table = data
            elif isinstance(data, pa.RecordBatch):
                arrow_table = pa.Table.from_batches([data])
            elif isinstance(data, dict):
                arrow_table = pa.Table.from_pydict(data)
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                arrow_table = pa.Table.from_pylist(data)
            elif hasattr(data, "to_arrow") or hasattr(data, "to_arrow_table"):
                arrow_table = getattr(data, "to_arrow", data.to_arrow_table)()
            else:
                arrow_table = pa.Table.from_pydict({"value": [str(data)]})

            self._table_store[name] = arrow_table
            logger.info("Registered table in Arrow substrate", name=name, num_rows=arrow_table.num_rows, num_columns=arrow_table.num_columns)
            return True
        except Exception as e:
            logger.exception("Failed to register table in Arrow substrate", name=name, error=str(e))
            self._table_store[name] = data
            return False

    def get_table(self, name: str) -> Any:
        """Retrieve a registered table from substrate."""
        return self._table_store.get(name)

    def serialize_ipc(self, name: str) -> bytes | None:
        """Serialize an Arrow table to IPC stream bytes for zero-copy transmission.

        Returns:
            Bytes buffer containing IPC stream payload or None if table missing/unsupported.
        """
        table = self.get_table(name)
        if table is None:
            return None

        if not _PYARROW_AVAILABLE or not isinstance(table, pa.Table):
            import json
            return json.dumps(table).encode("utf-8")

        sink = pa.BufferOutputStream()
        with ipc.new_stream(sink, table.schema) as writer:
            writer.write_table(table)
        return sink.getvalue().to_pybytes()

    def deserialize_ipc(self, name: str, payload: bytes) -> bool:
        """Deserialize an Arrow IPC stream byte payload into substrate store."""
        if not _PYARROW_AVAILABLE:
            import json
            self._table_store[name] = json.loads(payload.decode("utf-8"))
            return True

        try:
            reader = ipc.open_stream(pa.BufferReader(payload))
            table = reader.read_all()
            self._table_store[name] = table
            return True
        except Exception as e:
            logger.exception("Deserialization of Arrow IPC payload failed", name=name, error=str(e))
            return False

    def to_pydict(self, name: str) -> dict[str, list[Any]] | None:
        """Convert substrate table to Python dictionary format for non-Arrow surfaces."""
        table = self.get_table(name)
        if table is None:
            return None

        if _PYARROW_AVAILABLE and isinstance(table, pa.Table):
            return table.to_pydict()
        if isinstance(table, dict):
            return table
        return {"data": table}

    def clear(self) -> None:
        """Clear all stored tables in substrate."""
        self._table_store.clear()
