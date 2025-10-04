import sys, importlib
from DB import setup
from Menus import report_menu


def run_new_project():
    """Run a fresh MoneySplit calculation and save it to DB."""
    importlib.invalidate_caches()
    if "Logic.ProgramBackend" in sys.modules:
        del sys.modules["Logic.ProgramBackend"]

    # This import executes ProgramBackend.py (asks for inputs, runs calculation, and saves to DB)
    pb = importlib.import_module("Logic.ProgramBackend")

    # Get the record_id that was already saved in ProgramBackend
    record_id = pb.LAST_RECORD_ID
    print(f"\n✅ Project results saved (record {record_id}).")
    print("✅ Calculation finished and stored in database.")

    # Auto-report (summary + top contributors)
    print("\n📊 Auto-generated report:")
    report_menu.show_report_menu(auto=True, record_id=record_id)
