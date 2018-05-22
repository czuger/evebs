class Banner

  def self.p( string )
    puts '*'*100
    puts string + ' - ' + Time.now.strftime( '%c')
    puts '*'*100
    STDOUT.flush
  end

end