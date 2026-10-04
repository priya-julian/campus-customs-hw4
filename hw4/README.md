# Campus Customs

A storefront for **Campus Customs** (Yale Bulldog Blue) with a shopping assistant called
Handsome Dan. React + Vite + TypeScript on the front, FastAPI with a PydanticAI agent on the
back, reading a local SQLite catalogue.

The agent answers questions about price, colour and stock, surfaces matching products onto
the page as you chat, and is built so it cannot quote a price or a stock level that is not in
the database.

## Layout

```
hw4/
├── AI_prompts.md            # log of the prompts used to build this
├── requirements.txt         # Python dependencies
├── .env.example             # placeholders only — copy to .env and fill in
├── .gitignore
├── README.md
├── frontend/                # Vite React TypeScript app
├── backend/
│   ├── main.py              # FastAPI app — run with: uvicorn main:app --reload --port 8000
│   ├── agent.py             # agent wiring: Portkey client, model, prompt, tools, deps
│   ├── models.py            # Pydantic types
│   ├── tools.py             # catalogue tools the agent can call
│   ├── auth.py              # password hashing and session tokens
│   ├── audit.py             # append-only audit trail writer
│   └── prompts/
│       └── prompt.md        # system prompt — voice and safety
└── output/
    ├── harness.md           # how the whole system works
    ├── design.md            # design decisions
    ├── usability.md         # the usability improvements and their evidence
    ├── app_check.html       # tested-site write-up with screenshots
    ├── app_check_images/    # screenshots linked from app_check.html
    └── audit_trail.json     # append-only record of agent runs
```

## 1. Put the data pack in place

The database and product images are **not in this repository** — the database contains user
accounts and the images are not ours to redistribute. Unpack the course data pack inside
`hw4/` so it looks like this:

```
hw4/data/
├── campus_customs.db
└── products/                # images referenced by the catalogue
```

The backend looks for `hw4/data/campus_customs.db` and serves images from
`hw4/data/products/`. Catalogue rows store image paths relative to `data/`, so no renaming
is needed.

## 2. Add your API key

The agent calls OpenAI through Portkey. Copy the example file and fill in your own key:

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your real key. `PORTKEY_API_KEY` is read from
the environment at run time and is never committed — `.env` is gitignored, `.env.example` is
not. The backend walks up from `backend/` looking for a `.env`, so `hw4/.env`,
`hw4/backend/.env`, or one in a project folder above all work.

## 3. Run the back end

All four commands run from `hw4/backend/`. Create the virtual environment and install into
it:

```bash
cd backend
```

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r ../requirements.txt
```

Then start the server:

```bash
uvicorn main:app --reload --port 8000
```

Check it came up, in another terminal:

```bash
curl localhost:8000/api/health
```

That should report `{"status":"ok","products":102}`.

## 4. Run the front end

In a second terminal, from `hw4/` (not `hw4/backend/`):

```bash
npm --prefix frontend install && npm --prefix frontend run dev
```

Open the URL Vite prints (usually http://localhost:5173). Vite proxies `/api` and `/media`
to the backend on port 8000, so **both have to be running**.

> If port 8000 or 5173 is already taken, pass a different one — e.g.
> `uvicorn main:app --reload --port 8001` and
> `npm --prefix frontend run dev -- --port 5174`. If you move the backend off 8000, update
> the proxy target in `frontend/vite.config.ts` to match.

## Signing in

The data pack ships with a test account:

```
email:    test@campuscustoms.yale.edu
password: password
```

Creating a new account through the site works too. Passwords are stored as salted
PBKDF2-HMAC-SHA256 digests at 600,000 iterations — see `output/harness.md` for the details.

## Talking to the agent without the website

```bash
cd backend && python agent.py "what navy hoodies do you have?"
```

## API

| Endpoint | Returns |
| --- | --- |
| `GET /api/health` | Status and product count |
| `GET /api/products` | All products, each with per-size availability |
| `GET /api/products/{id}` | One product plus stock by size |
| `GET /media/products/{file}` | Product images |
| `POST /api/auth/signup` | Create an account |
| `POST /api/auth/login` | Sign in |
| `GET /api/auth/me` | The signed-in user |
| `POST /api/chat` | Ask the agent; returns a reply plus matching products |
| `GET /api/chat/history` | Saved conversation for the signed-in shopper |

## Where to read more

`output/harness.md` is the full write-up: the database, the Pydantic types and why they have
the fields they do, the tools, how accounts and passwords work, the agent's safety rules, and
the loop limits and caps.
