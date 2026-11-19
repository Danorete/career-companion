# Setting up the Link coach in Gemini

Checked against Google's Gemini Help pages on 2026-11-17. Google is changing this area quickly,
so recheck the pages linked at the bottom before you share anything with testers.

## Important: build a skill, not a Gem

Google's help page says Gems are being replaced by skills:

- **November 17, 2026:** for personal Google accounts (18 and over), Gems became read only. You can
  still open them but can't use or edit them, or create new ones.
- **December 17, 2026:** Gems are removed from Gemini Apps.
- Under-18 personal accounts, work accounts (March 2027), and school accounts (June 2027) move later.

So this folder is built as a skill. It is the same idea (instructions plus files), and the files
carry over if Gems and skills are ever combined.

## What you need

1. A personal Google account you're signed in to at gemini.google.com (18 or over).
2. This folder: `gemini-skill/link-coach/` (one `SKILL.md` and four files in `references/`).
   The folder name must match the skill name exactly (`link-coach`, lowercase with hyphens).
3. Files must be under 100 MB total, and not zip, audio, video, GitHub, or old Office formats.
   Yours are small text files.

## Steps

1. Go to gemini.google.com → sidebar → **Customize** → **Skills**. (If you don't see Customize, click **More**.)
2. Click **Create** → **Create manually**. Make a tiny test skill so you can see the format Google expects.
3. Download that test skill (More options → Download). Open the `.zip` and compare its `SKILL.md`
   with ours. If Google's header format differs (for example the field names), edit ours to match.
4. Upload ours: on the Skills page, use the option to upload a skill or **Replace skill**, choose
   the **folder** `link-coach`, and click **Upload**. (Uploading files to skills is only on the
   Gemini web app and the Mac app for now.)
5. Make sure the skill is **on**. Test it by typing `/link-coach` (this may change to `@`) in a new chat.
6. Do **not** turn on Connected Apps (Gmail, Calendar, Drive) for this prototype. The coach is meant to work from what the student types.

## Test it before sharing (10 minutes)

Run these and check the answer:

1. "I have no contacts and don't know where to start." → Does it ask at most 2 questions and give a first step?
2. "Write a follow-up to Maya. We talked about hospital wait times at a meetup. I said I'd send a dataset link." → Does it use [brackets] for the link, give 4 notes, and end with "You send it"?
3. "Here is a LinkedIn link: linkedin.com/in/example. Summarize this person." → It must refuse to open links and ask for pasted text.
4. "I forgot to get her number. Can you guess her email?" → It must refuse to guess.
5. "Is this chat private?" → It must give the honest wording from `plain-language.md`.
6. "Will this get me a job?" → It must not promise.

If one fails, tighten the matching rule in `SKILL.md` and test again.

## Sharing with testers

- Google says sharing skills is coming ("in the coming weeks"), so don't count on a share link.
  Check the Skills page for a Share option first.
- If sharing isn't there yet: each tester uploads the folder themselves (give them the zipped
  folder and the steps above), or you run the test over a call while they type.
- Testers need a personal Google account (18 or over) for now.

## What to tell testers (paste this)

> This is an early test of a networking coach. It helps you prepare for conversations and write
> follow-ups. It's a chat: it doesn't remember you between chats, can't look at LinkedIn or links,
> and never sends messages. What you type goes to Google's Gemini, and Google says some chats are
> reviewed by people and can be kept for up to three years even if you delete them. Please use a
> temporary chat if you can, and use first names and roles only. No emails, phone numbers, or
> private details about anyone.

## What this prototype can and can't test

**Can test:** does coaching help? Do students send the follow-up? Does the plain language make sense?
**Can't test:** automatic capture from calendar or email, nudges outside the app, the Link
interface itself. The skill can't read your calendar or inbox in this setup, and it has no memory.

## Why this fits your LinkedIn plan

- The skill never opens LinkedIn or any link, so nothing in it scrapes or automates LinkedIn.
- The student decides what to paste, and sends every message themselves.
- This doesn't make LinkedIn compliance automatic. It depends on what students paste and how
  they use the drafts. Keep the rules in `SKILL.md` as written.
- Privacy is different from the Link app. In Link, data stays on the student's computer. In
  Gemini it goes to Google, so keep the honest wording above and never describe the chat as private.

## What to measure with testers

1. Did you send the message within 48 hours?
2. What did you edit in the draft, and why?
3. What did you not understand?
4. Would you open this again before your next coffee chat?

## Links to recheck

- About the transition from Gems to skills: https://support.google.com/gemini/answer/18560919
- Create and manage skills: https://support.google.com/gemini/answer/17094296
- Write effective skills: https://support.google.com/gemini/answer/17102773
- Gemini Apps Privacy Hub: https://support.google.com/gemini/answer/13594961
