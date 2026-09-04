# Household Chores

A small Django application for managing shared household chores.

## MVP

- Create a household chore
- Assign one family member
- Set a required due date and optional due time
- Mark a chore as completed

## Project Plan

See `_docs/plan.md` for the product specification.

## Development

Install or synchronize the project dependencies:

```bash
uv sync
```

Apply the database migrations:

```bash
uv run python manage.py migrate
```

Start the Django development server:

```bash
uv run python manage.py runserver
```

Run the full test suite:

```bash
uv run python manage.py test
```

### Local MVP verification

The assignment form lists existing `HouseholdMember` records. For a minimal
local setup, create one from the Django shell after applying migrations:

```bash
uv run python manage.py shell -c "from chores.models import HouseholdMember; HouseholdMember.objects.get_or_create(name='Alex')"
```

Then create a chore at `/chores/new/`, assign the member from `/chores/`, and
mark it completed. Completed chores are available at `/chores/completed/`.

## Status

Homework 1 — AI Dev Tools Zoomcamp 2026.
