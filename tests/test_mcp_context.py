import os
import tempfile
from pr_gatekeeper.mcp_server import ContextMCPServer

def test_mcp_ast_extraction():
    with tempfile.TemporaryDirectory() as tmpdir:
        sample_file = os.path.join(tmpdir, "sample.py")
        with open(sample_file, "w") as f:
            f.write("""
class BillingManager:
    def process_invoice(self, invoice_id: str):
        pass

def calculate_tax(amount: float):
    return amount * 0.11
""")
        mcp = ContextMCPServer(root_dir=tmpdir)
        symbols = mcp.get_ast_symbols("sample.py")

        assert len(symbols) == 2
        class_symbol = next(s for s in symbols if s["type"] == "class")
        func_symbol = next(s for s in symbols if s["type"] == "function")

        assert class_symbol["name"] == "BillingManager"
        assert "process_invoice" in class_symbol["methods"]
        assert func_symbol["name"] == "calculate_tax"

def test_mcp_arch_guidelines_fallback():
    with tempfile.TemporaryDirectory() as tmpdir:
        mcp = ContextMCPServer(root_dir=tmpdir)
        guidelines = mcp.get_arch_guidelines()
        assert "Enterprise Engineering Architecture Guidelines" in guidelines
