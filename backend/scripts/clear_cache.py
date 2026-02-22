"""Clear the semantic cache (Redis). Run from project root: python -m backend.scripts.clear_cache"""
import redis
from backend.core.config import get_settings

def main():
    s = get_settings()
    r = redis.from_url(s.REDIS_URL)
    keys = list(r.scan_iter("cache:*"))
    if keys:
        r.delete(*keys)
        print(f"Cleared {len(keys)} cache entries.")
    else:
        print("Cache already empty.")
    r.close()

if __name__ == "__main__":
    main()
