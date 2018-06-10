class Esi::UpdateStructures < Esi::Download

  def initialize( debug_request: false )
    super( 'sovereignty/structures/', {}, debug_request: debug_request )
  end

  def update

    Banner.p 'About to update the structures.'

    structures = get_all_pages

    ActiveRecord::Base.transaction do
      structures.each do |structure|
        db_structure = Structure.where( cpp_structure_id: structure['structure_id'] ).first_or_initialize

        th = TradeHub.find_by_eve_system_id( structure['solar_system_id'] )
        if th
          db_structure.trade_hub_id = th.id
          db_structure.save!
        end

      end
    end
  end
end