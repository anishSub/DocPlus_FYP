
document.addEventListener('DOMContentLoaded', function() {
        const faqItems = document.querySelectorAll('.faq-item');

        faqItems.forEach(item => {
            const header = item.querySelector('.faq-header');
            const body = item.querySelector('.faq-body'); // Select the answer part

            header.addEventListener('click', () => {
                // 1. Check if the currently clicked item is already active
                const isActive = item.classList.contains('active');

                // 2. Close ALL FAQ items first
                faqItems.forEach(otherItem => {
                    otherItem.classList.remove('active');
                    const otherBody = otherItem.querySelector('.faq-body');
                    if (otherBody) {
                        otherBody.style.maxHeight = null; // This closes the previous answer
                    }
                });

                // 3. If the clicked item wasn't active before, open it now
                if (!isActive) {
                    item.classList.add('active');
                    // This line calculates the exact height of the text and opens it
                    body.style.maxHeight = body.scrollHeight + "px";
                }
            });
        });
});
