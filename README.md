# IA Verify - GitHub Action (Direct OpenAI Integration)

Validate CI/CD steps, configurations, or any security payload using OpenAI (ChatGPT) **directly from your workflow**, with no backend required.
This action sends your payload to OpenAI, prints a security report, and blocks the pipeline if risks are detected.

## 🚀 How does it work?

- Receives an OpenAI token and a payload (JSON) for analysis.
- Sends the data to the GPT-4 model (or another, if you prefer).
- The AI analyzes and returns a report.
- If the AI indicates risk, the action automatically blocks the pipeline.

## 📦 Installation

1. Add the action to your repository:

```yaml
- name: Security validation with AI
  uses: renatomateusx/ia-verify@main  # or action_alt.yml if separated
  with:
    openai_token: ${{ secrets.OPENAI_TOKEN }}
    payload: |
      {
        "type": "kubernetes",
        "content": "apiVersion: v1\nkind: Pod\nmetadata:..."
      }
```

2. Create a secret in your repository named `OPENAI_TOKEN` with your OpenAI API key.

## 📝 Full Workflow Example

```yaml
name: CI with AI Validation
on:
  push:
    branches: [main]
jobs:
  validate-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Security validation with AI
        uses: renatomateusx/ia-verify@main
        with:
          openai_token: ${{ secrets.OPENAI_TOKEN }}
          payload: |
            {
              "type": "kubernetes",
              "content": "apiVersion: v1\nkind: Pod\nmetadata:..."
            }

      - name: Deploy (only runs if AI approves)
        run: echo "Deploy approved!"
```

## ⚙️ How does the decision work?

The prompt sent to the AI asks it to generate a report and **always** finish with a line:

```
DECISION: OK
```
or
```
DECISION: BLOCK
```

The action reads this line:
- If it's `OK`, the workflow continues.
- If it's `BLOCK`, the pipeline is stopped and the report is printed in the logs.

## 🔒 Security
- The OpenAI token is never exposed in logs.
- The payload can be any JSON (YAML, configs, code, etc).

## 💡 Use Cases
- Validate Kubernetes, Terraform, Dockerfile, pipeline YAML, RBAC, etc.
- Check for dangerous permissions, exposed secrets, bad practices.

## 🛠️ Customization
- You can edit the prompt in `index_alt.js` to match your policy.
- You can change the model (`gpt-4`, `gpt-3.5-turbo`, etc).

## 📄 Output
- The full AI report is printed to the console.
- The `relatorio` output can be used in other workflow steps.

## 🧑‍💻 Contributing
Pull requests are welcome!

---

**Example payload:**

```json
{
  "type": "github-actions",
  "content": "jobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo Hello World"
}
```

---

**Questions?** Open an issue or send a PR! 