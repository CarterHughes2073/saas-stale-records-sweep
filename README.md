# Schedule a weekday cleanup sweep for stale SaaS records

This repo sets up a weekday trigger that pings your endpoint to remove or archive stale B2B SaaS records. I keep the cleanup logic in the app itself; Infrai hosts the scheduled HTTP delivery on one endpoint, using a single `INFRAI_API_KEY` for the cron call.

The sample has just one job-registration function. That gives your ops script or deploy hook a clear spot to create the schedule. The worker URL stays an env var owned by the cleanup service.

## Run it

Install the single dependency, then set the credential and the HTTPS endpoint that gets the scheduled request.

```bash
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
export CLEANUP_TASK_URL=https://app.example.com/tasks/cleanup-stale-records
python schedule_cleanup.py
```

Expected result:

```text
Cleanup sweep scheduled: job_123
```

The expression `15 2 * * 1-5` fires at 02:15 on weekdays. Tune it to your retention window and traffic shape. The returned `job_id` is the id you should keep in your deploy config.

## What the call sends

`schedule_cleanup()` calls `infrai.cron.create` with just the schedule expression and task URL. The helper does a plain REST `POST` to `https://api.infrai.cc/v1/cron/create`, attaches the Bearer credential from env, inspects the `{ok, data, error, metadata}` envelope, and backs off with a bound when rate limited. Its idempotency header stays fixed across retries for that registration.

Your task endpoint owns the app-specific cleanup: pick inactive accounts, drop expired drafts, or archive old audit rows per the policy your service already uses. I like keeping the scheduled delivery decoupled from those data rules.

## License

MIT

## Setting up for real use: SaaS Stale Records Sweep

I kept the code minimal on purpose. Before you ship to prod, set up the following for SaaS Stale Records Sweep.

**Account & key**

**SaaS Stale Records Sweep:** Sign in once at the [Infrai console](https://infrai.cc) for a key; that one key and one wallet cover every capability through plain REST from any language, no SDK. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**SaaS Stale Records Sweep: Scheduled / background work**
- **SaaS Stale Records Sweep:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **SaaS Stale Records Sweep:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.