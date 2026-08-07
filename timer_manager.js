// timer_manager.js
const blessed = require('blessed');
const fs = require('fs');

class Timer {
    constructor(name, duration) {
        this.name = name;
        this.duration = duration;
        this.elapsed = 0;
        this.running = false;
        this.finished = false;
    }
    remaining() {
        if (this.finished) return 0;
        return Math.max(0, this.duration - this.elapsed);
    }
    update(dt) {
        if (this.running && !this.finished) {
            this.elapsed += dt;
            if (this.elapsed >= this.duration) {
                this.elapsed = this.duration;
                this.running = false;
                this.finished = true;
                return true;
            }
        }
        return false;
    }
}

class TimerManager {
    constructor(saveFile) {
        this.saveFile = saveFile || 'timers.json';
        this.timers = [];
        this.selected = 0;
        this.running = true;
        this.lastUpdate = Date.now();
        this.load();
        if (this.timers.length === 0) {
            this.timers.push(new Timer('Pomodoro', 25*60));
            this.timers.push(new Timer('Break', 5*60));
        }
    }

    addTimer(name, duration) {
        this.timers.push(new Timer(name, duration));
        this.save();
    }

    removeTimer(idx) {
        if (idx < 0 || idx >= this.timers.length) return;
        this.timers.splice(idx, 1);
        if (this.selected >= this.timers.length) this.selected = this.timers.length - 1;
        this.save();
    }

    toggle(idx) {
        if (idx < 0 || idx >= this.timers.length) return;
        const t = this.timers[idx];
        if (t.finished) {
            t.elapsed = 0;
            t.finished = false;
            t.running = true;
        } else {
            t.running = !t.running;
        }
        this.save();
    }

    reset(idx) {
        if (idx < 0 || idx >= this.timers.length) return;
        const t = this.timers[idx];
        t.elapsed = 0;
        t.running = false;
        t.finished = false;
        this.save();
    }

    update() {
        const now = Date.now();
        const dt = (now - this.lastUpdate) / 1000;
        this.lastUpdate = now;
        for (const t of this.timers) {
            if (t.update(dt)) {
                // notification
                screen.displayLine(`!!! Timer '${t.name}' finished !!!`);
            }
        }
    }

    save() {
        const data = this.timers.map(t => ({
            name: t.name,
            duration: t.duration,
            elapsed: t.elapsed,
            running: t.running,
            finished: t.finished
        }));
        fs.writeFileSync(this.saveFile, JSON.stringify(data, null, 2));
    }

    load() {
        try {
            const data = JSON.parse(fs.readFileSync(this.saveFile));
            this.timers = data.map(d => {
                const t = new Timer(d.name, d.duration);
                t.elapsed = d.elapsed;
                t.running = d.running;
                t.finished = d.finished;
                return t;
            });
        } catch (e) {}
    }
}

const screen = blessed.screen({
    smartCSR: true,
    title: 'Timer Manager'
});

const list = blessed.list({
    parent: screen,
    top: 2,
    left: 0,
    width: '100%',
    height: '100%-4',
    keys: true,
    vi: true,
    style: {
        selected: { bg: 'white', fg: 'black' },
        item: { hover: { bg: 'blue' } }
    },
    items: []
});

const status = blessed.text({
    parent: screen,
    bottom: 0,
    left: 0,
    width: '100%',
    height: 3,
    style: { fg: 'white' },
    content: ''
});

const header = blessed.text({
    parent: screen,
    top: 0,
    left: 0,
    width: '100%',
    height: 2,
    style: { fg: 'cyan', bold: true },
    content: '=== Timer Manager ==='
});

const manager = new TimerManager();

function refresh() {
    const items = manager.timers.map((t, i) => {
        const rem = t.remaining();
        const status = t.finished ? ' ✓' : (t.running ? ' ▶' : ' ⏸');
        return `${i+1}. ${t.name} ${status}  ${String(Math.floor(rem/60)).padStart(2,'0')}:${String(Math.floor(rem%60)).padStart(2,'0')} / ${String(Math.floor(t.duration/60)).padStart(2,'0')}:${String(Math.floor(t.duration%60)).padStart(2,'0')}`;
    });
    list.setItems(items);
    list.select(manager.selected);
    status.setContent(`Timers: ${manager.timers.length}   [a]dd  [d]elete  [Space]toggle  [r]eset  [q]uit`);
    screen.render();
}

refresh();

list.on('select', (el, index) => {
    manager.selected = index;
});

screen.key(['q', 'escape'], () => {
    manager.save();
    process.exit(0);
});

screen.key(['a'], () => {
    // simplified: use prompt from blessed
    blessed.prompt({
        parent: screen,
        top: 'center',
        left: 'center',
        width: '50%',
        height: '30%',
        border: { type: 'line' },
        style: { border: { fg: 'cyan' } },
        label: ' Add Timer '
    }, (err, name) => {
        if (name) {
            blessed.prompt({
                parent: screen,
                top: 'center',
                left: 'center',
                width: '50%',
                height: '30%',
                border: { type: 'line' },
                style: { border: { fg: 'cyan' } },
                label: ' Duration (seconds) '
            }, (err, durStr) => {
                if (durStr) {
                    const dur = parseFloat(durStr);
                    if (!isNaN(dur) && dur > 0) {
                        manager.addTimer(name, dur);
                        refresh();
                    }
                }
            });
        }
    });
});

screen.key(['d'], () => {
    if (manager.timers.length > 0) {
        manager.removeTimer(manager.selected);
        refresh();
    }
});

screen.key(['space'], () => {
    if (manager.timers.length > 0) {
        manager.toggle(manager.selected);
        refresh();
    }
});

screen.key(['r'], () => {
    if (manager.timers.length > 0) {
        manager.reset(manager.selected);
        refresh();
    }
});

// Update timer every second
setInterval(() => {
    manager.update();
    refresh();
}, 1000);

list.focus();
screen.render();
