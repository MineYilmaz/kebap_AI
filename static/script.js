const form = document.getElementById('idea-form');
const resultCard = document.getElementById('result');
const resultTitle = document.getElementById('result-title');
const resultSummary = document.getElementById('result-summary');

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const dish = document.getElementById('dish').value.trim() || 'kebab';
  const mood = document.getElementById('mood').value.trim() || 'fresh';

  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dish, mood }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Please try again later.');
    }

    resultTitle.textContent = data.title;
    resultSummary.textContent = data.summary;
  } catch (error) {
    resultTitle.textContent = 'Could not generate an idea';
    resultSummary.textContent = error.message || 'Please try again later.';
  } finally {
    resultCard.classList.remove('hidden');
  }
});
