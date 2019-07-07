require 'ostruct'

module Esi

  class GetCharacterInfo < Download

    def initialize
      super
      @character_infos = {}
    end

    def get( character_id )
      unless @character_infos[ character_id ]
        @rest_url = "characters/#{character_id}/"
        character_data = get_page_retry_on_error
        @character_infos[character_id] = OpenStruct.new( character_data )
      end

      @character_infos[character_id]
    end

  end

end
