⏱️ Таймер-менеджер — управляйте временем с умом
Версия: 1.0.0 | Лицензия: MIT | Статус: ✅ Активная разработка

https://img.shields.io/github/repo-size/yourusername/multi-timer https://img.shields.io/github/last-commit/yourusername/multi-timer https://img.shields.io/github/languages/count/yourusername/multi-timer

⏳ Описание
Таймер-менеджер – это консольное приложение для создания и управления несколькими таймерами одновременно. Идеально подходит для готовки, тренировок, работы по методу Pomodoro или любых других задач, где требуется отслеживать несколько временных интервалов.

Программа поддерживает:

✅ Создание неограниченного количества таймеров с пользовательскими именами

✅ Запуск, пауза и сброс каждого таймера по отдельности

✅ Отображение оставшегося времени в реальном времени (формат ЧЧ:ММ:СС)

✅ Звуковое и текстовое уведомление по окончании таймера

✅ Сохранение и загрузка состояния таймеров в JSON-файл

✅ Интерактивный интерфейс с клавиатурным управлением

✅ Работа в фоновом режиме (опционально)

Проект содержит 8 полноценных реализаций на разных языках программирования. Все версии используют консольный интерфейс и минимальные зависимости.

✨ Возможности
🔹 Мультизадачность – запускайте несколько таймеров параллельно

🔹 Именованные таймеры – легко идентифицируйте каждый таймер

🔹 Управление – клавиши для старта, паузы, сброса и удаления

🔹 Автосохранение – состояние автоматически сохраняется при выходе

🔹 Уведомления – звуковой сигнал и сообщение при завершении

🔹 Кроссплатформенность – работает в Linux, macOS, Windows (WSL/Cygwin)

🔹 Настраиваемый интервал обновления – частота обновления экрана

🖥️ Скриншоты
(В реальном репозитории замените на свои изображения)

https://via.placeholder.com/800x400?text=%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA+%D1%82%D0%B0%D0%B9%D0%BC%D0%B5%D1%80%D0%BE%D0%B2
Отображение активных таймеров с прогресс-барами.

https://via.placeholder.com/800x400?text=%D0%A3%D0%B2%D0%B5%D0%B4%D0%BE%D0%BC%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5+%D0%BE+%D0%B7%D0%B0%D0%B2%D0%B5%D1%80%D1%88%D0%B5%D0%BD%D0%B8%D0%B8
Сообщение по окончании таймера.

📦 Установка и запуск
Каждая реализация находится в отдельной папке. Для запуска требуется компилятор/интерпретатор и, при необходимости, зависимости.

Язык	Файл	Зависимости	Команда запуска
Python	timer_manager.py	curses (встроен)	python3 timer_manager.py
Go	timer_manager.go	golang.org/x/term	go run timer_manager.go
Rust	timer_manager.rs	crossterm, serde_json	cargo run
C++	timer_manager.cpp	ncurses, nlohmann/json	g++ -std=c++17 -lncurses -o timer timer_manager.cpp && ./timer
Java	TimerManager.java	нет (ANSI-коды)	javac TimerManager.java && java TimerManager
C#	timer_manager.cs	Newtonsoft.Json	dotnet add package Newtonsoft.Json && dotnet run
Ruby	timer_manager.rb	io/console, json	ruby timer_manager.rb
Node.js	timer_manager.js	blessed	npm install blessed && node timer_manager.js
📂 Структура репозитория
text
.
├── README.md
├── python/
│   └── timer_manager.py
├── go/
│   └── timer_manager.go
├── rust/
│   ├── Cargo.toml
│   └── src/
│       └── main.rs
├── cpp/
│   └── timer_manager.cpp
├── java/
│   └── TimerManager.java
├── csharp/
│   └── timer_manager.cs
├── ruby/
│   └── timer_manager.rb
└── javascript/
    ├── package.json
    └── timer_manager.js
🛠️ Особенности реализаций
Python – использует curses для интерфейса, простота и гибкость.

Go – высокая производительность, нативная работа с терминалом.

Rust – безопасность и скорость, управление памятью.

C++ – классический ncurses, быстрый и надёжный.

Java – ANSI-коды, работает на любой JVM.

C# – аналогично Java, использует ANSI.

Ruby – встроенный io/console, элегантный синтаксис.

Node.js – blessed для полноценного TUI.

🎮 Управление (общее для всех версий)
Добавить таймер – нажмите a и введите имя и длительность (в секундах)

Удалить таймер – выделите таймер и нажмите d

Запустить/Пауза – выделите и нажмите Space

Сбросить – выделите и нажмите r

Выход – q или Esc (состояние сохраняется)

🤝 Вклад
PR и issues приветствуются. Добавляйте новые фичи, улучшайте интерфейс, поддержку большего количества форматов сохранения.

📄 Лицензия
MIT License.
