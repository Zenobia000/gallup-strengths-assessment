"""
Cache Utilities - Comprehensive Caching Infrastructure

This module provides the foundational caching utilities and abstractions
used throughout the strength assessment system. It supports multiple
backend implementations and provides a consistent interface.

Key Features:
- Abstract cache interface for multiple backends
- Memory-based cache with LRU eviction
- TTL (Time To Live) support
- Cache statistics and monitoring
- Thread-safe operations
- Fallback mechanisms

Design Philosophy:
- Interface segregation (CacheInterface)
- Strategy pattern for different backends
- Dependency injection ready
- Comprehensive error handling

Author: TaskMaster Agent (3.4.7)
Date: 2025-09-30
Version: 1.0
"""

import hashlib
import json
import time
import threading
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union, TypeVar, Generic
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

# Type variables for generic cache operations
K = TypeVar('K')  # Key type
V = TypeVar('V')  # Value type

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Cache statistics for monitoring and optimization."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0

    # Memory usage (for memory-based caches)
    current_entries: int = 0
    max_entries: int = 0
    memory_usage_bytes: int = 0

    # Timing statistics
    avg_get_time_ms: float = 0.0
    avg_set_time_ms: float = 0.0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate percentage."""
        return 100.0 - self.hit_rate


@dataclass
class CacheEntry:
    """Individual cache entry with metadata."""
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def access(self):
        """Record an access to this entry."""
        self.access_count += 1
        self.last_accessed = datetime.now()


class CacheInterface(ABC, Generic[K, V]):
    """
    Abstract interface for cache implementations.

    This interface provides a consistent API across different
    cache backend implementations.
    """

    @abstractmethod
    async def get(self, key: K) -> Optional[V]:
        """Get a value from the cache."""
        pass

    @abstractmethod
    async def set(self, key: K, value: V, ttl: Optional[int] = None) -> bool:
        """Set a value in the cache with optional TTL."""
        pass

    @abstractmethod
    async def delete(self, key: K) -> bool:
        """Delete a value from the cache."""
        pass

    @abstractmethod
    async def exists(self, key: K) -> bool:
        """Check if a key exists in the cache."""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all entries from the cache."""
        pass

    @abstractmethod
    async def keys(self, pattern: Optional[str] = None) -> List[K]:
        """Get all keys, optionally matching a pattern."""
        pass

    @abstractmethod
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        pass


class MemoryCache(CacheInterface[str, Any]):
    """
    High-performance in-memory cache with LRU eviction and TTL support.

    This implementation provides:
    - LRU (Least Recently Used) eviction policy
    - TTL (Time To Live) expiration
    - Thread-safe operations
    - Comprehensive statistics
    - Memory usage monitoring
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize memory cache.

        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl

        # Storage with LRU ordering
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()

        # Statistics
        self._stats = CacheStats(max_entries=max_size)

        # Cleanup task
        self._cleanup_interval = 60  # seconds
        self._last_cleanup = time.time()

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        start_time = time.time()

        async with asyncio.Lock():
            with self._lock:
                entry = self._cache.get(key)

                if entry is None:
                    self._stats.misses += 1
                    self._update_avg_time('get', start_time)
                    return None

                # Check expiration
                if entry.is_expired():
                    del self._cache[key]
                    self._stats.misses += 1
                    self._stats.evictions += 1
                    self._update_avg_time('get', start_time)
                    return None

                # Update access and move to end (most recent)
                entry.access()
                self._cache.move_to_end(key)

                self._stats.hits += 1
                self._update_avg_time('get', start_time)
                return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in the cache with optional TTL."""
        start_time = time.time()

        async with asyncio.Lock():
            with self._lock:
                # Calculate expiration
                ttl_seconds = ttl if ttl is not None else self.default_ttl
                expires_at = datetime.now() + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None

                # Estimate size (rough approximation)
                size_bytes = self._estimate_size(value)

                # Create entry
                entry = CacheEntry(
                    value=value,
                    created_at=datetime.now(),
                    expires_at=expires_at,
                    size_bytes=size_bytes
                )

                # Check if key already exists
                if key in self._cache:
                    # Update existing
                    old_entry = self._cache[key]
                    self._stats.memory_usage_bytes -= old_entry.size_bytes
                    self._cache[key] = entry
                    self._cache.move_to_end(key)
                else:
                    # Add new entry
                    self._cache[key] = entry
                    self._stats.current_entries += 1

                self._stats.memory_usage_bytes += size_bytes
                self._stats.sets += 1

                # Evict if necessary
                self._evict_if_needed()

                # Periodic cleanup
                self._periodic_cleanup()

                self._update_avg_time('set', start_time)
                return True

    async def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        async with asyncio.Lock():
            with self._lock:
                entry = self._cache.pop(key, None)

                if entry is not None:
                    self._stats.deletes += 1
                    self._stats.current_entries -= 1
                    self._stats.memory_usage_bytes -= entry.size_bytes
                    return True

                return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        async with asyncio.Lock():
            with self._lock:
                entry = self._cache.get(key)

                if entry is None:
                    return False

                if entry.is_expired():
                    del self._cache[key]
                    self._stats.evictions += 1
                    self._stats.current_entries -= 1
                    self._stats.memory_usage_bytes -= entry.size_bytes
                    return False

                return True

    async def clear(self) -> bool:
        """Clear all entries from the cache."""
        async with asyncio.Lock():
            with self._lock:
                self._cache.clear()
                self._stats.current_entries = 0
                self._stats.memory_usage_bytes = 0
                return True

    async def keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all keys, optionally matching a pattern."""
        async with asyncio.Lock():
            with self._lock:
                all_keys = list(self._cache.keys())

                if pattern is None:
                    return all_keys

                # Simple pattern matching (could be enhanced with regex)
                if '*' in pattern:
                    prefix = pattern.rstrip('*')
                    return [key for key in all_keys if key.startswith(prefix)]

                return [key for key in all_keys if pattern in key]

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                sets=self._stats.sets,
                deletes=self._stats.deletes,
                evictions=self._stats.evictions,
                current_entries=self._stats.current_entries,
                max_entries=self._stats.max_entries,
                memory_usage_bytes=self._stats.memory_usage_bytes,
                avg_get_time_ms=self._stats.avg_get_time_ms,
                avg_set_time_ms=self._stats.avg_set_time_ms
            )

    def _evict_if_needed(self):
        """Evict least recently used entries if cache is full."""
        while len(self._cache) > self.max_size:
            # Remove least recently used (first item)
            key, entry = self._cache.popitem(last=False)
            self._stats.evictions += 1
            self._stats.current_entries -= 1
            self._stats.memory_usage_bytes -= entry.size_bytes

    def _periodic_cleanup(self):
        """Remove expired entries periodically."""
        current_time = time.time()

        if current_time - self._last_cleanup < self._cleanup_interval:
            return

        self._last_cleanup = current_time
        now = datetime.now()

        expired_keys = []
        for key, entry in self._cache.items():
            if entry.expires_at and now > entry.expires_at:
                expired_keys.append(key)

        for key in expired_keys:
            entry = self._cache.pop(key, None)
            if entry:
                self._stats.evictions += 1
                self._stats.current_entries -= 1
                self._stats.memory_usage_bytes -= entry.size_bytes

    def _estimate_size(self, value: Any) -> int:
        """Estimate the memory size of a value in bytes."""
        try:
            # Use JSON serialization as approximation
            return len(json.dumps(value, default=str).encode('utf-8'))
        except (TypeError, ValueError):
            # Fallback for non-serializable objects
            return len(str(value).encode('utf-8'))

    def _update_avg_time(self, operation: str, start_time: float):
        """Update average operation time."""
        elapsed_ms = (time.time() - start_time) * 1000

        if operation == 'get':
            # Simple moving average
            total_ops = self._stats.hits + self._stats.misses
            if total_ops == 1:
                self._stats.avg_get_time_ms = elapsed_ms
            else:
                self._stats.avg_get_time_ms = (
                    (self._stats.avg_get_time_ms * (total_ops - 1) + elapsed_ms) / total_ops
                )
        elif operation == 'set':
            if self._stats.sets == 1:
                self._stats.avg_set_time_ms = elapsed_ms
            else:
                self._stats.avg_set_time_ms = (
                    (self._stats.avg_set_time_ms * (self._stats.sets - 1) + elapsed_ms) / self._stats.sets
                )


class CacheKeyBuilder:
    """
    Utility class for building consistent cache keys.

    This class provides methods to create deterministic, collision-resistant
    cache keys from various data types commonly used in the application.
    """

    @staticmethod
    def build_report_key(
        big_five_scores: Dict[str, float],
        report_type: str,
        report_format: str = "pdf",
        version: str = "v1"
    ) -> str:
        """
        Build cache key for report generation.

        Args:
            big_five_scores: Dictionary of Big Five dimension scores
            report_type: Type of report (e.g., "full_assessment")
            report_format: Output format (e.g., "pdf")
            version: Report template version

        Returns:
            Deterministic cache key string
        """
        # Sort scores for consistency
        sorted_scores = sorted(big_five_scores.items())
        scores_str = json.dumps(sorted_scores, sort_keys=True)

        # Create hash of scores for fixed-length key
        scores_hash = hashlib.md5(scores_str.encode('utf-8')).hexdigest()[:16]

        return f"report:{scores_hash}:{report_type}:{report_format}:{version}"

    @staticmethod
    def build_session_key(session_id: str, data_type: str = "responses") -> str:
        """
        Build cache key for session data.

        Args:
            session_id: Assessment session identifier
            data_type: Type of session data

        Returns:
            Cache key string
        """
        return f"session:{session_id}:{data_type}"

    @staticmethod
    def build_content_key(
        content_type: str,
        parameters: Dict[str, Any],
        language: str = "zh"
    ) -> str:
        """
        Build cache key for generated content.

        Args:
            content_type: Type of content being cached
            parameters: Parameters that affect content generation
            language: Content language

        Returns:
            Cache key string
        """
        # Sort parameters for consistency
        params_str = json.dumps(parameters, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode('utf-8')).hexdigest()[:12]

        return f"content:{content_type}:{params_hash}:{language}"

    @staticmethod
    def build_chart_key(
        chart_type: str,
        data: Dict[str, Any],
        style: str = "default"
    ) -> str:
        """
        Build cache key for chart/visualization data.

        Args:
            chart_type: Type of chart (e.g., "radar", "bar")
            data: Chart data
            style: Chart style/theme

        Returns:
            Cache key string
        """
        data_str = json.dumps(data, sort_keys=True, default=str)
        data_hash = hashlib.md5(data_str.encode('utf-8')).hexdigest()[:12]

        return f"chart:{chart_type}:{data_hash}:{style}"


class CacheManager:
    """
    High-level cache manager that orchestrates multiple cache instances.

    This manager provides:
    - Cache instance management
    - Fallback mechanisms
    - Cache warming strategies
    - Health monitoring
    """

    def __init__(self):
        self._caches: Dict[str, CacheInterface] = {}
        self._primary_cache: Optional[str] = None
        self._fallback_caches: List[str] = []

        # Initialize default memory cache
        self.register_cache("memory", MemoryCache(max_size=1000, default_ttl=3600))
        self.set_primary("memory")

    def register_cache(self, name: str, cache: CacheInterface):
        """Register a cache instance."""
        self._caches[name] = cache
        logger.info(f"Registered cache instance: {name}")

    def set_primary(self, name: str):
        """Set the primary cache instance."""
        if name not in self._caches:
            raise ValueError(f"Cache instance '{name}' not registered")

        self._primary_cache = name
        logger.info(f"Set primary cache: {name}")

    def add_fallback(self, name: str):
        """Add a fallback cache instance."""
        if name not in self._caches:
            raise ValueError(f"Cache instance '{name}' not registered")

        if name not in self._fallback_caches:
            self._fallback_caches.append(name)

    async def get(self, key: str) -> Optional[Any]:
        """Get value with fallback support."""
        # Try primary cache first
        if self._primary_cache:
            try:
                value = await self._caches[self._primary_cache].get(key)
                if value is not None:
                    return value
            except Exception as e:
                logger.warning(f"Primary cache get failed: {e}")

        # Try fallback caches
        for cache_name in self._fallback_caches:
            try:
                value = await self._caches[cache_name].get(key)
                if value is not None:
                    # Warm primary cache if available
                    if self._primary_cache:
                        try:
                            await self._caches[self._primary_cache].set(key, value)
                        except Exception:
                            pass  # Don't fail get operation
                    return value
            except Exception as e:
                logger.warning(f"Fallback cache {cache_name} get failed: {e}")

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in all available caches."""
        success = False

        # Set in primary cache
        if self._primary_cache:
            try:
                await self._caches[self._primary_cache].set(key, value, ttl)
                success = True
            except Exception as e:
                logger.warning(f"Primary cache set failed: {e}")

        # Set in fallback caches
        for cache_name in self._fallback_caches:
            try:
                await self._caches[cache_name].set(key, value, ttl)
                success = True
            except Exception as e:
                logger.warning(f"Fallback cache {cache_name} set failed: {e}")

        return success

    def get_all_stats(self) -> Dict[str, CacheStats]:
        """Get statistics from all registered caches."""
        return {name: cache.get_stats() for name, cache in self._caches.items()}


# Global cache manager instance
_cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return _cache_manager


# Convenience functions for direct cache operations
async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache using global manager."""
    return await _cache_manager.get(key)


async def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set value in cache using global manager."""
    return await _cache_manager.set(key, value, ttl)


async def cache_delete(key: str) -> bool:
    """Delete value from cache using global manager."""
    if _cache_manager._primary_cache:
        return await _cache_manager._caches[_cache_manager._primary_cache].delete(key)
    return False


def build_report_cache_key(
    big_five_scores: Dict[str, float],
    report_type: str,
    report_format: str = "pdf",
    version: str = "v1"
) -> str:
    """Convenience function to build report cache keys."""
    return CacheKeyBuilder.build_report_key(
        big_five_scores, report_type, report_format, version
    )