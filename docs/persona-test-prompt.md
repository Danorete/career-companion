# Persona test prompt for Link

A rehearsal, not research. This prompt asks Claude to invent 100 realistic people, pitch Link to each one, and
report who would use it, who wouldn't, and why. Use the result to sharpen the pitch and to decide what to ask
**real** students and career-services staff. Simulated people are kinder and more predictable than real ones, so
never quote the numbers as evidence.

How to use it: paste everything inside the box into a new Claude conversation. Change the bracketed parts if you
want to test a different pitch or audience. Don't add anyone's real name or details.

```text
You are helping me pressure-test a product idea before I show it to real users. Be a tough, realistic
simulator, not a cheerleader. Most new apps are ignored; reflect that.

## The product
Link is a free desktop app for students and recent graduates who find professional networking awkward.
- Today: one suggested next step (for example "Send Jordan the article you mentioned"), beside your most
  recent conversations.
- People: each connection with your notes and conversation history.
- Quick log: write down a conversation right after it happens, even with fuzzy names and dates.
- Import: bring in your LinkedIn connections file, chosen message excerpts, or a calendar file.
- An AI companion helps you prepare questions, find a genuine reason to follow up, and draft messages.
  It only suggests a follow-up when something real happened (a promise, a suggestion), never just because
  time passed.
- Privacy: everything is stored on your own Mac. It never browses LinkedIn and never sends messages for you.
- Current limits: Mac only, desktop only (no phone app yet), and you have to open it; there are no notifications.

## The pitch to test
[PITCH A] "LinkedIn and Handshake help you find people. Link helps you have the conversation and keep the
relationship going."
[PITCH B] "Think of it as Hinge for professional relationships: it gets you past 'hey' to a real conversation,
then reminds you why to follow up."

## Step 1: build 100 people
Create 100 distinct people in these groups (keep the counts):
- 30 undergraduates across years and majors (include business, computer science, nursing, arts, undeclared)
- 15 first-generation college students
- 10 international students
- 10 graduate students
- 20 recent graduates (0 to 2 years out), some employed, some job hunting
- 10 university career-services staff or advisors
- 5 sceptics who already network easily or dislike productivity apps

For each person give: a one-line background, how comfortable they are with networking (1 to 5), the tools they
use now (LinkedIn, Handshake, notes app, spreadsheet, nothing), their device (Mac, Windows, phone only), how
much time they'd give a new app in a week, and one honest reason they might say no.
Keep each person to one row of a table. If you run out of space, stop at a clean point and I'll say "continue".

## Step 2: pitch each person
Show each person [PITCH A]. Have them react in one or two sentences in their own voice, then decide:
- "Would install and try it this week" / "Maybe later" / "No"
- For career-services staff instead: "Would recommend it to students" / "Maybe" / "No"
Base decisions on the person's situation, device and habits, not on how good the pitch sounds.
Windows-only and phone-only people cannot install it; count them as "No" and say so.

## Step 3: report
1. A table: group, number shown, would try, maybe, no.
2. The 5 most common reasons for "No", each with the count and two short quotes.
3. Who said yes most often, and the specific situation that made them say yes.
4. For each of these claimed differentiators, did people care? Score each "mattered / didn't matter / confused
   them" with counts: (a) help having the conversation, not finding people; (b) follow-ups only with a real
   reason; (c) logging fuzzy memories; (d) everything stays on your Mac.
5. What would turn the most "Maybe" answers into "Would try"? List the top 3 changes.
6. Repeat Steps 2 and 3 with [PITCH B] for the same 100 people and say which pitch did better, by group.

## Step 4: what to check with real people
Write 6 interview questions I can ask real students and one career-services advisor to test the three most
important findings. Avoid leading questions; ask about what they did last time they tried to network.

Finally, list the biggest ways this simulation could be wrong.
```

## Reading the results

- Treat percentages as rough direction. A simulated "would try" rate is usually higher than reality.
- The most useful parts are usually the reasons for "No" and the questions in Step 4.
- Before showing results to anyone, check them against at least a few real conversations.
