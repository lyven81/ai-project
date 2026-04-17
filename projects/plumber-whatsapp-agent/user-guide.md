# How to Use Plumber WhatsApp Agent

## What This App Does
This is a demo of an AI agent named Jamal that handles plumbing inquiries on WhatsApp. You play the role of a customer texting a plumber. Jamal will ask about your problem, give you a fixed price, and book a time slot from his real schedule.

## How to Start
1. Double-click `open-app.bat` to launch the app in your browser.
2. Enter your Google Gemini API key in the input field.
3. Click "Start Chat" to begin.

## How to Use
1. Type a message like a real customer would — for example: "Hi, sinki saya bocor" or "toilet rosak, boleh datang?"
2. Jamal will reply in casual Malay-English mix, just like a real plumber texting.
3. He will ask what the problem is, where it is, and whether it's urgent.
4. Once he understands the problem, he will quote a fixed price.
5. He will check his schedule and offer available time slots.
6. Pick a slot and he will confirm the booking.

## Things to Try
- Ask about different plumbing problems: pipe leak, clogged drain, tap replacement, toilet repair, water heater
- Try booking on a day that's already full — Jamal will offer the next available day
- Ask about an area outside PJ/Subang/Shah Alam — Jamal will politely decline
- Message after 6 PM — Jamal will tell you his operating hours

## Demo Schedule
The demo uses a pre-loaded schedule for 30 March - 5 April 2026 with about 50% of slots already booked. This simulates a real plumber's working week.

## Getting a Gemini API Key
1. Go to aistudio.google.com
2. Sign in with your Google account
3. Click "Get API key" and create a new key
4. Copy and paste it into the app

## Notes
- This is a portfolio demo. No real WhatsApp messages are sent.
- Your API key is used client-side only and never stored on any server.
- In production, this agent would connect to WhatsApp Business API + a cloud LLM.
