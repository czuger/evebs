module Misc
  class Banner

    def self.p( string )
      out '*'*100
      out string + ' - ' + Time.now.strftime( '%c')
      out '*'*100
      STDOUT.flush
      STDERR.flush
    end

    private

    def self.out( string )
      puts string
      warn string
    end

  end
end
