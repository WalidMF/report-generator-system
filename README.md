# تعليمات التثبيت والتشغيل

## المتطلبات
قم بتثبيت المكتبات المطلوبة:
```bash
pip install flask flask-cors
```

## هيكل المشروع
```
report-generator-system/
├── app.py                 # خادم Flask
├── report_generator_system.py  # كود توليد PDF
├── reports.db            # قاعدة بيانات SQLite
├── uploads/             # مجلد الصور المرفوعة
├── reports/             # مجلد ملفات PDF
└── reports/form/        # ملفات الواجهة
    ├── index.html
    ├── styles.css
    └── script.js
```

## التشغيل
1. شغل الخادم:
```bash
python app.py
```
2. افتح النموذج في المتصفح:
   - افتح `reports/form/index.html`
   - أو اذهب إلى `http://localhost:5000`

## الميزات
- رفع النموذج مع 4 صور
- توليد PDF تلقائياً
- حفظ السجلات في قاعدة بيانات
- عرض التقارير السابقة
- تحميل ملفات PDF