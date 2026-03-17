class RiskEngine:

    def __init__(self):
        pass

    def evaluate(self, message_result=None, link_result=None, account_result=None):

        score = 0
        reasons = []

        # Message risk
        if message_result == "scam":
            score += 40
            reasons.append("Scam message detected")

        # Link risk
        if link_result == "Dangerous":
            score += 40
            reasons.append("Dangerous link detected")

        # Account risk
        if account_result == "fake":
            score += 30
            reasons.append("Fake account pattern detected")

        # Risk level
        if score >= 70:
            risk_level = "HIGH"
        elif score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return risk_level, score, reasons