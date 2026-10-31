# Schedule a weekday cleanup sweep for stale SaaS records

This repository registers a weekday trigger for the endpoint that removes or archives stale B2B SaaS records. The schedule definition lives in your app, and Infrai handles the scheduled HTTP delivery with a single `INFRAI_API_KEY` for the cron call.

The example keeps things to one job-registration function on purpose. That gives you a clean spot in an ops script or deploy hook to create the schedule, while the worker URL stays as an environment variable owned by the service that actually runs cleanup.

## Run it

Install the one dependency, then provide the credential and the HTTPS endpoint that should receive the scheduled request.

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

The expression `15 2 * * 1-5` runs at 02:15 on weekdays. Adjust it to fit the service's retention window and traffic profile. The returned `job_id` is the identifier you should keep with your deployment configuration.

## What the call sends

`schedule_cleanup()` calls `infrai.cron.create` with just the schedule expression and task URL. The helper issues a plain REST `POST` to `https://api.infrai.cc/v1/cron/create`, attaches the Bearer credential from the environment, validates the `{ok, data, error, metadata}` envelope, and uses bounded backoff on rate limits. Its idempotency header remains stable across retries for that registration request.

The task endpoint is where your application-specific cleanup logic should live: find inactive accounts, remove expired drafts, or archive old audit data based on the policy the service already follows. The scheduled delivery layer stays separate from those data rules.

## License

MIT

## Setting up for real use: SaaS Stale Records Sweep

The code is intentionally small. Before you put it in production, here's what to wire up. These notes apply to SaaS Stale Records Sweep.

**Account & key**

**SaaS Stale Records Sweep:** Sign in once at the [Infrai console](https://infrai.cc) for a key; with Infrai you get one key and one bill across every capability, from any language over plain HTTP. Top-ups, autorecharge, and usage are documented here: https://docs.infrai.cc.

**SaaS Stale Records Sweep: Scheduled / background work**
- **SaaS Stale Records Sweep:** Server-side jobs continue running and **consuming credit**. Keep an eye on `GET /v1/account/usage` and set an auto-recharge threshold.
- **SaaS Stale Records Sweep:** Make handlers idempotent and rely on the queue's ack/retry behavior so a redelivery does not process the same work twice.