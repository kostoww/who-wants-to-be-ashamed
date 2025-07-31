document.addEventListener('DOMContentLoaded', () => {
    const agentGrid = document.getElementById('agent-selection-grid');
    const resultPodium = document.getElementById('result-podium');

    // Podium Elements
    const podiumHeader = document.getElementById('podium-header');
    const podiumAgentName = document.getElementById('podium-agent-name');
    const podiumQuestion = document.getElementById('podium-question-text');
    const podiumAnswer = document.getElementById('podium-ai-answer');
    const podiumExplanation = document.getElementById('podium-ai-explanation');
    const podiumFooter = document.getElementById('podium-footer');
    const podiumResultText = document.getElementById('podium-result-text');

    async function loadAgents() {
        try {
            const response = await fetch('/api/agents/');
            if (!response.ok) throw new Error('Could not fetch agents.');
            const agents = await response.json();

            agentGrid.innerHTML = ''; // Clear loading state
            for (const agentKey in agents) {
                const agent = agents[agentKey];
                const card = document.createElement('div');
                card.className = 'col-md-6 col-lg-4';
                card.innerHTML = `
                    <div class="agent-card">
                        <h3 class="agent-name">${agent.name}</h3>
                        <p class="agent-description">${agent.description}</p>
                        <button class="btn btn-agent-action" data-agent-key="${agentKey}">
                            See Sample Answer
                        </button>
                    </div>
                `;
                agentGrid.appendChild(card);
            }
        } catch (error) {
            agentGrid.innerHTML = `<p class="text-danger text-center">${error.message}</p>`;
        }
    }

    agentGrid.addEventListener('click', async (event) => {
        if (!event.target.matches('.btn-agent-action')) return;

        const agentKey = event.target.dataset.agentKey;
        if (!agentKey) return;

        // Show podium and loading state
        resultPodium.classList.remove('d-none');
        podiumAgentName.textContent = 'FETCHING QUESTION...';
        podiumQuestion.textContent = '...';
        podiumAnswer.textContent = '';
        podiumExplanation.textContent = '';
        podiumFooter.className = 'podium-footer';
        podiumHeader.className = 'podium-header';
        podiumResultText.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>';


        try {
            const response = await fetch(`/api/agent-play/${agentKey}`, { method: 'POST' });
            if (!response.ok) throw new Error(`Failed to get response for ${agentKey}`);
            const result = await response.json();
            displayResult(result);
        } catch (error) {
            podiumResultText.textContent = 'Error!';
            podiumQuestion.textContent = error.message;
        }
    });

    function displayResult(result) {
        podiumAgentName.textContent = result.agent_name;
        podiumQuestion.textContent = result.question;
        podiumAnswer.textContent = result.ai_answer;
        podiumExplanation.textContent = result.ai_explanation;

        if (result.is_correct) {
            podiumResultText.textContent = 'CORRECT';
            podiumFooter.className = 'podium-footer correct';
            podiumHeader.className = 'podium-header correct';
        } else {
            podiumResultText.textContent = 'INCORRECT';
            podiumFooter.className = 'podium-footer incorrect';
            podiumHeader.className = 'podium-header incorrect';
        }
    }

    // Initial Load
    loadAgents();
});