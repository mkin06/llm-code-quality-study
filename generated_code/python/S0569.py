# Generated: rep=4, llm=claude-3.5-sonnet
"""Event bus - Baseline implementation."""

data_store = {}
next_id = 1



def create_event(event_type, payload, timestamp, source):
    global next_id
    item = {"id": next_id, "event_type": event_type, "payload": payload, "timestamp": timestamp, "source": source}
    data_store[next_id] = item
    next_id += 1
    return item

def get_event(item_id):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    return data_store[item_id]

def list_all():
    return list(data_store.values())

def update_event(item_id, **kwargs):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    for k, v in kwargs.items():
        if v is not None:
            data_store[item_id][k] = v
    return data_store[item_id]

def delete_event(item_id):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    del data_store[item_id]


def process(action, **kwargs):
    if action == "create":
        return create_event(**{k: kwargs[k] for k in kwargs})
    elif action == "get":
        return get_event(kwargs["id"])
    elif action == "list":
        return list_all()
    elif action == "delete":
        return delete_event(kwargs["id"])
    raise ValueError("Unknown action")

