require 'ostruct'

module Esi

  class GetSystemInfo < Download

    def initialize
      super
      @system_infos = {}
    end

    def get( system_id )
      unless @system_infos[ system_id ]
        @rest_url = "universe/systems/#{system_id}/"

        # p @rest_url
        system_data = get_page_retry_on_error

        # p system_data
        @system_infos[system_id] = OpenStruct.new( system_data )
      end

      @system_infos[system_id]
    end

  end

end
