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

// Relative dates in the News panel ("today", "3d ago", "2w ago"); older items keep the printed date.
document.querySelectorAll("time[data-relative]").forEach((el) => {
  // Count calendar days in the visitor's time zone, not elapsed 24-hour periods.
  const then = new Date(el.getAttribute("datetime") + "T00:00:00");
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const days = Math.round((today - then) / 86400000);
  if (Number.isNaN(days) || days < 0) return;
  const label = days === 0 ? "today" : days < 7 ? `${days}d ago` : days < 35 ? `${Math.floor(days / 7)}w ago` : null;
  if (label) {
    el.title = el.textContent;
    el.textContent = label;
  }
});
