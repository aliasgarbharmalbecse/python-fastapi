import redis
import json
import functools
import hashlib
from typing import Any, Optional, Callable, TypeVar, Type, Union, List
from fastapi import Request, Response
import os
from pydantic import BaseModel

# Simple Redis client
redis_client = None

# Generic Pydantic model type
T = TypeVar("T", bound=BaseModel)

async def setup_redis(host="localhost", port=6379, password=None, db=0):
    """Initialize the Redis client"""
    global redis_client
    redis_client = redis.Redis(
        host=host,
        port=port,
        password=password,
        db=db,
        decode_responses=False  # Keep as bytes for proper serialization
    )
    return redis_client


def hash_request_body(body: Any) -> str:
    if isinstance(body, BaseModel):
        body_str = body.json()
    else:
        body_str = json.dumps(body, sort_keys=True)
    return hashlib.sha256(body_str.encode()).hexdigest()


def cache(
        model: Union[Type[BaseModel], Type[List[BaseModel]]],
        ttl: int = 60,
        is_list: bool = False,
        cache_key: str = None,  # Accepts a simple string as the cache key
):
    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Ensure redis_client is initialized
            if not redis_client:
                raise Exception("Redis client is not initialized.")

            # 1. If cache_key is provided, use it
            if cache_key:
                key = cache_key
            else:
                # 2. If cache_key is not provided, auto-generate the key using function name + arguments
                key_raw = f"{func.__name__}:" + ":".join(
                    f"{k}={v}" for k, v in kwargs.items()
                )
                key = f"cache:{hashlib.md5(key_raw.encode()).hexdigest()}"

            print(f"Cache key: {key}")  # You can remove this line after testing

            print("#" * 100)
            print(key)
            # Try to get data from cache
            cached = redis_client.get(key)
            if cached:
                print(f"Cache hit: {key}")
                data = json.loads(cached)
                if is_list:
                    return [model.__args__[0](**item) for item in data]
                else:
                    return model.parse_obj(data)

            # Cache miss - execute function and set the cache
            print(f"Cache miss: {key}")
            result = await func(*args, **kwargs)

            if is_list:
                await redis_client.setex(key, ttl, json.dumps([item.dict() for item in result]))
            elif isinstance(result, BaseModel):
                await redis_client.setex(key, ttl, result.json())
            else:
                raise ValueError("Result must be a Pydantic model or list of models")

            return result

        return wrapper

    return decorator


def invalidate_cache(pattern: str = None):
    """
    Decorator to invalidate cache after function execution

    Args:
        pattern: Optional pattern to delete specific keys
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute the function first
            response = await func(*args, **kwargs)

            # Then invalidate cache
            if not redis_client:
                return response

            if pattern:
                # Delete keys matching pattern
                for key in redis_client.scan_iter(pattern):
                    redis_client.delete(key)

            return response

        return wrapper

    return decorator