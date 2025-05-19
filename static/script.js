async function generateAnimation() {
  const promptInput = document.getElementById("prompt");
  const prompt = promptInput.value.trim();
  const resultDiv = document.getElementById("result");
  const button = document.getElementById("generateBtn");

  if (!prompt) {
    resultDiv.innerHTML = '<p class="error">Please enter a prompt.</p>';
    return;
  }

  resultDiv.innerHTML = '<div class="spinner"></div>';
  button.disabled = true;

  try {
    const res = await fetch("/api/generate-animation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });

    if (!res.ok) {
      throw new Error(`HTTP error! Status: ${res.status}`);
    }

    const data = await res.json();

    if (data.error) {
      throw new Error(data.error);
    }

    const { videoUrl } = data;

    resultDiv.innerHTML = `
      <div class="download-icon" onclick="window.open('${videoUrl}', '_blank')"></div>
      <video controls>
        <source src="${videoUrl}" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    `;
  } catch (e) {
    resultDiv.innerHTML = `<p class="error">Error: ${e.message}</p>`;
    console.error(e);
  } finally {
    button.disabled = false;
  }
}
