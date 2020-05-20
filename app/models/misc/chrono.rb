module Misc
  class Chrono

    def initialize
      @chrono = Time.now
    end

    def p
      Misc::Banner.p to_s
    end

    def pl
      puts to_s
    end

    private

    def to_s
      diff = TimeDifference.between(Time.now, @chrono)
      "#{Process.pid} - Total process duration : " + ( diff.humanize || "#{diff.in_seconds} seconds" )
    end

  end
end