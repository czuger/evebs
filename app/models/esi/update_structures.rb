class Esi::UpdateStructures < Esi::Download

  def initialize( debug_request: false )
    super( 'universe/structures/', {}, debug_request: debug_request )
  end

  def update

    Banner.p 'About to update the structures.'

    set_auth_token

    structures_ids = get_all_pages

    structures_ids -= Structure.pluck( :cpp_structure_id )

    ActiveRecord::Base.transaction do
      structures_ids.each do |structure_id|

        @rest_url = "universe/structures/#{structure_id.to_s}/"
        forbidden = false
        structure_data = nil
        begin
          structure_data = get_page
        rescue Esi::Errors::Forbidden
          forbidden = true
        end

        db_structure = Structure.where( cpp_structure_id: structure_id ).first_or_initialize

        db_structure.forbidden = forbidden

        unless forbidden
          pp structure_data
          exit
          # db_structure.trade_hub_id = TradeHub.find_by_eve_system_id( structure['solar_system_id'] )
          # if th
          #    = th.id
          # end
        end
        db_structure.save!


      end
    end
  end
end