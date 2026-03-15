from analyzers.message_analyzer import MessageAnalyzer
from analyzers.link_analyzer import LinkAnalyzer

print("SocioGuard Security Analyzer")

# Initialize analyzers
message_analyzer = MessageAnalyzer()
link_analyzer = LinkAnalyzer()

message_analyzer.train("data/message_dataset.csv")

print("\n1. Analyze Message")
print("2. Analyze Link")

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

    if reasons:
        print("Reasons:")
        for r in reasons:
            print("-", r)