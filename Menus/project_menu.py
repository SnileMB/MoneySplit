import sys, importlib

def run_new_project():
    """Run a fresh MoneySplit calculation and save it to DB."""
    importlib.invalidate_caches()
    if "MoneySplit.Logic.ProgramBackend" in sys.modules:
        del sys.modules["MoneySplit.Logic.ProgramBackend"]

    # This import executes ProgramBackend.py (asks for inputs)
    importlib.import_module("MoneySplit.Logic.ProgramBackend")

    from MoneySplit.DB import setup
    setup.save_to_db()
    print("\n✅ Project results saved.")
    print("✅ Calculation finished and stored in database.")
