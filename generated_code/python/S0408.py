# Generated: rep=3, llm=claude-3.5-sonnet
"""Task scheduler - Baseline implementation."""

data_store = {}
next_id = 1



def create_task(name, priority, scheduled_time, status, max_retries):
    global next_id
    item = {"id": next_id, "name": name, "priority": priority, "scheduled_time": scheduled_time, "status": status, "max_retries": max_retries}
    data_store[next_id] = item
    next_id += 1
    return item

def get_task(item_id):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    return data_store[item_id]

def list_all():
    return list(data_store.values())

def update_task(item_id, **kwargs):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    for k, v in kwargs.items():
        if v is not None:
            data_store[item_id][k] = v
    return data_store[item_id]

def delete_task(item_id):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    del data_store[item_id]


def process(action, **kwargs):
    if action == "create":
        return create_task(**{k: kwargs[k] for k in kwargs})
    elif action == "get":
        return get_task(kwargs["id"])
    elif action == "list":
        return list_all()
    elif action == "delete":
        return delete_task(kwargs["id"])
    raise ValueError("Unknown action")

