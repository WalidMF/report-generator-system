document.addEventListener('DOMContentLoaded', function() {
    const API_URL = 'http://localhost:5000/api';
    const form = document.getElementById('activityForm');
    const fileInput = document.getElementById('images');
    const imagePreview = document.getElementById('imagePreview');
    const previousReports = document.getElementById('previousReports');
    const MAX_FILES = 4;

    // Handle file selection
    fileInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        
        // Check number of files
        if (files.length > MAX_FILES) {
            alert(`الرجاء اختيار ${MAX_FILES} صور كحد أقصى`);
            fileInput.value = '';
            imagePreview.innerHTML = '';
            return;
        }

        // Clear previous previews
        imagePreview.innerHTML = '';
        
        // Create previews
        files.forEach(file => {
            if (!file.type.startsWith('image/')) {
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                const preview = document.createElement('div');
                preview.className = 'preview-item';
                
                const img = document.createElement('img');
                img.src = e.target.result;
                img.alt = file.name;
                
                preview.appendChild(img);
                imagePreview.appendChild(preview);
            }
            reader.readAsDataURL(file);
        });
    });

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate file count
        const files = fileInput.files;
        if (files.length !== MAX_FILES) {
            alert(`الرجاء اختيار ${MAX_FILES} صور بالضبط`);
            return;
        }

        try {
            const formData = new FormData(form);
            
            // Send to server
            const response = await fetch(`${API_URL}/submit`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                alert('تم إنشاء التقرير بنجاح!');
                // Open PDF in new tab
                window.open(`${API_URL}/reports/${result.report_id}/pdf`, '_blank');
                // Reset form
                form.reset();
                imagePreview.innerHTML = '';
                // Refresh reports list
                loadPreviousReports();
            } else {
                throw new Error(result.error || 'حدث خطأ أثناء إنشاء التقرير');
            }
        } catch (error) {
            alert(error.message);
        }
    });

    // Clear preview when form is reset
    form.addEventListener('reset', function() {
        imagePreview.innerHTML = '';
    });

    // Load previous reports
    async function loadPreviousReports() {
        try {
            const response = await fetch(`${API_URL}/reports`);
            const reports = await response.json();
            
            if (previousReports) {
                previousReports.innerHTML = '';
                
                if (reports.length === 0) {
                    previousReports.innerHTML = '<p class="no-reports">لا توجد تقارير سابقة</p>';
                    return;
                }

                const table = document.createElement('table');
                table.className = 'reports-table';
                
                table.innerHTML = `
                    <thead>
                        <tr>
                            <th>اسم النشاط</th>
                            <th>تاريخ التنفيذ</th>
                            <th>المسؤول</th>
                            <th>تاريخ الإنشاء</th>
                            <th>التقرير</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${reports.map(report => `
                            <tr>
                                <td>${report.activity_name}</td>
                                <td>${report.execution_date}</td>
                                <td>${report.executor_name}</td>
                                <td>${new Date(report.created_at).toLocaleString('ar-SA')}</td>
                                <td>
                                    <a href="${API_URL}/reports/${report.id}/pdf" target="_blank" class="btn-download">
                                        تحميل PDF
                                    </a>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                `;
                
                previousReports.appendChild(table);
            }
        } catch (error) {
            console.error('Error loading reports:', error);
            if (previousReports) {
                previousReports.innerHTML = '<p class="error">حدث خطأ أثناء تحميل التقارير السابقة</p>';
            }
        }
    }

    // Load reports on page load
    loadPreviousReports();
});