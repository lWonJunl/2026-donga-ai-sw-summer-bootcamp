const apiUrl = document.body.dataset.listUrl;
const form = document.querySelector("#api-form");
const categoryInput = document.querySelector("#api-category");
const languageInput = document.querySelector("#api-language");
const keywordInput = document.querySelector("#api-keyword");
const requestUrlView = document.querySelector("#api-request-url");
const responseView = document.querySelector("#api-response");
const statusView = document.querySelector("#api-status");
const countView = document.querySelector("#api-count");
const projectList = document.querySelector("#api-projects");

function displayText(value, language) {
  if (typeof value === "string") return value;
  return language === "en" ? value.en : value.ko;
}

function textElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = text;
  return element;
}

function renderProjects(projects, language) {
  projectList.replaceChildren();
  countView.textContent = String(projects.length);
  if (!projects.length) {
    projectList.append(textElement("p", "api-empty", "조건에 맞는 프로젝트가 없습니다."));
    return;
  }

  projects.forEach((project) => {
    const card = document.createElement("article");
    card.className = "api-card";
    const meta = document.createElement("div");
    meta.className = "api-card-meta";
    meta.append(textElement("span", "", project.category), textElement("span", "", project.year));
    const title = textElement("h3", "", displayText(project.title, language));
    const description = textElement("p", "", displayText(project.description, language));
    const tags = document.createElement("div");
    tags.className = "api-tags";
    project.technologies.forEach((value) => tags.append(textElement("span", "", value)));
    card.append(meta, title, description, tags);
    projectList.append(card);
  });
}

function fillCategories(categories) {
  if (categoryInput.options.length > 1) return;
  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    categoryInput.append(option);
  });
}

async function fetchProjects(redirectOnUnauthorized = false) {
  const url = new URL(apiUrl, window.location.origin);
  if (categoryInput.value) url.searchParams.set("category", categoryInput.value);
  if (keywordInput.value.trim()) url.searchParams.set("q", keywordInput.value.trim());
  url.searchParams.set("lang", languageInput.value);
  requestUrlView.textContent = `${url.pathname}${url.search}`;
  statusView.textContent = "요청 중...";
  form.querySelector("button").disabled = true;

  try {
    const response = await fetch(url, { headers: { Accept: "application/json" } });
    const payload = await response.json();
    if (response.status === 401) {
      if (redirectOnUnauthorized) {
        window.alert("로그인이 필요한 서비스입니다. 로그인 화면으로 이동합니다.");
        const next = encodeURIComponent(`${window.location.pathname}${window.location.search}`);
        window.location.assign(`${payload.login_url}?next=${next}&reason=authentication_required`);
        return;
      }
      statusView.textContent = "로그인 필요";
      responseView.textContent = JSON.stringify(payload, null, 2);
      renderProjects([], "ko");
      return;
    }
    responseView.textContent = JSON.stringify(payload, null, 2);
    if (!response.ok || !payload.success) throw new Error(payload.error || `HTTP ${response.status}`);
    fillCategories(payload.categories);
    renderProjects(payload.data, languageInput.value === "all" ? "ko" : languageInput.value);
    statusView.textContent = `HTTP ${response.status} · ${payload.count} records`;
  } catch (error) {
    statusView.textContent = "요청 실패";
    responseView.textContent = JSON.stringify({ success:false, error:error.message }, null, 2);
    renderProjects([], "ko");
  } finally {
    form.querySelector("button").disabled = false;
  }
}

form.addEventListener("submit", (event) => { event.preventDefault(); fetchProjects(true); });
fetchProjects();
