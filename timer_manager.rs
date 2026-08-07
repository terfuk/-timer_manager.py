// timer_manager.rs
use crossterm::{
    cursor, event, terminal, ExecutableCommand, QueueableCommand, Result,
    style::{Color, Print, ResetColor, SetForegroundColor, SetBackgroundColor},
};
use serde::{Deserialize, Serialize};
use std::fs;
use std::io::{stdout, Write};
use std::time::{Duration, Instant};

#[derive(Serialize, Deserialize, Clone)]
struct Timer {
    name: String,
    duration: f64, // seconds
    elapsed: f64,
    running: bool,
    finished: bool,
}

impl Timer {
    fn remaining(&self) -> f64 {
        if self.finished { 0.0 } else { (self.duration - self.elapsed).max(0.0) }
    }
    fn update(&mut self, dt: f64) -> bool {
        if self.running && !self.finished {
            self.elapsed += dt;
            if self.elapsed >= self.duration {
                self.elapsed = self.duration;
                self.running = false;
                self.finished = true;
                return true;
            }
        }
        false
    }
}

struct TimerManager {
    timers: Vec<Timer>,
    selected: usize,
    save_file: String,
    running: bool,
}

impl TimerManager {
    fn new(save_file: &str) -> Self {
        let mut tm = TimerManager {
            timers: Vec::new(),
            selected: 0,
            save_file: save_file.to_string(),
            running: true,
        };
        tm.load();
        if tm.timers.is_empty() {
            tm.timers.push(Timer { name: "Pomodoro".to_string(), duration: 25.0*60.0, elapsed: 0.0, running: false, finished: false });
            tm.timers.push(Timer { name: "Break".to_string(), duration: 5.0*60.0, elapsed: 0.0, running: false, finished: false });
        }
        tm
    }

    fn add_timer(&mut self, name: String, duration: f64) {
        self.timers.push(Timer { name, duration, elapsed: 0.0, running: false, finished: false });
        self.save();
    }

    fn remove_timer(&mut self, idx: usize) {
        if idx < self.timers.len() {
            self.timers.remove(idx);
            if self.selected >= self.timers.len() { self.selected = self.timers.len().saturating_sub(1); }
            self.save();
        }
    }

    fn toggle(&mut self, idx: usize) {
        if idx < self.timers.len() {
            let t = &mut self.timers[idx];
            if t.finished {
                t.elapsed = 0.0;
                t.finished = false;
                t.running = true;
            } else {
                t.running = !t.running;
            }
            self.save();
        }
    }

    fn reset(&mut self, idx: usize) {
        if idx < self.timers.len() {
            let t = &mut self.timers[idx];
            t.elapsed = 0.0;
            t.running = false;
            t.finished = false;
            self.save();
        }
    }

    fn update(&mut self, dt: f64) {
        for t in &mut self.timers {
            if t.update(dt) {
                // notification
                println!("\n!!! Timer '{}' finished !!!", t.name);
            }
        }
    }

    fn save(&self) {
        let data = serde_json::to_string_pretty(&self.timers).unwrap();
        fs::write(&self.save_file, data).ok();
    }

    fn load(&mut self) {
        if let Ok(data) = fs::read_to_string(&self.save_file) {
            if let Ok(timers) = serde_json::from_str(&data) {
                self.timers = timers;
            }
        }
    }

    fn run(&mut self) -> Result<()> {
        let mut stdout = stdout();
        terminal::enable_raw_mode()?;
        stdout.execute(cursor::Hide)?;

        let mut last_update = Instant::now();

        while self.running {
            stdout.execute(terminal::Clear(terminal::ClearType::All))?;
            stdout.queue(cursor::MoveTo(0, 0))?.queue(Print("=== Timer Manager ==="))?;
            stdout.queue(cursor::MoveTo(0, 1))?.queue(Print(format!("Timers: {}   [a]dd  [d]elete  [Space]toggle  [r]eset  [q]uit", self.timers.len())))?;

            let mut line = 3;
            for (i, t) in self.timers.iter().enumerate() {
                let rem = t.remaining();
                let status = if t.finished { " ✓" } else if t.running { " ▶" } else { " ⏸" };
                let display = format!("{}. {} {}  {:02.0}:{:02.0} / {:02.0}:{:02.0}",
                    i+1, t.name, status,
                    rem/60.0, rem%60.0,
                    t.duration/60.0, t.duration%60.0);
                stdout.queue(cursor::MoveTo(0, line))?;
                if i == self.selected {
                    stdout.queue(SetBackgroundColor(Color::White))?.queue(SetForegroundColor(Color::Black))?
                          .queue(Print(display))?.queue(ResetColor)?;
                } else {
                    let color = if t.running { Color::Green } else if t.finished { Color::Red } else { Color::Yellow };
                    stdout.queue(SetForegroundColor(color))?.queue(Print(display))?.queue(ResetColor)?;
                }
                line += 1;
            }
            stdout.queue(cursor::MoveTo(0, line+1))?.queue(Print("Commands: a=add, d=delete, Space=toggle, r=reset, q=quit"))?;
            stdout.flush()?;

            // Non-blocking input
            if event::poll(Duration::from_millis(50))? {
                if let event::Event::Key(key) = event::read()? {
                    match key.code {
                        event::KeyCode::Char('q') => self.running = false,
                        event::KeyCode::Char('a') => {
                            // Упрощённо: ввод имени и длительности
                            // В реальном коде нужно организовать диалог, здесь пропустим для краткости
                        }
                        event::KeyCode::Char('d') => if !self.timers.is_empty() { self.remove_timer(self.selected); }
                        event::KeyCode::Char(' ') => if !self.timers.is_empty() { self.toggle(self.selected); }
                        event::KeyCode::Char('r') => if !self.timers.is_empty() { self.reset(self.selected); }
                        event::KeyCode::Up => if self.selected > 0 { self.selected -= 1; }
                        event::KeyCode::Down => if self.selected < self.timers.len()-1 { self.selected += 1; }
                        _ => {}
                    }
                }
            }

            // Update timers
            let now = Instant::now();
            let dt = now.duration_since(last_update).as_secs_f64();
            last_update = now;
            self.update(dt);
            std::thread::sleep(Duration::from_millis(50));
        }

        terminal::disable_raw_mode()?;
        stdout.execute(cursor::Show)?;
        Ok(())
    }
}

fn main() -> Result<()> {
    let mut manager = TimerManager::new("timers.json");
    manager.run()
}
