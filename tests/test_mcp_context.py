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

def test_mcp_polyglot_symbols():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test Go file
        go_file = os.path.join(tmpdir, "main.go")
        with open(go_file, "w") as f:
            f.write("package main\n\nfunc CalculateBalance() int {\n  return 100\n}\n\ntype Order struct {}\n")

        # Test TypeScript file
        ts_file = os.path.join(tmpdir, "service.ts")
        with open(ts_file, "w") as f:
            f.write("export class UserService {}\nexport const fetchUser = async () => {};\n")

        mcp = ContextMCPServer(root_dir=tmpdir)
        go_symbols = mcp.get_ast_symbols("main.go")
        ts_symbols = mcp.get_ast_symbols("service.ts")

        assert any(s["name"] == "CalculateBalance" for s in go_symbols)
        assert any(s["name"] == "Order" for s in go_symbols)
        assert any(s["name"] == "UserService" for s in ts_symbols)
        assert any(s["name"] == "fetchUser" for s in ts_symbols)

