"""Synthetic offline end-to-end reliable reports; no network or credentials."""
from pathlib import Path
from tempfile import TemporaryDirectory

from shopextract._capture import capture
from shopextract._normalize import normalize
from shopextract.monitor import get_evidence, reliable_changes, save_snapshot


def observed(price, warranty, title):
    raw = {"sku": "demo-42", "title": title, "price": price, "currency": "EUR",
           "attributes": {"warranty": warranty}, "pack_quantity": 1,
           "product_url": "https://fixtures.example/products/demo-42"}
    capture(raw, "https://fixtures.example/catalog", "synthetic-fixture")
    product = normalize(raw, shop_url="https://fixtures.example")
    assert product is not None
    return product


def main():
    with TemporaryDirectory(prefix="reliable-changes-") as directory:
        db = str(Path(directory) / "snapshots.db")
        metadata = {"observation_scope": "synthetic:full-catalog", "catalog_complete": True}
        old_id = save_snapshot([observed("100", "12 months", "Widget")],
                               "fixtures.example", db_path=db, metadata=metadata)
        new_id = save_snapshot([observed("50", "24 months", "Renamed widget")],
                               "fixtures.example", db_path=db, metadata=metadata)
        options = dict(previous_snapshot_id=old_id, current_snapshot_id=new_id, db_path=db)
        first = reliable_changes("fixtures.example", **options)
        assert len(first["events"]) == 1
        assert first["events"][0]["field_path"] == "/attributes/warranty"
        assert any(c["field_path"] == "/price" and c["state"] == "pending"
                   for c in first["candidates"])
        recheck_id = save_snapshot([observed("50", "24 months", "Renamed widget")],
                                   "fixtures.example", db_path=db, metadata=metadata)
        checked = reliable_changes("fixtures.example", recheck_snapshot_id=recheck_id, **options)
        assert len(checked["events"]) == 2 and len(checked["new_events"]) == 1
        assert checked["new_events"][0]["field_path"] == "/price"
        for side in ["old", "new"]:
            for ref in checked["new_events"][0][side]["references"]:
                for evidence_id in ref["evidence_ids"]:
                    source = get_evidence(evidence_id, snapshot_id=ref["snapshot_id"],
                                          record_key=ref["record_key"], db_path=db)
                    assert source.status == "available"
        replay = reliable_changes("fixtures.example", recheck_snapshot_id=recheck_id, **options)
        assert replay["events"] == checked["events"] and replay["new_events"] == []
        print("Synthetic demo passed: warranty confirmed, price rechecked, rename preserved, replay deduplicated.")


if __name__ == "__main__":
    main()
