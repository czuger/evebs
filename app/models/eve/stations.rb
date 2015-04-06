# require 'open-uri'
# require 'open-uri/cached'
require 'pp'

OpenURI::Cache.cache_path = 'tmp'

class Eve::Stations
  def initialize
    @stations = {}
    open( 'http://biotronics.basicaware.de/eve/download/StationID2Name.txt' ) do |file|
      file.readlines.each do |line|
        sl = line.split( "\t" )
        @stations[sl[0]]=sl[1][0..-2].strip
      end
    end
  end
  def name(id)
    @stations[id]
  end
end

