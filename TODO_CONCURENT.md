# Анализ конкурентов — eInvoice (приём XRechnung / ZUGFeRD)

Документ: обзор рынка и конкурентов для веб-утилиты **eInvoice**.  
Фокус продукта: немецкие B2B SME / Handwerk — **приём** (не отправка) электронных счетов: загрузка → чтение → валидация → экспорт в бухгалтерию (CSV / Excel / DATEV).

Связанные документы: `TODO_VIP_PRODUCT.md` (качество MVP), `TODO_SUBSCRIPTION.md` (регистрация и платный Empfang).

Дата обзора: август 2026.

---

## 1. Позиционирование eInvoice (база для сравнения)

| Параметр | eInvoice |
|----------|----------|
| Главная боль | Получил XRechnung/ZUGFeRD и не понимаю, что платить / что отдать Steuerberater |
| Happy path | Upload → Parse → Validate → читаемый счёт → предупреждение PDF↔XML (ZUGFeRD) → Export |
| Целевая аудитория | Мастерские, ремесленники, мелкий B2B + помощник Steuerberater |
| Не в MVP | PEPPOL, отправка счетов, замена ERP, полноценный SaaS-биллинг |

**Ключевой дифференциатор:** лёгкий «приёмник + экспорт для бухгалтера», а не полная бухгалтерия и не генератор исходящих E-Rechnungen.

---

## 2. Карта рынка (типы игроков)

| Тип | Примеры | Пересечение с eInvoice |
|-----|---------|------------------------|
| A. Официальный / бесплатный viewer | ELSTER E-Rechnung-Viewer | Очень высокое (бесплатный «просто открыть») |
| B. Offline open-source viewer/validator | Quba, Open XRechnung Toolbox | Высокое (privacy + валидация) |
| C. Онлайн utility (viewer / validate / convert) | RechneX, Get ZUGFeRD, xrechnungs.de | Максимальное (тот же сегмент utility) |
| D. Desktop toolkit | Treesoft E-Rechnung Toolkit | Среднее–высокое |
| E. Бухгалтерия / Belegplattform | sevDesk, Lexware Office, DATEV UO, Norman | Косвенное (поглощают сценарий «всё в одном») |
| F. Developer API / white-label SaaS | [rechnungsapi.de](https://www.rechnungsapi.de) | Среднее по UX Handwerk; высокое по parse/validate/API и Kanzlei |

---

## 3. Сводная таблица конкурентов

Легенда оценок относительно ценности eInvoice (приём + чтение + валидация + DATEV/Excel):  
●●● сильная сторона · ●● средняя · ● слабая / нет · — не применимо

| Конкурент | Тип | Цена (ориентир) | Viewer | ZUGFeRD | Валидация EN 16931 | PDF↔XML check | Экспорт DATEV/Excel | Отправка / генерация | UX для Handwerk |
|-----------|-----|-----------------|--------|---------|--------------------|---------------|---------------------|----------------------|-----------------|
| **ELSTER Viewer** | A | Бесплатно | ●●● | ● (слабее; фокус XRechnung) | ● | — | — | — | ●●● (доверие государства) |
| **Quba Viewer** | B | Бесплатно (OSS) | ●●● | ●●● | ●● (через Mustang online) | ●● | — | — | ●● (нужна установка) |
| **Open XRechnung Toolbox** | B | Бесплатно (OSS) | ●●● | ●● (EN 16931 XML) | ●●● (KoSIT) | — | — | — | ● (техничнее) |
| **RechneX** | C | Free + Pro ~12–19 €/мес | ●●● | ●●● | ●●● | ● | ● (DATEV скорее как convert, не «пакет бухгалтеру») | ●●● | ●●● |
| **Get ZUGFeRD** | C | Free лимит + Premium | ●●● | ●●● | ●●● (отдельные tools) | ● | ● | ●●● | ●●● |
| **xrechnungs.de** | C | Бесплатный viewer | ●●● | ●● | ● | — | — | ● | ●●● |
| **Treesoft Toolkit** | D | Платный desktop | ●●● | ●●● | ●●● | ● | ●● (архив / workflow) | ●●● | ●● |
| **sevDesk** | E | Free / от ~14 €/мес | ●● | ●●● | ●● | — | ●●● | ●●● | ●●● |
| **Lexware Office** | E | от ~8 €/мес | ●● | ●●● | ●● | — | ●●● (DATEVconnect) | ●●● | ●●● |
| **DATEV Unternehmen online** | E | через Steuerberater | ●● | ●●● | ●●● | — | ●●● (native) | ●● | ●● |
| **Norman** | E | Free-план заявлен | ●●● | ●●● | ●● | — | ●● (в книгу учёта) | ●● | ●●● |
| **rechnungsapi.de** | F | Free: 10 сч./мес API + бесплатный Validator; далее платные тарифы | ●● (email→читаемый PDF; не Handwerk-UI) | ●●● | ●●● | ● | ●● (JSON/ERP; не DATEV-пакет Meister→Kanzlei) | ●●● | ● (для Meister) / ●●● (для IT) |

---

## 4. Плюсы и минусы по конкурентам

### 4.1 ELSTER E-Rechnung-Viewer (`e-rechnung.elster.de`)

| + Плюсы | − Минусы |
|---------|----------|
| Официальный сервис налоговой администрации — максимальное доверие | По сути только визуализация XRechnung, не полноценный продукт-workflow |
| Бесплатно, без регистрации | Лимиты: 1 файл, ~10 MB |
| Нулевая установка, знаком Handwerk через Innungen / BMF | Нет DATEV/Excel-экспорта «для Steuerberater» |
| Закрывает минимальную обязанность «мочь прочитать» | Нет явной проверки несоответствия PDF↔XML у ZUGFeRD |
| | Нет пакета «отправить бухгалтеру» |

**Угроза для eInvoice:** высокий — «зачем платить, если ELSTER бесплатно открывает».  
**Контратака:** валидация простым языком + mismatch ZUGFeRD + one-click export CSV/Excel/DATEV + пакет для Steuerberater.

---

### 4.2 Quba Viewer (ZUGFeRD / open source)

| + Плюсы | − Минусы |
|---------|----------|
| Бесплатно, offline — данные не уходят в облако | Нужна установка (Win/Mac/Linux) |
| XRechnung + Factur-X/ZUGFeRD | Нет готового DATEV/Excel-экспорта под Handwerk |
| Privacy-friendly (сильный аргумент для Kanzlei) | UX ближе к «утилите сообщества», не к продукту для Meister |
| Может помогать проверять согласованность hybrid-документов | Валидация зависит от онлайн Mustangserver |
| Open source, доверие технической аудитории | Нет «accountant package» / немецких next-step подсказок |

**Угроза:** средняя (для privacy-sensitive пользователей).  
**Контратака:** web без установки + явный export + немецкие подсказки «что делать дальше».

---

### 4.3 Open XRechnung Toolbox (OXT)

| + Плюсы | − Минусы |
|---------|----------|
| Официальные KoSIT-компоненты (валидация + визуализация) | Desktop/Java, порог входа выше |
| HTML/PDF visualization, отчёты валидации | Ориентация на XRechnung / Peppol, не на Handwerk-workflow |
| Leitweg-ID калькулятор, CLI | Нет фокуса на DATEV-пакет для Steuerberater |
| Бесплатно и прозрачно | UI не «30 секунд до понимания суммы» для Meister |

**Угроза:** низкая–средняя (скорее для IT/администраций).  
**Контратака:** простота и экспорт, а не «ещё один KoSIT GUI».

---

### 4.4 RechneX (`rechnex.de`) — ближайший онлайн-конкурент

| + Плюсы | − Минусы |
|---------|----------|
| Полный utility-стек: viewer, validator (KoSIT/Mustang), convert PDF→XRechnung/ZUGFeRD | Сильный уклон в **создание/конвертацию исходящих** счетов |
| Понятный freemium (лимиты на free) | Не замена DATEV; DATEV — скорее convert «из DATEV-PDF в E-Rechnung» |
| Batch, Pro ~12–19 €/мес | Privacy: загрузка реальных счетов в чужой SaaS |
| Немецкоязычный продукт, быстрый старт в браузере | Меньше акцента на «пакет для Steuerberater» при **входящих** |
| | Риск «ещё один converter» — шум на рынке |

**Угроза:** высокая (тот же канал поиска: «XRechnung öffnen / validieren»).  
**Контратака:** узкий фокус **Empfang** + mismatch PDF↔XML + экспорт CSV/Excel/DATEV + accountant ZIP, без раздувания в генератор.

---

### 4.5 Get ZUGFeRD (`getzugferd.com`)

| + Плюсы | − Минусы |
|---------|----------|
| Очень широкий набор tools (viewer, validate, convert, extract, create) | Free: жёсткие дневные лимиты (маркетинг Premium) |
| Удобный browser viewer, ZUGFeRD XML extraction | Много функций → размытый фокус |
| Заявляют: файл в памяти, не хранят | Опять же: исходящая конвертация конкурирует за внимание |
| PDF-preview из XRechnung | Датаenschutz нужно проверять отдельно (как у любого online) |

**Угроза:** высокая в SEO/«открыть XRechnung онлайн».  
**Контратака:** немецкая UX специально для Handwerk + валидация простым языком + DATEV/Excel mapping для Steuerberater.

---

### 4.6 xrechnungs.de (и похожие free online viewers)

| + Плюсы | − Минусы |
|---------|----------|
| Бесплатно, без установки | Часто только просмотр |
| Низкий порог | Слабая/непрозрачная валидация |
| Хорошо ловят поисковый трафик | Сомнения по Datenschutz у пользователей |
| | Нет экспорта в бухгалтерию |

**Угроза:** средняя (забирают «просто посмотреть»).  
**Контратака:** trust + validation + export в одном happy path.

---

### 4.7 Treesoft E-Rechnung Toolkit

| + Плюсы | − Минусы |
|---------|----------|
| Локальная установка, без cloud-принуждения | Платный desktop, внедрение тяжелее |
| Приём + создание + валидация + архив | Не web-MVP «открыл и готово» |
| Подходит, если ERP не умеет E-Rechnung | Overkill для Meister, которому нужно 5 счетов в неделю |
| GoBD-ориентированное хранение | Конкурирует скорее с «дополнением к ERP» |

**Угроза:** низкая–средняя для целевого Handwerk-solo.  
**Контратака:** мгновенный web-flow без покупки toolkit.

---

### 4.8 sevDesk / Lexware Office (косвенные)

| + Плюсы | − Минусы |
|---------|----------|
| Полный цикл: Belege, банк, UStVA, исходящие счета | Дорого и тяжело, если нужна только «прочитать входящий XML» |
| Встроенный приём XRechnung/ZUGFeRD | Смена привычного процесса / обучение |
| DATEV-передача (особенно Lexware DATEVconnect) | Не решают узкую боль «файл с почты → понять за 30 сек» без перехода в бухгалтерию |
| Знакомы Handwerk | Избыточность для пользователя, который уже отдаёт всё Steuerberater |

**Угроза:** высокая на длинной дистанции (поглощение сценария).  
**Контратака:** complementary tool — «до DATEV/sevDesk/Lexware»: быстро понять + отдать пакет бухгалтеру, без подписки на полную Buchhaltung.

---

### 4.9 DATEV Unternehmen online

| + Плюсы | − Минусы |
|---------|----------|
| Стандарт Steuerberater в DE | Не «открыть файл за 30 секунд» для Meister |
| Нативный приём/обработка E-Rechnung + ASR | Зависит от Kanzlei / тарифов |
| Максимальное доверие к проводкам | Сложность и стоимость для малого Handwerk |
| | Не конкурирует в SEO «XRechnung Viewer» напрямую |

**Угроза:** косвенная (Steuerberater тянет клиента в DATEV).  
**Контратака:** быть **мостом** в DATEV (чистый EXTF/CSV + mapping-док), не пытаться заменить DATEV.

---

### 4.10 Norman (и похожие «финансы + E-Rechnung»)

| + Плюсы | − Минусы |
|---------|----------|
| Приём + читаемый вид + хранение (в т.ч. free claims) | Уводит в полноценный financial product |
| Email-ingest / автоматизация | Другой ICP и go-to-market |
| GoBD-архив как ценность | Слабее как «одноразовая утилита» |

**Угроза:** средняя.  
**Контратака:** оставаться лёгким receiver/export utility без lock-in.

---

### 4.11 rechnungsapi.de — API / white-label SaaS ([сайт](https://www.rechnungsapi.de))

**Кто это:** немецкая REST API и SaaS для E-Rechnung (с 2018, позиционируют себя как ZUGFeRD-пионеры). Не «кнопка для Meister», а инфраструктура: ERP, IT-команды, SaaS, Kanzleien, n8n/Make/Zapier, Excel-макросы.

**Что умеют (по публичному сайту):**
- Создавать / конвертировать **XRechnung** и **ZUGFeRD** (в т.ч. PDF → структурированная E-Rechnung через KI)
- Валидировать XML/ZUGFeRD (есть **бесплатный eRechnung-Validator** без регистрации)
- Извлекать данные в **JSON** для ERP
- **E-Mail-Workflow:** входящая XRechnung → ответ с читаемым ZUGFeRD-PDF + XML
- White-label для Steuerberater / E-Invoicing-партнёров; Peppol — через партнёров (свой Access Point не заявляют)
- Хостинг в DE (Open Telekom Cloud), ISO/IEC 27001 у процессора, DSGVO + AVV; данные после обработки заявляют как не хранящиеся долговременно
- Free API: **10 счетов/мес** без карты; XRechnung 3.0.1, ZUGFeRD 2.4 / Factur-X

| + Плюсы | − Минусы |
|---------|----------|
| Зрелый API-продукт: parse, validate, create, convert в одном B2B-предложении | ICP — разработчики/ERP/Kanzlei-автоматизация, не Handwerk «drag & drop за 30 сек» |
| Сильный trust: серверы в DE, AVV, ISO-инфра, немецкий support | Нет явного фокуса на DATEV/Excel **accountant package** для Meister |
| Бесплатный Validator без логина — перехватывает SEO «prüfen» | Outbound/convert (Ausstellung) доминирует в повествовании; Empfang — часть, не весь продукт |
| Email-workflow делает XRechnung «читаемой» без новой UI | Порог: токен, интеграция, n8n — для Meister избыточно |
| White-label + сегмент Steuerberater — пересечение с вашим пилотом Kanzlei | Маркетинг «Vorsteuer-Sicherheit» / полная Umstellung — шире и рискованнее по обещаниям, чем eInvoice disclaimer |
| Может стать **поставщиком бэкенда** (buy vs build) для чужих продуктов | Конкурирует с будущим «Solution 3: Public API» eInvoice, если вы пойдёте в developer-API |

**Пересечение с eInvoice**

| Область | rechnungsapi.de | eInvoice |
|---------|-----------------|----------|
| Открыть/понять счёт | Email→PDF или JSON в чужой системе | Web UI для Meister |
| Валидация | Free validator + API | Валидация в UI простым немецким |
| ZUGFeRD PDF↔XML mismatch | Не выделенный USP | Явный UX-дифференциатор MVP |
| Экспорт Steuerberater | Через ERP/JSON/Kanzlei-tools | CSV / Excel / DATEV + ZIP-пакет |
| Генерация исходящих | Ядро бизнеса | Вне MVP (намеренно) |
| Канал | IT, SaaS, Kanzlei white-label | Handwerk + помощник Steuerberater |

**Угроза для eInvoice**
- **Сейчас (Handwerk MVP):** средняя — другой buyer и UX; Meister не покупает REST API.
- **Валидатор / «prüfen» SEO:** средняя–высокая — бесплатный validator уводит часть трафика «проверить файл».
- **Пилот Steuerberater:** высокая косвенная — Kanzlei может взять white-label API вместо лёгкого web-инструмента для Mandanten.
- **Post-MVP Public API:** высокая — прямой конкурент, если eInvoice productизирует API.

**Контратака**
1. Не соревноваться в «API для ERP» — оставаться Empfang-UI + Steuerberater-пакет.
2. На лендинге отдельно от ELSTER: «Validator + lesbare Rechnung + DATEV Export» (не только validate).
3. Для Kanzlei: white-label **не обещать**; предлагать простой Mandanten-link / пакет, complementary к DATEV.
4. Если позже нужен heavy convert/PDF-KI — рассматривать rechnungsapi как **возможный vendor** (build vs buy), а не копировать весь стек.
5. В `TODO_LIST_FUTURE.md` при Public API явно учесть: либо узкий Empfang-API, либо не идти в полный create/convert против зрелых игроков.

---

## 5. Сравнительная матрица «угроза × схожесть»

| Конкурент | Схожесть продукта | Угроза сейчас | Комментарий |
|-----------|-------------------|---------------|-------------|
| RechneX | ★★★★★ | Высокая | Тот же browser-utility сегмент |
| Get ZUGFeRD | ★★★★☆ | Высокая | Viewer + suite tools |
| ELSTER Viewer | ★★★☆☆ | Высокая | Free default для Handwerk |
| sevDesk / Lexware | ★★☆☆☆ | Высокая (долгосрочно) | Поглощают процесс целиком |
| **rechnungsapi.de** | ★★★☆☆ (функции) / ★☆☆☆☆ (UX Handwerk) | Средняя сейчас / высокая для API-будущего | Developer API + free Validator + Kanzlei white-label |
| Quba / OXT | ★★★☆☆ | Средняя | Offline / tech users |
| DATEV UO | ★★☆☆☆ | Средняя | Через Kanzlei |
| Treesoft | ★★★☆☆ | Низкая–средняя | Desktop toolkit |
| Free SEO-viewers | ★★☆☆☆ | Средняя | Забирают «просто открыть» |

---

## 6. Выводы: где eInvoice выигрывает / проигрывает

### Сильные стороны eInvoice относительно рынка
1. **Узкий Empfang-фокус** — меньше шума, чем у converter-suite (RechneX / Get ZUGFeRD).
2. **ZUGFeRD PDF↔XML mismatch** — редкий явный UX-дифференциатор у lightweight tools.
3. **One-click accounting export + accountant package** — то, чего нет у ELSTER / Quba / простых viewers.
4. **Немецкие next-step подсказки** (платить / спросить поставщика / экспортировать) — ближе к Handwerk, чем tech-validator UI.
5. **Не претендует на Vorsteuer-гарантию** — честный disclaimer vs маркетинг «всё легально автоматически».

### Слабые стороны / риски
1. ELSTER закрывает «просто посмотреть» бесплатно и с максимальным доверием.
2. Online-upload = чувствительный Datenschutz (конкурируют offline Quba/OXT/Treesoft; у rechnungsapi — сильный DE-hosting/AVV narrative).
3. Полные Buchhaltung (sevDesk/Lexware/DATEV) могут сделать отдельный viewer «лишним», если клиент уже внутри экосистемы.
4. Converter/API-продукты (RechneX, Get ZUGFeRD, **rechnungsapi.de**) сильнее в SEO, исходящем сценарии и B2B-интеграциях (2027/2028 Ausstellungspflicht).
5. Пока нет email-ingest / архива / API — меньше stickiness; email-readable workflow у rechnungsapi уже закрывает кусок «XRechnung пришла на почту».

### Рекомендуемое позиционирование (1 фраза)
> «Не бухгалтерия и не генератор счетов: за 30 секунд понять входящий XRechnung/ZUGFeRD, проверить ошибки и отдать Steuerberater готовый DATEV/Excel-пакет.»

---

## 7. TODO по конкурентной стратегии

### 7.1 Продукт (усилить дифференциаторы)
- [ ] На лендинге явно противопоставить ELSTER: «Viewer + Validierung + DATEV/Excel Export + ZUGFeRD Abgleich»
- [ ] Сделать mismatch PDF↔XML заметным USP (скрин/демо на `/`)
- [ ] Упаковать «Steuerberater-Paket» как главный CTA после просмотра
- [ ] Документ mapping (`EXPORT_MAPPING.md`) сделать публичным trust-артефактом для Kanzlei
- [ ] Добавить сравнительную таблицу «ELSTER vs eInvoice vs Buchhaltung» на лендинг (коротко)
- [ ] Privacy-режим: явный текст «файлы не храним / удаляем сразу» (+ опционально позже: локальный/on-prem)

### 7.2 Go-to-market
- [ ] SEO-страницы DE: «XRechnung öffnen», «ZUGFeRD prüfen», «XRechnung DATEV Export», «E-Rechnung Handwerk»
- [ ] Партнёрский пилот с 1–2 Steuerberater (валидация реального DATEV-пути)
- [ ] Материалы для Innungen / Handwerkskammer: «Empfangspflicht erfüllt + Export an Kanzlei»
- [ ] Не конкурировать лобово с sevDesk/Lexware: позиционировать как **дополнение**, не замену
- [ ] Не позиционировать eInvoice как «Rechnungs-API для ERP» против [rechnungsapi.de](https://www.rechnungsapi.de); для IT-buyer — другой продукт
- [ ] В питче Kanzlei явно отличать: Mandanten-Self-Service Empfang vs white-label API-платформа

### 7.3 Мониторинг конкурентов (регулярно)
- [ ] Раз в квартал пересматривать: ELSTER, RechneX, Get ZUGFeRD, **rechnungsapi.de**, Quba, OXT, sevDesk, Lexware, DATEV
- [ ] Следить за лимитами/ценами freemium у RechneX, Get ZUGFeRD и rechnungsapi (10/мес API + free Validator)
- [ ] Отслеживать, добавляют ли lightweight viewers DATEV-export (если да — ускорить USP)
- [ ] Следить, не появится ли у rechnungsapi простой Mandanten-Portal / Handwerk-UI (тогда угроза растёт)
- [ ] После 2027: оценить давление Ausstellungspflicht → не размывать Empfang-MVP без спроса

### 7.4 Решения «не делать пока»
- [ ] Не строить полный PDF→XRechnung generator как ядро (это поле RechneX / Get ZUGFeRD / **rechnungsapi.de**)
- [ ] Не обещать native DATEVconnect / замену Unternehmen online
- [ ] Не уходить в PEPPOL AP до подтверждённого спроса пилота
- [ ] Не копировать полный developer-API стек rechnungsapi; при необходимости — buy/partner, не reinvent

Монетизация Empfang (batch, история, дубликаты, узкий API, не генератор) —
в `TODO_SUBSCRIPTION.md`; критерии качества MVP — в `TODO_VIP_PRODUCT.md`.

---

## 8. Источники (для повторной проверки)

- ELSTER: https://e-rechnung.elster.de / https://www.elster.de/eportal/e-rechnung  
- Quba: https://github.com/ZUGFeRD/quba-viewer  
- Open XRechnung Toolbox: https://jcthiele.github.io/OpenXRechnungToolbox/  
- RechneX: https://rechnex.de/ (viewer, validator, Preise)  
- Get ZUGFeRD: https://www.getzugferd.com/preview  
- **rechnungsapi.de:** https://www.rechnungsapi.de (REST API, free Validator, email-workflow, Kanzlei/white-label)  
- Treesoft: https://treesoft.de/software/treesoft-e-rechnung-toolkit  
- sevDesk / Lexware / DATEV — обзоры рынка Buchhaltung + E-Rechnung 2025/2026  
- Контекст обязанности Empfangspflicht с 01.01.2025 (BMF / отраслевые разъяснения)

---

## 9. Краткий вердикт

| Вопрос | Ответ |
|--------|-------|
| Кто главный прямой конкурент? | **RechneX** и **Get ZUGFeRD** (online utility) + **ELSTER** (free default) |
| Кто главный API-/интеграционный конкурент? | **[rechnungsapi.de](https://www.rechnungsapi.de)** (ERP/SaaS/Kanzlei white-label; не Handwerk-UI) |
| Кто забирает бюджет клиента целиком? | **sevDesk / Lexware / DATEV** |
| Где окно для eInvoice? | Empfang-only + mismatch ZUGFeRD + one-click Steuerberater export, без ERP |
| Главный риск? | «Хватит ELSTER» / «уже есть sevDesk» / для API-будущего — «возьмём rechnungsapi» |
| Главный ответ на риск? | Скорость + понятная валидация + DATEV/Excel пакет именно для входящих |
