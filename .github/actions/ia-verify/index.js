const core = require('@actions/core');
const axios = require('axios');

async function run() {
  try {
    // Obtém os inputs
    const token = core.getInput('token');
    const payload = core.getInput('payload');
    const apiUrl = core.getInput('api_url');

    // Faz a requisição para a API
    const response = await axios.post(`${apiUrl}/validate`, {
      token,
      payload: JSON.parse(payload)
    });

    // Verifica o resultado
    if (response.data.status !== 'OK') {
      core.setFailed(`Validation failed: ${response.data.message}`);
      return;
    }

    // Log do sucesso
    core.info('Validation successful!');
    core.info(`Detalhes: ${JSON.stringify(response.data.details, null, 2)}`);

  } catch (error) {
    // Trata erros
    if (error.response) {
      core.setFailed(`API error: ${error.response.data.detail || error.message}`);
    } else {
      core.setFailed(`Error: ${error.message}`);
    }
  }
}

run(); 