# -------------------------------------------------
# TRY TO LOAD YOUR REAL AI (ai_agent.py)
# -------------------------------------------------
try:
    print("🔍 Trying to import AdvancedAI from ai_agent.py ...")
    from ai_agent import AdvancedAI
    print("✅ Imported AdvancedAI successfully. Now creating instance...")
    ai = AdvancedAI()
    AI_MODE = "REAL"
    print("✅ AdvancedAI instance created. REAL mode ON.")
except Exception:
    import traceback
    AI_MODE = "STUB"
    print("❌ REAL AI failed to load. Traceback:")
    traceback.print_exc()

    class AIStub:
        name = "Saba"
        version = "Stub"

        def process_input(self, text: str) -> str:
            return f"(stub) You said: {text}"

        def save_persistent_memory(self):
            pass

    ai = AIStub()
