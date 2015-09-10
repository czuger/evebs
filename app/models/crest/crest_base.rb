module Crest::CrestBase

  CREST_TMP_DIR='tmp/public-crest.eveonline.com'
  CREST_BASE_URL='https://public-crest.eveonline.com/'

  def manage_cache
    # Refresh the eve central API cache each 4 hours
    if File.exist?( CREST_TMP_DIR ) && Time.now - File.ctime( CREST_TMP_DIR ) > (3600*24)
      `rm -r #{CREST_TMP_DIR}`
    end
  end

  def get_crest_url( rest )
    "#{CREST_BASE_URL}/#{rest}/"
  end


end