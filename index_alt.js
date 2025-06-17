const core = require("@actions/core");
const axios = require("axios");
const { encode } = require('gpt-3-encoder');

// Configurações internas
const MAX_TOKENS_PER_CHUNK = 12000;
const MAX_CHUNKS = 5; // Limite de chunks para evitar custos excessivos

async function splitIntoChunks(text) {
    const tokens = encode(text);
    const chunks = [];
    let currentChunk = [];
    let currentLength = 0;

    for (const token of tokens) {
        if (currentLength + 1 > MAX_TOKENS_PER_CHUNK) {
            chunks.push(currentChunk);
            currentChunk = [token];
            currentLength = 1;
        } else {
            currentChunk.push(token);
            currentLength++;
        }
    }

    if (currentChunk.length > 0) {
        chunks.push(currentChunk);
    }

    // Se exceder o limite de chunks, avisa o usuário
    if (chunks.length > MAX_CHUNKS) {
        core.warning(`Content was split into ${chunks.length} chunks, which exceeds the recommended limit of ${MAX_CHUNKS}. Consider reducing the content size.`);
    }

    return chunks;
}

async function analyzeChunk(chunk, openaiToken) {
    const response = await axios.post(
        'https://api.openai.com/v1/chat/completions',
        {
            model: 'gpt-3.5-turbo',
            messages: [
                {
                    role: 'system',
                    content: 'You are a security validator for CI/CD pipelines. Analyze the provided chunk and identify security issues. End your response with DECISION: OK or DECISION: BLOCK'
                },
                {
                    role: 'user',
                    content: `This is part ${chunk.index + 1} of ${chunk.total} chunks. Analyze this portion:\n\n${chunk.content}`
                }
            ]
        },
        {
            headers: {
                'Authorization': `Bearer ${openaiToken}`,
                'Content-Type': 'application/json'
            }
        }
    );

    return response.data.choices[0].message.content;
}

async function run() {
    try {
        const openaiToken = core.getInput("openai_token");
        const payload = core.getInput("payload");

        // Parse the payload
        const payloadObj = JSON.parse(payload);
        const content = payloadObj.content;

        // Split content into chunks
        const chunks = await splitIntoChunks(content);
        
        core.info(`Content split into ${chunks.length} chunks for analysis`);

        // Analyze each chunk
        const results = [];
        for (let i = 0; i < chunks.length; i++) {
            core.info(`Analyzing chunk ${i + 1} of ${chunks.length}`);
            
            const chunkResult = await analyzeChunk({
                content: decode(chunks[i]),
                index: i,
                total: chunks.length
            }, openaiToken);
            
            results.push(chunkResult);

            // Se algum chunk já indicar BLOCK, podemos parar por aí
            if (chunkResult.includes('DECISION: BLOCK')) {
                core.warning('Security issue detected in chunk ' + (i + 1));
                core.setFailed(`Pipeline blocked by AI analysis:\n${chunkResult}`);
                return;
            }
        }

        // Se chegou aqui, todos os chunks foram OK
        core.info('All chunks analyzed successfully');
        core.setOutput('analysis', results.join('\n\n'));
        core.info('Pipeline approved by AI analysis');

    } catch (error) {
        core.setFailed(error.message);
        if (error.response) {
            console.error(error.response.data);
        }
    }
}

run();