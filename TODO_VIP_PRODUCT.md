# TODO — хороший продукт eInvoice

Документ формулирует, каким должен быть качественный и готовый к реальному использованию
продукт **eInvoice** с учётом анализа конкурентов из `TODO_CONCURENT.md`.

Связанные документы:

- `TODO_CONCURENT.md` — рынок, конкуренты, что не копировать (генератор, полный API).
- `TODO_SUBSCRIPTION.md` — регистрация, организации, тарифы и платные Empfang-фичи
  **после** закрытия P0; P1/P2 ниже на него ссылаются.

Фокус продукта: немецкие B2B SME / Handwerk — **приём**, чтение, проверка и передача
входящих XRechnung / ZUGFeRD в бухгалтерию.

Главный сценарий:

> Загрузить счёт → за 30 секунд понять, кому, сколько и когда платить → увидеть ошибки
> и расхождения → передать корректный пакет Steuerberater.

---

## 1. Что должен иметь хороший продукт

### P0 — обязательно до публичного запуска

#### 1.1 Понятная ценность и простой сценарий

- [x] Показать отличие от ELSTER: чтение + проверка + PDF↔XML-сверка + экспорт.
- [x] Обеспечить happy path без регистрации: загрузка → результат → экспорт.
      Платный кабинет не должен это ломать (`TODO_SUBSCRIPTION.md`, тариф Free).
- [x] Давать пользователю понятный итог: `можно обрабатывать`, `нужно проверить`, `нужно запросить исправление`.
- [x] Все технические ошибки переводить на простой немецкий язык и сопровождать следующим действием.
- [x] Явно показывать поддерживаемые форматы, профили, максимальный размер файла и ограничения.
- [x] Не обещать юридическую или налоговую гарантию; показывать корректный disclaimer.

#### 1.2 Приём и чтение счетов

- [x] Надёжно принимать XRechnung UBL Invoice и CreditNote.
- [x] Надёжно принимать UN/CEFACT CII, ZUGFeRD и Factur-X.
- [x] Проверять реальный тип и сигнатуру файла, а не только расширение.
- [x] Безопасно отклонять повреждённые, неподдерживаемые и опасные XML/PDF.
- [x] Корректно читать основные данные: номер, даты, продавца, покупателя, суммы, валюту, НДС, IBAN, платёжную ссылку и позиции.
- [x] Поддерживать скидки, надбавки, несколько ставок НДС, кредит-ноты, отрицательные суммы и единицы измерения.
- [x] Сохранять точность денежных расчётов без использования двоичного `float` в финансовой логике.
- [x] Показывать исходный PDF рядом со структурированными данными для ZUGFeRD.
- [x] Давать возможность загрузить другой файл и повторить сценарий без перезагрузки страницы.

#### 1.3 Валидация и доверие к результату

- [x] В production всегда выполнять полную EN 16931 / XRechnung-проверку актуальным KoSIT validator.
- [x] Показывать версию стандарта, профиль и версию validation engine.
- [x] Разделять ошибки схемы, бизнес-правил, предупреждения и информационные сообщения.
- [x] Объяснять каждую ошибку человеческим языком и указывать поле/BT-код.
- [x] Проверять обязательные реквизиты и арифметическую согласованность сумм.
- [x] Для ZUGFeRD сверять минимум номер, дату, итоговую сумму, НДС и IBAN между PDF и XML.
- [x] Не показывать «валидно», если полная проверка KoSIT не выполнялась.
- [x] Регулярно обновлять validation scenarios при изменениях XRechnung / EN 16931.
- [x] Иметь набор эталонных валидных, невалидных и пограничных счетов для регрессии.

#### 1.4 Результат и действия пользователя

- [x] Наиболее важные данные — поставщик, сумма, срок оплаты, IBAN и статус — показывать первыми.
- [x] Визуально выделять отсутствующие поля, ошибки и PDF↔XML-расхождения.
- [x] При расхождении рекомендовать не платить и связаться с поставщиком.
- [x] Показывать конкретные следующие шаги в зависимости от результата проверки.
- [x] Позволять скачать отчёт о валидации для поставщика или Steuerberater.
- [x] Не разрешать экспорт явно ошибочного результата без заметного предупреждения.

#### 1.5 Экспорт для бухгалтерии

- [x] Поддерживать CSV и Excel с документированным стабильным mapping.
- [ ] Поддерживать DATEV-совместимый экспорт, проверенный на импорте вместе со Steuerberater.
- [x] Формировать одним действием Steuerberater-Paket: исходник, краткое резюме, validation report, Excel и DATEV.
- [x] Сохранять исходный XML в пакете; для ZUGFeRD — исходный PDF с embedded XML.
- [x] Корректно обрабатывать немецкие даты, десятичные разделители, кодировку и безопасные имена файлов.
- [x] Версионировать формат экспорта, чтобы обновления не ломали процесс Kanzlei.
- [x] Публично документировать ограничения DATEV-экспорта и не называть минимальный CSV «native DATEVconnect».

#### 1.6 Datenschutz, безопасность и юридическая готовность

- [x] Опубликовать Impressum, Datenschutzerklärung и понятное описание обработки файлов.
- [x] Явно указать, где обрабатываются данные, хранятся ли файлы и когда они удаляются.
- [x] Не сохранять содержимое счетов и персональные данные в application logs.
- [x] Гарантированно удалять все временные XML/PDF и результаты validator после обработки.
- [x] Использовать HTTPS, безопасные HTTP-заголовки, строгий CORS и ограничение размера запроса на reverse proxy.
- [x] Добавить rate limiting, timeout и защиту от ресурсно-тяжёлых PDF/XML.
- [x] Проверять XML против XXE, entity expansion и других parser attacks.
- [x] Не возвращать пользователю traceback и внутренние детали ошибок.
- [x] Зафиксировать subprocess/Java validator с минимальными правами и лимитами ресурсов.
- [x] Зафиксировать threat model (`docs/THREAT_MODEL.md`) до работы с реальными счетами клиентов.
- [ ] Выполнить независимую security-проверку до работы с реальными счетами клиентов.
- [x] Подготовить AVV/DPA и список subprocessors (`docs/AVV_DPA.md`); данные оператора и хостера ещё не заполнены.

#### 1.7 Качество интерфейса

- [x] Интерфейс должен полноценно работать на desktop, tablet и mobile.
- [x] Обеспечить keyboard navigation, видимый focus, корректные labels и screen-reader announcements.
- [x] Проверить цветовой контраст и не передавать статус только цветом.
- [x] Показывать прогресс обработки и не допускать повторной случайной отправки.
- [x] Сохранять понятный интерфейс при длинных названиях, больших таблицах и отсутствии части данных.
- [x] Проверить последние версии Chrome, Edge, Firefox и Safari.
- [x] Обеспечить базовую WCAG 2.1 AA доступность.

#### 1.8 Надёжность и эксплуатация

- [x] Иметь автоматический CI для backend tests, frontend lint, typecheck и production build.
- [x] Добавить frontend unit/component tests и критический end-to-end happy-path test.
- [x] Проверять API contract между FastAPI DTO и TypeScript types.
- [x] Иметь readiness/health checks, structured logs, request ID, error tracking и метрики.
- [x] Настроить alerts на рост 5xx, timeout, parse failures и недоступность API.
- [x] Определить SLO: доступность, максимальное время обработки и допустимая доля ошибок.
- [x] Ограничить версии зависимостей, включить dependency/security scanning и процесс обновления.
- [x] Автоматизировать воспроизводимый deployment с rollback и smoke test.
- [x] Подготовить резервный сценарий при недоступности KoSIT/Java.
- [x] Документировать incident response и порядок сообщения об утечке данных.

#### 1.9 Готовность к реальным пользователям

- [ ] Провести пилот минимум с 5 представителями Handwerk и 1–2 Steuerberater.
- [ ] Проверить DATEV-файл реальным импортом, а не только структурой CSV.
- [x] Добавить безопасный канал обратной связи без прикрепления конфиденциального счёта по умолчанию.
- [x] Измерять funnel без содержимого счетов: landing → upload → successful parse → export.
- [x] Определить продуктовые KPI: time-to-understand, parse success rate, export rate, returning users.
- [x] Подготовить FAQ: что такое XML, что оплачивать при mismatch, что передать Steuerberater.
- [ ] Указать support-контакт, ожидаемое время ответа и статус сервиса.

### P1 — усиление продукта после подтверждения MVP

Детальный каталог, тарифы и этапы 1–2: `TODO_SUBSCRIPTION.md`.
Регистрацию и хранение счетов не начинать до закрытия P0 (этап 0 там же).

- [x] Batch upload und пакетная обработка нескольких счетов.
      (`TODO_SUBSCRIPTION.md` A1, этап 2)
- [x] История последних операций только при явном согласии пользователя.
      (`TODO_SUBSCRIPTION.md` A2; оригинал файла — opt-in + retention)
- [x] Поиск дублей по file_hash или номеру, продавцу, дате и сумме.
      (`TODO_SUBSCRIPTION.md` A3)
- [x] Экспорт нескольких счетов одним бухгалтерским пакетом.
      (`TODO_SUBSCRIPTION.md` A4)
- [x] Регистрация организации, лимиты по плану и профиль фирмы / Steuerberater.
      (`TODO_SUBSCRIPTION.md` этапы 1–2, A5–A6)
- [ ] Mandanten-Link / безопасная передача пакета Kanzlei.
      (`TODO_SUBSCRIPTION.md` B7, этап 4)
- [ ] Email-ingest с отдельным адресом и строгими правилами безопасности.
      (`TODO_SUBSCRIPTION.md` B9, этап 4)
- [ ] Настраиваемый mapping счетов и Kontenrahmen совместно со Steuerberater.
      (`TODO_SUBSCRIPTION.md` B8, этап 4)
- [ ] Локальный/offline или on-premise режим для privacy-sensitive клиентов.
      (`TODO_SUBSCRIPTION.md` этап 5, не тариф v1)
- [ ] SEO-страницы: XRechnung öffnen, ZUGFeRD prüfen, DATEV Export, E-Rechnung Handwerk.
- [ ] Короткое сравнение eInvoice с ELSTER и полноценными Buchhaltung-продуктами.
- [ ] Немецкий onboarding с примером анонимизированного счёта.

### P2 — только после подтверждённого спроса

Детализация API / Kanzlei: `TODO_SUBSCRIPTION.md` этапы 4–5.
Не копировать полный create/convert-стек rechnungsapi (`TODO_CONCURENT.md` §4.11, §7.4).

- [ ] Узкий Empfang API для интеграции входящих счетов.
      (`TODO_SUBSCRIPTION.md` B10: parse / validate / accountant-package + webhooks)
- [ ] Интеграции с DATEV, sevDesk, Lexware или DMS через официальные API.
- [ ] GoBD-совместимый архив только как отдельный, юридически проработанный продукт.
- [ ] PEPPOL receive/access-point интеграция через проверенного партнёра.
- [ ] White-label для Kanzlei только после успешных пилотов.
- [ ] Генератор исходящих XRechnung / ZUGFeRD только как отдельный add-on или партнёр,
      не как ядро Plus (`TODO_SUBSCRIPTION.md` §3.C и этап 5).

### Осознанно не делать сейчас

- [ ] Не превращать MVP в полную бухгалтерию или ERP.
- [ ] Не строить генератор исходящих E-Rechnung как ядро продукта.
- [ ] Не обещать автоматическое право на Vorsteuerabzug.
- [ ] Не заявлять GoBD-архив, DATEVconnect или PEPPOL без фактической сертифицированной интеграции.
- [ ] Не хранить счета «для удобства» без отдельной необходимости, согласия и retention policy.
- [ ] Не делать регистрацию обязательной для одного файла (гостевой Free в `TODO_SUBSCRIPTION.md`).

---

## 2. Что у нас уже есть

Ниже отмечены только возможности, подтверждённые текущим кодом и документацией
репозитория. Наличие реализации не означает, что она уже проверена в production.

### Продукт и пользовательский сценарий

- [x] Узкое позиционирование: приём и обработка входящих XRechnung / ZUGFeRD.
- [x] Немецкоязычный landing page с описанием сценария в три шага.
- [x] Работа без регистрации и личного кабинета.
- [x] Drag & drop и выбор одного `.xml` или `.pdf` файла.
- [x] Адаптивная вёрстка, видимый focus, skip-link и объявления для screen reader.
- [x] Статусы и ошибки дублируются текстом, не только цветом; длинные поля и таблицы не ломают макет.
- [x] Читаемое представление реквизитов, сторон, сумм и позиций.
- [x] Понятные статусы `success`, `partial`, `error` и отдельный validation status.
- [x] Немецкие подсказки «Was tun als Nächstes?».
- [x] Disclaimer о том, что решение по Vorsteuerabzug остаётся у пользователя/Steuerberater.

### Форматы, parsing и безопасность XML

- [x] Определение XRechnung XML и ZUGFeRD PDF.
- [x] Поддержка UBL Invoice, UBL CreditNote и UN/CEFACT CII.
- [x] Извлечение embedded XML из ZUGFeRD/Factur-X PDF.
- [x] Явное отклонение обычного PDF без embedded invoice XML.
- [x] Явное отклонение openTRANS и неизвестных XML-форматов.
- [x] Ограничение загрузки по расширению и размеру до 10 MB на уровне API.
- [x] Проверка PDF-сигнатуры перед обработкой PDF.
- [x] Защищённый XML parsing через `defusedxml` и отдельные unsafe-XML checks.
- [x] Обработка пустых, повреждённых и неверно закодированных файлов.
- [x] Golden regression fixtures для обычных и пограничных случаев.

### Чтение, проверка и PDF↔XML

- [x] Чтение номера, дат, платёжной ссылки, продавца, покупателя, VAT ID и IBAN.
- [x] Чтение netto, MwSt, brutto, валюты и позиций счёта.
- [x] Базовые структурные и бизнес-проверки обязательных EN 16931 полей.
- [x] Проверка согласованности `net + tax = gross`.
- [x] Проверка суммы позиций относительно netto.
- [x] Опциональный запуск официального KoSIT validator через Java CLI.
- [x] В production KoSIT обязателен; `/api/health` сообщает `kosit_ready`.
- [x] Явное сообщение, если полная KoSIT-проверка не настроена.
- [x] В интерфейсе показываются стандарт, профиль и версия validation engine.
- [x] Сверка PDF↔XML для номера, даты, brutto, MwSt и IBAN.
- [x] Заметное предупреждение при mismatch и рекомендация связаться с поставщиком.
- [x] Side-by-side preview исходного ZUGFeRD PDF и структурированных данных.
- [x] Тесты validation mismatch, XML/PDF extraction, parsers и edge cases.

### Экспорт и Steuerberater

- [x] Экспорт CSV.
- [x] Экспорт Excel с листами `Invoice`, `Lines` и `Flat`.
- [x] Минимальный DATEV CSV в CP1252 с немецким форматом чисел и дат.
- [x] Steuerberater-Paket в ZIP: исходный XML/PDF + краткое резюме + Prüfbericht + Excel + DATEV.
- [x] Отдельный Prüfbericht (TXT) для поставщика или Steuerberater.
- [x] Отдельный API endpoint с machine-readable export mapping.
- [x] Документация mapping и DATEV-ограничений в `docs/EXPORT_MAPPING.md`.
- [x] Версия формата экспорта (`1.0`) в mapping API, Excel и ZIP-манифесте.
- [x] Безопасные генерируемые имена экспортных файлов.
- [x] Backend tests для export service.

### Backend, наблюдаемость и deployment

- [x] FastAPI application factory и типизированные Pydantic DTO.
- [x] Health endpoint (`/api/health`), liveness (`/api/health/live`) and readiness (`/api/health/ready`).
- [x] Request ID middleware (`X-Request-ID`) on API and frontend fetches.
- [x] Централизованная обработка HTTP, validation и unexpected errors.
- [x] JSON structured logs without request body and invoice content.
- [x] Отдельное логирование timeout и parse failures; error tracking counters for 5xx / timeout / parse.
- [x] Prometheus metrics on `GET /metrics` (localhost scrape; nginx does not expose it).
- [x] Alerts on 5xx, timeout, severe parse failures, and API down/not ready (systemd watchdog + Prometheus rules).
- [x] Настраиваемые CORS origins, log level, upload limit и KoSIT paths.
- [x] Systemd unit, nginx SPA snippet и deployment script.
- [x] Deployment health check после перезапуска API; `--rollback` на предыдущий git SHA.
- [x] Frontend lint и production build scripts.
- [x] Backend unit и golden-file regression tests.
- [x] GitHub Actions CI: backend pytest, frontend lint, typecheck, production build, pip-audit, npm audit.
- [x] Сверка FastAPI OpenAPI DTO с TypeScript types (`frontend/openapi.json`).
- [x] Frontend Vitest (unit/component) и Playwright happy-path e2e в CI.
- [x] Impressum- und Datenschutzerklärung-Seiten (Betreiberdaten noch offen); zwei Verarbeitungsmodelle dokumentiert.
- [x] Öffentliche Beschreibung: Datei nur während der Anfrage, danach Löschung.
- [x] Security-Header, Rate-Limit, Request-Timeout und härtere CORS-Methoden.
- [x] nginx-Snippets: HTTPS-Header, `client_max_body_size`, `limit_req`, API-Proxy.
- [x] systemd-Härtung und begrenzter KoSIT-Java-Prozess (`-Xmx`, POSIX rlimits).
- [x] Threat-Model-Dokument und AVV/DPA-Vorlage ohne Firmendaten.
- [x] FAQ, text-only feedback, privacy-safe funnel counters, SLO and incident docs.

---

## 3. Главные пробелы на текущем этапе

1. **Полная валидация зависит от деплоя KoSIT:** в production проверка обязательна,
   но без установленного JAR и актуальных scenarios сервис остаётся `degraded`
   и не показывает «gültig».
2. **DATEV ещё нужно подтвердить пилотом:** текущий экспорт намеренно минимальный и не является
   DATEVconnect; реальный импорт в Kanzlei-Rechnungswesen остаётся пунктом 1.9.
3. **Trust/legal слой частично готов:** Impressum и Datenschutzerklärung есть в
   интерфейсе, но данные оператора, точный hosting-Standort и подписанный AVV ещё
   не заполнены.
4. **Production security baseline в репозитории, внешний review открыт:** заголовки,
   rate limit, timeout, XML/PDF-защита и nginx/systemd-сниппеты есть; независимая
   security-проверка перед реальными Mandantenakten ещё не выполнена.
5. **Пилот ещё не начат:** funnel/KPI/FAQ в коде есть; реальные Handwerk- и
   Steuerberater-пилоты и публичный support-Kontakt отсутствуют.

---

## 4. Рекомендуемый порядок работ

1. Обязательный KoSIT в production и корректная модель статусов проверки.
2. Заполнить Impressum/Verantwortlicher, подписать AVV с хостером и провести независимый security review.
3. Реальный пилот DATEV/Steuerberater и доработка полного accountant package.
4. Пилот с Handwerk, сбор продуктовых метрик и улучшение UX.
5. Только после подтверждения спроса — регистрация и Plus по `TODO_SUBSCRIPTION.md`:
   batch, история, дубликаты, мульти-ZIP; затем биллинг; затем API / email / Kanzlei.
