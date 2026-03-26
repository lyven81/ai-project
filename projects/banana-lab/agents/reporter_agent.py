from datetime import datetime

from utils.state_manager import StateManager
from utils.email_sender import EmailSender


class ReporterAgent:
    """
    Runs every Sunday.
    Reports from local state.json (no Gumroad API needed).
    Sends weekly summary email to the owner.
    """

    USD_TO_MYR = 4.7
    COST_PER_PRODUCT_BUILD_MYR = 0.40   # ~Claude tokens for one full build
    GUMROAD_FEE_PCT = 0.10

    def __init__(self, config):
        self.config = config
        self.state = StateManager(config["state_file"])
        self.email = EmailSender(
            sender=config["email_sender"],
            app_password=config["email_app_password"],
            recipient=config["email_recipient"]
        )

    def run(self):
        print("[Reporter] Compiling weekly report...")
        products = self.state.get_products()
        week = self.state.get_week_number() + 1
        report = self._build_report(products, week)
        self.email.send(f"Banana Lab — Week {week} Report", report)
        self.state.increment_week()
        print("[Reporter] Report sent.")

    # ------------------------------------------------------------------ #

    def _build_report(self, products, week):
        live     = [p for p in products if p.get("status") == "live"]
        pending  = [p for p in products if p.get("status") == "pending_upload"]
        new_week = [p for p in products if self._days_ago(p.get("created_date","") + "T00:00:00") <= 7]

        # Sales from state (incremented via --register or manual edit)
        total_sales   = sum(p.get("sales", 0) for p in live)
        revenue_gross = sum(p.get("sales", 0) * p.get("price", 0) for p in live)
        gumroad_fees  = revenue_gross * self.GUMROAD_FEE_PCT
        revenue_net   = revenue_gross - gumroad_fees
        revenue_myr   = revenue_net * self.USD_TO_MYR

        api_cost_myr  = len(new_week) * self.COST_PER_PRODUCT_BUILD_MYR
        net_myr       = revenue_myr - api_cost_myr

        # Best seller
        best = max(live, key=lambda p: p.get("sales", 0), default=None)
        best_line = (
            f"{best['title']} — {best.get('sales',0)} sale(s)"
            if best and best.get("sales", 0) > 0
            else "No sales recorded yet."
        )

        # Underperformers
        underperformers = [
            p for p in live
            if p.get("weeks_live", 0) >= 3 and p.get("sales", 0) == 0
        ]

        lines = [
            f"Banana Lab — Week {week} Report",
            "=" * 45,
            "",
            f"Products live:          {len(live)}",
            f"Pending Gumroad upload: {len(pending)}",
            f"New this week:          {len(new_week)}",
            f"Total sales (all time): {total_sales}",
            f"Gross revenue:          ${revenue_gross:.2f}  (RM {revenue_gross * self.USD_TO_MYR:.2f})",
            f"Gumroad fee (10%):      -${gumroad_fees:.2f}",
            f"Est. API cost:          -RM {api_cost_myr:.2f}",
            f"Net profit:             RM {net_myr:.2f}",
            "",
            f"Best seller:  {best_line}",
        ]

        for u in underperformers:
            lines.append(
                f"Low performer: \"{u['title']}\" — {u.get('weeks_live',0)} weeks live, 0 sales → consider price cut or removal"
            )

        if pending:
            lines += ["", "Pending uploads (need your action):"]
            for p in pending:
                lines.append(f"  • {p['title']}")
                lines.append(f"    PDF: products/{p['slug']}.pdf")
                lines.append(f"    Run: python main.py --register {p['slug']} YOUR_GUMROAD_URL")

        lines += [
            "",
            "Builder runs next Monday to publish a new pack.",
            "",
            "=" * 45,
            "Your call: APPROVE / CHANGE [niche] / PAUSE / REMOVE [product name]",
        ]

        return "\n".join(lines)

    @staticmethod
    def _days_ago(date_str):
        if not date_str:
            return 9999
        try:
            dt = datetime.fromisoformat(date_str[:19])
            return (datetime.now() - dt).days
        except Exception:
            return 9999
