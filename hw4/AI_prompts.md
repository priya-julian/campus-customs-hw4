# AI Prompts — Homework 4 (Campus Customs)

A log of the prompts I typed into the vibe coder while building this project. One section per
problem. The wording is mine, lightly cleaned up for typos and punctuation. Where my first
prompt was not enough to get what I wanted, I have included the follow-up and a note on what
the first prompt was missing.

---

## Setup — Workspace and project context

*Not a numbered problem, but these were the first things I typed, so they belong in the log.*

**Prompt:**

> /folder-joke-workspace homework 4

**Prompt:**

> First, I am just going to give you some context about the homework, so don't do anything
> just yet.
>
> In this homework, Campus Customs needs a real customer website with a helpful chatbot. We
> will build a React + Vite TypeScript front end and a Python FastAPI backend whose brain is
> a Pydantic agent. Shoppers need to be able to browse products, create an account, chat about
> merch, see matching items appear on the page, and get honest answers about price and stock
> from a local database.
>
> You are given campus_customs.db with tables for the product catalogue, inventory by size,
> and users (with hashed passwords). Product image file paths are in the catalogue table.
> Research https://yalebulldogblue.com/ to learn the style of the Campus Customs page and
> information for the agent prompt. Use my PORTKEY_API_KEY for the agent's AI calls. If using
> OpenAI through Portkey, use any model in the 5.6 or 6 series. We may want a smarter model
> for harder agent steps.
>
> In the end, we will push the project to a public GitHub repo and submit the repo URL on
> Canvas. Do not commit the database or product images.
>
> So again, we don't need to do anything right now. Just remember all this context as we work.

**Follow-up prompt:**

> I think they are in the Homework 4 folder. Double check.

**What was lacking in the first prompt:** I said the database and product images were "given"
but never said where they lived, so the model reported it could not find them. (They were in
`data.zip`, which had not been unpacked yet when it first looked.) The follow-up made it
re-check the folder, where it found `data/campus_customs.db` and the 102 product images.

---

## Problem 1 — Vibe coder prompts

**Prompt:**

> Problem 1: vibe coder prompts. Create AI_prompts.md at the start of the assignment and keep
> it updated as we work. This file is the log of what I type into the vibe coder. Put one
> section for each problem. Each section needs: the problem number and title, at least one
> prompt I typed in my own words as much as possible, and one follow-up prompt if we needed
> it, and a sentence on what was lacking from the first prompt.

**Follow-up prompt:**

> Would rather you clean up what I type a little.

**What was lacking in the first prompt:** I asked for my prompts "in my own words" without
saying how literally to take that, so the first version of this file reproduced my typos
exactly. The follow-up clarified that light copy-editing is fine as long as the wording and
intent stay mine.

---

## Problem 2 — Analyze the database

**Prompt:**

> Problem 2: Analyze the database. Look at the database/campus_customs.db and understand the
> fields of each table. Open it so I can look through it too. At a minimum, you must understand
> catalogue, inventory, and users. Start the file output/harness.md. Write down each table and
> its fields, and one short line on why each field matters for the shop or the chatbot. We will
> continue working on this file throughout the assignment (models, tools, safety, specs). Got it?

**Follow-up prompt:** None needed — the first prompt named the file to create, the tables to
cover, and the format for each field.

---

## Problem 3 — Build the Campus Customs website

**Prompt:**

> Problem 3: Build the Campus Customs website. Scaffold a React + Vite + TypeScript front end
> for Campus Customs. Put a nav bar at the top that links to the main pages, which are: Home,
> Products, About Us, Log in, Create Account. Pull Campus Customs style wording from
> https://yalebulldogblue.com/, BUT write the pages in your own voice (do not just copy the
> original site text).
>
> On the products page, show product images from the catalogue (use the image paths in the
> database) with basic product info (name, price, short description). Make each product open a
> single item page (large image on one side, full product text on the other — description,
> price, sizes/stock when you have them). Clicking a card on products should take the shopper
> there.
>
> Add a chat interface in the bottom right of the site (a floating chat panel is fine). The
> chat interface doesn't need to talk to an agent yet — a stub that will call the backend later
> is enough for right now. We will need a small API soon to read the database. It is fine to
> start a simple FastAPI app in backend/main.py just to serve products and images for now, then
> we will grow it into the agent backend in problem 5.
>
> Just get all this done and don't work ahead.

**Follow-up prompt:** None needed — the first prompt was specific about the stack, the nav
pages, the product-page layout, how far the chat should go, and where to stop.

---

## Problem 4 — Create account and login

**Prompt:**

> Problem 4: Create account and login. Now, build a normal create-account / login flow. Create
> account: first name, last name, email, password, and confirm password. Login: email and
> password. New accounts need to go into the users table. Make sure to store passwords securely
> so that hackers (human or AI) can't get access to them. You should see that the seed database
> already has a test user you can use while building. For that test user we have
> email: test@campuscustoms.yale.edu, password: password. Confirm that you can login as that
> user, and that a brand new account you create also works. Finally, update output/harness.md
> with how auth works (what you store for a user and how their passwords are protected).
> Again, just focus on these steps for now and don't work ahead.

**Follow-up prompt:** None needed — the first prompt listed the fields for both forms, gave me
the test credentials to check against, and said exactly what to document.

---

## Problem 5 — PydanticAI agent backend

**Prompt:**

> Problem 5: PydanticAI agent backend. Now we want to build the shop chatbot as a PydanticAI
> agent behind FastAPI, plugged into your front-end chat widget. Put the API app in
> backend/main.py — that is the file you run with uvicorn. Keep the agent as these four files
> next to it (same idea as in Homework 3):
>
> 1. backend/prompts/prompt.md — system prompt (we will grow this same file later)
> 2. backend/agent.py — agent entry/wiring
> 3. backend/tools.py — tools the agent can call
> 4. backend/models.py — pydantic/PydanticAI structured types
>
> Then in main.py, expose a chat route so a message from the website returns a reply from the
> agent (and whatever else you need for products/auth). You will need your AI model API key
> for the agent.
>
> Put Campus Customs voice and safety basics into prompts/prompt.md (you will expand tools and
> safety later). Start or update types in models.py for chat replies/product cards as needed.
> In output/harness.md note how the front end talks to FastAPI and how the agent is loaded
> (prompt file + model). Make sure the backend runs from the backend/ folder like this:
> `uvicorn main:app --reload --port 8000`. Sound good?

**Follow-up prompt:** None needed on the substance. I did interrupt twice with "wait stop"
and "no stop again sorry" before letting the work run, then re-sent the same prompt with the
file list numbered more clearly.

**What was lacking in the first prompt:** nothing about the task — the two stops were me
pausing, not correcting. The only thing the prompt left open was the filename `pagent.py`,
which was a typo for `agent.py`; I matched Homework 3's naming.

---

## Problem 6 — Tools: product info and stock

**Prompt:**

> Problem 6: Tools: product info and stock. Now, we want to give the agent tools that look up
> real information from campus_customs.db: product description, price, how many are in stock
> (by size when the customer asks). The agent must use the database — it should never invent
> prices or quantities. If a size is out of stock, please say so clearly. Expand
> prompts/prompt.md so the agent knows to call these tools for price and stock questions. Add
> or update return types in models.py. Then in output/harness.md, list each tool and explain
> which model fields you chose for lookup results and why.

**Follow-up prompt:** None needed.

**Note on overlap:** Problem 5 had already built the three tools and the honesty rules, so
this round was mostly strengthening rather than starting fresh — typing `check_stock`'s
return value as a real `StockAnswer` model, putting stock data into search results so the
agent stops recommending sold-out items, separating "sold out" from "we never made that
size", and adding a price audit.

---

## Problem 7 — Chat search that updates the page

**Prompt:**

> Problem 7: Chat search that updates the page. Now, we want to add a cool feature to the
> site. When a customer asks about a type of item (ex. "What hoodies do you have?") the agent
> should search the catalogue and the website should dynamically show those matching items as
> product cards (image, name, price, short info). This is an API contract: the agent returns
> structured product matches and then the front end renders them on the website. It looks
> really neat. After the dynamic product cards are loaded by the new feature, make sure the
> same single-item page behavior we built in Problem 3 still works: each product card
> (including the ones that chat just put on the page) should still open that detail view
> (large image + full info) when clicked. Update prompts/prompt.md and output/harness.md so it
> is clear how search results reach the page.

**Follow-up prompt:** None needed — the prompt specified the feature, the contract, and the
regression to check afterwards.

---

## Problem 8 — Customer memory

**Prompt:**

> Problem 8: Customer memory. When a shopper is logged in, save their chat history in the
> database in an appropriate table and reload it when they return. The agent should know who
> is chatting (name, email) — put that in agent deps (or an equivalent clear pattern) and/or
> tools the agent can call. Also pass enough page context that if someone is on a product page
> and asks "Do you have this in pink?", the agent knows what item they mean. You can put code
> into the agent context. Guests can still chat, but history only needs to persist for logged
> in users. Document in output/harness.md: how user chat history is stored, what customer
> fields the agent sees, and how page context is passed. Got all that?

**Follow-up prompt:** None needed — the prompt named the pattern to use (agent deps), gave a
concrete test case for page context, and listed the three things to document.

---

## Problem 9 — Usability improvements

**Prompt:**

> Problem 9: Usability improvements. Now that the core shop works, let's improve it. Choose
> and implement 2 front-end usability improvements and 2 agent/backend usability improvements.
> Front end improvements need to be things that make the site look better and make it easier
> to use. Agent/backend improvements are things that make the agent output better, more
> accurate, or safer. These could be new agent tools or things that make the agent run faster
> or cheaper. Write output/usability.md before or as you build. For each of the improvements
> say what you added and why it helps a Campus Customs shopper or the business. Then make sure
> all the improvements actually show up in the running app.

**Follow-up prompt:** None needed — the prompt set the count, the two categories, the
document to write, and the requirement to verify in the running app.

**Note:** I probed the app first and let the findings pick the improvements, then revised two
of them mid-build when the data contradicted my plan — an "in stock only" filter would have
filtered nothing, and a single match count let the agent conflate "13 matched my words" with
"13 in your budget". Both corrections are recorded in `output/usability.md`.

---

## Problem 10 — Creative design

**Prompt:**

> Problem 10: Now we want to add creative design so the site feels like a real Campus Customs
> storefront — fonts, color, hierarchy, motion, product presentation, chat feel. We will get
> more points for imaginative design. Some ideas I have are to make the fonts all feel more
> collegiate and fancy, add a Handsome Dan the bulldog personality to the chat (maybe with a
> little image of the dog), and use more colors of blue throughout. Feel free to get creative
> on your end. Please write output/design.md: what you changed and why it should help
> customers stick around and buy merch — keep this concrete and short.

**Follow-up prompt:** None needed — the prompt gave both a direction and permission to go
beyond it.

**Note:** Handsome Dan is drawn in HTML and CSS rather than as an image file, per the project
rule about implementing creatures in HTML. Building him surfaced a real bug — the agent's
prompt file was being cached for the life of the process, so prompt-only edits never reached
the running server; the cache is now keyed on the file's modification time.

---

## Problem 11 — Site testing (app check)

**Prompt:**

> Problem 11: Site testing (app check). Test the live site and document it in
> output/app_check.html (a page you can double click open). Include clear screenshots and
> short captions for:
>
> 1. chat checking the inventory level of an item (honest stock/price from the DB)
> 2. the dynamic search result card appearing after a category question (ex. hoodies)
> 3. one of the usability features you added in Problem 9
>
> Please ensure that the HTML is easy to grade: heading for each check, screenshot, one or two
> sentences on what the screenshot proves. Put the screenshot image files in
> output/app_check_images/ and link them from app_check.html with relative paths
> (ex. app_check_images/inventory.png).

**Follow-up prompt:** None needed — the prompt listed the three checks, the file layout, the
link style, and the structure each section should have.

---

## Problem 12 — Audit trail, safety, finish harness

**Prompt:**

> Problem 12: Audit trail, safety, finish harness. Keep an append-only
> output/audit_trail.json of agent loop activity (time, tool name, short args/result, stop
> reason). Do not wipe it between runs. Also, think of some safety rules to give the agent and
> put them in prompts/prompt.md. Then, finish output/harness.md so it is clear how the system
> works: model fields in models.py and why you chose them, tools and abilities, safety rules,
> specs (loop limits, result caps, models, how to run front + back).

**Follow-up prompt:** None needed — the prompt listed the fields to record, the no-wipe
requirement, and every section harness.md had to end with.

**Note:** the audit trail immediately caught something. A prompt-injection probe was coming
back as a 502, and the recorded stop reason showed why — the provider's own content filter
rejected it with a 400 before the model ran. That is a refusal, not an outage, so it now
answers in character with a 200.

---

## Problem 13 — Push to GitHub and submit the URL

**Prompt:**

> Problem 13: Push to GitHub and submit the URL. Put your code in a folder named hw4 and push
> it to a public GitHub repo. Do not put your real .env, campus_customs.db, or product images
> in the GitHub repo. Use .gitignore. Include .env.example with placeholders only. The first
> image shows the expected file layout. The second image shows the local-only data pack (not
> in git). Remember, the agent itself is four files under backend/: prompts/prompt.md,
> agent.py, tools.py, and models.py. README.md should explain how to run the front end and
> back end after placing the data pack.

**Follow-up prompt:**

> done

**What was lacking in the first prompt:** nothing about the task — the two screenshots pinned
the layout down precisely. The follow-up was me confirming I had created the empty GitHub
repo, which Claude could not do itself: the `gh` CLI is not installed on this machine, so it
could prepare and commit everything but needed the repo to exist before it could push.

**Result:** https://github.com/priya-julian/campus-customs-hw4

---

<!-- Append a new "## Problem N — Title" section here as each problem is tackled. -->
