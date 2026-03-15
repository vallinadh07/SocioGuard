from analyzers.message_analyzer import MessageAnalyzer
from analyzers.link_analyzer import LinkAnalyzer
from analyzers.account_analyzer import AccountAnalyzer

print("SocioGuard Security Analyzer")

message_analyzer = MessageAnalyzer()
link_analyzer = LinkAnalyzer()
account_analyzer = AccountAnalyzer()

message_analyzer.train("data/message_dataset.csv")
account_analyzer.train("data/account_dataset.csv")

print("\n1. Analyze Message")
print("2. Analyze Link")
print("3. Analyze Account")

choice = input("\nChoose option: ")

if choice == "1":

    message = input("\nEnter message: ")
    label, confidence = message_analyzer.predict(message)

    print("\nMessage Result:", label)
    print("Confidence:", confidence, "%")


elif choice == "2":

    url = input("\nEnter URL: ")
    risk, reasons = link_analyzer.analyze(url)

    print("\nLink Status:", risk)

    for r in reasons:
        print("-", r)


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