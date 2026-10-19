# AI Prompts Used
## AI Usage
Цей проєкт було оптимізовано за допомогою штучного інтелекту (AI) відповідно до вимог завдання.
- **Code Review:** AI виявив потенційну N+1 проблему у `BookListView` та відсутність перевірок на порожній кошик в `order_create`. Рекомендації імплементовано в код (деталі у `AI_REVIEW.md`).
- **Tests Generation:** Юніт та інтеграційні тести (з використанням `pytest`, `factory-boy`, `unittest.mock`) були згенеровані AI, перевірені та адаптовані під специфіку проєкту. Досягнуто покриття (Coverage) ≥ 70%.
- **Documentation:** Всі docstrings у `views.py` створені за допомогою AI. Детальний перелік запитів до ШІ знаходиться у файлі `AI_PROMPTS.md`.
Під час виконання цього завдання були використані наступні промпти:

1. **Code Review:** 
   * "Please do a code review of my Django views (order_create, process_payment, BookListView). Are there any security issues, N+1 query problems, or missing validations? Suggest refactoring."
2. **Test Generation:** 
   * "Generate Pytest unit and integration tests for Django Book and Order models using factory-boy. Write  testing user flows and mocking Stripe checkout."
   * "How to fix django.db.utils.IntegrityError: null value in column 'category_id' in my pytest factories?"
3. **Docstrings Generation:**
   * "Generate PEP 257 compliant docstrings for all my Django Class-Based Views and Functional Views in views.py."