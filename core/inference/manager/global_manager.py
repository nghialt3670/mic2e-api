"""
Global predictor manager instance (singleton pattern).
"""

from typing import Optional

from core.inference.manager.predictor_manager import PredictorManager


class GlobalPredictorManager:
    """Singleton wrapper for PredictorManager."""

    _instance: Optional[PredictorManager] = None
    _initialized: bool = False

    @classmethod
    def get_instance(cls) -> PredictorManager:
        """Get the global predictor manager instance."""
        if cls._instance is None:
            cls._instance = PredictorManager()
            cls._initialized = False
        return cls._instance

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if the manager is initialized."""
        return cls._initialized

    @classmethod
    def mark_initialized(cls):
        """Mark the manager as initialized."""
        cls._initialized = True

    @classmethod
    def reset(cls):
        """Reset the singleton instance."""
        cls._instance = None
        cls._initialized = False


# Convenience function for getting the global manager
def get_predictor_manager() -> PredictorManager:
    """Get the global predictor manager instance."""
    return GlobalPredictorManager.get_instance()


# Convenience function for shutdown
async def shutdown_predictor_manager():
    """Shutdown the global predictor manager."""
    if GlobalPredictorManager._instance is not None:
        await GlobalPredictorManager._instance.shutdown()
        GlobalPredictorManager.reset()
