/* ===================================================
   CareerAI — resume.js
   Handles drag-and-drop upload, file validation,
   preview, and form submission loading state
   =================================================== */

const uploadZone = document.getElementById("uploadZone");
const resumeInput = document.getElementById("resumeInput");
const filePreview = document.getElementById("filePreview");
const fileNameEl = document.getElementById("fileName");
const analyzeBtn = document.getElementById("analyzeBtn");
const btnText = document.getElementById("btnText");
const btnLoader = document.getElementById("btnLoader");
const uploadForm = document.getElementById("uploadForm");

const MAX_SIZE_MB = 5;
const ALLOWED_EXTS = ["pdf", "docx", "doc"];

// ─── Drag & Drop Handlers ────────────────────────────
function handleDragOver(e) {
  e.preventDefault();
  e.stopPropagation();
  uploadZone.classList.add("drag-over");
}

function handleDragLeave(e) {
  e.preventDefault();
  uploadZone.classList.remove("drag-over");
}

function handleDrop(e) {
  e.preventDefault();
  e.stopPropagation();
  uploadZone.classList.remove("drag-over");

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    processFile(files[0]);
  }
}

// ─── File Input Change ───────────────────────────────
function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) processFile(file);
}

// ─── Process Selected File ───────────────────────────
function processFile(file) {
  // Validate extension
  const ext = file.name.split(".").pop().toLowerCase();
  if (!ALLOWED_EXTS.includes(ext)) {
    showFileError(
      `❌ Invalid file type ".${ext}". Please upload a PDF or DOCX file.`,
    );
    return;
  }

  // Validate size
  const sizeMB = file.size / (1024 * 1024);
  if (sizeMB > MAX_SIZE_MB) {
    showFileError(
      `❌ File too large (${sizeMB.toFixed(1)} MB). Maximum allowed is ${MAX_SIZE_MB} MB.`,
    );
    return;
  }

  // Assign dropped file to input manually
  try {
    const dt = new DataTransfer();
    dt.items.add(file);
    resumeInput.files = dt.files;
  } catch (err) {
    console.log("DataTransfer not supported");
  }

  // Show preview
  showFilePreview(file.name, sizeMB);
}

// ─── Show File Preview ───────────────────────────────
function showFilePreview(name, sizeMB) {
  if (fileNameEl) fileNameEl.textContent = `${name} (${sizeMB.toFixed(2)} MB)`;
  if (filePreview) filePreview.classList.remove("hidden");

  // Hide the upload prompt text
  const uploadTexts = uploadZone.querySelectorAll("h3, p:not(.upload-hint)");
  uploadTexts.forEach((el) => (el.style.opacity = "0.4"));

  // Enable the analyze button
  if (analyzeBtn) analyzeBtn.disabled = false;
}

// ─── Clear File Selection ────────────────────────────
function clearFile() {
  if (resumeInput) resumeInput.value = "";
  if (filePreview) filePreview.classList.add("hidden");
  if (analyzeBtn) analyzeBtn.disabled = true;

  // Restore upload zone text
  const uploadTexts = uploadZone.querySelectorAll("h3, p:not(.upload-hint)");
  uploadTexts.forEach((el) => (el.style.opacity = "1"));

  uploadZone.classList.remove("drag-over");
}

// ─── Show Error Message ──────────────────────────────
function showFileError(message) {
  clearFile();

  // Remove existing error if any
  const existing = document.getElementById("fileError");
  if (existing) existing.remove();

  const errDiv = document.createElement("div");
  errDiv.id = "fileError";
  errDiv.style.cssText = `
    margin-top: 0.75rem;
    padding: 0.6rem 1rem;
    background: rgba(255,68,68,0.1);
    border: 1px solid rgba(255,68,68,0.3);
    border-radius: 8px;
    color: #ff8888;
    font-size: 0.85rem;
  `;
  errDiv.textContent = message;
  uploadZone.insertAdjacentElement("afterend", errDiv);

  // Auto-remove after 4 seconds
  setTimeout(() => errDiv.remove(), 4000);
}

// ─── Form Submit Loading State ───────────────────────
if (uploadForm) {
  uploadForm.addEventListener("submit", (e) => {
    // Validate file is selected
    if (!resumeInput || !resumeInput.files.length) {
      e.preventDefault();
      showFileError("Please select a resume file first.");
      return;
    }

    // Show loading state
    if (btnText) btnText.classList.add("hidden");
    if (btnLoader) btnLoader.classList.remove("hidden");
    if (analyzeBtn) {
      analyzeBtn.disabled = true;
      analyzeBtn.style.opacity = "0.8";
    }
  });
}

// ─── Click Upload Zone ───────────────────────────────
// The file input covers the zone absolutely, so clicking anywhere triggers it.
// This handler adds visual feedback.
if (uploadZone) {
  uploadZone.addEventListener("click", () => {
    uploadZone.classList.add("drag-over");

    setTimeout(() => {
      uploadZone.classList.remove("drag-over");
    }, 300);
  });
}

// ─── Animate Analysis Bars on Result Page ────────────
// (bars are animated by main.js but here we add color-coding)
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".breakdown-item").forEach((item) => {
    const fill = item.querySelector(".mini-fill");
    const pts = item.querySelector(".breakdown-pts");
    if (!fill || !pts) return;

    const widthPct = parseFloat(fill.style.width);
    if (widthPct >= 70) {
      fill.style.background = "linear-gradient(90deg, #00ff88, #00d4a0)";
    } else if (widthPct >= 40) {
      fill.style.background = "linear-gradient(90deg, #ffd700, #fb923c)";
    } else {
      fill.style.background = "linear-gradient(90deg, #ff6868, #ff4444)";
    }
  });
});
