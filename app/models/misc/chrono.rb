module Misc
  class Chrono

    def initialize
      @chrono = Time.now
    end

    def p
      Misc::Banner.p ("#{Process.pid} - Total process duration : " + TimeDifference.between(Time.now, @chrono).humanize )
    end

    def pl
      puts ("#{Process.pid} - Total process duration : " + TimeDifference.between(Time.now, @chrono).humanize )
    end

  end
end