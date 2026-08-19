# Generated: rep=4, llm=claude-3.5-sonnet
"""Shopping cart - Baseline implementation."""

data_store = {}
next_id = 1



def create_product(name, price, stock_quantity, category):
    global next_id
    item = {"id": next_id, "name": name, "price": price, "stock_quantity": stock_quantity, "category": category}
    data_store[next_id] = item
    next_id += 1
    return item

def get_product(item_id):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    return data_store[item_id]

def list_all():
    return list(data_store.values())

def update_product(item_id, **kwargs):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    for k, v in kwargs.items():
        if v is not None:
            data_store[item_id][k] = v
    return data_store[item_id]

def delete_product(item_id):
    if item_id not in data_store:
        raise ValueError(f"{item_id} not found")
    del data_store[item_id]


def process(action, **kwargs):
    if action == "create":
        return create_product(**{k: kwargs[k] for k in kwargs})
    elif action == "get":
        return get_product(kwargs["id"])
    elif action == "list":
        return list_all()
    elif action == "delete":
        return delete_product(kwargs["id"])
    raise ValueError("Unknown action")

