#!/usr/bin/env python3
"""
01_prompt_dataset.py
Generates the complete prompt dataset: 10 tasks × 4 levels × 2 languages = 80 unique prompts.
Each prompt is then used with 2 LLMs × 5 repetitions = 800 total code samples.
"""
import json, os

TASKS = {
    "T01": {
        "name": "CRUD REST API",
        "key_pattern": "Layered architecture",
        "description": (
            "Implement a complete CRUD REST API for managing a library of books. "
            "The system should support creating, reading (single and list), updating, and deleting books. "
            "Each book has: id (auto-generated), title, author, isbn, published_year, and genre. "
            "Include proper error handling for not-found and validation errors. "
            "Use in-memory storage (dictionary/map)."
        )
    },
    "T02": {
        "name": "Authentication system",
        "key_pattern": "Security + sessions",
        "description": (
            "Implement a user authentication system with registration, login, logout, and session management. "
            "Users have: id, username, email, hashed_password, created_at. "
            "Support password hashing (use hashlib/bcrypt simulation), token-based session creation, "
            "session validation, and session expiration (30 min). "
            "Include rate limiting for login attempts (max 5 per minute per user)."
        )
    },
    "T03": {
        "name": "File management system",
        "key_pattern": "I/O + error handling",
        "description": (
            "Implement a file management system that supports uploading, downloading, listing, "
            "and deleting files with metadata tracking. "
            "Each file record has: id, filename, size_bytes, mime_type, upload_date, checksum. "
            "Simulate file storage with in-memory byte arrays. "
            "Include proper error handling for file-not-found, size limits (max 10MB), and duplicate detection via checksum."
        )
    },
    "T04": {
        "name": "Notification system",
        "key_pattern": "Observer pattern",
        "description": (
            "Implement a notification system that supports multiple notification channels "
            "(email, SMS, push notification). "
            "Users can subscribe/unsubscribe to specific event types (order_placed, payment_received, shipping_update). "
            "When an event occurs, all subscribers for that event type receive notifications via their preferred channels. "
            "Include a notification log and retry mechanism for failed deliveries (max 3 retries)."
        )
    },
    "T05": {
        "name": "Shopping cart",
        "key_pattern": "State + domain logic",
        "description": (
            "Implement a shopping cart system with product catalog, cart management, and checkout. "
            "Products have: id, name, price, stock_quantity, category. "
            "Cart operations: add item, remove item, update quantity, apply discount code, calculate total. "
            "Support percentage and fixed-amount discount codes with expiration dates. "
            "Validate stock availability before checkout and update stock after successful checkout."
        )
    },
    "T06": {
        "name": "Task scheduler",
        "key_pattern": "Concurrency + queue",
        "description": (
            "Implement a task scheduler that manages and executes tasks with priorities and scheduling. "
            "Tasks have: id, name, priority (1-10), scheduled_time, status (pending/running/completed/failed), "
            "max_retries, retry_count. "
            "Support adding tasks, canceling tasks, executing the next highest-priority task, "
            "and automatic retry on failure. Include a task execution history log."
        )
    },
    "T07": {
        "name": "Caching system",
        "key_pattern": "Decorator pattern",
        "description": (
            "Implement a caching system with multiple eviction policies (LRU, LFU, TTL-based). "
            "The cache supports get, put, delete, and clear operations. "
            "Each cache entry has: key, value, created_at, last_accessed, access_count, ttl_seconds. "
            "Support configurable max capacity and automatic eviction when full. "
            "Include cache hit/miss statistics tracking."
        )
    },
    "T08": {
        "name": "Event bus",
        "key_pattern": "Pub-sub architecture",
        "description": (
            "Implement an event bus system supporting publish-subscribe messaging. "
            "Support event types with typed payloads, synchronous and asynchronous handler execution, "
            "handler priority ordering, wildcard subscriptions (e.g., 'order.*' matches 'order.created'). "
            "Include dead letter queue for failed event handling and event replay capability from history."
        )
    },
    "T09": {
        "name": "Data pipeline",
        "key_pattern": "Chain of responsibility",
        "description": (
            "Implement a data processing pipeline that chains multiple transformation stages. "
            "Support stages: validation, normalization, enrichment, filtering, and aggregation. "
            "Input data are records (dictionaries) with various fields. "
            "Each stage can pass, transform, or reject records. "
            "Include pipeline metrics (records processed, rejected, processing time per stage) "
            "and the ability to add/remove stages dynamically."
        )
    },
    "T10": {
        "name": "RBAC system",
        "key_pattern": "Strategy + composite",
        "description": (
            "Implement a Role-Based Access Control (RBAC) system. "
            "Support users, roles, and permissions. Users can have multiple roles; roles can have multiple permissions. "
            "Permissions are defined as resource:action pairs (e.g., 'document:read', 'user:delete'). "
            "Support role hierarchy (admin inherits all manager permissions). "
            "Include permission checking, role assignment/revocation, and audit logging of access decisions."
        )
    }
}

def make_prompt(task_desc, language, level):
    """Generate prompt for given task, language, and constraint level."""
    base = f"You are a software engineer. Write a complete, working implementation in {language}.\n\nTask: {task_desc}\n\n"
    
    if level == "P0":
        return base + "Provide the complete source code. Include all necessary classes, functions, and imports."
    
    arch_req = (
        "Architectural Requirements:\n"
        "- Apply separation of concerns: separate business logic from data access and presentation/API\n"
        "- Organize code into distinct, cohesive modules or classes with single responsibilities\n"
        "- Use meaningful, descriptive names for all classes, methods, and variables\n"
        "- Keep functions/methods focused and short (prefer < 20 lines per method)\n"
        "- Group related functionality together\n\n"
    )
    
    if level == "P1":
        return base + arch_req + "Provide the complete source code. Include all necessary classes, functions, and imports."
    
    pattern_req = (
        "Design Pattern Requirements:\n"
        "- Use the Repository pattern for all data access operations (abstract storage behind an interface)\n"
        "- Use the Factory pattern for creating complex objects\n"
        "- Use the Strategy pattern where multiple algorithms or behaviors are interchangeable\n"
        "- Define interfaces/abstract base classes for all major component boundaries\n"
        "- Apply Dependency Injection: pass dependencies through constructors, not hard-coded instantiation\n\n"
    )
    
    if level == "P2":
        return base + arch_req + pattern_req + "Provide the complete source code. Include all necessary classes, functions, and imports."
    
    clean_req = (
        "Clean Architecture Requirements:\n"
        "- Organize code into 4 layers: Entities (domain models), Use Cases (application logic), "
        "Interface Adapters (controllers, presenters, gateways), Frameworks & Drivers (external tools)\n"
        "- Dependencies must point inward: outer layers depend on inner layers, never the reverse\n"
        "- Use Data Transfer Objects (DTOs) for data crossing layer boundaries\n\n"
        "SOLID Principles (apply ALL five):\n"
        "- Single Responsibility Principle: each class has exactly one reason to change\n"
        "- Open/Closed Principle: classes are open for extension, closed for modification\n"
        "- Liskov Substitution: subtypes must be substitutable for their base types\n"
        "- Interface Segregation: prefer many small interfaces over one large interface\n"
        "- Dependency Inversion: depend on abstractions, not concretions\n\n"
    )
    
    # P3
    return base + arch_req + pattern_req + clean_req + "Provide the complete source code. Include all necessary classes, functions, and imports."


def generate_full_dataset():
    """Generate all 80 unique prompts and 800 sample configurations."""
    prompts = []
    samples = []
    sample_id = 0
    
    for task_id, task_info in TASKS.items():
        for lang in ["python", "java"]:
            for level in ["P0", "P1", "P2", "P3"]:
                prompt_text = make_prompt(task_info["description"], lang.capitalize(), level)
                prompt_entry = {
                    "prompt_id": f"{task_id}_{level}_{lang}",
                    "task_id": task_id,
                    "task_name": task_info["name"],
                    "key_pattern": task_info["key_pattern"],
                    "language": lang,
                    "prompt_level": level,
                    "prompt": prompt_text,
                    "prompt_word_count": len(prompt_text.split())
                }
                prompts.append(prompt_entry)
                
                for llm in ["gpt-4o", "claude-3.5-sonnet"]:
                    for rep in range(1, 6):
                        sample_id += 1
                        samples.append({
                            "sample_id": f"S{sample_id:04d}",
                            "prompt_id": prompt_entry["prompt_id"],
                            "task_id": task_id,
                            "task_name": task_info["name"],
                            "language": lang,
                            "prompt_level": level,
                            "llm": llm,
                            "repetition": rep,
                            "temperature": 0.7
                        })
    
    return prompts, samples


if __name__ == "__main__":
    out_dir = "/home/user/workspace/experiment/prompts"
    os.makedirs(out_dir, exist_ok=True)
    
    prompts, samples = generate_full_dataset()
    
    with open(f"{out_dir}/prompt_dataset.json", "w") as f:
        json.dump(prompts, f, indent=2)
    
    with open(f"{out_dir}/sample_manifest.json", "w") as f:
        json.dump(samples, f, indent=2)
    
    print(f"=== Prompt Dataset Generated ===")
    print(f"Unique prompts: {len(prompts)}")
    print(f"Total sample configurations: {len(samples)}")
    print(f"\nPrompt word counts by level:")
    for level in ["P0", "P1", "P2", "P3"]:
        items = [p for p in prompts if p["prompt_level"] == level]
        avg_wc = sum(p["prompt_word_count"] for p in items) / len(items)
        print(f"  {level}: {len(items)} prompts, avg {avg_wc:.0f} words")
    print(f"\nSamples per condition:")
    print(f"  Per task × level × lang × llm: 5 repetitions")
    print(f"  Per prompt level: {len(samples)//4} samples")
    print(f"  Total: {len(samples)} samples")
