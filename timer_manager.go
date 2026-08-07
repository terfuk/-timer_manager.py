// timer_manager.go
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"
)

type Timer struct {
	Name     string  `json:"name"`
	Duration float64 `json:"duration"` // seconds
	Elapsed  float64 `json:"elapsed"`
	Running  bool    `json:"running"`
	Finished bool    `json:"finished"`
}

func (t *Timer) Remaining() float64 {
	if t.Finished {
		return 0
	}
	rem := t.Duration - t.Elapsed
	if rem < 0 {
		return 0
	}
	return rem
}

func (t *Timer) Update(dt float64) bool {
	if t.Running && !t.Finished {
		t.Elapsed += dt
		if t.Elapsed >= t.Duration {
			t.Elapsed = t.Duration
			t.Running = false
			t.Finished = true
			return true
		}
	}
	return false
}

type TimerManager struct {
	Timers   []Timer
	Selected int
	SaveFile string
	running  bool
}

func NewTimerManager(saveFile string) *TimerManager {
	tm := &TimerManager{
		Timers:   []Timer{},
		Selected: 0,
		SaveFile: saveFile,
		running:  true,
	}
	tm.Load()
	if len(tm.Timers) == 0 {
		tm.Timers = append(tm.Timers, Timer{Name: "Pomodoro", Duration: 25 * 60, Elapsed: 0, Running: false, Finished: false})
		tm.Timers = append(tm.Timers, Timer{Name: "Break", Duration: 5 * 60, Elapsed: 0, Running: false, Finished: false})
	}
	return tm
}

func (tm *TimerManager) AddTimer(name string, duration float64) {
	tm.Timers = append(tm.Timers, Timer{Name: name, Duration: duration, Elapsed: 0, Running: false, Finished: false})
	tm.Save()
}

func (tm *TimerManager) RemoveTimer(idx int) {
	if idx < 0 || idx >= len(tm.Timers) {
		return
	}
	tm.Timers = append(tm.Timers[:idx], tm.Timers[idx+1:]...)
	if tm.Selected >= len(tm.Timers) {
		tm.Selected = len(tm.Timers) - 1
	}
	tm.Save()
}

func (tm *TimerManager) Toggle(idx int) {
	if idx < 0 || idx >= len(tm.Timers) {
		return
	}
	t := &tm.Timers[idx]
	if t.Finished {
		t.Elapsed = 0
		t.Finished = false
		t.Running = true
	} else {
		t.Running = !t.Running
	}
	tm.Save()
}

func (tm *TimerManager) Reset(idx int) {
	if idx < 0 || idx >= len(tm.Timers) {
		return
	}
	t := &tm.Timers[idx]
	t.Elapsed = 0
	t.Running = false
	t.Finished = false
	tm.Save()
}

func (tm *TimerManager) Update(dt float64) {
	for i := range tm.Timers {
		if tm.Timers[i].Update(dt) {
			fmt.Printf("\n!!! Timer '%s' finished !!!\n", tm.Timers[i].Name)
		}
	}
}

func (tm *TimerManager) Save() {
	data, err := json.MarshalIndent(tm.Timers, "", "  ")
	if err == nil {
		os.WriteFile(tm.SaveFile, data, 0644)
	}
}

func (tm *TimerManager) Load() {
	data, err := os.ReadFile(tm.SaveFile)
	if err == nil {
		json.Unmarshal(data, &tm.Timers)
	}
}

func (tm *TimerManager) Run() {
	scanner := bufio.NewScanner(os.Stdin)
	fmt.Print("\033[?25l") // hide cursor
	defer fmt.Print("\033[?25h")
	lastUpdate := time.Now()

	for tm.running {
		// Clear screen
		fmt.Print("\033[2J\033[H")
		fmt.Println("=== Timer Manager ===")
		fmt.Printf("Timers: %d   [a]dd  [d]elete  [Space]toggle  [r]eset  [q]uit\n", len(tm.Timers))

		// Display timers
		for i, t := range tm.Timers {
			remaining := t.Remaining()
			status := " ▶"
			if t.Finished {
				status = " ✓"
			} else if !t.Running {
				status = " ⏸"
			}
			line := fmt.Sprintf("%d. %s %s  %02.0f:%02.0f / %02.0f:%02.0f",
				i+1, t.Name, status,
				remaining/60, remaining,
				t.Duration/60, t.Duration)
			if i == tm.Selected {
				fmt.Print("\033[7m") // reverse
			}
			fmt.Println(line)
			fmt.Print("\033[0m")
		}
		fmt.Println("\nCommands: a=add, d=delete, Space=toggle, r=reset, q=quit")

		// Input (non-blocking)
		scanner.Scan()
		cmd := scanner.Text()
		switch cmd {
		case "q":
			tm.running = false
		case "a":
			fmt.Print("Enter name: ")
			scanner.Scan()
			name := scanner.Text()
			fmt.Print("Enter duration (seconds): ")
			scanner.Scan()
			durStr := scanner.Text()
			dur, err := strconv.ParseFloat(durStr, 64)
			if err == nil {
				tm.AddTimer(name, dur)
			}
		case "d":
			if len(tm.Timers) > 0 {
				tm.RemoveTimer(tm.Selected)
			}
		case " ":
			if len(tm.Timers) > 0 {
				tm.Toggle(tm.Selected)
			}
		case "r":
			if len(tm.Timers) > 0 {
				tm.Reset(tm.Selected)
			}
		case "\x1b[A": // up
			if tm.Selected > 0 {
				tm.Selected--
			}
		case "\x1b[B": // down
			if tm.Selected < len(tm.Timers)-1 {
				tm.Selected++
			}
		default:
			// ignore
		}

		// Update timers
		now := time.Now()
		dt := now.Sub(lastUpdate).Seconds()
		lastUpdate = now
		tm.Update(dt)
		time.Sleep(50 * time.Millisecond)
	}
	tm.Save()
}

func main() {
	manager := NewTimerManager("timers.json")
	manager.Run()
}
