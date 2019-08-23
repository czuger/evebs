module Misc
  class PrintProcessMemUsage

    def initialize
      puts "Process mem : #{GetProcessMem.new.mb.round(0)} Mb"
    end

  end
end