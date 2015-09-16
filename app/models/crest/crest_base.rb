require 'json'

module Crest::CrestBase

  CREST_TMP_DIR='tmp/public-crest.eveonline.com'
  CREST_BASE_URL='https://public-crest.eveonline.com/'

  def manage_cache
    # EAAL::Cache handle the cache for us
    # Refresh the eve central API cache each 4 hours
    # if File.exist?( CREST_TMP_DIR ) && Time.now - File.ctime( CREST_TMP_DIR ) > (3600*24)
    #   `rm -r #{CREST_TMP_DIR}`
    # end
  end

  def get_crest_url( rest )
    "#{CREST_BASE_URL}/#{rest}/"
  end

  def get_parsed_data( rest, debug_request = false )
    html_req = get_crest_url( rest )
    puts "#{self.class}::#{__method__} html_req = #{html_req}" if debug_request
    json_result = open( html_req ).read
    JSON.parse( json_result )
  end

end