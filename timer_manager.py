# timer_manager.py
import curses
import json
import os
import time
import threading
import queue
from datetime import datetime

class Timer:
    def __init__(self, name, duration, elapsed=0, running=False):
        self.name = name
        self.duration = duration  # секунды
        self.elapsed = elapsed    # сколько прошло
        self.running = running
        self.finished = False

    def remaining(self):
        return max(0, self.duration - self.elapsed)

    def update(self, dt):
        if self.running and not self.finished:
            self.elapsed += dt
            if self.elapsed >= self.duration:
                self.elapsed = self.duration
                self.running = False
                self.finished = True
                return True  # сигнал о завершении
        return False

    def to_dict(self):
        return {
            'name': self.name,
            'duration': self.duration,
            'elapsed': self.elapsed,
            'running': self.running,
            'finished': self.finished
        }

    @classmethod
    def from_dict(cls, data):
        t = cls(data['name'], data['duration'], data['elapsed'], data['running'])
        t.finished = data.get('finished', False)
        return t

class TimerManager:
    def __init__(self, save_file='timers.json'):
        self.save_file = save_file
        self.timers = []
        self.selected = 0
        self.running = True
        self.last_update = time.time()
        self.notify_queue = queue.Queue()
        self.load()

    def add_timer(self, name, duration):
        self.timers.append(Timer(name, duration))
        self.save()

    def remove_timer(self, idx):
        if 0 <= idx < len(self.timers):
            del self.timers[idx]
            if self.selected >= len(self.timers):
                self.selected = len(self.timers) - 1
            self.save()

    def toggle(self, idx):
        if 0 <= idx < len(self.timers):
            t = self.timers[idx]
            if t.finished:
                # перезапуск
                t.elapsed = 0
                t.finished = False
                t.running = True
            else:
                t.running = not t.running
            self.save()

    def reset(self, idx):
        if 0 <= idx < len(self.timers):
            t = self.timers[idx]
            t.elapsed = 0
            t.running = False
            t.finished = False
            self.save()

    def update(self):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now
        for i, timer in enumerate(self.timers):
            if timer.update(dt):
                self.notify_queue.put(timer.name)

    def save(self):
        data = [t.to_dict() for t in self.timers]
        with open(self.save_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    self.timers = [Timer.from_dict(d) for d in data]
            except:
                self.timers = []

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    manager = TimerManager()
    if not manager.timers:
        # Добавим пример
        manager.add_timer("Pomodoro", 25*60)
        manager.add_timer("Break", 5*60)

    input_buffer = ""
    input_mode = False
    new_name = ""
    new_duration = ""

    while manager.running:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        # Заголовок
        stdscr.addstr(0, 0, "=== Timer Manager ===", curses.A_BOLD)
        stdscr.addstr(1, 0, f"Timers: {len(manager.timers)}   [a]dd  [d]elete  [Space]toggle  [r]eset  [q]uit", curses.color_pair(1))

        # Список таймеров
        max_display = height - 6
        start = max(0, manager.selected - max_display//2)
        end = min(len(manager.timers), start + max_display)
        for i in range(start, end):
            t = manager.timers[i]
            remaining = t.remaining()
            status = " ▶" if t.running else " ⏸" if not t.finished else " ✓"
            if t.finished:
                status = " ✓"
            line = f"{i+1}. {t.name} {status}  {int(remaining//60):02d}:{int(remaining%60):02d} / {t.duration//60:02d}:{t.duration%60:02d}"
            if i == manager.selected:
                stdscr.addstr(i-start+2, 0, line, curses.A_REVERSE)
            else:
                color = curses.color_pair(2) if t.running else curses.color_pair(3) if t.finished else curses.color_pair(4)
                stdscr.addstr(i-start+2, 0, line, color)

        # Уведомления
        try:
            while True:
                name = manager.notify_queue.get_nowait()
                stdscr.addstr(height-3, 0, f"!!! Timer '{name}' finished !!!", curses.A_BOLD | curses.color_pair(3))
        except queue.Empty:
            pass

        # Подсказка внизу
        stdscr.addstr(height-2, 0, "Commands: a=add, d=delete, Space=toggle, r=reset, q=quit")
        if input_mode:
            stdscr.addstr(height-1, 0, f"Enter name: {new_name}  (press Enter to confirm)")
        stdscr.refresh()

        # Обработка ввода
        key = stdscr.getch()
        if key == ord('q') or key == 27:
            manager.save()
            break
        elif input_mode:
            if key == 10:  # Enter
                if new_name and new_duration:
                    try:
                        dur = int(new_duration)
                        manager.add_timer(new_name, dur)
                    except:
                        pass
                input_mode = False
                new_name = ""
                new_duration = ""
            elif key == 27:
                input_mode = False
                new_name = ""
                new_duration = ""
            elif key == ord('\t'):
                # переключение между name и duration
                pass
            elif key == curses.KEY_BACKSPACE or key == 127:
                if len(new_name) > 0:
                    new_name = new_name[:-1]
            else:
                if 32 <= key <= 126:
                    new_name += chr(key)
        else:
            if key == ord('a'):
                input_mode = True
                new_name = ""
                new_duration = ""
                stdscr.addstr(height-1, 0, "Enter timer name: ")
                curses.echo()
                name = stdscr.getstr().decode()
                curses.noecho()
                stdscr.addstr(height-1, 0, "Enter duration (seconds): ")
                curses.echo()
                dur_str = stdscr.getstr().decode()
                curses.noecho()
                try:
                    dur = int(dur_str)
                    manager.add_timer(name, dur)
                except:
                    pass
                # Обновим сразу
            elif key == ord('d'):
                if manager.timers:
                    manager.remove_timer(manager.selected)
            elif key == ord(' '):
                if manager.timers:
                    manager.toggle(manager.selected)
            elif key == ord('r'):
                if manager.timers:
                    manager.reset(manager.selected)
            elif key == curses.KEY_UP:
                manager.selected = max(0, manager.selected-1)
            elif key == curses.KEY_DOWN:
                manager.selected = min(len(manager.timers)-1, manager.selected+1)

        # Обновление таймеров
        manager.update()
        time.sleep(0.05)

if __name__ == "__main__":
    curses.wrapper(main)
