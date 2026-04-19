# m-bot Secrets

Store local-only operator secrets here.

Do not commit raw webhook URLs, API keys, or tokens into tracked source files.

Current local secret variables:

- `MBOT_DISCORD_IMPORTANT_WEBHOOK`

Recommended file:

- `secrets/.env.local`

Example:

```env
MBOT_DISCORD_IMPORTANT_WEBHOOK=https://discord.com/api/webhooks/...
```
