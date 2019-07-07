require 'ostruct'

module Esi

  class GetCorporationInfo < Download

    def initialize
      super
      @corporation_infos = {}
    end

    def get( corporation_id )
      unless @corporation_infos[ corporation_id ]
        @rest_url = "corporations/#{corporation_id}/"
        corporation_data = get_page_retry_on_error
        @corporation_infos[corporation_id] = OpenStruct.new( corporation_data )
      end

      @corporation_infos[corporation_id]
    end

  end

end
