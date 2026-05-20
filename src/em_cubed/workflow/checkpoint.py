"""Durable execution and state management for Em-Cubed workflows."""

from __future__ import annotations

import json
import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from abc import abstractmethod
from pathlib import Path
import structlog

logger = structlog.get_logger()


@dataclass
class Checkpoint:
    """Represents a workflow execution checkpoint."""
    checkpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    execution_id: str = ""
    timestamp: float = field(default_factory=time.time)
    step_name: str = ""
    state_data: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    substrate: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "workflow_id": self.workflow_id,
            "execution_id": self.execution_id,
            "timestamp": self.timestamp,
            "step_name": self.step_name,
            "state_data": self.state_data,
            "variables": self.variables,
            "context": self.context,
            "substrate": self.substrate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        """Create from dictionary."""
        return cls(
            checkpoint_id=data["checkpoint_id"],
            workflow_id=data["workflow_id"],
            execution_id=data["execution_id"],
            timestamp=data["timestamp"],
            step_name=data["step_name"],
            state_data=data.get("state_data", {}),
            variables=data.get("variables", {}),
            context=data.get("context", {}),
            substrate=data.get("substrate", {})
        )


class CheckpointStorage:
    """Abstract base class for checkpoint storage backends."""
    
    @abstractmethod
    def save_checkpoint(self, checkpoint: Checkpoint) -> bool:
        """Save a checkpoint.
        
        Args:
            checkpoint: The checkpoint to save
            
        Returns:
            True if save successful
        """
        pass
    
    @abstractmethod
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Load a checkpoint by ID.
        
        Args:
            checkpoint_id: The checkpoint ID to load
            
        Returns:
            The checkpoint if found, None otherwise
        """
        pass
    
    @abstractmethod
    def list_checkpoints(self, workflow_id: Optional[str] = None) -> List[str]:
        """List checkpoint IDs.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            
        Returns:
            List of checkpoint IDs
        """
        pass
    
    @abstractmethod
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint.
        
        Args:
            checkpoint_id: The checkpoint ID to delete
            
        Returns:
            True if deletion successful
        """
        pass


class FileCheckpointStorage(CheckpointStorage):
    """File-based checkpoint storage."""
    
    def __init__(self, storage_dir: Path):
        """Initialize file-based storage.
        
        Args:
            storage_dir: Directory to store checkpoint files
        """
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger.bind(component="file_checkpoint_storage")
    
    def _get_checkpoint_path(self, checkpoint_id: str) -> Path:
        """Get file path for a checkpoint."""
        # Create a subdirectory based on first 2 chars of ID for better filesystem performance
        subdir = checkpoint_id[:2] if len(checkpoint_id) >= 2 else "00"
        checkpoint_dir = self.storage_dir / subdir
        checkpoint_dir.mkdir(exist_ok=True)
        return checkpoint_dir / f"{checkpoint_id}.json"
    
    def save_checkpoint(self, checkpoint: Checkpoint) -> bool:
        """Save a checkpoint to file."""
        try:
            checkpoint_path = self._get_checkpoint_path(checkpoint.checkpoint_id)
            with open(checkpoint_path, 'w') as f:
                json.dump(checkpoint.to_dict(), f, indent=2)
            self.logger.debug("Checkpoint saved", checkpoint_id=checkpoint.checkpoint_id)
            return True
        except Exception as e:
            self.logger.error("Failed to save checkpoint", 
                            checkpoint_id=checkpoint.checkpoint_id, error=str(e))
            return False
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Load a checkpoint from file."""
        try:
            checkpoint_path = self._get_checkpoint_path(checkpoint_id)
            if not checkpoint_path.exists():
                return None
            
            with open(checkpoint_path, 'r') as f:
                data = json.load(f)
            checkpoint = Checkpoint.from_dict(data)
            self.logger.debug("Checkpoint loaded", checkpoint_id=checkpoint_id)
            return checkpoint
        except Exception as e:
            self.logger.error("Failed to load checkpoint", 
                            checkpoint_id=checkpoint_id, error=str(e))
            return None
    
    def list_checkpoints(self, workflow_id: Optional[str] = None) -> List[str]:
        """List checkpoint IDs."""
        checkpoint_ids = []
        try:
            for subdir in self.storage_dir.iterdir():
                if subdir.is_dir():
                    for checkpoint_file in subdir.glob("*.json"):
                        # Optionally load and filter by workflow_id
                        if workflow_id is not None:
                            try:
                                with open(checkpoint_file, 'r') as f:
                                    data = json.load(f)
                                if data.get("workflow_id") == workflow_id:
                                    checkpoint_ids.append(data["checkpoint_id"])
                            except Exception:  # nosec B112
                                # If we can't read the file, skip it
                                continue
                        else:
                            # Extract ID from filename (without .json extension)
                            checkpoint_ids.append(checkpoint_file.stem)
        except Exception as e:
            self.logger.error("Failed to list checkpoints", error=str(e))
        return checkpoint_ids
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint file."""
        try:
            checkpoint_path = self._get_checkpoint_path(checkpoint_id)
            if checkpoint_path.exists():
                checkpoint_path.unlink()
                self.logger.debug("Checkpoint deleted", checkpoint_id=checkpoint_id)
                return True
            return False
        except Exception as e:
            self.logger.error("Failed to delete checkpoint", 
                            checkpoint_id=checkpoint_id, error=str(e))
            return False


class CheckpointManager:
    """Manages workflow checkpointing and recovery."""
    
    def __init__(self, storage: CheckpointStorage):
        """Initialize checkpoint manager.
        
        Args:
            storage: The storage backend to use for checkpoints
        """
        self.storage = storage
        self.logger = logger.bind(component="checkpoint_manager")
        self._checkpoints: Dict[str, Checkpoint] = {}  # In-memory cache
    
    def create_checkpoint(self, workflow_id: str, execution_id: str, 
                         step_name: str, state_data: Optional[Dict[str, Any]] = None,
                         variables: Optional[Dict[str, Any]] = None,
                         context: Optional[Dict[str, Any]] = None,
                         substrate: Optional[Dict[str, Any]] = None) -> str:
        """Create a new checkpoint.
        
        Args:
            workflow_id: The workflow ID
            execution_id: The execution ID
            step_name: Name of the current step
            state_data: Workflow state data
            variables: Variable bindings
            context: Execution context
            substrate: Shared substrate data
            
        Returns:
            The checkpoint ID
        """
        checkpoint = Checkpoint(
            workflow_id=workflow_id,
            execution_id=execution_id,
            step_name=step_name,
            state_data=state_data or {},
            variables=variables or {},
            context=context or {},
            substrate=substrate or {}
        )
        
        # Save to storage
        if self.storage.save_checkpoint(checkpoint):
            # Cache in memory
            self._checkpoints[checkpoint.checkpoint_id] = checkpoint
            self.logger.info("Checkpoint created", 
                           checkpoint_id=checkpoint.checkpoint_id,
                           workflow_id=workflow_id,
                           step_name=step_name)
            return checkpoint.checkpoint_id
        else:
            self.logger.error("Failed to create checkpoint",
                            workflow_id=workflow_id,
                            step_name=step_name)
            return ""
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Load a checkpoint by ID.
        
        Args:
            checkpoint_id: The checkpoint ID to load
            
        Returns:
            The checkpoint if found, None otherwise
        """
        # Check memory cache first
        if checkpoint_id in self._checkpoints:
            return self._checkpoints[checkpoint_id]
        
        # Load from storage
        checkpoint = self.storage.load_checkpoint(checkpoint_id)
        if checkpoint:
            # Cache in memory
            self._checkpoints[checkpoint_id] = checkpoint
        return checkpoint
    
    def list_checkpoints(self, workflow_id: Optional[str] = None) -> List[str]:
        """List checkpoint IDs.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            
        Returns:
            List of checkpoint IDs
        """
        return self.storage.list_checkpoints(workflow_id)
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint.
        
        Args:
            checkpoint_id: The checkpoint ID to delete
            
        Returns:
            True if deletion successful
        """
        # Remove from cache
        self._checkpoints.pop(checkpoint_id, None)
        
        # Delete from storage
        return self.storage.delete_checkpoint(checkpoint_id)
    
    def get_latest_checkpoint(self, workflow_id: str, 
                             execution_id: Optional[str] = None) -> Optional[Checkpoint]:
        """Get the latest checkpoint for a workflow.
        
        Args:
            workflow_id: The workflow ID
            execution_id: Optional execution ID to filter by
            
        Returns:
            The latest checkpoint if found, None otherwise
        """
        checkpoint_ids = self.list_checkpoints(workflow_id)
        if not checkpoint_ids:
            return None
        
        # Load all checkpoints for this workflow
        checkpoints = []
        for checkpoint_id in checkpoint_ids:
            checkpoint = self.load_checkpoint(checkpoint_id)
            if checkpoint:
                # Filter by execution_id if specified
                if execution_id is None or checkpoint.execution_id == execution_id:
                    checkpoints.append(checkpoint)
        
        if not checkpoints:
            return None
        
        # Return the most recent
        return max(checkpoints, key=lambda cp: cp.timestamp)


# Global checkpoint manager instance
_checkpoint_manager: Optional[CheckpointManager] = None


def get_checkpoint_manager() -> Optional[CheckpointManager]:
    """Get the global checkpoint manager instance."""
    global _checkpoint_manager
    return _checkpoint_manager


def initialize_checkpoint_manager(storage_dir: Optional[Path] = None) -> CheckpointManager:
    """Initialize the global checkpoint manager.
    
    Args:
        storage_dir: Directory to store checkpoints (defaults to ~/.em-cubed/checkpoints)
        
    Returns:
        The initialized CheckpointManager instance
    """
    global _checkpoint_manager
    
    if storage_dir is None:
        storage_dir = Path.home() / ".em-cubed" / "checkpoints"
    
    storage = FileCheckpointStorage(storage_dir)
    _checkpoint_manager = CheckpointManager(storage)
    logger.info("Checkpoint manager initialized", storage_dir=str(storage_dir))
    return _checkpoint_manager