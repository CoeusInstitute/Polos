from pathlib import Path

from polos.audit.logger import AuditLogger
from polos.audit.reader import read_jsonl, verify_hash_chain


def test_audit_reader_verifies_hash_chain(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    logger = AuditLogger(path)

    logger.append({"event_type": "one"})
    logger.append({"event_type": "two"})

    assert len(read_jsonl(path)) == 2
    assert verify_hash_chain(path)


def test_audit_reader_detects_tamper(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    logger = AuditLogger(path)
    logger.append({"event_type": "one"})
    text = path.read_text(encoding="utf-8").replace("one", "changed")
    path.write_text(text, encoding="utf-8")

    assert not verify_hash_chain(path)
