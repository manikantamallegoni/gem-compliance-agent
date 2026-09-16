from app.engine import run_compliance_check
from app.models import BidderData, TenderRules

def main():
    bidder = BidderData.from_json_file("data/sample_bidder.json")
    tender = TenderRules.from_json_file("data/sample_tender_rules.json")

    report = run_compliance_check(bidder, tender)

    print("\n" + "=" * 70)
    print("SIH 26100 - BID COMPLIANCE REPORT")
    print("=" * 70)
    print(f"Bidder: {bidder.company_name}")
    print(f"Tender: {tender.tender_id}")
    print("-" * 70)

    for item in report.results:
        print(f"{item.rule_name:25} {item.status:12} {item.reason}")

    print("-" * 70)
    print(f"Compliance Score : {report.compliance_score}%")
    print(f"Risk Level       : {report.risk_level}")
    print(f"Recommendation   : {report.recommendation}")
    print(f"Review Required  : {report.review_required}")
    print("=" * 70)

if __name__ == "__main__":
    main()
