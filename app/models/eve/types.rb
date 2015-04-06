# require 'open-uri'
# require 'open-uri/cached'
require 'pp'

OpenURI::Cache.cache_path = 'tmp'

class Eve::Types
  def initialize
    @types = {}
    open( 'http://eve-files.com/chribba/typeid.txt' ) do |file|
      file.readlines.each do |line|
        # pp line
        key = line[0..11]
        value = line[12..-2]
        @types[key.strip]=value.strip if value
      end
    end
  end
  def name(id)
    @types[id]
  end
end