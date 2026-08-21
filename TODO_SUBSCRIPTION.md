# TODO — регистрация, организации и подписка

Документ детализирует платный слой поверх MVP. Базовый продукт и критерии качества —
в `TODO_VIP_PRODUCT.md`. Рынок и конкуренты — в `TODO_CONCURENT.md`.

**Правило порядка:** не начинать этапы 1–5, пока не закрыты блокеры этапа 0
(P0 из `TODO_VIP_PRODUCT.md`: KoSIT в production, AVV, security review, пилот DATEV).

Главный сценарий подписки:

> Пачка входящих XRechnung / ZUGFeRD → сводка и дубликаты → один Steuerberater-Paket,
> без повторного ручного ввода.

Гостевой happy path **без аккаунта** остаётся: открыть один файл, проверить, экспортировать.
Подписка продаёт объём, историю, пакет на много счетов и интеграции — не «доступ к сайту».

---

## 0. Связь с текущим планом продукта

| Пункт в `TODO_VIP_PRODUCT.md` | Где раскрыт здесь |
|-------------------------------|-------------------|
| P0 1.1 happy path без регистрации | Этап 0, тариф Free |
| P0 1.6 Datenschutz / AVV / threat model | Этап 0 |
| P0 1.9 пилот Handwerk + Steuerberater | Этап 0, затем пилот Plus |
| P1 Batch upload | Этап 2, фича A1 |
| P1 История с явным согласием | Этап 2, фича A2 |
| P1 Поиск дублей | Этап 2, фича A3 |
| P1 Экспорт нескольких счетов одним пакетом | Этап 2, фича A4 |
| P1 Mandanten-Link | Этап 4, фича B7 |
| P1 Email-ingest | Этап 4, фича B9 |
| P1 Настраиваемый mapping / Kontenrahmen | Этап 4, фича B8 |
| P1 On-prem / offline | Этап 5, не в тариф v1 |
| P2 Узкий Empfang API | Этап 4, фича B10 |
| P2 Интеграции DATEV / sevDesk / Lexware | Этап 5 |
| P2 GoBD-архив | Не делать в подписке v1 |
| P2 PEPPOL | Не делать в подписке v1 |
| P2 White-label Kanzlei | Этап 5, после пилотов |
| «Не строить генератор как ядро» | Раздел 4 и этап 5 |

---

## 1. Покупатели и что им продаём

| Покупатель | Боль | Платит за |
|------------|------|-----------|
| Meister / Handwerk | 5–50 входящих в месяц, не хочет каждый раз ELSTER и ручной перенос | Batch, дубликаты, один ZIP бухгалтеру, выше лимиты |
| Firma / Büro | Десятки–сотни файлов, несколько сотрудников | Team seats, API, позже email-ingest |
| Steuerberater / Kanzlei | Много Mandanten, стабильный DATEV/Excel | Mapping, Mandanten-папки — только после пилота |

Не позиционировать тариф как замену sevDesk / Lexware / DATEV и не как
developer-API против [rechnungsapi.de](https://www.rechnungsapi.de).

---

## 2. Тарифы (ориентир)

Цены — ориентир относительно RechneX Pro (~12–19 €/мес) и ниже полной Buchhaltung
(sevDesk от ~14 €). Уточнить после пилота.

| Возможность | **Free (гость)** | **Plus ~9–15 €/мес** | **Team / Firma ~19–29 €/мес** | **Kanzlei (позже)** |
|-------------|------------------|----------------------|-------------------------------|---------------------|
| Открыть + проверить + PDF↔XML mismatch | да | да | да | да |
| Один файл за раз, суточный лимит | да (как сейчас) | выше | высокий | высокий |
| Steuerberater-ZIP на 1 счёт | да | да | да | да |
| Batch 10–50 файлов | нет | да | да | да |
| История 30–90 дней | нет | да | да | да |
| Дубликаты | нет | да | да | да |
| N счетов → один DATEV/Excel ZIP | нет | да | да | да |
| Профиль фирмы / Steuerberater | нет | да | да | да |
| Сохранённый mapping счетов | нет | опционально | да | да |
| 2–10 пользователей | нет | нет | да | да |
| Empfang API + ключ | нет | нет / мало | да | да |
| Email-inbox | нет | нет | да | да |
| Mandanten-папки | нет | нет | нет | да |

Регистрация без оплаты допустима как тонкая воронка (email + фирма), если гость
по-прежнему может обработать один счёт без логина.

---

## 3. Каталог фич

### A. Делать первыми (причина платить) — этап 2

#### A1. Batch-загрузка

- [ ] Несколько XML/PDF за один раз: очередь, прогресс, сводка `gültig` / `prüfen` / `ablehnen`.
- [ ] Вариант: ZIP или папка со смешанными файлами.
- [ ] Не запускать тяжёлый KoSIT синхронно в одном uvicorn-worker на всю пачку.

Связано: `TODO_VIP_PRODUCT.md` P1 «Batch upload».

#### A2. История обработок (opt-in)

- [ ] Список: дата, поставщик, номер, сумма, статус, повторный download пакета.
- [ ] По умолчанию хранить только метаданные + хэш файла, не оригинал.
- [ ] Хранение оригинала — отдельный checkbox «Dateien merken», retention 30 дней (настраиваемо).
- [ ] Без согласия история не пишется (гостевой режим как сейчас: файл живёт только в запросе).

Связано: `TODO_VIP_PRODUCT.md` P1 «История» и «Не хранить счета без согласия».

#### A3. Дубликаты

- [ ] Ключ: поставщик + номер счёта + дата + brutto (нормализованные).
- [ ] Показывать: «Diesen Beleg haben Sie bereits am TT.MM.JJJJ verarbeitet».

Связано: `TODO_VIP_PRODUCT.md` P1 «Поиск дублей».

#### A4. Мульти-экспорт для бухгалтера

- [ ] N счетов → один Excel + один DATEV CSV + манифест + исходники в ZIP.
- [ ] Версия формата экспорта совместима с `docs/EXPORT_MAPPING.md`.

Связано: `TODO_VIP_PRODUCT.md` P1 «Экспорт нескольких счетов одним пакетом» и P0 1.5.

#### A5. Лимиты по плану

- [x] Квоты: число parse/export в сутки, размер файла (гость 10 MB → Plus выше), параллелизм.
- [x] Отдельный rate limit для гостя и для аккаунта.
- [x] Понятное немецкое сообщение при исчерпании лимита + CTA на Plus.

#### A6. Профиль организации

- [ ] Название, Steuernummer / USt-IdNr, IBAN, email Steuerberater.
- [ ] Подстановка в пакет и в письмо/ссылку Kanzlei.

### B. Вторым этапом — этап 4

#### B7. Mandanten-Link

- [ ] «An Steuerberater senden»: одноразовая ссылка или email с ZIP.
- [ ] Не white-label и не портал Mandanten как у rechnungsapi.

Связано: `TODO_VIP_PRODUCT.md` P1 «Mandanten-Link».

#### B8. Настраиваемый DATEV-mapping

- [ ] Kreditor / счёт затрат на поставщика, который Kanzlei настраивает один раз.
- [ ] Без этого batch-экспорт быстро упрётся в ручную доработку в Kanzlei.

Связано: `TODO_VIP_PRODUCT.md` P1 «Настраиваемый mapping».

#### B9. Email-ingest

- [ ] Адрес вида `rechnungen+firma@…` → parse → письмо со сводкой и статусом.
- [ ] Отдельный сервис, sandbox, антивирус, лимиты вложений, не логировать тело письма.

Связано: `TODO_VIP_PRODUCT.md` P1 «Email-ingest».

#### B10. Узкий Empfang API (не полный стек rechnungsapi)

Минимум:

- [ ] `POST /v1/invoices/parse`
- [ ] `POST /v1/invoices/validate`
- [ ] `POST /v1/exports/accountant-package`
- [ ] Webhook `invoice.processed`
- [ ] API-ключ, квоты, отдельный OpenAPI для внешних клиентов
- [ ] Free-ключ с жёстким лимитом (ориентир: 10 счетов/мес, как у конкурента) только осознанно — не открывать create/convert

**Не в v1 API:** create XRechnung, PDF→XML, Peppol, white-label.

Связано: `TODO_VIP_PRODUCT.md` P2 «Узкий Empfang API»; `TODO_CONCURENT.md` §4.11 и §7.4.

#### B11. Команда

- [ ] Модель сразу: `User` + `Organization` + `Membership` (роли: Inhaber / Büro / nur Export).
- [ ] Не делать «один user = одна фирма» — иначе Team и Kanzlei придётся переписывать.

### C. Варианты, которые сознательно не входят в подписку v1

| Тема | Решение | Когда пересмотреть |
|------|---------|-------------------|
| Генератор XRechnung / ZUGFeRD | Не ядро. Варианты: не делать / лёгкая форма / partner (rechnungsapi) / «исправить входящий XML» | После спроса пилота и давления Ausstellungspflicht 2027+ (`TODO_CONCURENT.md` §7.3) |
| GoBD-архив | Отдельный юридический продукт | `TODO_VIP_PRODUCT.md` P2 |
| DATEVconnect / замена UO | Не обещать | `TODO_CONCURENT.md` §7.4 |
| Peppol AP | Только партнёр, не свой access point | P2 |
| White-label Kanzlei | После успешных пилотов | P2 |
| On-prem | Отдельный прайс | P1, этап 5 |

---

## 4. Что не продаём в тарифе v1

- [ ] Не делать регистрацию обязательной, чтобы открыть один счёт (проигрыш ELSTER).
- [ ] Не строить генератор исходящих E-Rechnung как ядро Plus (`TODO_VIP_PRODUCT.md`, `TODO_CONCURENT.md` §7.4).
- [ ] Не обещать Vorsteuer-гарантию, native DATEVconnect, GoBD-архив, Peppol.
- [ ] Не хранить счета «для удобства» без checkbox, legal basis и retention.
- [ ] Не копировать полный developer-API rechnungsapi (create/convert/KI/white-label).

---

## 5. План реализации

### Этап 0 — блокеры (до любого аккаунта)

Подписка со хранением счетов раньше этого ломает trust («файл только в запросе»)
и усиливает риск DSGVO.

- [ ] Закрыть P0 из `TODO_VIP_PRODUCT.md`: KoSIT в production, статусы проверки.
- [ ] Заполнить Impressum / Verantwortlicher, hosting-Standort, подписать AVV с хостером.
- [ ] Независимый security review до реальных Mandantenakten.
- [ ] Пилот DATEV-импорта со Steuerberater (пункт 1.9).
- [x] Зафиксировать две модели обработки:
      гость — файл не персистится;
      аккаунт — отдельный legal basis (Art. 6 DSGVO + AVV) и opt-in на файлы.
- [x] Обновить Datenschutzerklärung: что хранится, TTL, subprocessors (email, платежи, object storage в DE).
- [x] Обновить `docs/THREAT_MODEL.md` и `docs/AVV_DPA.md` под аккаунты и биллинг.
- [ ] Пилот с Handwerk и метрики воронки (1.9) — спрос на batch/историю подтверждён, не угадан.

Готовность этапа 0 = можно начинать этап 1.

### Этап 1 — фундамент аккаунта

Ориентир: 4–6 недель. Биллинг можно отложить: план Plus вручную для пилотных фирм.

- [x] Postgres (не SQLite в production): `users`, `organizations`, `memberships`, `plans`.
- [x] Регистрация: email + пароль или Magic Link, подтверждение email.
- [x] Session cookie / JWT, logout, смена пароля, позже 2FA.
- [x] Страницы: Login, Register, Verify, Org-Einstellungen.
- [x] Гостевой `/api/invoices/parse` без изменений по смыслу (без хранения).
- [x] Authenticated запросы несут org-контекст; квоты ещё могут быть заглушкой.
- [x] Ручной `plan=plus` в админке для 5–10 пилотных организаций.

### Этап 2 — платные Empfang-фичи (минимальный Plus)

Ориентир: 6–8 недель. Это пакет, который можно сравнивать с RechneX Pro, не уходя в create.

Порядок внутри этапа:

1. [x] Лимиты по плану (гость / plus / team) на parse и export (A5).
2. [ ] Batch UI + очередь (Celery/RQ или отдельный worker) (A1).
3. [ ] Мульти-accountant ZIP (A4).
4. [ ] История метаданных + повторный экспорт, если файл ещё в retention (A2).
5. [ ] Дубликаты до тяжёлого KoSIT, если возможно (A3).
6. [ ] Профиль организации в пакет (A6).

Критерий готовности: Meister загружает 10 счетов и скачивает один ZIP для Kanzlei.

### Этап 3 — монетизация

Ориентир: 2–3 недели, можно параллельно с концом этапа 2.

- [ ] Stripe Billing или Mollie (DE/VAT): месяц / год, счета.
- [ ] Webhook → `plan`, `seats`, `status` (active / past_due / canceled).
- [ ] Customer portal: карта, отмена, invoices.
- [ ] Paywall только на batch / history / повышенный лимит — не на гостевой parse.
- [ ] Немецкие тексты тарифа на лендинге: отличие от ELSTER и от Buchhaltung
      (`TODO_VIP_PRODUCT.md` P1 SEO/сравнение; `TODO_CONCURENT.md` §7.1).

### Этап 4 — Firma и интеграции

Только после первых платящих Plus.

- [ ] Team seats и роли (B11).
- [ ] Empfang API v1 + ключи + квоты (B10).
- [ ] Email-ingest (B9).
- [ ] Mandanten-Link (B7).
- [ ] Mapping Kreditor/Konto (B8).

### Этап 5 — только по подтверждённому спросу

- [ ] Add-on «XRechnung erstellen» **или** партнёрский convert (buy, не reinvent).
- [ ] Kanzlei: несколько Mandanten, общий mapping; white-label не обещать заранее.
- [ ] On-prem / privacy-sensitive — отдельный прайс.
- [ ] Официальные интеграции DATEV / sevDesk / Lexware / DMS — P2 продукта.
- [ ] Пересмотреть Ausstellungspflicht 2027+ по мониторингу в `TODO_CONCURENT.md` §7.3.

---

## 6. Технический скелет

Не ломать текущий гостевой API. Новый слой — квоты, орг-контекст и отдельные v1-роуты.

```
guest  ──► POST /api/invoices/parse          (как сейчас, без хранения)
user   ──► same + org context + quota middleware
plus   ──► POST /api/invoices/batch
       ──► GET  /api/invoices/history
       ──► POST /api/exports/accountant-package  (несколько id)
team   ──► Authorization: Bearer einv_live_...
       ──► POST /v1/invoices/parse
```

Новое относительно текущего репозитория (сейчас нет персистентного store счетов):

- [x] Postgres: users, orgs, memberships, plans (invoice_jobs, invoice_records, api_keys — этапы 2/4).
- [ ] Object storage S3-compatible **в DE** только для opt-in файлов: TTL, encryption at rest.
- [ ] Очередь для batch/KoSIT.
- [ ] Идемпотентность batch и дедуп до запуска validator, где это безопасно.
- [ ] Default хранения оригинала: **выкл**.

---

## 7. Приоритет (ценность × сложность)

```
Высокая ценность, умеренная сложность     ← Plus v1
  Batch + мульти-ZIP + лимиты
  История метаданных + дубликаты
  Профиль фирмы / Steuerberater

Высокая ценность, высокая сложность       ← этап 4
  Email-ingest
  Empfang API + квоты
  DATEV mapping per Kreditor
  Биллинг + VAT + org seats

Отложить
  Генератор XRechnung
  GoBD-архив
  Peppol, white-label, on-prem
```

---

## 8. Рекомендуемый порядок относительно VIP-продукта

Повторяет и уточняет раздел 4 в `TODO_VIP_PRODUCT.md`:

1. P0: KoSIT, legal/AVV, security review (`TODO_VIP_PRODUCT.md` §4 п.1–2).
2. P0: пилот DATEV + Handwerk, метрики (`TODO_VIP_PRODUCT.md` §4 п.3, 5 и 1.9).
3. Этап 1–2 этой подписки = детализация «batch, история, дубликаты, мульти-ZIP».
4. Этап 3 — оплата, когда Plus уже можно показать пилотным фирмам.
5. Этап 4–5 = P2 продукта (API, email, Kanzlei), только после спроса.

Не начинать регистрацию и хранение счетов, пока гостевой Empfang не проверен пилотом.
