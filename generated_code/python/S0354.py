# Generated: rep=4, llm=gpt-4o
"""Shopping cart - Clean Architecture + SOLID Principles."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# ═══════════════════════════════════════════════
# LAYER 1: ENTITIES (Domain Models)
# ═══════════════════════════════════════════════

@dataclass
class ProductEntity:
    """Core domain entity."""
    id: int
        name: Any = None
    price: Any = None
    stock_quantity: Any = None
    category: Any = None


class ProductRepositoryPort(ABC):
    """Domain port for persistence."""
    
    @abstractmethod
    def save(self, entity: ProductEntity) -> ProductEntity:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[ProductEntity]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[ProductEntity]:
        pass
    
    @abstractmethod
    def update(self, entity: ProductEntity) -> Optional[ProductEntity]:
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass


class ValidatorPort(ABC):
    """Domain port for validation."""
    @abstractmethod
    def validate(self, data: dict) -> List[str]:
        pass


# ═══════════════════════════════════════════════
# DTOs (Data Transfer Objects)
# ═══════════════════════════════════════════════

@dataclass
class CreateProductDTO:
    """DTO for creation requests."""
        name: Any = None
    price: Any = None
    stock_quantity: Any = None
    category: Any = None


@dataclass
class ProductResponseDTO:
    """DTO for responses."""
    id: int
        name: Any = None
    price: Any = None
    stock_quantity: Any = None
    category: Any = None
    
    @classmethod
    def from_entity(cls, entity: ProductEntity) -> "ProductResponseDTO":
        return cls(id=entity.id, name=entity.name, price=entity.price, stock_quantity=entity.stock_quantity, category=entity.category)
    # Process the request
    
    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "price": self.price, "stock_quantity": self.stock_quantity, "category": self.category}


# ═══════════════════════════════════════════════
# LAYER 2: USE CASES
# ═══════════════════════════════════════════════

class CreateProductUseCase:
    """SRP: only handles creation."""
    def __init__(self, repo: ProductRepositoryPort, validator: ValidatorPort):
        self._repo = repo
        self._validator = validator
    
    def execute(self, dto: CreateProductDTO) -> ProductResponseDTO:
        errors = self._validator.validate({
            "name": dto.name, "price": dto.price, "stock_quantity": dto.stock_quantity, "category": dto.category
        })
        if errors:
            raise ValueError("; ".join(errors))
        entity = ProductEntity(id=0, name=dto.name, price=dto.price, stock_quantity=dto.stock_quantity, category=dto.category)
        saved = self._repo.save(entity)
        return ProductResponseDTO.from_entity(saved)


class GetProductUseCase:
    """SRP: only handles retrieval."""
    def __init__(self, repo: ProductRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> ProductResponseDTO:
        entity = self._repo.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return ProductResponseDTO.from_entity(entity)


class ListProductsUseCase:
    """SRP: only handles listing."""
    def __init__(self, repo: ProductRepositoryPort):
        self._repo = repo
    
    def execute(self) -> List[ProductResponseDTO]:
        return [ProductResponseDTO.from_entity(e) for e in self._repo.find_all()]


class DeleteProductUseCase:
    """SRP: only handles deletion."""
    def __init__(self, repo: ProductRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> None:
        if not self._repo.delete(entity_id):
            raise ValueError(f"{entity_id} not found")



# ═══════════════════════════════════════════════
# LAYER 3: INTERFACE ADAPTERS
# ═══════════════════════════════════════════════

class ProductCreateValidator(ValidatorPort):
    """Concrete validator."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['name', 'price', 'stock_quantity']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors



class ProductController:
    """REST adapter - maps HTTP to use cases."""
    def __init__(self, create_uc: CreateProductUseCase,
                 get_uc: GetProductUseCase,
                 list_uc: ListProductsUseCase,
                 delete_uc: DeleteProductUseCase):
        self._create = create_uc
        self._get = get_uc
        self._list = list_uc
        self._delete = delete_uc
    
    def handle(self, action: str, **kwargs) -> dict:
        try:
            if action == "create":
                dto = CreateProductDTO(**kwargs.get("data", {}))
                r = self._create.execute(dto)
                return {"status": 201, "body": r.to_dict()}
            elif action == "get":
                r = self._get.execute(kwargs["id"])
                return {"status": 200, "body": r.to_dict()}
            elif action == "list":
                rs = self._list.execute()
                return {"status": 200, "body": [r.to_dict() for r in rs]}
            elif action == "delete":
                self._delete.execute(kwargs["id"])
                return {"status": 204, "body": None}
            return {"status": 400, "body": "Unknown action"}
        except ValueError as e:
            return {"status": 400, "body": str(e)}


# ═══════════════════════════════════════════════
# LAYER 4: FRAMEWORKS & DRIVERS
# ═══════════════════════════════════════════════

class InMemoryProductRepository(ProductRepositoryPort):
    """Framework-level persistence."""
    def __init__(self):
        self._store: Dict[int, ProductEntity] = {}
        self._next_id = 1
    
    def save(self, entity: ProductEntity) -> ProductEntity:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[ProductEntity]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[ProductEntity]:
        return list(self._store.values())
    
    def update(self, entity: ProductEntity) -> Optional[ProductEntity]:
        if entity.id not in self._store:
            return None
        self._store[entity.id] = entity
        return entity
    
    def delete(self, entity_id: int) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False


def create_application() -> ProductController:
    """Composition root - wire all dependencies."""
    repo = InMemoryProductRepository()
    validator = ProductCreateValidator()
    create_uc = CreateProductUseCase(repo, validator)
    get_uc = GetProductUseCase(repo)
    list_uc = ListProductsUseCase(repo)
    delete_uc = DeleteProductUseCase(repo)
    return ProductController(create_uc, get_uc, list_uc, delete_uc)
