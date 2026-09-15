ضع ملفات Alembic migration هنا عند تفعيل الترحيلات:

```bash
alembic init app/db/migrations
alembic revision --autogenerate -m "init"
alembic upgrade head
```
