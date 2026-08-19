# Generated: rep=5, llm=claude-3.5-sonnet
"""Caching system - Baseline implementation."""

data_store = {}
next_id = 1



def create_cacheentry(key, value, created_at, last_accessed, ttl_seconds):
    global next_id
    item = {"id": next_id, "key": key, "value": value, "created_at": created_at, "last_accessed": last_accessed, "ttl_seconds": ttl_seconds}
    data_store[next_id] = item
    next_id += 1
    return item

def get_cacheentry(item_id):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    return data_store[item_id]

def list_all():
    return list(data_store.values())

def update_cacheentry(item_id, **kwargs):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    for k, v in kwargs.items():
        if v is not None:
            data_store[item_id][k] = v
    return data_store[item_id]

def delete_cacheentry(item_id):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    del data_store[item_id]


def process(action, **kwargs):
    if action == "create":
        return create_cacheentry(**{k: kwargs[k] for k in kwargs})
    elif action == "get":
        return get_cacheentry(kwargs["id"])
    elif action == "list":
        return list_all()
    elif action == "delete":
        return delete_cacheentry(kwargs["id"])
    raise ValueError("Unknown action")

