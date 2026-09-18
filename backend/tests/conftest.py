import pytest
from app.database.session import (
    init_all_databases,
    SourceSessionLocal,
    PolicySessionLocal
)
from app.models import SourceCustomer, ProtectionPolicy

@pytest.fixture(scope="session", autouse=True)
def setup_test_databases():
    # Initialize all database tables
    init_all_databases()

    # Seed source customer records for testing
    sdb = SourceSessionLocal()
    try:
        if sdb.query(SourceCustomer).count() == 0:
            customers = [
                SourceCustomer(customer_id="C001", name="John Doe", email="john.doe@example.com", mobile="9876543210", city="Chennai", segment="Premium"),
                SourceCustomer(customer_id="C002", name="Alice Smith", email="alice.smith@techcorp.io", mobile="9123456789", city="Bangalore", segment="Enterprise"),
                SourceCustomer(customer_id="C003", name="Bob Johnson", email="bob.j@cloudnet.org", mobile="9845123456", city="Mumbai", segment="Standard"),
            ]
            for c in customers:
                sdb.add(c)
            sdb.commit()
    finally:
        sdb.close()

    # Seed default policies
    pdb = PolicySessionLocal()
    try:
        from app.services.batch.engine import batch_engine
        batch_engine.get_or_seed_policies(pdb)
    finally:
        pdb.close()
