// Global Custom Toast & Confirm Library
// Designed for DocPlus

window.showCustomToast = function(message, type='error', actionText=null, actionUrl=null) {
    let container = document.getElementById('message-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'message-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `custom-toast ${type}`;
    
    // Fallbacks for FontAwesome if RemixIcon isn't loaded (SuperAdmin usually has FA)
    let iconHtml = type === 'success' 
        ? '<i class="ri-checkbox-circle-line fas fa-check-circle" style="margin-right:8px"></i>' 
        : '<i class="ri-error-warning-line fas fa-exclamation-circle" style="margin-right:8px"></i>';
    
    let actionHtml = '';
    if (actionText && actionUrl) {
        actionHtml = `<a href="${actionUrl}" style="margin-left: 12px; padding: 4px 10px; background: rgba(255,255,255,0.2); border-radius: 4px; color: inherit; text-decoration: none; font-weight: 600; font-size: 13px;">${actionText}</a>`;
    }

    toast.innerHTML = `
        <span style="display: flex; align-items: center;">
            ${iconHtml}
            ${message}
            ${actionHtml}
        </span>
        <button class="toast-close" onclick="this.parentElement.remove();" style="background:none; border:none; color:inherit; font-size:18px; cursor:pointer; margin-left:15px;">&times;</button>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.5s ease';
        setTimeout(() => {
            if (toast.parentElement) toast.remove();
        }, 500);
    }, 4000);
};

window.showCustomConfirm = function(message, onConfirmCallback) {
    let container = document.getElementById('message-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'message-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `custom-toast error`; // Using error style (red/yellow) for confirms
    toast.style.display = 'flex';
    toast.style.flexDirection = 'column';
    toast.style.alignItems = 'flex-start';
    toast.style.minWidth = '300px';

    toast.innerHTML = `
        <div style="display: flex; align-items: center; width: 100%;">
            <i class="ri-question-line fas fa-question-circle" style="margin-right:8px; font-size: 18px;"></i>
            <span style="flex-grow: 1;">${message}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove();" style="background:none; border:none; color:inherit; font-size:18px; cursor:pointer; margin-left:15px;">&times;</button>
        </div>
        <div style="margin-top: 12px; display: flex; gap: 10px; width: 100%; justify-content: flex-end;">
            <button onclick="this.parentElement.parentElement.remove();" style="padding: 6px 14px; background: transparent; border: 1px solid rgba(255,255,255,0.6); border-radius: 6px; color: inherit; cursor: pointer; font-size: 13px; font-weight: 500;">Cancel</button>
            <button class="confirm-ok" style="padding: 6px 14px; background: white; border: none; border-radius: 6px; color: #ef4444; font-weight: 600; cursor: pointer; font-size: 13px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">Confirm</button>
        </div>
    `;
    
    const okBtn = toast.querySelector('.confirm-ok');
    okBtn.addEventListener('click', () => {
        toast.remove();
        if (onConfirmCallback) onConfirmCallback();
    });

    container.appendChild(toast);
};

// Attached to <a> tags: <a href="..." onclick="confirmLink(event, 'Message?')">
window.confirmLink = function(event, message) {
    event.preventDefault();
    const url = event.currentTarget.href;
    window.showCustomConfirm(message, () => {
        window.location.href = url;
    });
};

// Attached to <form> tags: <form onsubmit="confirmForm(event, 'Message?')">
window.confirmForm = function(event, message) {
    event.preventDefault();
    const form = event.currentTarget;
    window.showCustomConfirm(message, () => {
        form.submit();
    });
};
