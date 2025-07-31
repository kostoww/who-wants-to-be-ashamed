document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const startScreen = document.getElementById('start-screen');
    const startGameBtn = document.getElementById('start-game-btn');
    const gameBoardView = document.getElementById('game-board-view');
    const gameBoardGrid = document.getElementById('game-board-grid');
    const scoreDisplay = document.getElementById('score-display');

    const clueModalElement = document.getElementById('clue-modal');
    const clueModal = new bootstrap.Modal(clueModalElement);
    const clueCategoryTitle = document.getElementById('clue-category');
    const clueTextDisplay = document.getElementById('clue-text');
    const answerInput = document.getElementById('answer-input');
    const submitAnswerBtn = document.getElementById('submit-answer-btn');
    const resultView = document.getElementById('result-view');
    const resultTitle = document.getElementById('result-title');
    const aiExplanation = document.getElementById('ai-explanation');
    const correctAnswerText = document.getElementById('correct-answer-text');
    const returnToBoardBtn = document.getElementById('return-to-board-btn');

    // --- Game State ---
    let score = 0;
    let currentClue = null;
    let currentRound = 'Jeopardy!'; // or 'Double Jeopardy!'

    // --- Event Listeners ---
    startGameBtn.addEventListener('click', () => initializeRound(currentRound));
    gameBoardGrid.addEventListener('click', handleClueClick);
    submitAnswerBtn.addEventListener('click', handleSubmitAnswer);
    returnToBoardBtn.addEventListener('click', () => clueModal.hide());

    // --- Functions ---
    async function initializeRound(roundName) {
        startScreen.classList.add('d-none');
        gameBoardView.classList.remove('d-none');
        gameBoardGrid.innerHTML = '<div class="spinner-border text-light" style="width: 5rem; height: 5rem; grid-column: 3 / 5; justify-self: center; align-self: center;" role="status"></div>';

        try {
            const response = await fetch(`/api/gameboard/${roundName}`);
            if (!response.ok) throw new Error('Failed to load game board.');
            const data = await response.json();
            buildGameBoard(data.categories);
        } catch (error) {
            gameBoardGrid.innerHTML = `<p class="text-danger">${error.message}</p>`;
        }
    }

    function buildGameBoard(categories) {
        gameBoardGrid.innerHTML = ''; // Clear spinner or old board
        const categoryNames = Object.keys(categories);

        // 1. Add category headers
        categoryNames.forEach(catName => {
            const catDiv = document.createElement('div');
            catDiv.className = 'category-header';
            catDiv.textContent = catName;
            gameBoardGrid.appendChild(catDiv);
        });

        // 2. Add clue boxes
        const values = [200, 400, 600, 800, 1000];
        if (currentRound === 'Double Jeopardy!') {
            values.forEach((v, i) => values[i] = v * 2);
        }

        for (let value of values) {
            for (let catName of categoryNames) {
                const clueBox = document.createElement('div');
                clueBox.className = 'clue-box';

                const clueData = categories[catName]?.find(c => c.value === value);

                if (clueData) {
                    clueBox.dataset.questionId = clueData.question_id;
                    clueBox.dataset.question = clueData.question;
                    clueBox.dataset.answer = clueData.answer;
                    clueBox.dataset.value = clueData.value;
                    clueBox.dataset.category = catName;

                    const valueDiv = document.createElement('div');
                    valueDiv.className = 'value';
                    valueDiv.textContent = `$${clueData.value}`;
                    clueBox.appendChild(valueDiv);
                } else {
                    clueBox.classList.add('answered');
                    clueBox.innerHTML = '<div class="value">–</div>';
                }
                gameBoardGrid.appendChild(clueBox);
            }
        }
    }

    function handleClueClick(event) {
        const clueBox = event.target.closest('.clue-box');
        if (!clueBox || clueBox.classList.contains('answered')) return;

        currentClue = {
            element: clueBox,
            id: clueBox.dataset.questionId,
            question: clueBox.dataset.question,
            answer: clueBox.dataset.answer,
            value: parseInt(clueBox.dataset.value),
            category: clueBox.dataset.category
        };

        // Populate and show the modal
        clueCategoryTitle.textContent = currentClue.category;
        clueTextDisplay.textContent = currentClue.question;

        // Reset modal state
        resultView.classList.add('d-none');
        answerInput.value = '';
        answerInput.disabled = false;
        submitAnswerBtn.classList.remove('d-none');

        clueModal.show();
    }

    async function handleSubmitAnswer() {
        const userAnswer = answerInput.value;
        if (!userAnswer) return;

        answerInput.disabled = true;
        submitAnswerBtn.classList.add('d-none');

        try {
            const response = await fetch('/api/verify-answer/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question_id: parseInt(currentClue.id),
                    user_answer: userAnswer,
                }),
            });
            const result = await response.json();
            showResult(result.is_correct, result.ai_response);

        } catch (error) {
            showResult(false, 'Error connecting to the verification service.');
        }
    }

    function showResult(isCorrect, explanation) {
        resultView.classList.remove('d-none');

        if (isCorrect) {
            resultTitle.textContent = 'Correct!';
            resultTitle.className = 'result-title correct';
            updateScore(currentClue.value);
        } else {
            resultTitle.textContent = 'Incorrect';
            resultTitle.className = 'result-title incorrect';
            updateScore(-currentClue.value);
        }

        aiExplanation.textContent = explanation;
        correctAnswerText.textContent = currentClue.answer;

        // Mark the clue as answered on the board
        currentClue.element.classList.add('answered');
    }

    function updateScore(amount) {
        score += amount;
        scoreDisplay.textContent = `$${score}`;
        scoreDisplay.style.color = score < 0 ? '#dc3545' : 'var(--jeopardy-gold)';
    }
});