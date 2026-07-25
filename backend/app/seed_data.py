"""
Optional helper: populates the database with a few already-committed sample
complaints so the Dashboard has something to show before you record your
demo video. Safe to run multiple times (adds new rows each time).

Usage:
    cd backend
    python -m app.seed_data
"""
from app.core.database import SessionLocal, engine, Base
from app.models.complaint import Complaint, ComplaintStatus

Base.metadata.create_all(bind=engine)

SAMPLE_COMPLAINTS = [
    dict(
        complaint_source="Pharmacy", customer_name="Apollo Pharmacy",
        product_name="Amoxicillin Capsules", product_strength="500 mg",
        batch_lot_number="AMX240602", affected_quantity="12 capsules",
        manufacturing_date="March 2026", expiry_date="February 2028",
        originating_site_block="Manufacturing", impacted_npm="Primary Packaging (Bottle)",
        complaint_category="Product Defect - Discoloration",
        complaint_description="Apollo Pharmacy reported 12 discolored capsules in a sealed bottle. Requesting investigation and replacement.",
        ai_severity_suggested="Major", ai_suggested_next_action="Route to QA Investigation & Issue Replacement",
        ai_initial_risk_assessment="Potential moisture ingress or primary packaging seal failure leading to capsule discoloration.",
        ai_root_cause_suggestion="Likely primary packaging seal failure allowing moisture ingress during storage/transit.",
        ai_capa_suggestion="Quarantine and replace affected batch; investigate packaging seal integrity; add in-process seal check.",
        ai_summary="Discoloration reported in 12 capsules from batch AMX240602 by Apollo Pharmacy; major severity, replacement recommended.",
        status=ComplaintStatus.COMMITTED,
    ),
    dict(
        complaint_source="Email", customer_name="ABC Formulations Ltd.",
        product_name="Metformin Hydrochloride API", product_strength="IP/BP",
        batch_lot_number="MFH260712A", affected_quantity="25 kg (1 HDPE Drum)",
        manufacturing_date="25 June 2026", expiry_date="Not Provided",
        originating_site_block="Manufacturing", impacted_npm="HDPE Drum",
        complaint_category="Foreign Matter Contamination",
        complaint_description="ABC Formulations Ltd. reported multiple dark foreign particles inside one sealed HDPE drum during incoming quality inspection. Material quarantined.",
        ai_severity_suggested="Critical", ai_suggested_next_action="Laboratory investigation & manufacturing record review",
        ai_initial_risk_assessment="Potential foreign matter contamination. High impact to API quality; investigation of manufacturing process required.",
        ai_root_cause_suggestion="Possible contamination during drum filling or raw material handling at the manufacturing site.",
        ai_capa_suggestion="Quarantine drum; conduct lab analysis of foreign particles; review filling line cleaning/handling procedures.",
        ai_summary="Foreign matter found in Metformin HCl API drum MFH260712A; critical severity, lab investigation recommended.",
        status=ComplaintStatus.COMMITTED,
    ),
    dict(
        complaint_source="Distributor", customer_name="MedLine Distributors",
        product_name="Paracetamol Tablets", product_strength="650 mg",
        batch_lot_number="PCM250311", affected_quantity="3 cartons",
        manufacturing_date="January 2026", expiry_date="December 2027",
        originating_site_block="Packaging", impacted_npm="Carton",
        complaint_category="Labeling Error",
        complaint_description="MedLine Distributors reported mismatched batch number printed on carton label versus blister foil for 3 cartons.",
        ai_severity_suggested="Minor", ai_suggested_next_action="Route to Packaging QA for label reconciliation",
        ai_initial_risk_assessment="Labeling inconsistency with low patient safety impact but requires GMP documentation correction.",
        status=ComplaintStatus.READY_TO_COMMIT,
    ),
]


def run():
    db = SessionLocal()
    try:
        for data in SAMPLE_COMPLAINTS:
            db.add(Complaint(**data))
        db.commit()
        print(f"Seeded {len(SAMPLE_COMPLAINTS)} sample complaints.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
