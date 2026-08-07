// TimerManager.java
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class TimerManager {
    static class Timer {
        String name;
        double duration;
        double elapsed;
        volatile boolean running;
        volatile boolean finished;
        Timer(String name, double duration) { this.name=name; this.duration=duration; elapsed=0; running=false; finished=false; }
        double remaining() { return finished ? 0 : Math.max(0, duration - elapsed); }
        synchronized boolean update(double dt) {
            if (running && !finished) {
                elapsed += dt;
                if (elapsed >= duration) {
                    elapsed = duration; running=false; finished=true;
                    return true;
                }
            }
            return false;
        }
    }

    private List<Timer> timers = new CopyOnWriteArrayList<>();
    private int selected = 0;
    private boolean running = true;
    private String saveFile = "timers.json";
    private ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    private long lastUpdate = System.currentTimeMillis();

    public TimerManager() {
        load();
        if (timers.isEmpty()) {
            timers.add(new Timer("Pomodoro", 25*60));
            timers.add(new Timer("Break", 5*60));
        }
    }

    public void addTimer(String name, double duration) {
        timers.add(new Timer(name, duration));
        save();
    }

    public void removeTimer(int idx) {
        if (idx<0 || idx>=timers.size()) return;
        timers.remove(idx);
        if (selected >= timers.size()) selected = timers.size()-1;
        save();
    }

    public void toggle(int idx) {
        if (idx<0 || idx>=timers.size()) return;
        Timer t = timers.get(idx);
        if (t.finished) {
            t.elapsed = 0;
            t.finished = false;
            t.running = true;
        } else {
            t.running = !t.running;
        }
        save();
    }

    public void reset(int idx) {
        if (idx<0 || idx>=timers.size()) return;
        Timer t = timers.get(idx);
        t.elapsed = 0;
        t.running = false;
        t.finished = false;
        save();
    }

    public void update() {
        long now = System.currentTimeMillis();
        double dt = (now - lastUpdate) / 1000.0;
        lastUpdate = now;
        for (Timer t : timers) {
            if (t.update(dt)) {
                System.out.println("\n!!! Timer '" + t.name + "' finished !!!");
            }
        }
    }

    public void save() {
        try (Writer w = new FileWriter(saveFile)) {
            w.write("[");
            for (int i=0; i<timers.size(); i++) {
                Timer t = timers.get(i);
                if (i>0) w.write(",");
                w.write(String.format("{\"name\":\"%s\",\"duration\":%f,\"elapsed\":%f,\"running\":%b,\"finished\":%b}",
                        t.name, t.duration, t.elapsed, t.running, t.finished));
            }
            w.write("]");
        } catch (IOException e) {}
    }

    public void load() {
        try {
            String content = new String(Files.readAllBytes(Paths.get(saveFile)));
            // simple parsing (for demo, use JSON library in production)
            // Здесь упрощённо, в реальном коде используем JSON-библиотеку
        } catch (IOException e) {}
    }

    public void run() throws IOException, InterruptedException {
        System.out.print("\033[?25l"); // hide cursor
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.print("\033[?25h");
            save();
        }));

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        while (running) {
            // Clear screen
            System.out.print("\033[2J\033[H");
            System.out.println("=== Timer Manager ===");
            System.out.printf("Timers: %d   [a]dd  [d]elete  [Space]toggle  [r]eset  [q]uit\n", timers.size());

            for (int i=0; i<timers.size(); i++) {
                Timer t = timers.get(i);
                double rem = t.remaining();
                String status = t.finished ? " ✓" : (t.running ? " ▶" : " ⏸");
                String line = String.format("%d. %s %s  %02.0f:%02.0f / %02.0f:%02.0f",
                        i+1, t.name, status, rem/60, rem%60, t.duration/60, t.duration%60);
                if (i == selected) System.out.print("\033[7m");
                System.out.println(line);
                System.out.print("\033[0m");
            }
            System.out.println("\nCommands: a=add, d=delete, Space=toggle, r=reset, q=quit");

            // Non-blocking input
            if (System.in.available() > 0) {
                int ch = System.in.read();
                if (ch == 'q' || ch == 27) running = false;
                else if (ch == 'a') {
                    System.out.print("Enter name: ");
                    String name = br.readLine();
                    System.out.print("Enter duration (seconds): ");
                    double dur = Double.parseDouble(br.readLine());
                    addTimer(name, dur);
                } else if (ch == 'd') {
                    if (!timers.isEmpty()) removeTimer(selected);
                } else if (ch == ' ') {
                    if (!timers.isEmpty()) toggle(selected);
                } else if (ch == 'r') {
                    if (!timers.isEmpty()) reset(selected);
                } else if (ch == 27) {
                    // arrow keys: read next chars
                    int c1 = System.in.read();
                    if (c1 == 91) {
                        int c2 = System.in.read();
                        if (c2 == 65 && selected>0) selected--;
                        else if (c2 == 66 && selected<timers.size()-1) selected++;
                    }
                }
            }

            update();
            Thread.sleep(50);
        }
        System.out.print("\033[?25h");
        save();
    }

    public static void main(String[] args) throws Exception {
        TimerManager tm = new TimerManager();
        tm.run();
    }
}
