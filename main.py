from analyzers.message_analyzer import MessageAnalyzer

print("SocioGuard - Message Analyzer")

analyzer = MessageAnalyzer()

analyzer.train("data/message_dataset.csv")

message = input("\nEnter message: ")

label, confidence = analyzer.predict(message)

print("\nResult:", label)
print("Confidence:", confidence, "%")