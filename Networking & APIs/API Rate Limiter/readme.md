Controls how many requests a user (or IP address) can make within a certain time frame.
build in pure Python using only:
	•	time (for timestamps)
	•	socket (for simple server demo)
	•	json (for returning data)

1. keeps a record of each client’s requests (by IP address).
2.	It allows only a certain number of requests per time window (e.g., 5 requests per 10 seconds).
3.	If a client exceeds that limit:
- The server responds with HTTP 429 Too Many Requests.
4.	If within the limit:
- The server responds normally with 200 OK.


Rate Limiting Logic
implement a sliding window counter:
	•	For each client IP, store a list of request timestamps.
	•	Every time they send a request:
	•	Remove old timestamps (outside the window).
	•	Count how many are left.
	•	If it exceeds the limit → block them.
