(function(){
    // Uses warSettings.apiBase provided by wp_localize_script in PHP plugin
    const API = (window.warSettings && window.warSettings.apiBase) ? window.warSettings.apiBase : 'http://127.0.0.1:5000/api';
    const form = document.getElementById('warForm');
    const statusEl = document.getElementById('warStatus');
    const MAX_FILES = 4;

    function setStatus(msg, isError){
        if(!statusEl) return;
        statusEl.textContent = msg;
        statusEl.style.color = isError ? 'crimson' : '#0a7e8c';
    }

    if(!form) return;

    form.addEventListener('submit', async function(e){
        e.preventDefault();
        setStatus('جارٍ الإرسال...');
        const files = document.getElementById('images').files;
        if(files.length !== MAX_FILES){
            setStatus('الرجاء اختيار 4 صور بالضبط', true);
            return;
        }

        const fd = new FormData(form);
        // append files (input already named 'images' and supports multiple; many browsers append automatically)
        // ensure proper field name
        // remove any existing images entries to avoid duplicates
        // (but FormData constructed from form will include file inputs)

        try{
            const res = await fetch(API + '/submit', { method: 'POST', body: fd, credentials: 'include' });
            const json = await res.json();
            if(!res.ok){
                setStatus(json.error || 'حدث خطأ من الخادم', true);
                return;
            }
            setStatus('تم إنشاء التقرير، جارٍ التحميل...');
            // download PDF by opening the returned report endpoint
            const id = json.report_id;
            // trigger download in new tab/window
            window.open(API.replace('/api','') + `/api/reports/${id}/pdf`, '_blank');
            setStatus('تم الإنشاء — سيتم فتح الملف في تبويب جديد.');
            form.reset();
        }catch(err){
            console.error(err);
            setStatus('تعذر الاتصال بالخادم: ' + err.message, true);
        }
    });
})();
