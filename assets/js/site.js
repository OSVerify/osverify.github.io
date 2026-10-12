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

// Keep the News panel newest first, whatever order the items are written in.
document.querySelectorAll("ul.news-list").forEach((list) => {
  const date = (li) => li.querySelector("time[datetime]")?.getAttribute("datetime") || "";
  [...list.children].sort((a, b) => date(b).localeCompare(date(a))).forEach((li) => list.appendChild(li));
});
