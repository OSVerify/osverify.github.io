// Copy-to-clipboard for the BibTeX block.
document.querySelectorAll("button.copy").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const target = document.getElementById(btn.dataset.copy);
    if (!target) return;
    try {
      await navigator.clipboard.writeText(target.innerText.trim());
      btn.textContent = "Copied";
    } catch {
      btn.textContent = "Press ⌘C / Ctrl+C";
      const range = document.createRange();
      range.selectNodeContents(target);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
    }
    setTimeout(() => { btn.textContent = "Copy"; }, 1800);
  });
});
