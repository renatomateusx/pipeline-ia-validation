const core = require("@actions/core");
const axios = require("axios");

async function run() {
  try {
    const openaiToken = core.getInput("openai_token");
    const payload = core.getInput("payload");

    const response = await axios.post(
      "https://api.openai.com/v1/chat/completions",
      {
        model: "gpt-4",
        messages: [
          { role: "system", content: "You are a security validator for CI/CD pipelines. Analyze the payload and generate a report. The report should be in JSON format. The report should be in English. The decisision should be in the field 'decision'. The decision should be 'OK' or 'BLOCK'." },
          { role: "user", content: payload }
        ]
      },
      {
        headers: {
          "Authorization": `Bearer ${openaiToken}`,
          "Content-Type": "application/json"
        }
      }
    );

    const resultado = response.data.choices[0].message.content;
    console.log("===== IA VERIFY  REPORT =====");
    console.log(resultado);
    core.setOutput("report", resultado);

  } catch (error) {
    core.setFailed(error.message);
    if (error.response) {
      console.error(error.response.data);
    }
  }
}

run();