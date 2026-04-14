const agents = [
  "Codex CLI",
  "Claude Code",
  "Cursor",
  "Gemini CLI",
  "OpenCode",
  "Kiro",
  "VS Code Copilot",
  "Antigravity",
];

const cases = [
  {
    id: "tech-hero",
    label: "Tech Hero",
    title: "Blue-purple tech hero, picked with depth",
    prompt:
      "Use $better-gradient and give me 3 blue-purple tech hero backgrounds. Prefer atmospheric depth and return the final CSS.",
    mode: "OKLAB",
    family: "blue-purple",
    name: "Dream Haze 梦霭",
    reasons: [
      "The brief names the blue-purple family directly, so the agent starts from a structured family instead of guessing.",
      "OKLAB is chosen because the target is a layered hero background rather than a short accent ramp.",
      "The output returns exact CSS, not just color adjectives.",
    ],
    css: "background: linear-gradient(135deg in oklab, #EBD5EB 0%, #A1BEE8 47.1%, #807BCA 100%);",
    preview: "linear-gradient(135deg, #EBD5EB 0%, #A1BEE8 47.1%, #807BCA 100%)",
  },
  {
    id: "airy-beauty",
    label: "Airy Beauty",
    title: "Skincare lightness, without bland pastels",
    prompt:
      "Use $better-gradient for a skincare landing page. Keep it airy and light, prefer oklch, and give me a production-ready ramp.",
    mode: "OKLCH",
    family: "light",
    name: "Pistachio Orchid Drift",
    reasons: [
      "The request maps to the light family through airy, skincare, and light cues.",
      "OKLCH keeps the short two-stop ramp clean and bright without muddy transitions.",
      "The chosen pair feels soft and premium instead of default pink-purple filler.",
    ],
    css: "background: linear-gradient(135deg in oklch, #C3FFC2 0%, #F0B3F5 100%);",
    preview: "linear-gradient(135deg, #C3FFC2 0%, #F0B3F5 100%)",
  },
  {
    id: "poster-cta",
    label: "Poster CTA",
    title: "High-contrast CTA with an explicit mode choice",
    prompt:
      "Use $better-gradient to find a bold poster CTA gradient. I want strong contrast, oklch only, and exact CSS.",
    mode: "OKLCH",
    family: "contrast",
    name: "Violet Lime Voltage",
    reasons: [
      "The prompt requests contrast as a family instead of relying on 'bold' alone.",
      "OKLCH is pinned explicitly because the desired result is a sharp, vivid, short ramp.",
      "The agent returns a single chosen preset plus portable fallback CSS.",
    ],
    css: "background: linear-gradient(135deg in oklch, #BA66FF 0%, #FCFF57 100%);",
    preview: "linear-gradient(135deg, #BA66FF 0%, #FCFF57 100%)",
  },
];

const families = [
  {
    name: "Red Yellow",
    cn: "红黄暖阳",
    summary: "Warm editorial ramps for sunrise, coral, peach, and sunset directions.",
    cues: ["sunset", "warm", "peach"],
    gradient: "linear-gradient(135deg, #B6D3EF 0%, #E8CCAF 39.9%, #F09050 62.5%, #F888A0 90.4%)",
  },
  {
    name: "Blue Purple",
    cn: "蓝紫夜空",
    summary: "Atmospheric cool gradients for AI products, tech heroes, and dreamier interfaces.",
    cues: ["tech", "cosmic", "blue-purple"],
    gradient: "linear-gradient(135deg, #EBD5EB 0%, #A1BEE8 47.1%, #807BCA 100%)",
  },
  {
    name: "Green Yellow",
    cn: "青绿春日",
    summary: "Fresh green-to-sky directions for wellness, travel, nature, and spring energy.",
    cues: ["fresh", "nature", "mint"],
    gradient: "linear-gradient(135deg, #EFEDAD 0%, #A7E1A7 26.9%, #3898EF 83.2%, #119AB8 100%)",
  },
  {
    name: "Contrast",
    cn: "高对比撞色",
    summary: "Punchier complementary ramps for poster work, fashion, music, and loud calls to action.",
    cues: ["bold", "poster", "contrast"],
    gradient: "linear-gradient(135deg, #FFD593 0%, #FFB48B 32.7%, #FF92DF 64.4%, #989BFF 100%)",
  },
  {
    name: "Dark",
    cn: "暗色电影感",
    summary: "Dense cinematic gradients for premium sections, nightlife moods, and darker launches.",
    cues: ["moody", "cinematic", "luxury"],
    gradient: "linear-gradient(135deg, #DEC4D1 0%, #878CB8 23%, #215C80 50%, #3D365C 72%, #210F17 100%)",
  },
  {
    name: "Light",
    cn: "浅色空气感",
    summary: "Airy pastel-leaning gradients for beauty, lifestyle, onboarding, and soft editorial moments.",
    cues: ["airy", "light", "skincare"],
    gradient: "linear-gradient(135deg, #FFD9C2 0%, #F5C7C4 22%, #D1BAE3 50%, #C2B8F0 80%, #D6A6F0 100%)",
  },
];

const agentList = document.getElementById("agent-list");
const exampleTabs = document.getElementById("example-tabs");
const familyGrid = document.getElementById("family-grid");

function renderAgents() {
  agentList.innerHTML = "";
  agents.forEach((agent) => {
    const li = document.createElement("li");
    li.textContent = agent;
    agentList.appendChild(li);
  });
}

function renderFamilies() {
  familyGrid.innerHTML = "";
  families.forEach((family) => {
    const article = document.createElement("article");
    article.className = "family-card";
    article.innerHTML = `
      <div class="family-strip" style="background:${family.gradient};"></div>
      <div class="family-content">
        <div class="family-head">
          <h3>${family.name}</h3>
          <div class="family-cn">${family.cn}</div>
        </div>
        <p>${family.summary}</p>
        <div class="chip-row">
          ${family.cues.map((cue) => `<span>${cue}</span>`).join("")}
        </div>
      </div>
    `;
    familyGrid.appendChild(article);
  });
}

function setCase(activeCase) {
  document.getElementById("after-title").textContent = activeCase.title;
  document.getElementById("after-prompt").textContent = activeCase.prompt;
  document.getElementById("after-mode").textContent = activeCase.mode;
  document.getElementById("after-name").textContent = activeCase.name;
  document.getElementById("after-family").textContent = `Family: ${activeCase.family}`;
  document.getElementById("after-css").textContent = activeCase.css;
  document.getElementById("after-preview").style.background = activeCase.preview;

  const reasonList = document.getElementById("after-reasons");
  reasonList.innerHTML = "";
  activeCase.reasons.forEach((reason) => {
    const li = document.createElement("li");
    li.textContent = reason;
    reasonList.appendChild(li);
  });

  Array.from(exampleTabs.querySelectorAll("button")).forEach((button) => {
    button.setAttribute("aria-selected", String(button.dataset.caseId === activeCase.id));
  });
}

function renderCases() {
  cases.forEach((item, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = item.label;
    button.dataset.caseId = item.id;
    button.setAttribute("role", "tab");
    button.setAttribute("aria-selected", String(index === 0));
    button.addEventListener("click", () => setCase(item));
    exampleTabs.appendChild(button);
  });

  setCase(cases[0]);
}

function wireCopyButtons() {
  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(button.dataset.copy);
        const previous = button.textContent;
        button.textContent = "Copied";
        window.setTimeout(() => {
          button.textContent = previous;
        }, 1400);
      } catch (error) {
        button.textContent = "Copy failed";
      }
    });
  });
}

renderAgents();
renderFamilies();
renderCases();
wireCopyButtons();
