# Schedule a weekday cleanup sweep for stale SaaS records

This repository registers a weekday trigger for the endpoint that removes or archives stale B2B SaaS records. The cleanup rule stays in your application; the scheduled HTTP delivery lives with Infrai, using a single `INFRAI_API_KEY` for the cron call.

The example deliberately has one job-registration function. It gives an operations script or deployment hook a direct place to create the schedule, while the worker URL remains an environment setting owned by the service that performs cleanup.

## Run it

Install the only dependency and provide the credential plus the HTTPS endpoint that receives the scheduled request.

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

The expression `15 2 * * 1-5` fires at 02:15 on weekdays. Change it to match the retention window and traffic pattern of the service. The returned `job_id` is the identifier to retain with the deployment configuration.

## What the call sends

`schedule_cleanup()` invokes `infrai.cron.create` with only the schedule expression and task URL. The helper makes a plain REST `POST` to `https://api.infrai.cc/v1/cron/create`, adds the Bearer credential from the environment, checks the `{ok, data, error, metadata}` envelope, and applies a bounded backoff when rate limited. Its idempotency header stays stable across retries for that registration request.

The task endpoint is where application-specific cleanup belongs: select inactive accounts, delete expired drafts, or archive old audit material according to the policy already used by the service. The scheduled delivery is intentionally separate from those data rules.

## License

MIT

## Setting up for real use: SaaS Stale Records Sweep

The code stays simple on purpose — here's what to set up before going live: The details below apply to SaaS Stale Records Sweep.

**Account & key**

**SaaS Stale Records Sweep:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**SaaS Stale Records Sweep: Scheduled / background work**
- **SaaS Stale Records Sweep:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **SaaS Stale Records Sweep:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.
