module Misc
  class Banner

    def self.p( string, with_separation_lines=false )
      out '' if with_separation_lines
      out '*'*100
      out string + ' - ' + Time.now.strftime( '%c')
      out '*'*100
      out '' if with_separation_lines
      STDOUT.flush
      STDERR.flush
    end

    private

    def self.out( string )
      unless Rails.env.test? # Never print banners in test environment
        puts string
        warn string
      end
    end

  end
end
