# timer_manager.rb
require 'io/console'
require 'json'
require 'time'

class Timer
  attr_accessor :name, :duration, :elapsed, :running, :finished

  def initialize(name, duration, elapsed=0, running=false, finished=false)
    @name = name
    @duration = duration
    @elapsed = elapsed
    @running = running
    @finished = finished
  end

  def remaining
    finished ? 0 : [duration - elapsed, 0].max
  end

  def update(dt)
    if running && !finished
      @elapsed += dt
      if @elapsed >= duration
        @elapsed = duration
        @running = false
        @finished = true
        return true
      end
    end
    false
  end

  def to_h
    {name: @name, duration: @duration, elapsed: @elapsed, running: @running, finished: @finished}
  end

  def self.from_h(h)
    new(h['name'], h['duration'], h['elapsed'], h['running'], h['finished'])
  end
end

class TimerManager
  def initialize(save_file='timers.json')
    @save_file = save_file
    @timers = []
    @selected = 0
    @running = true
    @last_update = Time.now
    load
    if @timers.empty?
      @timers << Timer.new("Pomodoro", 25*60)
      @timers << Timer.new("Break", 5*60)
    end
  end

  def add_timer(name, duration)
    @timers << Timer.new(name, duration)
    save
  end

  def remove_timer(idx)
    return if idx < 0 || idx >= @timers.size
    @timers.delete_at(idx)
    @selected = @timers.size-1 if @selected >= @timers.size
    save
  end

  def toggle(idx)
    return if idx < 0 || idx >= @timers.size
    t = @timers[idx]
    if t.finished
      t.elapsed = 0
      t.finished = false
      t.running = true
    else
      t.running = !t.running
    end
    save
  end

  def reset(idx)
    return if idx < 0 || idx >= @timers.size
    t = @timers[idx]
    t.elapsed = 0
    t.running = false
    t.finished = false
    save
  end

  def update
    now = Time.now
    dt = now - @last_update
    @last_update = now
    @timers.each do |t|
      if t.update(dt)
        puts "\n!!! Timer '#{t.name}' finished !!!"
      end
    end
  end

  def save
    File.write(@save_file, JSON.pretty_generate(@timers.map(&:to_h)))
  end

  def load
    if File.exist?(@save_file)
      begin
        data = JSON.parse(File.read(@save_file))
        @timers = data.map { |h| Timer.from_h(h) }
      rescue
        @timers = []
      end
    end
  end

  def run
    system('stty -echo -icanon min 1') rescue nil
    at_exit { system('stty echo icanon'); print "\e[?25h" }
    print "\e[?25l"

    loop do
      print "\e[2J\e[H"
      puts "=== Timer Manager ==="
      puts "Timers: #{@timers.size}   [a]dd  [d]elete  [Space]toggle  [r]eset  [q]uit"

      @timers.each_with_index do |t, i|
        rem = t.remaining
        status = t.finished ? " ✓" : (t.running ? " ▶" : " ⏸")
        line = sprintf("%d. %s %s  %02.0f:%02.0f / %02.0f:%02.0f",
                       i+1, t.name, status, rem/60, rem%60, t.duration/60, t.duration%60)
        if i == @selected
          print "\e[7m"
        else
          color = t.running ? "\e[32m" : (t.finished ? "\e[31m" : "\e[33m")
          print color
        end
        puts line
        print "\e[0m"
      end
      puts "\nCommands: a=add, d=delete, Space=toggle, r=reset, q=quit"

      # Non-blocking input
      begin
        c = STDIN.getc
        case c
        when 'q' then break
        when 'a'
          print "Enter name: "
          name = STDIN.gets.chomp
          print "Enter duration (seconds): "
          dur = STDIN.gets.chomp.to_f
          add_timer(name, dur)
        when 'd'
          remove_timer(@selected) if @timers.any?
        when ' '
          toggle(@selected) if @timers.any?
        when 'r'
          reset(@selected) if @timers.any?
        when "\e"
          c2 = STDIN.getc
          if c2 == '['
            c3 = STDIN.getc
            case c3
            when 'A' then @selected = [0, @selected-1].max
            when 'B' then @selected = [@timers.size-1, @selected+1].min
            end
          end
        end
      rescue
        # no input
      end

      update
      sleep 0.05
    end
    save
    print "\e[?25h"
  end
end

if __FILE__ == $0
  manager = TimerManager.new
  manager.run
end
