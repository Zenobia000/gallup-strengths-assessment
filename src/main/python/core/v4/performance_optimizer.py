"""
Performance Optimizer for v4.0 IRT System
Task 9.2.4: 效能優化與快取

Implements caching and performance optimizations for:
1. IRT parameter loading
2. Theta estimation results
3. Normative score conversions
4. Block design generation
"""

import hashlib
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
from pathlib import Path
import numpy as np
from dataclasses import dataclass, asdict
import pickle
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with expiration"""
    data: Any
    timestamp: float
    ttl: float  # Time to live in seconds

    def is_valid(self) -> bool:
        """Check if cache entry is still valid"""
        return time.time() - self.timestamp < self.ttl


class PerformanceOptimizer:
    """
    Central performance optimization manager for v4.0 system.

    Implements multiple caching strategies:
    - Memory cache for frequently accessed data
    - File cache for expensive computations
    - LRU cache for function results
    """

    def __init__(self,
                 cache_dir: Optional[Path] = None,
                 max_memory_cache: int = 100,
                 default_ttl: float = 3600):
        """
        Initialize performance optimizer.

        Args:
            cache_dir: Directory for file-based cache
            max_memory_cache: Maximum number of items in memory cache
            default_ttl: Default time-to-live for cache entries (seconds)
        """
        self.cache_dir = cache_dir or Path('cache/v4')
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.memory_cache: Dict[str, CacheEntry] = {}
        self.max_memory_cache = max_memory_cache
        self.default_ttl = default_ttl

        # Performance metrics
        self.cache_hits = 0
        self.cache_misses = 0
        self.computation_times: List[float] = []

    def get_cache_key(self, prefix: str, data: Any) -> str:
        """
        Generate cache key from prefix and data.

        Args:
            prefix: Cache key prefix (e.g., 'theta_estimation')
            data: Data to hash

        Returns:
            Unique cache key
        """
        # Convert data to JSON string for hashing
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True)
        elif isinstance(data, np.ndarray):
            data_str = data.tobytes()
        else:
            data_str = str(data)

        # Generate hash
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}_{hash_obj.hexdigest()}"

    def get_from_cache(self, key: str) -> Optional[Any]:
        """
        Retrieve data from cache (memory first, then file).

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found/expired
        """
        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if entry.is_valid():
                self.cache_hits += 1
                logger.debug(f"Memory cache hit: {key}")
                return entry.data
            else:
                # Remove expired entry
                del self.memory_cache[key]

        # Check file cache
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    entry = pickle.load(f)
                if isinstance(entry, CacheEntry) and entry.is_valid():
                    # Promote to memory cache
                    self._add_to_memory_cache(key, entry)
                    self.cache_hits += 1
                    logger.debug(f"File cache hit: {key}")
                    return entry.data
                else:
                    # Remove expired file
                    cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to load cache file {cache_file}: {e}")

        self.cache_misses += 1
        return None

    def save_to_cache(self, key: str, data: Any, ttl: Optional[float] = None):
        """
        Save data to cache (both memory and file).

        Args:
            key: Cache key
            data: Data to cache
            ttl: Time-to-live in seconds
        """
        ttl = ttl or self.default_ttl
        entry = CacheEntry(data=data, timestamp=time.time(), ttl=ttl)

        # Save to memory cache
        self._add_to_memory_cache(key, entry)

        # Save to file cache
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(entry, f)
            logger.debug(f"Saved to cache: {key}")
        except Exception as e:
            logger.warning(f"Failed to save cache file {cache_file}: {e}")

    def _add_to_memory_cache(self, key: str, entry: CacheEntry):
        """Add entry to memory cache with LRU eviction"""
        # Evict oldest entries if cache is full
        if len(self.memory_cache) >= self.max_memory_cache:
            # Remove oldest entry
            oldest_key = min(self.memory_cache.keys(),
                           key=lambda k: self.memory_cache[k].timestamp)
            del self.memory_cache[oldest_key]
            logger.debug(f"Evicted from memory cache: {oldest_key}")

        self.memory_cache[key] = entry

    def cache_theta_estimation(self,
                              responses: List[Dict],
                              blocks: List[Dict],
                              theta: np.ndarray,
                              ttl: float = 7200):
        """
        Cache theta estimation results.

        Args:
            responses: User responses
            blocks: Block configuration
            theta: Estimated theta values
            ttl: Cache duration (2 hours default)
        """
        key = self.get_cache_key('theta', {'responses': responses, 'blocks': blocks})
        self.save_to_cache(key, theta, ttl)

    def get_cached_theta(self,
                        responses: List[Dict],
                        blocks: List[Dict]) -> Optional[np.ndarray]:
        """
        Retrieve cached theta estimation.

        Args:
            responses: User responses
            blocks: Block configuration

        Returns:
            Cached theta values or None
        """
        key = self.get_cache_key('theta', {'responses': responses, 'blocks': blocks})
        return self.get_from_cache(key)

    @lru_cache(maxsize=128)
    def cached_percentile_conversion(self, theta: float, dimension: str) -> float:
        """
        Cached conversion from theta to percentile.

        Args:
            theta: Theta score
            dimension: Dimension name

        Returns:
            Percentile value
        """
        # This is a placeholder - actual implementation would use norm tables
        from scipy import stats
        return stats.norm.cdf(theta) * 100

    def optimize_block_generation(self, statements: List[Any], num_blocks: int) -> str:
        """
        Cache block generation results.

        Args:
            statements: Statement pool
            num_blocks: Number of blocks to generate

        Returns:
            Cache key for generated blocks
        """
        # Create cache key based on statements and block count
        key = self.get_cache_key('blocks', {
            'num_statements': len(statements),
            'num_blocks': num_blocks
        })
        return key

    def clear_cache(self, prefix: Optional[str] = None):
        """
        Clear cache entries.

        Args:
            prefix: Clear only entries with this prefix
        """
        # Clear memory cache
        if prefix:
            keys_to_remove = [k for k in self.memory_cache.keys()
                            if k.startswith(prefix)]
            for key in keys_to_remove:
                del self.memory_cache[key]
        else:
            self.memory_cache.clear()

        # Clear file cache
        for cache_file in self.cache_dir.glob('*.pkl'):
            if not prefix or cache_file.stem.startswith(prefix):
                cache_file.unlink()

        logger.info(f"Cache cleared: {prefix or 'all'}")

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.

        Returns:
            Dictionary of performance metrics
        """
        hit_rate = (self.cache_hits / (self.cache_hits + self.cache_misses) * 100
                   if (self.cache_hits + self.cache_misses) > 0 else 0)

        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate,
            'memory_cache_size': len(self.memory_cache),
            'avg_computation_time': (np.mean(self.computation_times)
                                    if self.computation_times else 0),
            'total_computations': len(self.computation_times)
        }

    def track_computation_time(self, duration: float):
        """Track computation time for performance analysis"""
        self.computation_times.append(duration)
        # Keep only last 1000 measurements
        if len(self.computation_times) > 1000:
            self.computation_times = self.computation_times[-1000:]


# Singleton instance
_optimizer_instance: Optional[PerformanceOptimizer] = None


def get_optimizer() -> PerformanceOptimizer:
    """Get or create the singleton optimizer instance"""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = PerformanceOptimizer()
    return _optimizer_instance


# Decorator for automatic caching
def cached_computation(prefix: str, ttl: float = 3600):
    """
    Decorator for caching expensive computations.

    Args:
        prefix: Cache key prefix
        ttl: Time-to-live in seconds
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            optimizer = get_optimizer()

            # Generate cache key
            cache_data = {
                'args': args,
                'kwargs': kwargs
            }
            key = optimizer.get_cache_key(f"{prefix}_{func.__name__}", cache_data)

            # Check cache
            result = optimizer.get_from_cache(key)
            if result is not None:
                return result

            # Compute result
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            # Track performance
            optimizer.track_computation_time(duration)

            # Cache result
            optimizer.save_to_cache(key, result, ttl)

            return result
        return wrapper
    return decorator


# Optimized batch operations
class BatchProcessor:
    """Optimized batch processing for multiple operations"""

    @staticmethod
    def batch_theta_estimation(responses_batch: List[List[Dict]],
                               blocks: List[Dict],
                               scorer) -> List[np.ndarray]:
        """
        Process multiple theta estimations in batch.

        Args:
            responses_batch: Batch of response sets
            blocks: Block configuration
            scorer: IRT scorer instance

        Returns:
            List of theta estimates
        """
        optimizer = get_optimizer()
        results = []

        for responses in responses_batch:
            # Check cache first
            cached = optimizer.get_cached_theta(responses, blocks)
            if cached is not None:
                results.append(cached)
            else:
                # Compute and cache
                start_time = time.time()
                theta = scorer.estimate_theta(responses, blocks)
                duration = time.time() - start_time

                optimizer.track_computation_time(duration)
                optimizer.cache_theta_estimation(responses, blocks, theta)
                results.append(theta)

        return results

    @staticmethod
    def batch_norm_conversion(theta_batch: List[np.ndarray],
                             norm_scorer) -> List[Dict]:
        """
        Convert multiple theta scores to norm scores in batch.

        Args:
            theta_batch: Batch of theta scores
            norm_scorer: Normative scorer instance

        Returns:
            List of norm score dictionaries
        """
        optimizer = get_optimizer()
        results = []

        for theta in theta_batch:
            # Use cached percentile conversion
            norm_scores = {}
            for i, dim in enumerate(norm_scorer.dimensions):
                percentile = optimizer.cached_percentile_conversion(
                    float(theta[i]), dim
                )
                norm_scores[dim] = {
                    'percentile': percentile,
                    't_score': 50 + 10 * theta[i],
                    'stanine': min(9, max(1, int(4 + 2 * theta[i])))
                }
            results.append(norm_scores)

        return results