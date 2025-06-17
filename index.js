const core = require('@actions/core');
const axios = require('axios');
const { encode } = require('gpt-3-encoder');

async function splitIntoChunks(text, maxTokens = 12000) {
    const tokens = encode(text);
    const chunks = [];
    let currentChunk = [];
    let currentLength = 0;

    for (const token of tokens) {
        if (currentLength + 1 > maxTokens) {
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

    return chunks;
}

async function analyzeChunk(chunk, openaiToken) {
    const response = await axios.post(
        'https://api.openai.com/v1/chat/completions',
        {
            model: 'gpt-4',
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
        const openaiToken = core.getInput('openai_token');
        const payload = core.getInput('payload');
        const maxTokensPerChunk = parseInt(core.getInput('max_tokens_per_chunk') || '12000');

        // Parse the payload
        const payloadObj = JSON.parse(payload);
        const content = payloadObj.content;

        // Split content into chunks
        const chunks = await splitIntoChunks(content, maxTokensPerChunk);
        
        core.info(`Content split into ${chunks.length} chunks for analysis`);

        // Analyze each chunk
        const results = [];
        for (let i = 0; i < chunks.length; i++) {
            core.info(`Analyzing chunk ${i + 1} of ${chunks.length}`);
            
            const chunkResult = await analyzeChunk({
                content: chunks[i],
                index: i,
                total: chunks.length
            }, openaiToken);
            
            results.push(chunkResult);
        }

        // Combine and analyze results
        const combinedAnalysis = await analyzeChunk({
            content: `Here are the analyses of all chunks:\n\n${results.join('\n\n')}`,
            index: 0,
            total: 1
        }, openaiToken);

        // Extract decision
        const decision = combinedAnalysis.match(/DECISION: (OK|BLOCK)/i);
        
        if (decision && decision[1].toUpperCase() === 'OK') {
            core.info('Pipeline approved by AI analysis');
            core.setOutput('analysis', combinedAnalysis);
        } else {
            core.setFailed(`Pipeline blocked by AI analysis:\n${combinedAnalysis}`);
        }

    } catch (error) {
        core.setFailed(error.message);
        if (error.response) {
            console.error(error.response.data);
        }
    }
}

run(); 