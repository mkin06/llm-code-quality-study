# Generated: rep=5, llm=gpt-4o
"""RBAC system - Baseline implementation."""

data_store = {}
next_id = 1



def create_permission(resource, action, role, granted):
    global next_id
    item = {"id": next_id, "resource": resource, "action": action, "role": role, "granted": granted}
    data_store[next_id] = item
    next_id += 1
    return item

def get_permission(item_id):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    return data_store[item_id]

def list_all():
    return list(data_store.values())

def update_permission(item_id, **kwargs):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    for k, v in kwargs.items():
        if v is not None:
            data_store[item_id][k] = v
    return data_store[item_id]

def delete_permission(item_id):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    del data_store[item_id]


def process(action, **kwargs):
    if action == "create":
        return create_permission(**{k: kwargs[k] for k in kwargs})
    elif action == "get":
        return get_permission(kwargs["id"])
    elif action == "list":
        return list_all()
    elif action == "delete":
        return delete_permission(kwargs["id"])
    raise ValueError("Unknown action")

