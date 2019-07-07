module Esi

  class GetFactions < Download

    def initialize
      super( 'universe/factions/', {} )
    end

    def get_ids
      get_page.map{ |f| f['faction_id'] }
    end

  end

end
