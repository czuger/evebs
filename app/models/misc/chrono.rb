module Misc
  class Chrono

    def initialize
      @chrono = Time.now
    end

    def p
      Misc::Banner.p ('Total process duration : ' + TimeDifference.between(Time.now, @chrono).humanize )
    end

  end
end