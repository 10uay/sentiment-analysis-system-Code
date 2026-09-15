# نظام تحليل مشاعر النصوص باستخدام نماذج اللغة الحديثة

مشروع كامل كبداية عملية قابلة للتشغيل لمشروع:
**Sentiment Analysis System Using Modern Language Models**

يدعم المشروع:
- واجهة React لتحليل النص وعرض النتائج.
- Backend باستخدام FastAPI.
- تنظيف النصوص العربية والإنكليزية.
- كشف اللغة.
- اختيار نموذج التحليل: AraBERT / XLM-R / Ensemble / LLM.
- منطق fallback يعمل دون تحميل نماذج ثقيلة.
- تخزين التحليلات في قاعدة بيانات.
- Redis Cache اختياري.
- RAG Service اختياري باستخدام embeddings وقاعدة متجهات بسيطة.
- توليد تقارير PDF/CSV.
- سكربتات تدريب وتقييم ومقارنة نماذج.
- Docker Compose للبنية الكاملة.

## التشغيل السريع بدون Docker

### Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

افتح:
```text
http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

افتح:
```text
http://localhost:5173
```

## التشغيل باستخدام Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## ملاحظات مهمة

1. المشروع يعمل مباشرة بنمط fallback lexicon حتى دون تحميل نماذج ضخمة.
2. لاستخدام نماذج Hugging Face فعلياً، فعّل المتغير:
   ```env
   ENABLE_HF_MODELS=true
   ```
   ثم اضبط أسماء النماذج في `.env`.
3. لاستخدام LLM خارجي، أضف مفتاح API في `.env`.
4. سكربتات التدريب موجودة في مجلد `training/` وتحتاج GPU عند استخدام نماذج Transformer كاملة.

## البنية

```text
backend/        FastAPI Backend
frontend/       React Frontend
data_pipeline/  جمع وتنظيف وفهرسة البيانات
training/       تدريب وتقييم ومقارنة النماذج
monitoring/     Prometheus/Grafana
.github/        CI
```
