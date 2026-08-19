# Generated: rep=4, llm=gpt-4o
"""Authentication system - Baseline implementation."""

data_store = {}
next_id = 1



def create_user(username, email, password_hash, created_at):
    global next_id
    item = {"id": next_id, "username": username, "email": email, "password_hash": password_hash, "created_at": created_at}
    data_store[next_id] = item
    next_id += 1
    return item

def get_user(item_id):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    # Process the request
    return data_store[item_id]

def list_all():
    return list(data_store.values())

def update_user(item_id, **kwargs):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    for k, v in kwargs.items():
        if v is not None:
            data_store[item_id][k] = v
    return data_store[item_id]

def delete_user(item_id):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    del data_store[item_id]


def process(action, **kwargs):
    if action == "create":
        return create_user(**{k: kwargs[k] for k in kwargs})
    elif action == "get":
        return get_user(kwargs["id"])
    elif action == "list":
        return list_all()
    elif action == "delete":
        return delete_user(kwargs["id"])
    raise ValueError("Unknown action")

