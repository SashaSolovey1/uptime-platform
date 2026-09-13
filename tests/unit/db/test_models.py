from uptime_platform.db.base import Base
from uptime_platform.db.models import (
    register_models,
)


def test_registered_model_foreign_keys_can_be_resolved() -> None:
    register_models()

    for table in Base.metadata.tables.values():
        for foreign_key in table.foreign_keys:
            assert foreign_key.column is not None
