// timer_manager.cpp
#include <ncurses.h>
#include <json.hpp>
#include <fstream>
#include <vector>
#include <string>
#include <unistd.h>
#include <chrono>
#include <thread>

using json = nlohmann::json;

struct Timer {
    std::string name;
    double duration; // seconds
    double elapsed;
    bool running;
    bool finished;

    double remaining() const {
        if (finished) return 0;
        double rem = duration - elapsed;
        return rem > 0 ? rem : 0;
    }

    bool update(double dt) {
        if (running && !finished) {
            elapsed += dt;
            if (elapsed >= duration) {
                elapsed = duration;
                running = false;
                finished = true;
                return true;
            }
        }
        return false;
    }

    json to_json() const {
        return {{"name", name}, {"duration", duration}, {"elapsed", elapsed}, {"running", running}, {"finished", finished}};
    }

    static Timer from_json(const json& j) {
        return {j["name"], j["duration"], j["elapsed"], j["running"], j["finished"]};
    }
};

class TimerManager {
public:
    std::vector<Timer> timers;
    int selected;
    bool running;
    std::string saveFile;

    TimerManager(const std::string& save) : selected(0), running(true), saveFile(save) {
        load();
        if (timers.empty()) {
            timers.push_back({"Pomodoro", 25*60, 0, false, false});
            timers.push_back({"Break", 5*60, 0, false, false});
        }
    }

    void addTimer(const std::string& name, double duration) {
        timers.push_back({name, duration, 0, false, false});
        save();
    }

    void removeTimer(int idx) {
        if (idx < 0 || idx >= (int)timers.size()) return;
        timers.erase(timers.begin() + idx);
        if (selected >= (int)timers.size()) selected = timers.size()-1;
        save();
    }

    void toggle(int idx) {
        if (idx < 0 || idx >= (int)timers.size()) return;
        Timer& t = timers[idx];
        if (t.finished) {
            t.elapsed = 0;
            t.finished = false;
            t.running = true;
        } else {
            t.running = !t.running;
        }
        save();
    }

    void reset(int idx) {
        if (idx < 0 || idx >= (int)timers.size()) return;
        Timer& t = timers[idx];
        t.elapsed = 0;
        t.running = false;
        t.finished = false;
        save();
    }

    void update(double dt) {
        for (auto& t : timers) {
            if (t.update(dt)) {
                mvprintw(0, 0, "!!! Timer '%s' finished !!!", t.name.c_str());
            }
        }
    }

    void save() {
        json j = json::array();
        for (const auto& t : timers) j.push_back(t.to_json());
        std::ofstream file(saveFile);
        file << j.dump(4);
    }

    void load() {
        std::ifstream file(saveFile);
        if (file.is_open()) {
            json j;
            file >> j;
            for (const auto& item : j) {
                timers.push_back(Timer::from_json(item));
            }
        }
    }

    void run() {
        initscr();
        cbreak();
        noecho();
        keypad(stdscr, TRUE);
        curs_set(0);
        nodelay(stdscr, TRUE);

        auto last = std::chrono::steady_clock::now();
        int ch;
        while (running) {
            clear();
            mvprintw(0, 0, "=== Timer Manager ===");
            mvprintw(1, 0, "Timers: %zu   [a]dd  [d]elete  [Space]toggle  [r]eset  [q]uit", timers.size());

            int line = 3;
            for (int i=0; i<(int)timers.size(); i++) {
                Timer& t = timers[i];
                double rem = t.remaining();
                const char* status = t.finished ? " ✓" : (t.running ? " ▶" : " ⏸");
                char buf[100];
                sprintf(buf, "%d. %s %s  %02.0f:%02.0f / %02.0f:%02.0f",
                        i+1, t.name.c_str(), status,
                        rem/60, fmod(rem,60),
                        t.duration/60, fmod(t.duration,60));
                if (i == selected) attron(A_REVERSE);
                else {
                    int color = t.running ? COLOR_GREEN : (t.finished ? COLOR_RED : COLOR_YELLOW);
                    attron(COLOR_PAIR(color));
                }
                mvprintw(line, 0, "%s", buf);
                if (i == selected) attroff(A_REVERSE);
                else attroff(COLOR_PAIR(t.running ? COLOR_GREEN : (t.finished ? COLOR_RED : COLOR_YELLOW)));
                line++;
            }
            mvprintw(line+1, 0, "Commands: a=add, d=delete, Space=toggle, r=reset, q=quit");
            refresh();

            ch = getch();
            if (ch == 'q' || ch == 27) running = false;
            else if (ch == 'a') {
                echo();
                char name[100]; int dur;
                mvprintw(20, 0, "Enter name: ");
                getstr(name);
                mvprintw(21, 0, "Enter duration (seconds): ");
                scanw("%d", &dur);
                noecho();
                addTimer(name, dur);
            } else if (ch == 'd') {
                if (!timers.empty()) removeTimer(selected);
            } else if (ch == ' ') {
                if (!timers.empty()) toggle(selected);
            } else if (ch == 'r') {
                if (!timers.empty()) reset(selected);
            } else if (ch == KEY_UP) {
                if (selected > 0) selected--;
            } else if (ch == KEY_DOWN) {
                if (selected < (int)timers.size()-1) selected++;
            }

            auto now = std::chrono::steady_clock::now();
            double dt = std::chrono::duration<double>(now - last).count();
            last = now;
            update(dt);
            usleep(50000);
        }
        endwin();
        save();
    }
};

int main() {
    TimerManager tm("timers.json");
    tm.run();
    return 0;
}
