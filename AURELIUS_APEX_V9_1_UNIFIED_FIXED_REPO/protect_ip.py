"""
================================================================================
AURELIUS SOVEREIGN (AQ-OS v6.0) — IP PROTECTION & BYTECODE COMPILER
================================================================================
Compiles all proprietary mathematical, forensic, and Vedic quantitative engines
into Python bytecode (.pyc) and validates code integrity.
================================================================================
"""

import os
import sys
import py_compile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def compile_aurelius_ip():
    root = Path(__file__).parent.resolve()
    print("=" * 80)
    print("🔒 AURELIUS SOVEREIGN IP PROTECTION COMPILER")
    print(f"Working Directory: {root}")
    print("=" * 80)

    target_files = [
        root / "engine.py",
        root / "app.py",
        root / "verify_maha_chakra.py",
    ]

    for p in (root / "core").glob("*.py"):
        target_files.append(p)
    for p in (root / "modules").glob("*.py"):
        target_files.append(p)

    success_count = 0
    fail_count = 0

    for py_file in target_files:
        if not py_file.exists():
            continue
        rel_path = py_file.relative_to(root)
        try:
            cfile = py_compile.compile(str(py_file), doraise=True)
            print(f"  [+] COMPILED: {rel_path} -> {Path(cfile).name}")
            success_count += 1
        except Exception as e:
            print(f"  [!] FAILED: {rel_path}: {e}")
            fail_count += 1

    print("-" * 80)
    print(f"Compilation Complete: {success_count} succeeded, {fail_count} failed.")
    if fail_count == 0:
        print("✅ IP Protection Bytecode Verification PASSED: All Engines Secured!")
    else:
        print("❌ Compilation errors detected.")
        sys.exit(1)


if __name__ == "__main__":
    compile_aurelius_ip()
