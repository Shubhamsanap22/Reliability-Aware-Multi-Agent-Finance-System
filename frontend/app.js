"use strict";

const API_BASE = "/api";

const state = {
    currentExecution: null,
    history: [],
    health: null,
    selectedAgent: null,
    busy: false,
    charts: []
};

const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function number(value) {
    const n = Number(value);
    return Number.isFinite(n) ? n.toLocaleString() : "—";
}

function statusValue(value) {
    return String(value?.value ?? value ?? "unknown").toLowerCase();
}

function statusTag(status) {
    const value = statusValue(status);
    const cls = value === "completed" ? "tag-success"
        : value === "failed" ? "tag-danger"
        : value === "replaced" ? "tag-warning"
        : "tag-neutral";

    return `<span class="tag ${cls}">${escapeHTML(value.toUpperCase())}</span>`;
}

function toast(message) {
    const container = $("#toastContainer");
    if (!container) return;

    const node = document.createElement("div");
    node.className = "toast";
    node.textContent = message;
    container.appendChild(node);

    window.setTimeout(() => node.remove(), 4000);
}

async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    const raw = await response.text();
    let data = {};

    try {
        data = raw ? JSON.parse(raw) : {};
    } catch {
        throw new Error("The API returned an invalid response.");
    }

    if (!response.ok) {
        throw new Error(
            data.detail || data.message || `API error ${response.status}`
        );
    }

    return data;
}

function getReport(execution) {
    return execution?.report || {};
}

function getResults(execution) {
    return Array.isArray(execution?.results) ? execution.results : [];
}

function getBudget(execution) {
    return execution?.budget || {};
}

function navigate(page) {
    $$(".page").forEach(section => {
        section.classList.toggle("active", section.id === `page-${page}`);
    });

    $$(".nav-item[data-page]").forEach(button => {
        button.classList.toggle("active", button.dataset.page === page);
    });

    const activeButton = $(`.nav-item[data-page="${page}"]`);
    const breadcrumb = $("#breadcrumbPage");

    if (breadcrumb) {
        breadcrumb.textContent =
            activeButton?.querySelector("span")?.textContent || page;
    }

    closeMobileSidebar();

    window.scrollTo({ top: 0, behavior: "smooth" });

    if (page === "history") loadHistory();
    if (page === "settings") renderSettings();
}

function showConnection(online, message) {
    const dotClass = online ? "online" : "offline";

    ["#connectionDot", "#topStatusDot"].forEach(selector => {
        const element = $(selector);
        if (element) element.className = `status-dot ${dotClass}`;
    });

    if ($("#connectionLabel")) {
        $("#connectionLabel").textContent =
            online ? "Backend connected" : "Backend offline";
    }

    if ($("#connectionCaption")) {
        $("#connectionCaption").textContent = message;
    }

    if ($("#topStatusText")) {
        $("#topStatusText").textContent =
            online ? "API connected" : "API unavailable";
    }

    if ($("#settingsApiStatus")) {
        $("#settingsApiStatus").textContent =
            online ? "CONNECTED" : "OFFLINE";
        $("#settingsApiStatus").className =
            `tag ${online ? "tag-success" : "tag-danger"}`;
    }

    if ($("#settingsConnectionText")) {
        $("#settingsConnectionText").textContent = message;
    }
}

async function checkHealth() {
    try {
        const health = await apiRequest("/health");
        state.health = health;
        showConnection(
            true,
            health.message || "FastAPI service is responding."
        );
        renderSettings();
        return true;
    } catch (error) {
        state.health = null;
        showConnection(
            false,
            error.message || "Could not connect to the API."
        );
        return false;
    }
}

function emptyMarkup(title, description) {
    return `
        <div class="empty-state">
            <div class="empty-icon"><i data-lucide="layers-3"></i></div>
            <h3>${escapeHTML(title)}</h3>
            <p>${escapeHTML(description)}</p>
        </div>
    `;
}

function detailRow(label, value) {
    return `
        <div class="detail-row">
            <span>${escapeHTML(label)}</span>
            <strong>${value}</strong>
        </div>
    `;
}

function formatBudget(execution) {
    const budget = getBudget(execution);
    const total = Number(budget.global_budget || 0);
    const used = Number(budget.used_budget || 0);
    const fraction = total > 0 ? Math.min(1, used / total) : 0;

    return `
        <div class="mini-metrics">
            <div class="mini-metric">
                <span>Global budget</span><strong>${number(total)}</strong>
            </div>
            <div class="mini-metric">
                <span>Allocated</span>
                <strong>${number(budget.allocated_budget)}</strong>
            </div>
            <div class="mini-metric">
                <span>Used</span><strong>${number(used)}</strong>
            </div>
            <div class="mini-metric">
                <span>Remaining</span>
                <strong>${number(
                    budget.remaining_budget ?? Math.max(0, total - used)
                )}</strong>
            </div>
        </div>
        <div class="progress-track">
            <div class="progress-fill" style="width:${fraction * 100}%"></div>
        </div>
        <div class="progress-caption">
            <span>Budget utilization</span>
            <span>${(fraction * 100).toFixed(1)}%</span>
        </div>
    `;
}

function renderOverview() {
    const history = state.history;
    const latest = state.currentExecution || history[0] || null;

    $("#metricExecutions").textContent = number(history.length);

    const allResults = history.flatMap(getResults);

    $("#metricCompleted").textContent = number(
        allResults.filter(
            item => statusValue(item.status) === "completed"
        ).length
    );

    $("#metricFailed").textContent = number(
        allResults.filter(
            item => statusValue(item.status) === "failed"
        ).length
    );

    if (!latest) {
        $("#metricBudget").textContent = "—";
        $("#metricBudgetFoot").textContent = "Run an analysis to view usage";
        $("#latestStatus").textContent = "NO RUN";

        $("#recentExecutions").innerHTML = emptyMarkup(
            "No executions yet",
            "Run a financial query to populate the dashboard."
        );

        $("#latestSummary").innerHTML = emptyMarkup(
            "Waiting for results",
            "The latest execution summary will appear here."
        );

        $("#overviewAgents").innerHTML = emptyMarkup(
            "No agent activity",
            "Agent statuses will appear after execution."
        );

        return;
    }

    const report = getReport(latest);
    const budget = getBudget(latest);

    $("#metricBudget").textContent = number(budget.used_budget);
    $("#metricBudgetFoot").textContent =
        `of ${number(budget.global_budget)} tokens`;

    $("#latestStatus").textContent =
        String(report.overall_status || "unknown").toUpperCase();

    $("#latestStatus").className =
        `tag ${
            report.overall_status === "completed"
                ? "tag-success"
                : report.overall_status === "failed"
                    ? "tag-danger"
                    : "tag-neutral"
        }`;

    $("#latestSummary").innerHTML = `
        <div class="detail-list">
            ${detailRow("Overall status", escapeHTML(report.overall_status || "unknown"))}
            ${detailRow("Total agents", number(report.total_agents))}
            ${detailRow("Completed", number(report.completed_agents))}
            ${detailRow("Failed", number(report.failed_agents))}
            ${detailRow("Incomplete", number(report.incomplete_agents))}
        </div>
        <p class="result-output" style="margin-top:14px">
            ${escapeHTML(report.summary || report.executive_summary || "No summary returned.")}
        </p>
    `;

    $("#recentExecutions").innerHTML = `
        <div class="table-wrap">
            <table>
                <thead><tr><th>Query</th><th>Status</th><th>Agents</th><th>Used</th></tr></thead>
                <tbody>
                    ${history.slice(0, 5).map(item => {
                        const r = getReport(item);
                        const b = getBudget(item);
                        return `
                            <tr>
                                <td>${escapeHTML(item.query || "—")}</td>
                                <td>${statusTag(r.overall_status)}</td>
                                <td>${number(r.total_agents)}</td>
                                <td>${number(b.used_budget)}</td>
                            </tr>
                        `;
                    }).join("")}
                </tbody>
            </table>
        </div>
    `;

    $("#overviewAgents").innerHTML = renderAgentCards(getResults(latest));
}

function renderUnderstanding(execution) {
    const requirement = execution?.requirement || {};
    const capabilities = requirement.required_capabilities || [];
    const symbols = requirement.symbols || [];

    const fields = [
        ["Capabilities", capabilities.length
            ? capabilities.map(x => String(x).replace(/_/g, " ")).join(", ")
            : "None identified"],
        ["Symbols", symbols.length ? symbols.join(", ") : "Not identified"],
        ["Risk preference", requirement.risk_preference || "Not specified"],
        ["Initial amount", requirement.initial_amount ?? "Not specified"],
        ["Target amount", requirement.target_amount ?? "Not specified"],
        ["Planning horizon", requirement.years ? `${requirement.years} years` : "Not specified"],
        ["Annual return assumption", requirement.annual_return ?? "Not specified"]
    ];

    $("#queryUnderstanding").innerHTML = `
        <div class="detail-list">
            ${fields.map(([label, value]) =>
                detailRow(label, escapeHTML(value))
            ).join("")}
        </div>
    `;
}

function renderQueryPage(execution) {
    if (!execution) return;

    const report = getReport(execution);
    const charts = Array.isArray(report.charts) ? report.charts : [];
    const findings = Array.isArray(report.key_findings)
        ? report.key_findings
        : (Array.isArray(report.findings)
            ? report.findings.map(item => item.output || "")
            : []);

    const risks = Array.isArray(report.risks) ? report.risks : report.limitations || [];
    const recommendations = Array.isArray(report.recommendations)
        ? report.recommendations
        : [];

    renderUnderstanding(execution);
    destroyCharts();

    const summary = report.summary || report.executive_summary ||
        "No consolidated summary was returned.";

    const chartMarkup = charts.length
        ? charts.map((chart, index) => `
            <article class="chart-card">
                <div class="panel-heading">
                    <div>
                        <h3>${escapeHTML(chart.title || "Analysis chart")}</h3>
                        <p>${escapeHTML(chart.note || "")}</p>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="finmas-chart-${index}"></canvas>
                </div>
            </article>
        `).join("")
        : emptyMarkup(
            "No chart available",
            "A chart is displayed only when the returned data supports one."
        );

    $("#findingCount").textContent =
        `${findings.length} FINDINGS`;

    $("#queryFindings").innerHTML = `
        <section class="report-summary">
            <div class="report-section-heading">
                <span class="tag tag-success">CONSOLIDATED REPORT</span>
                <h3>Summary</h3>
            </div>
            <div class="result-output report-prose">
                ${String(summary).split(/\n\s*\n/).filter(Boolean)
                    .map(paragraph => `<p>${escapeHTML(paragraph)}</p>`)
                    .join("")}
            </div>
        </section>

        ${findings.length ? `
            <section class="report-section">
                <h3>Key findings</h3>
                <ul>${findings.map(item =>
                    `<li>${escapeHTML(typeof item === "string" ? item : JSON.stringify(item))}</li>`
                ).join("")}</ul>
            </section>
        ` : ""}

        ${recommendations.length ? `
            <section class="report-section">
                <h3>Recommendations</h3>
                <ul>${recommendations.map(item =>
                    `<li>${escapeHTML(item)}</li>`
                ).join("")}</ul>
            </section>
        ` : ""}

        ${risks.length ? `
            <section class="report-section">
                <h3>Risks and limitations</h3>
                <ul>${risks.map(item =>
                    `<li>${escapeHTML(item)}</li>`
                ).join("")}</ul>
            </section>
        ` : ""}

        <section class="report-section">
            <h3>Charts and visual analysis</h3>
            <div class="report-charts">${chartMarkup}</div>
        </section>
    `;

    charts.forEach((chart, index) => {
        renderChart(`finmas-chart-${index}`, chart);
    });

    $("#querySummary").innerHTML = `
        <div class="detail-list">
            ${detailRow("Status", escapeHTML(report.overall_status || "unknown"))}
            ${detailRow("Total agents", number(report.total_agents))}
            ${detailRow("Completed", number(report.completed_agents))}
            ${detailRow("Failed", number(report.failed_agents))}
        </div>
    `;

    $("#queryBudget").innerHTML = formatBudget(execution);
}

function destroyCharts() {
    state.charts.forEach(chart => {
        try {
            chart.destroy();
        } catch {
            // Ignore an already-destroyed chart instance.
        }
    });
    state.charts = [];
}

function renderChart(canvasId, spec) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !window.Chart) return;

    const data = Array.isArray(spec.data) ? spec.data : [];
    if (!data.length) return;

    const type = String(spec.type || "").toLowerCase();
    const supportedTypes = ["pie", "doughnut", "line", "bar", "scatter"];

    if (!supportedTypes.includes(type)) return;

    let chartData;
    let options = {
        responsive: true,
        maintainAspectRatio: false
    };

    if (type === "pie" || type === "doughnut") {
        chartData = {
            labels: data.map(point => point.label),
            datasets: [{
                label: spec.title || "Allocation",
                data: data.map(point => Number(point.value))
            }]
        };
        options.plugins = {
            legend: { position: "bottom" }
        };
    } else if (type === "scatter") {
        chartData = {
            datasets: [{
                label: spec.title || "Risk vs return",
                data: data.map(point => ({
                    x: Number(point.x),
                    y: Number(point.y)
                }))
            }]
        };
        options.scales = {
            x: { title: { display: true, text: spec.x_label || "Risk" } },
            y: { title: { display: true, text: spec.y_label || "Return" } }
        };
    } else {
        chartData = {
            labels: data.map(point => point.x ?? point.label),
            datasets: [{
                label: spec.y_label || spec.title || "Value",
                data: data.map(point => Number(point.y ?? point.value)),
                tension: type === "line" ? 0.25 : 0
            }]
        };
        options.plugins = {
            legend: { position: "bottom" }
        };
        options.scales = {
            x: { title: { display: Boolean(spec.x_label), text: spec.x_label || "" } },
            y: { title: { display: Boolean(spec.y_label), text: spec.y_label || "" } }
        };
    }

    state.charts.push(new Chart(canvas, {
        type,
        data: chartData,
        options
    }));
}

function renderAgentCards(results) {
    if (!results.length) {
        return emptyMarkup("No agents", "No agent execution results are available.");
    }

    return results.map(agent => `
        <article class="agent-card">
            <div class="panel-heading">
                <h3>${escapeHTML(agent.agent_name)}</h3>
                ${statusTag(agent.status)}
            </div>
            <div class="detail-list">
                ${detailRow("Reliability", escapeHTML(Number(agent.reliability || 0).toFixed(2)))}
                ${detailRow("Allocated budget", number(agent.allocated_budget))}
                ${detailRow("Used budget", number(agent.used_budget))}
            </div>
        </article>
    `).join("");
}

function renderAgents(execution) {
    const results = getResults(execution);

    $("#agentTotal").textContent = number(results.length);
    $("#agentCompleted").textContent = number(
        results.filter(x => statusValue(x.status) === "completed").length
    );
    $("#agentFailed").textContent = number(
        results.filter(x => statusValue(x.status) === "failed").length
    );

    $("#agentTable").innerHTML = results.length ? `
        <table>
            <thead>
                <tr><th>Agent</th><th>Status</th><th>Reliability</th><th>Allocated</th><th>Used</th><th>Output</th></tr>
            </thead>
            <tbody>
                ${results.map((agent, index) => `
                    <tr class="agent-row" data-agent-index="${index}" tabindex="0">
                        <td>${escapeHTML(agent.agent_name)}</td>
                        <td>${statusTag(agent.status)}</td>
                        <td>${Number(agent.reliability || 0).toFixed(2)}</td>
                        <td>${number(agent.allocated_budget)}</td>
                        <td>${number(agent.used_budget)}</td>
                        <td>${escapeHTML(String(agent.output || agent.failure_reason || "").slice(0, 120))}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    ` : emptyMarkup("No agent data", "Run a query to view agent performance.");

    $$(".agent-row").forEach(row => {
        const selectAgent = () => {
            const agent = results[Number(row.dataset.agentIndex)];
            state.selectedAgent = agent;
            renderAgentInspector(agent);
        };
        row.addEventListener("click", selectAgent);
        row.addEventListener("keydown", event => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                selectAgent();
            }
        });
    });

    renderAgentInspector(state.selectedAgent);
}

function renderAgentInspector(agent) {
    if (!agent) {
        $("#agentInspector").innerHTML = emptyMarkup(
            "No agent selected",
            "Select an agent row to inspect its output."
        );
        return;
    }

    $("#agentInspector").innerHTML = `
        <article class="result-card">
            <div class="panel-heading">
                <h3>${escapeHTML(agent.agent_name)}</h3>
                ${statusTag(agent.status)}
            </div>
            <div class="detail-list">
                ${detailRow("Reliability", escapeHTML(Number(agent.reliability || 0).toFixed(2)))}
                ${detailRow("Allocated budget", number(agent.allocated_budget))}
                ${detailRow("Used budget", number(agent.used_budget))}
                ${detailRow("Remaining budget", number(agent.remaining_agent_budget))}
            </div>
            <h4>Output</h4>
            <pre class="result-output">${escapeHTML(agent.output || "No output returned.")}</pre>
            ${agent.failure_reason ? `
                <h4>Failure reason</h4>
                <p>${escapeHTML(agent.failure_reason)}</p>
            ` : ""}
        </article>
    `;
}

function renderWorkflow(execution) {
    const results = getResults(execution);

    const stages = [
        ["Query received", Boolean(execution?.query)],
        ["Requirements extracted", Boolean(execution?.requirement)],
        ["Agent execution", results.length > 0],
        ["Results aggregated", Boolean(execution?.report)],
        ["Consolidated report", Boolean(execution?.report?.summary)]
    ];

    $("#workflowStages").innerHTML = `
        <div class="workflow-stages">
            ${stages.map(([label, complete], index) => `
                <div class="workflow-stage">
                    <span class="workflow-stage-number">${index + 1}</span>
                    <div>
                        <strong>${escapeHTML(label)}</strong>
                        <p>${complete ? "Data available" : "Not reported"}</p>
                    </div>
                    ${statusTag(complete ? "completed" : "incomplete")}
                </div>
            `).join("")}
        </div>
    `;

    $("#workflowAgents").innerHTML = results.length
        ? results.map(agent => `
            <article class="result-card">
                <div class="panel-heading">
                    <h3>${escapeHTML(agent.agent_name)}</h3>
                    ${statusTag(agent.status)}
                </div>
                <p class="result-output">${escapeHTML(
                    agent.failure_reason || agent.output || "No output returned."
                )}</p>
            </article>
        `).join("")
        : emptyMarkup("No workflow data", "Run a query to inspect execution states.");
}

function renderRecovery(execution) {
    const results = getResults(execution);
    const failed = results.filter(x => statusValue(x.status) === "failed");
    const replaced = results.filter(x => statusValue(x.status) === "replaced");
    const incomplete = results.filter(
        x => !["completed", "failed", "replaced"].includes(statusValue(x.status))
    );

    $("#failureCount").textContent = number(failed.length);
    $("#replacedCount").textContent = number(replaced.length);
    $("#incompleteCount").textContent = number(incomplete.length);

    $("#failureList").innerHTML = failed.length
        ? failed.map(agent => `
            <article class="failure-card">
                <div class="panel-heading">
                    <h3>${escapeHTML(agent.agent_name)}</h3>
                    ${statusTag(agent.status)}
                </div>
                <p class="result-output">${escapeHTML(agent.failure_reason || "No failure reason provided.")}</p>
            </article>
        `).join("")
        : emptyMarkup("No failed agents", "The latest execution reported no failed agents.");

    $("#recoveryList").innerHTML = replaced.length
        ? replaced.map(agent => `
            <article class="result-card">
                <div class="panel-heading">
                    <h3>${escapeHTML(agent.agent_name)}</h3>
                    ${statusTag(agent.status)}
                </div>
                <p>${escapeHTML(agent.failure_reason || "A replaced status was reported.")}</p>
            </article>
        `).join("")
        : emptyMarkup("No replacements reported", "No replacement status was returned.");
}

function renderHistory() {
    const history = state.history;
    $("#historyCount").textContent = `${history.length} RUNS`;

    if (!history.length) {
        $("#historyTable").innerHTML = emptyMarkup(
            "No execution history",
            "Submit a query to create a history entry."
        );
        return;
    }

    $("#historyTable").innerHTML = `
        <table>
            <thead>
                <tr><th>#</th><th>Query</th><th>Status</th><th>Agents</th><th>Completed</th><th>Failed</th><th>Budget used</th></tr>
            </thead>
            <tbody>
                ${history.map((item, index) => {
                    const report = getReport(item);
                    const budget = getBudget(item);
                    return `
                        <tr>
                            <td>${history.length - index}</td>
                            <td>${escapeHTML(item.query || "—")}</td>
                            <td>${statusTag(report.overall_status)}</td>
                            <td>${number(report.total_agents)}</td>
                            <td>${number(report.completed_agents)}</td>
                            <td>${number(report.failed_agents)}</td>
                            <td>${number(budget.used_budget)}</td>
                        </tr>
                    `;
                }).join("")}
            </tbody>
        </table>
    `;
}

function renderSettings() {
    $("#apiEndpointLabel").textContent = `${location.origin}${API_BASE}`;

    const execution = state.currentExecution;
    if (execution?.budget) {
        $("#settingsBudget").innerHTML = formatBudget(execution);
    }

    if (state.health?.data_source) {
        $("#settingsDataSource").innerHTML = `
            <div class="detail-list">
                ${Object.entries(state.health.data_source).map(([key, value]) =>
                    detailRow(key, escapeHTML(value))
                ).join("")}
            </div>
        `;
    } else {
        $("#settingsDataSource").innerHTML = `
            <div class="notice notice-info">
                <strong>Data-source status unavailable</strong>
                <p>The health endpoint does not currently provide data-source diagnostics.</p>
            </div>
        `;
    }
}

function renderAll() {
    renderOverview();
    renderQueryPage(state.currentExecution);
    renderAgents(state.currentExecution);
    renderWorkflow(state.currentExecution);
    renderRecovery(state.currentExecution);
    renderHistory();
    renderSettings();

    if (window.lucide) window.lucide.createIcons();
}

async function runQuery() {
    const query = $("#queryInput").value.trim();
    const button = $("#runQueryButton");
    const errorBox = $("#queryError");

    errorBox.classList.add("hidden");

    if (!query) {
        errorBox.textContent = "Enter a financial query before running the analysis.";
        errorBox.classList.remove("hidden");
        return;
    }

    if (state.busy) return;

    state.busy = true;
    button.disabled = true;
    button.innerHTML = '<i data-lucide="loader-circle"></i> Running analysis...';

    if (window.lucide) window.lucide.createIcons();

    try {
        const result = await apiRequest("/query", {
            method: "POST",
            body: JSON.stringify({ query })
        });

        state.currentExecution = result;

        // API history is newest-first. Avoid duplicating the same run.
        state.history = [
            result,
            ...state.history.filter(item =>
                !(item.query === result.query && item === result)
            )
        ];

        renderAll();
        toast("Analysis completed. Review the consolidated report.");
    } catch (error) {
        errorBox.textContent = error.message || "The query could not be executed.";
        errorBox.classList.remove("hidden");
        toast("Analysis failed. Check the API and backend logs.");
    } finally {
        state.busy = false;
        button.disabled = false;
        button.innerHTML = '<i data-lucide="play"></i> Run analysis';
        if (window.lucide) window.lucide.createIcons();
    }
}

async function loadHistory() {
    try {
        const response = await apiRequest("/history");

        if (Array.isArray(response.items)) {
            state.history = response.items;

            if (!state.currentExecution && state.history.length) {
                state.currentExecution = state.history[0];
            }

            renderAll();
        }
    } catch {
        renderHistory();
    }
}

function toCSV(rows) {
    if (!rows.length) return "";

    const columns = [...new Set(rows.flatMap(row => Object.keys(row)))];
    const quote = value =>
        `"${String(value ?? "").replace(/"/g, '""')}"`;

    return [
        columns.map(quote).join(","),
        ...rows.map(row =>
            columns.map(column => quote(row[column])).join(",")
        )
    ].join("\r\n");
}

function downloadCSV(filename, rows) {
    if (!rows.length) {
        toast("There is no data to export yet.");
        return;
    }

    const blob = new Blob(["\uFEFF", toCSV(rows)], {
        type: "text/csv;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

function exportAgents() {
    const rows = getResults(state.currentExecution).map(agent => ({
        agent_name: agent.agent_name,
        status: statusValue(agent.status),
        reliability: agent.reliability,
        allocated_budget: agent.allocated_budget,
        used_budget: agent.used_budget,
        remaining_agent_budget: agent.remaining_agent_budget,
        output: agent.output,
        failure_reason: agent.failure_reason
    }));

    downloadCSV("finmas_agents.csv", rows);
}

function exportHistory() {
    const rows = state.history.map(item => {
        const report = getReport(item);
        const budget = getBudget(item);

        return {
            query: item.query,
            overall_status: report.overall_status,
            total_agents: report.total_agents,
            completed_agents: report.completed_agents,
            failed_agents: report.failed_agents,
            allocated_budget: budget.allocated_budget,
            used_budget: budget.used_budget
        };
    });

    downloadCSV("finmas_history.csv", rows);
}

function closeMobileSidebar() {
    $("#sidebar").classList.remove("open");
    $("#mobileOverlay").classList.remove("show");
}

function setupEvents() {
    $$(".nav-item[data-page]").forEach(button => {
        button.addEventListener("click", () => navigate(button.dataset.page));
    });

    $$("[data-goto]").forEach(button => {
        button.addEventListener("click", () => navigate(button.dataset.goto));
    });

    $$(".example-chip").forEach(button => {
        button.addEventListener("click", () => {
            $("#queryInput").value = button.dataset.query;
            $("#characterCount").textContent =
                `${button.dataset.query.length} / 5000 characters`;
            navigate("query");
        });
    });

    $("#queryInput").addEventListener("input", event => {
        $("#characterCount").textContent =
            `${event.target.value.length} / 5000 characters`;
    });

    $("#runQueryButton").addEventListener("click", runQuery);
    $("#exportAgents").addEventListener("click", exportAgents);
    $("#exportHistory").addEventListener("click", exportHistory);

    $("#refreshButton").addEventListener("click", async () => {
        await checkHealth();
        await loadHistory();
        renderAll();
        toast("Dashboard refreshed.");
    });

    $("#retryConnection").addEventListener("click", checkHealth);
    $("#settingsRetry").addEventListener("click", checkHealth);

    $("#refreshWorkflow").addEventListener("click", () => {
        renderWorkflow(state.currentExecution);
        toast("Workflow view refreshed.");
    });

    $("#mobileMenu").addEventListener("click", () => {
        $("#sidebar").classList.add("open");
        $("#mobileOverlay").classList.add("show");
    });

    $("#sidebarClose").addEventListener("click", closeMobileSidebar);
    $("#mobileOverlay").addEventListener("click", closeMobileSidebar);
}

document.addEventListener("keydown", event => {
    if (event.key === "Escape") closeMobileSidebar();
});

window.matchMedia("(min-width: 1051px)")
    .addEventListener("change", closeMobileSidebar);

async function init() {
    setupEvents();

    if (window.lucide) window.lucide.createIcons();

    await checkHealth();
    await loadHistory();
    renderAll();
}

document.addEventListener("DOMContentLoaded", init);