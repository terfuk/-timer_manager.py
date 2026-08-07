// timer_manager.cs
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;

class Timer
{
    public string Name { get; set; }
    public double Duration { get; set; }
    public double Elapsed { get; set; }
    public bool Running { get; set; }
    public bool Finished { get; set; }

    public double Remaining() => Finished ? 0 : Math.Max(0, Duration - Elapsed);

    public bool Update(double dt)
    {
        if (Running && !Finished)
        {
            Elapsed += dt;
            if (Elapsed >= Duration)
            {
                Elapsed = Duration;
                Running = false;
                Finished = true;
                return true;
            }
        }
        return false;
    }
}

class TimerManager
{
    private List<Timer> timers = new List<Timer>();
    private int selected = 0;
    private bool running = true;
    private string saveFile = "timers.json";
    private DateTime lastUpdate = DateTime.Now;

    public TimerManager()
    {
        Load();
        if (timers.Count == 0)
        {
            timers.Add(new Timer { Name = "Pomodoro", Duration = 25 * 60 });
            timers.Add(new Timer { Name = "Break", Duration = 5 * 60 });
        }
    }

    public void AddTimer(string name, double duration)
    {
        timers.Add(new Timer { Name = name, Duration = duration });
        Save();
    }

    public void RemoveTimer(int idx)
    {
        if (idx < 0 || idx >= timers.Count) return;
        timers.RemoveAt(idx);
        if (selected >= timers.Count) selected = timers.Count - 1;
        Save();
    }

    public void Toggle(int idx)
    {
        if (idx < 0 || idx >= timers.Count) return;
        var t = timers[idx];
        if (t.Finished)
        {
            t.Elapsed = 0;
            t.Finished = false;
            t.Running = true;
        }
        else
        {
            t.Running = !t.Running;
        }
        Save();
    }

    public void Reset(int idx)
    {
        if (idx < 0 || idx >= timers.Count) return;
        var t = timers[idx];
        t.Elapsed = 0;
        t.Running = false;
        t.Finished = false;
        Save();
    }

    public void Update()
    {
        var now = DateTime.Now;
        double dt = (now - lastUpdate).TotalSeconds;
        lastUpdate = now;
        foreach (var t in timers)
        {
            if (t.Update(dt))
            {
                Console.WriteLine($"\n!!! Timer '{t.Name}' finished !!!");
            }
        }
    }

    public void Save()
    {
        string json = JsonConvert.SerializeObject(timers, Formatting.Indented);
        File.WriteAllText(saveFile, json);
    }

    public void Load()
    {
        if (File.Exists(saveFile))
        {
            string json = File.ReadAllText(saveFile);
            timers = JsonConvert.DeserializeObject<List<Timer>>(json) ?? new List<Timer>();
        }
    }

    public void Run()
    {
        Console.CursorVisible = false;
        Console.Clear();
        lastUpdate = DateTime.Now;

        while (running)
        {
            Console.SetCursorPosition(0, 0);
            Console.WriteLine("=== Timer Manager ===");
            Console.WriteLine($"Timers: {timers.Count}   [a]dd  [d]elete  [Space]toggle  [r]eset  [q]uit");

            for (int i=0; i<timers.Count; i++)
            {
                var t = timers[i];
                double rem = t.Remaining();
                string status = t.Finished ? " ✓" : (t.Running ? " ▶" : " ⏸");
                string line = $"{i+1}. {t.Name} {status}  {rem/60:00}:{rem%60:00} / {t.Duration/60:00}:{t.Duration%60:00}";
                if (i == selected)
                {
                    Console.BackgroundColor = ConsoleColor.White;
                    Console.ForegroundColor = ConsoleColor.Black;
                }
                else
                {
                    Console.ResetColor();
                    if (t.Running) Console.ForegroundColor = ConsoleColor.Green;
                    else if (t.Finished) Console.ForegroundColor = ConsoleColor.Red;
                    else Console.ForegroundColor = ConsoleColor.Yellow;
                }
                Console.WriteLine(line);
                Console.ResetColor();
            }
            Console.WriteLine("\nCommands: a=add, d=delete, Space=toggle, r=reset, q=quit");

            if (Console.KeyAvailable)
            {
                var key = Console.ReadKey(true);
                switch (key.Key)
                {
                    case ConsoleKey.Q: running = false; break;
                    case ConsoleKey.A:
                        Console.Write("Enter name: ");
                        string name = Console.ReadLine();
                        Console.Write("Enter duration (seconds): ");
                        if (double.TryParse(Console.ReadLine(), out double dur))
                            AddTimer(name, dur);
                        break;
                    case ConsoleKey.D:
                        if (timers.Count > 0) RemoveTimer(selected);
                        break;
                    case ConsoleKey.Spacebar:
                        if (timers.Count > 0) Toggle(selected);
                        break;
                    case ConsoleKey.R:
                        if (timers.Count > 0) Reset(selected);
                        break;
                    case ConsoleKey.UpArrow:
                        if (selected > 0) selected--;
                        break;
                    case ConsoleKey.DownArrow:
                        if (selected < timers.Count-1) selected++;
                        break;
                }
            }

            Update();
            Thread.Sleep(50);
        }
        Save();
        Console.CursorVisible = true;
    }

    static void Main()
    {
        var tm = new TimerManager();
        tm.Run();
    }
}
