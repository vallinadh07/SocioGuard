from analyzers.message_analyzer import MessageAnalyzer
from analyzers.link_analyzer import LinkAnalyzer
from analyzers.account_analyzer import AccountAnalyzer
from utils.risk_engine import RiskEngine

print("SocioGuard Security Analyzer")

message_analyzer = MessageAnalyzer()
link_analyzer = LinkAnalyzer()
account_analyzer = AccountAnalyzer()
risk_engine = RiskEngine()

message_analyzer.train("data/message_dataset.csv")
account_analyzer.train("data/account_dataset.csv")

print("\n1. Analyze Message")
print("2. Analyze Link")
print("3. Analyze Account")
print("4. Full Interaction Analysis")

choice = input("\nChoose option: ")

# MESSAGE
if choice == "1":

    message = input("\nEnter message: ")
    label, confidence = message_analyzer.predict(message)

    print("\nMessage Result:", label)
    print("Confidence:", confidence, "%")


# LINK
elif choice == "2":

    url = input("\nEnter URL: ")
    risk, reasons = link_analyzer.analyze(url)

    print("\nLink Status:", risk)

    for r in reasons:
        print("-", r)


# ACCOUNT
elif choice == "3":

    followers = int(input("Followers: "))
    following = int(input("Following: "))
    posts = int(input("Posts: "))
    age = int(input("Account Age (days): "))

    label, confidence = account_analyzer.predict(
        followers, following, posts, age
    )

    print("\nAccount Status:", label)
    print("Confidence:", confidence, "%")


# FULL ANALYSIS
elif choice == "4":

    message = input("Message: ")
    url = input("Link: ")

    followers = int(input("Followers: "))
    following = int(input("Following: "))
    posts = int(input("Posts: "))
    age = int(input("Account Age (days): "))

    msg_result, _ = message_analyzer.predict(message)
    link_result, _ = link_analyzer.analyze(url)
    acc_result, _ = account_analyzer.predict(followers, following, posts, age)

    risk_level, score, reasons = risk_engine.evaluate(
        msg_result,
        link_result,
        acc_result
    )

    print("\nSOCIOGUARD FINAL REPORT")
    print("----------------------")
    print("Message:", msg_result)
    print("Link:", link_result)
    print("Account:", acc_result)

    print("\nFinal Risk Level:", risk_level)
    print("Risk Score:", score)

    print("\nReasons:")
    for r in reasons:
        print("-", r)

else:
    print("Invalid option")