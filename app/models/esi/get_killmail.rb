module Esi

  class GetKillmail < Download

    def initialize( killmail_id, killmail_hash )
      super( "killmails/#{killmail_id}/#{killmail_hash}/", {} )
    end

    def get
      get_page_retry_on_error
    end

  end

end
