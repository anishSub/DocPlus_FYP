/**
 * SuperAdmin Analytics Charts
 * Library: Chart.js v4 (loaded via CDN in analytics.html)
 * ────────────────────────────────────────────────────────
 * Reads JSON data injected into the page by Django template
 * and creates 6 charts: 3 doughnut + 3 bar.
 */

// ── Color Palettes ───────────────────────────────────────
const DOUGHNUT_COLORS = [
    '#0092b8', '#1c398e', '#16a34a', '#d97706',
    '#dc2626', '#8b5cf6', '#ec4899', '#06b6d4'
];

const BAR_GRADIENT_FROM = '#0092b8';
const BAR_GRADIENT_TO   = '#1c398e';

// ── Shared Config ────────────────────────────────────────
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 13;
Chart.defaults.color = '#6b7280';

// ── Helper: create a doughnut chart ──────────────────────
function createDoughnutChart(canvasId, dataObj) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = Object.keys(dataObj);
    const values = Object.values(dataObj);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: DOUGHNUT_COLORS.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 16,
                        usePointStyle: true,
                        pointStyle: 'circle',
                    }
                },
                tooltip: {
                    backgroundColor: '#1f2937',
                    titleColor: '#f9fafb',
                    bodyColor: '#e5e7eb',
                    borderColor: '#374151',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                }
            }
        }
    });
}

// ── Helper: create a bar chart ───────────────────────────
function createBarChart(canvasId, dataObj, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = Object.keys(dataObj);
    const values = Object.values(dataObj);
    const isHorizontal = options.horizontal || false;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: options.label || 'Count',
                data: values,
                backgroundColor: createBarGradients(ctx, values.length, isHorizontal),
                borderRadius: 6,
                borderSkipped: false,
                maxBarThickness: 48,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: isHorizontal ? 'y' : 'x',
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1f2937',
                    titleColor: '#f9fafb',
                    bodyColor: '#e5e7eb',
                    borderColor: '#374151',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            let val = context.parsed[isHorizontal ? 'x' : 'y'];
                            if (options.currency) {
                                return ' Rs ' + val.toLocaleString('en-IN');
                            }
                            return ' ' + val;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: !isHorizontal, color: '#f3f4f6' },
                    ticks: { display: !isHorizontal },
                    border: { display: false },
                },
                y: {
                    grid: { display: isHorizontal, color: '#f3f4f6' },
                    ticks: {
                        display: true,
                        callback: function(value) {
                            if (options.currency && !isHorizontal) {
                                return 'Rs ' + value.toLocaleString('en-IN');
                            }
                            return value;
                        }
                    },
                    border: { display: false },
                    beginAtZero: true,
                }
            }
        }
    });
}

// ── Helper: generate gradient fills for bars ─────────────
function createBarGradients(ctx, count, isHorizontal) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        const ratio = count > 1 ? i / (count - 1) : 0;
        // Interpolate between the two brand colors
        const r = Math.round(lerp(0, 28, ratio));
        const g = Math.round(lerp(146, 57, ratio));
        const b = Math.round(lerp(184, 142, ratio));
        colors.push(`rgb(${r}, ${g}, ${b})`);
    }
    return colors;
}

function lerp(a, b, t) {
    return a + (b - a) * t;
}

// ── Initialize all charts on page load ───────────────────
document.addEventListener('DOMContentLoaded', function() {
    // Data is injected by Django template as global variables
    // on the window object: window.chartData

    const d = window.chartData || {};

    // Doughnut Charts
    if (d.userRoles)      createDoughnutChart('chartUserRoles', d.userRoles);
    if (d.apptStatus)     createDoughnutChart('chartApptStatus', d.apptStatus);
    if (d.hospitalTypes)  createDoughnutChart('chartHospitalTypes', d.hospitalTypes);

    // Bar Charts
    if (d.specializations) {
        createBarChart('chartSpecializations', d.specializations, {
            horizontal: true,
            label: 'Doctors',
        });
    }
    if (d.monthlyAppts) {
        createBarChart('chartMonthlyAppts', d.monthlyAppts, {
            label: 'Appointments',
        });
    }
    if (d.monthlyRevenue) {
        createBarChart('chartMonthlyRevenue', d.monthlyRevenue, {
            label: 'Revenue',
            currency: true,
        });
    }
});
