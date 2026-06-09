# How to Use Borrower Risk Evaluator

## What This App Does

It takes real past loan borrowers and asks an AI to predict, for each one, whether the loan will default. It then checks every prediction against what actually happened, and shows you how accurate the AI really is. You can also see how it sorts borrowers into "approve on its own", "flag", and "send to a human".

## What You Need First

A free Google Gemini API key. Get one at https://aistudio.google.com/apikey. The key stays in your browser and is sent only to Google. Nothing is stored on a server.

## How to Start

1. Double-click `open-app.bat` to open the app in your browser (or open `index.html`).
2. On the "Evaluation scorecard" tab, paste your Gemini key into the box.
3. Choose how many borrowers to test (50 is fast, 150 is more reliable).
4. Click "Run evaluation". A progress bar fills as the AI classifies each borrower. This takes about a minute.

## How to Read the Results

- The two big numbers up top: accuracy on all borrowers, and accuracy on just the cases the AI was confident enough to clear on its own. The second is usually higher, which is the point.
- The "95% CI" line under each number is the margin of error. A wider range means fewer cases, so trust the number a little less.
- The confusion matrix shows where it was right and wrong. "Caught" and "Cleared" are correct; "Missed" and "False alarm" are mistakes.
- Recall, precision, and F1 describe how well it handles the rare, costly defaults, which plain accuracy hides.
- The chart at the bottom shows the trade-off: the stricter you set the dial, the more accurate the auto-cleared pile, but the fewer cases clear and the more go to a human.

## The Safety Dial

The slider at the very top sets how sure the AI must be before a case clears without a human. Drag it and every number and pile updates live. Stricter means safer but more manual review.

## The Triage Console

The second tab shows the three piles: auto-approve, auto-flag, and your review queue. Only the uncertain cases reach the queue. You can click Approve or Flag on each one to clear it. The "By loan type" rows let you filter to one purpose (education, medical, and so on).

## Portfolio to Production

The third tab explains, in plain terms, how this single-page demo would become a real system handling 10,000 or more borrowers, and what stays the same versus what changes.

## Notes

- Nothing here is pre-computed. Every number comes from a live run against real recorded loan outcomes.
- Tick the "Remember the key" box to save the key in this browser for next time.
- This is decision support. A human should own the final call on any flagged borrower.
